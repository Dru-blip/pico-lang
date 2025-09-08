# semantic analyzer

from hir import Cast, HirNodeTag
from pico_ast import OpTag
from pico_types import TypeRegistry


class Sema:
    def __init__(self, block):
        self.block = block
        self.type_registry: TypeRegistry = TypeRegistry.get_instance()

    def analyze(self):
        for node in self.block.nodes:
            self._analyze_function_block(node)

    def _analyze_function_block(self, fb):
        for node in fb.nodes:
            self._analyze_stmt(node)

    def _analyze_stmt(self, node):
        kind = node.kind
        if kind == HirNodeTag.Return:
            # ret_type = self.type_registry.get_ret_type(node.func_type)
            # if node.expr:
            #     val_type = self._analyze_expr(node.expr)
            #     # TODO: check for type compatibility for cast
            #     if val_type != ret_type:
            #         node.expr = Cast(node.token, node.expr, val_type, ret_type)
            node.type_id = TypeRegistry.VoidType
        elif kind == HirNodeTag.Log:
            self._analyze_expr(node.expr)
        elif kind == HirNodeTag.Block:
            for stmt in node.nodes:
                self._analyze_stmt(stmt)
        elif kind == HirNodeTag.LoopBlock:
            for stmt in node.nodes:
                self._analyze_stmt(stmt)
        elif kind == HirNodeTag.Branch:
            # TODO: check if condition expr type is boolean else insert BoolCast
            cond_type = self._analyze_expr(node.condition)
            self._analyze_stmt(node.then_block)
            if node.else_block:
                self._analyze_stmt(node.else_block)
        elif kind == HirNodeTag.StoreLocal:
            type_id = self._analyze_expr(node.value)
            if not node.symbol.type:
                node.symbol.type = type_id
        elif kind == HirNodeTag.Break or kind == HirNodeTag.Continue:
            pass
        else:
            self._analyze_expr(node)

    def _analyze_expr(self, node):
        kind = node.kind
        if kind == HirNodeTag.ConstInt:
            return TypeRegistry.IntType
        elif kind == HirNodeTag.VarRef:
            return node.symbol.type
        elif kind == HirNodeTag.BinOp:
            left_type = self._analyze_expr(node.lhs)
            right_type = self._analyze_expr(node.rhs)
            if node.op_tag in [OpTag.AND, OpTag.OR]:
                if left_type == TypeRegistry.BoolType and left_type != right_type:
                    raise Exception(f"Error: both operand types should be boolean for logical operators")
                node.type_id = left_type
                return node.type_id

            if node.op_tag in [OpTag.EQ, OpTag.NEQ, OpTag.LT, OpTag.LTE, OpTag.GT, OpTag.GTE]:
                node.type_id = TypeRegistry.BoolType
                return node.type_id

            wider_type = self.type_registry.get_common_type(left_type, right_type)
            if wider_type == TypeRegistry.NoneType:
                raise Exception(f"Error: cannot perform {node.op_tag.lower()} on incompatible types")

            if left_type != wider_type:
                node.lhs = Cast(node.lhs.token, node.lhs, left_type, wider_type)

            if right_type != wider_type:
                node.rhs = Cast(node.rhs.token, node.rhs, right_type, wider_type)

            node.type_id = wider_type
            return node.type_id
        elif kind == HirNodeTag.Call:
            if node.calle.kind != HirNodeTag.VarRef:
                raise Exception("Uncallable expression")
            for arg in node.args:
                # TODO: check for type compatibility of args
                arg_type = self._analyze_expr(arg)
            return self.type_registry.get_ret_type(node.calle.symbol.type)
        else:
            print(node)
            raise Exception(f"implementation error: cannot analyze node: {node.kind} yet")
