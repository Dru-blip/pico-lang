from typing import Optional

from pico_ast import Program, FunctionDeclaration, FunctionPrototype, Param, Block, Return, IntLiteral, Identifier, \
    NodeTag
from hir import BinOp, HirBlock, FunctionBlock, Return as HirReturn, ConstInt, HirNodeTag, HirLog, StoreLocal, BlockTag, \
    VarRef, Branch
from pico_types import TypeRegistry
from symtab import Symbol, SymbolKind


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

    def generate(self):
        for node in self.program.nodes:
            self._gen_function(node)
        return self.global_block

    def _begin_scope(self):
        self.scope_depth += 1

    def _end_scope(self):
        self.scope_depth -= 1

    def _gen_function(self, node: FunctionDeclaration):
        self._begin_scope()
        func_symbol = self._gen_fn_prototype(node.proto, node.body is not None)
        if node.body:
            func_symbol.is_defined = True
            self.function_block = FunctionBlock(
                node.proto.name,
                symbol=func_symbol,
                type_id=func_symbol.type,
                parent=self.global_block,
                scope_depth=self.scope_depth
            )
            self.current_block = self.function_block

            # Add parameters
            for index, param in enumerate(node.proto.params):
                self.function_block.symbols[param.name] = Symbol(param.name, SymbolKind.Parameter, param.type,
                                                                 self.scope_depth)

            self._generate_stmt(node.body)
            self.global_block.add_node(self.function_block)
            self.function_block = None
            self.current_block = None
        self._end_scope()

    def _gen_fn_prototype(self, proto: FunctionPrototype, has_body: bool):
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
                raise Exception("Incompatible function declarations")
            already_defined = old_decl.is_defined
            if already_defined and has_body:
                raise Exception(f"Function {proto.name} already defined")

        func_symbol = Symbol(proto.name, SymbolKind.Function, func_type_id, 0)
        func_symbol.is_defined = already_defined or has_body
        self.global_block.symbols[proto.name] = func_symbol
        return func_symbol

    def _generate_var_decl(self, node):
        if node.type_:
            type_id = self._transform_type(node.type_)
        else:
            type_id = TypeRegistry.NoneType
        name = self.current_block.resolve(node.name)

        if name and name.scope_depth == self.scope_depth:
            raise Exception(f"duplicate variable decl {name.name}")

        if name:
            symbol = Symbol(
                self._make_unique_name(node.name),
                SymbolKind.Variable,
                type_id,
                self.scope_depth,
            )
            self.current_block.name_map[node.name] = symbol
        else:
            symbol = Symbol(
                node.name,
                SymbolKind.Variable,
                type_id,
                self.scope_depth,
            )

        self.current_block.add_symbol(symbol)
        value = self._generate_expr(node.init)

        # self.current_block.add_node(
        #     Alloca(symbol.name, type_id, symbol, node.token)
        # )
        self.current_block.add_node(
            StoreLocal(symbol.name, node.token, symbol, value)
        )
        symbol.local_offset = self.function_block.local_count
        self.function_block.local_count += 1

    def _generate_stmt(self, node):
        if node.tag == NodeTag.Block:
            self._generate_block(node)
        elif node.tag == NodeTag.If:
            self._generate_if_stmt(node)
        elif node.tag == NodeTag.Return:
            self._generate_return(node)
        elif node.tag == NodeTag.Log:
            self._generate_log(node)
        elif node.tag == NodeTag.VarDecl:
            self._generate_var_decl(node)
        elif node.tag == NodeTag.ExprStmt:
            self.current_block.add_node(self._generate_expr(node.expr))
        else:
            raise NotImplementedError(f"Statement {node.tag} not implemented")

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
        expr = self._generate_expr(node.expr)
        self.current_block.add_node(HirReturn(node.token, expr))

    def _generate_log(self, node: HirLog):
        expr = self._generate_expr(node.expr)
        self.current_block.add_node(HirLog(node.token, expr))

    def _generate_expr(self, node):
        if node.tag == NodeTag.IntLiteral:
            return ConstInt(node.value)
        elif node.tag == NodeTag.Identifier:
            symbol = self.current_block.name_map.get(node.name)
            if symbol:
                return VarRef(node.token, symbol)

            symbol = self.current_block.resolve(node.name)
            if not symbol:
                raise Exception(f"undeclared identifier {node.name}")

            return VarRef(node.token, symbol)
        elif node.tag == NodeTag.BinOp:
            lhs = self._generate_expr(node.lhs)
            rhs = self._generate_expr(node.rhs)
            return BinOp(node.token, node.op_tag, lhs, rhs)
        elif node.tag == NodeTag.Assignment:
            lhs = self._generate_expr(node.target)
            rhs = self._generate_expr(node.val)
            return StoreLocal(lhs.symbol.name, node.token, lhs.symbol, rhs)
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
        raise Exception(f"Unknown type {type_node.name}")

    def _make_unique_name(self, name: str) -> str:
        unique_name = f"{name}{self.var_id_counter}"
        self.var_id_counter += 1
        return unique_name
