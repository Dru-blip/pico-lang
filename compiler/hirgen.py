from typing import Optional
from pico_ast import Program, FunctionDeclaration, FunctionPrototype, Param, Block, Return, IntLiteral, Identifier, \
    NodeTag
from hir import BinOp, HirBlock, FunctionBlock, Return as HirReturn, ConstInt, HirNodeTag
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
        self.global_block = HirBlock("Global")
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

    def _generate_stmt(self, node):
        if node.tag == NodeTag.Block:
            self._generate_block(node)
        elif node.tag == NodeTag.Return:
            self._generate_return(node)
        else:
            raise NotImplementedError(f"Statement {node.tag} not implemented")

    def _generate_block(self, node: Block):
        self._begin_scope()
        block = HirBlock(BlockLabelGenerator.temp(), parent=self.current_block, scope_depth=self.scope_depth)
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

    def _generate_expr(self, node):
        if node.tag == NodeTag.IntLiteral:
            return ConstInt(node.value)
        elif node.tag == NodeTag.Identifier:
            symbol = self.current_block.symbols.get(node.name)
            if not symbol:
                raise Exception(f"Undeclared identifier {node.name}")
            return symbol
        elif node.tag==NodeTag.BinOp:
            return BinOp(node.token,node.op_tag,node.lhs,node.rhs)
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
