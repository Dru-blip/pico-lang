from typing import Optional

from function_id import FunctionIdGenerator
from hir import BinOp, HirBlock, FunctionBlock, Return as HirReturn, ConstInt, HirNodeTag, HirLog, StoreLocal, BlockTag, \
    VarRef, Branch, LoopBlock, Continue, Break, Call, HirExternalLibBlock, ConstStr, ConstBool, StaticAccess, \
    FieldValue, CreateStruct, FieldAccess, Cast, UnOp, StoreField
from pico_ast import Program, FunctionDeclaration, FunctionPrototype, Block, Return, NodeTag, OpTag
from pico_error import PicoError
from pico_types import TypeRegistry
from symtab import Symbol, SymbolKind, Linkage


class BlockLabelGenerator:
    counter = 0
    temp_counter = 0
    default_prefix = "block"

    @classmethod
    def next(cls, prefix=None):
        p = prefix or cls.default_prefix
        val = f".L{p}{cls.counter}"
        cls.counter += 1
        return val

    @classmethod
    def temp(cls):
        val = f".LBB{cls.temp_counter}"
        cls.temp_counter += 1
        return val


class HirGen:
    def __init__(self, program: Program):
        self.program = program
        self.global_block = HirBlock(HirNodeTag.Block, "Global", None, BlockTag.Global, 0, None)
        self.type_registry = TypeRegistry.get_instance()
        self.function_block: Optional[FunctionBlock] = None
        self.current_block: Optional[HirBlock] = None
        self.scope_depth = 0
        self.var_id_counter = 0
        self.loop_stack = []
        self.loop_counter = 0
        self.function_id_gen = FunctionIdGenerator.get_instance()

    def _type_gen_pass(self):
        """
        iterate through top level nodes and when struct decl appears add it to the type registery
        :return:None
        """
        for node in self.program.nodes:
            if node.tag == NodeTag.StructDecl:
                struct_type = self.type_registry.add_incomplete_struct()
                self.global_block.add_symbol(Symbol(node.name, SymbolKind.Struct, struct_type))
            continue

    def generate(self):
        self._type_gen_pass()
        for node in self.program.nodes:
            self._gen_decl(node)
        return self.global_block

    def _begin_scope(self):
        self.scope_depth += 1

    def _end_scope(self):
        self.scope_depth -= 1

    def _gen_decl(self, node):
        if node.tag == NodeTag.ExternLibBlock:
            symbols = []
            for decl in node.decls:
                symbol = self._gen_fn_prototype(decl, has_body=False, linkage=Linkage.External)
                symbol.lib_prefix = node.lib_prefix
                symbols.append(symbol)
            module_symbol = Symbol(node.lib_prefix, SymbolKind.Module, 0, self.scope_depth)
            self.global_block.add_symbol(module_symbol)
            self.global_block.add_node(HirExternalLibBlock(node.token, node.lib_prefix, module_symbol, symbols))
        elif node.tag == NodeTag.StructDecl:
            fields = []
            for i, field in enumerate(node.fields):
                field_type = self._transform_type(field.type)
                field_name = field.name.value
                field_symbol = Symbol(field_name, SymbolKind.StructField, field_type)
                field_symbol.field_index = i
                fields.append(field_symbol)
            struct_symbol = self.global_block.resolve(node.name)
            struct_type = self.type_registry.get_type(struct_symbol.type)
            struct_type.fields = fields
            struct_type.is_complete = True
            struct_symbol.fields = fields
            self.global_block.add_symbol(struct_symbol)
        else:
            self._gen_function(node)

    def _gen_function(self, node: FunctionDeclaration):
        self._begin_scope()
        func_symbol = self._gen_fn_prototype(node.proto, node.body is not None)
        if node.body:
            func_symbol.is_defined = True
            func_symbol.function_id = self.function_id_gen.get_next_id()
            self.function_block = FunctionBlock(
                func_symbol.function_id,
                node.proto.name,
                symbol=func_symbol,
                type_id=func_symbol.type,
                parent=self.global_block,
                scope_depth=self.scope_depth
            )
            self.current_block = self.function_block

            # Add parameters
            for index, param in enumerate(node.proto.params):
                sym = Symbol(param.name, SymbolKind.Parameter, param.type,
                             self.scope_depth)
                self.function_block.symbols[param.name] = sym
                sym.local_offset = self.function_block.local_count
                self.function_block.local_count += 1

            self._generate_stmt(node.body)
            self.global_block.add_node(self.function_block)
            self.function_block = None
            self.current_block = None
        self._end_scope()

    def _gen_fn_prototype(self, proto: FunctionPrototype, has_body: bool = True, linkage: Linkage = Linkage.Internal):
        # Transform return type
        return_type_id = self._transform_type(proto.returnType)
        params = []
        for param in proto.params:
            param_type = self._transform_type(param.type)
            params.append(Symbol(param.name, SymbolKind.Parameter, param_type, self.scope_depth))

        func_type_id = self.type_registry.add_function(return_type_id, params)

        # Check for previous declarations
        old_decl = self.global_block.symbols.get(proto.name)
        already_defined = False
        if old_decl:
            if old_decl.type != func_type_id:
                raise PicoError("Incompatible function declarations", proto.token)
            already_defined = old_decl.is_defined
            if already_defined and has_body:
                raise PicoError(f"Function {proto.name} already defined", proto.token)

        func_symbol = Symbol(proto.name, SymbolKind.Function, func_type_id, 0)
        func_symbol.params = params
        func_symbol.linkage = linkage
        func_symbol.is_defined = already_defined or has_body
        self.global_block.symbols[proto.name] = func_symbol
        return func_symbol

    def _generate_var_decl(self, node):
        if node.type_:
            type_id = self._transform_type(node.type_)
        else:
            type_id = TypeRegistry.NoneType

        existing = self.current_block.symbols.get(node.name)
        if existing and existing.scope_depth == self.scope_depth:
            raise PicoError(f"duplicate variable decl {node.name}", node.token)

        symbol = Symbol(
            node.name,
            SymbolKind.Variable,
            type_id,
            self.scope_depth,
        )

        self.current_block.add_symbol(symbol)
        value = self._generate_expr(node.init)

        self.current_block.add_node(
            StoreLocal(node.name, node.token, None, value)
        )
        symbol.local_offset = self.function_block.local_count
        self.function_block.local_count += 1

    def _generate_stmt(self, node):
        if node.tag == NodeTag.Block:
            self._generate_block(node)
        elif node.tag == NodeTag.If:
            self._generate_if_stmt(node)
        elif node.tag == NodeTag.LoopStmt:
            self._generate_loop_stmt(node)
        elif node.tag == NodeTag.WhileLoopStmt:
            self._generate_while_loop(node)
        elif node.tag == NodeTag.Return:
            self._generate_return(node)
        elif node.tag == NodeTag.Log:
            self._generate_log(node)
        elif node.tag == NodeTag.Continue:
            self._generate_continue(node)
        elif node.tag == NodeTag.Break:
            self._generate_break(node)
        elif node.tag == NodeTag.VarDecl:
            self._generate_var_decl(node)
        elif node.tag == NodeTag.ExprStmt:
            self.current_block.add_node(self._generate_expr(node.expr))
        else:
            raise NotImplementedError(f"Statement {node.tag} not implemented")

    def _generate_while_loop(self, node):
        self._begin_scope()
        loop_id = self._next_loop_id()

        # desugar while loop into generic loop construct
        """
            while(cond){
                loop_body            
            }
            
            into 
            
            loop{
                if(!cond)break;
                loop_body
            }
        """
        loop_block = LoopBlock(
            BlockLabelGenerator.next("loop"),
            loop_id,
            node.token,
            self.current_block,
            self.scope_depth,
        )
        self.current_block.add_node(loop_block)
        self.current_block = loop_block
        self.loop_stack.append(loop_id)

        # desugar start
        # invert the condtion and create loop break block
        condition_val = self._generate_expr(node.condition)
        inverted_condition = UnOp(condition_val.token, OpTag.Not, condition_val)
        break_block = HirBlock(
            HirNodeTag.Block,
            BlockLabelGenerator.next("while_break"),
            node.token,
            BlockTag.Local,
            self.scope_depth,
            self.current_block,
        )
        break_block.add_node(Break(node.token, loop_id))

        # branch: if (!cond) break
        self.current_block.add_node(
            Branch(
                node.token,
                inverted_condition,
                break_block,
                None,
                BlockLabelGenerator.next("while_merge"),
            )
        )
        self._generate_stmt(node.body)
        self.loop_stack.pop()
        self._end_scope()
        self.current_block = self.current_block.parent

    def _generate_loop_stmt(self, node):
        self._begin_scope()
        loop_id = self._next_loop_id()
        loop_block = LoopBlock(BlockLabelGenerator.next("loop"), loop_id, node.token, self.current_block,
                               self.scope_depth)
        self.current_block.add_node(loop_block)
        self.current_block = loop_block
        self.loop_stack.append(loop_id)
        self._generate_stmt(node.body)
        self.loop_stack.pop()
        self._end_scope()
        self.current_block = self.current_block.parent

    def _generate_continue(self, node):
        if len(self.loop_stack) == 0:
            raise PicoError("continue statement out of side", node.token)
        self.current_block.add_node(Continue(node.token, self.loop_stack[-1]))

    def _generate_break(self, node):
        if len(self.loop_stack) == 0:
            raise PicoError("break statement out of side", node.token)
        self.current_block.add_node(Break(node.token, self.loop_stack[-1]))

    def _generate_if_stmt(self, node):
        condition = self._generate_expr(node.condition)

        # then block
        self._begin_scope()
        then_block = HirBlock(
            HirNodeTag.Block,
            BlockLabelGenerator.next("then"),
            node.token,
            BlockTag.Local,
            self.scope_depth,
            self.current_block,
        )
        self.current_block = then_block
        self._generate_stmt(node.then_stmt)
        self._end_scope()
        self.current_block = self.current_block.parent

        # else block (optional)
        else_block = None
        if node.else_stmt:
            self._begin_scope()
            else_block = HirBlock(
                HirNodeTag.Block,
                BlockLabelGenerator.next("else"),
                node.token,
                BlockTag.Local,
                self.scope_depth,
                self.current_block,
            )
            self.current_block = else_block
            self._generate_stmt(node.else_stmt)
            self._end_scope()
            self.current_block = self.current_block.parent

        # branch node
        self.current_block.add_node(
            Branch(
                node.token,
                condition,
                then_block,
                else_block,
                BlockLabelGenerator.next("merge"),
            )
        )

    def _generate_block(self, node: Block):
        self._begin_scope()
        block = HirBlock(HirNodeTag.Block, BlockLabelGenerator.temp(), node.token, block_tag=BlockTag.Local,
                         parent=self.current_block, scope_depth=self.scope_depth)
        if self.current_block:
            self.current_block.add_node(block)
        self.current_block = block
        for stmt in node.stmts:
            self._generate_stmt(stmt)
        self._end_scope()
        self.current_block = block.parent

    def _generate_return(self, node: Return):
        expr = None
        if node.expr:
            expr = self._generate_expr(node.expr)
        self.current_block.add_node(HirReturn(node.token, expr))

    def _generate_log(self, node: HirLog):
        expr = self._generate_expr(node.expr)
        self.current_block.add_node(HirLog(node.token, expr))

    def _generate_expr(self, node):
        if node.tag == NodeTag.IntLiteral:
            return ConstInt(node.value)
        elif node.tag == NodeTag.StrLiteral:
            return ConstStr(node.value)
        elif node.tag == NodeTag.BoolLiteral:
            return ConstBool(node.value)
        elif node.tag == NodeTag.Identifier:
            return VarRef(node.token, node.name)
        elif node.tag == NodeTag.UnOp:
            expr = self._generate_expr(node.expr)
            return UnOp(node.token, node.op_tag, expr)
        elif node.tag == NodeTag.BinOp:
            lhs = self._generate_expr(node.lhs)
            rhs = self._generate_expr(node.rhs)
            return BinOp(node.token, node.op_tag, lhs, rhs)
        elif node.tag == NodeTag.Assignment:
            target = self._generate_expr(node.target)
            value = self._generate_expr(node.val)
            if target.kind == HirNodeTag.VarRef:
                return StoreLocal(target.name, node.token, None, value)
            if target.kind == HirNodeTag.FieldAccess:
                return StoreField(node.token, target.obj, target.target, value)
            raise PicoError("invalid assignment target", node.token)
        elif node.tag == NodeTag.CompoundAssignment:
            target = self._generate_expr(node.target)
            value = self._generate_expr(node.val)

            if isinstance(target, VarRef):
                return StoreLocal(
                    target.name,
                    node.token,
                    None,
                    BinOp(node.val.token, node.op_tag, target, value)
                )
            elif isinstance(target, FieldAccess):
                return StoreField(
                    node.token,
                    target.obj,
                    target.target,
                    BinOp(node.val.token, node.op_tag, target, value)
                )
            else:
                raise PicoError("Invalid assignment target", node.token)
        elif node.tag == NodeTag.Call:
            callee = self._generate_expr(node.calle)
            args = []
            for arg in node.args:
                args.append(self._generate_expr(arg))
            return Call(node.token, callee, args)
        elif node.tag == NodeTag.StaticAccess:
            qualifier = self._generate_expr(node.qualifier)
            name = self._generate_expr(node.name)
            return StaticAccess(node.token, qualifier, name)
        elif node.tag == NodeTag.FieldAccess:
            obj = self._generate_expr(node.obj)
            return FieldAccess(node.token, obj, node.target)
        elif node.tag == NodeTag.StructLiteral:
            name = self._generate_expr(node.name)
            field_values = []
            for field in node.values:
                field_value = self._generate_expr(field.value)
                field_values.append(FieldValue(field.name, field_value))
            return CreateStruct(node.token, name, field_values)
        elif node.tag == NodeTag.Cast:
            expr = self._generate_expr(node.expr)
            type_id = self._transform_type(node.target_type)
            # from_type will be later set by sema after. for now leave it as NoneType
            return Cast(node.token, expr, TypeRegistry.NoneType, type_id)
        else:
            raise NotImplementedError(f"Expression {node.tag} not implemented")

    def _transform_type(self, type_node):
        if type_node.tag == NodeTag.NamedType:
            if type_node.name == "void":
                return TypeRegistry.VoidType
            elif type_node.name == "int":
                return TypeRegistry.IntType
            elif type_node.name == "long":
                return TypeRegistry.LongType
            elif type_node.name == "str":
                return TypeRegistry.StrType
            elif type_node.name == "bool":
                return TypeRegistry.BoolType
            else:
                type_symbol = self.global_block.resolve(type_node.name)
                if not type_symbol:
                    raise PicoError(f"Unknown type {type_node.name}", type_node.token)
                if type_symbol.kind != SymbolKind.Struct:
                    raise PicoError(f"Unknown type {type_node.name}", type_node.token)
                return type_symbol.type

        raise PicoError(f"Unknown type {type_node.name}", type_node.token)

    def _make_unique_name(self, name: str) -> str:
        unique_name = f"{name}{self.var_id_counter}"
        self.var_id_counter += 1
        return unique_name

    def _next_loop_id(self) -> int:
        next_id = self.loop_counter
        self.loop_counter += 1
        return next_id
