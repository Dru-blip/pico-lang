# semantic analyzer
from hir import Cast, HirNodeTag, BoolCast
from pico_ast import OpTag
from pico_error import PicoError
from pico_types import TypeRegistry
from symtab import Symbol


class Sema:
    def __init__(self, block):
        self.block = block
        self.type_registry: TypeRegistry = TypeRegistry.get_instance()
        self.function_block = None

    def analyze(self):
        for node in self.block.nodes:
            if node.kind == HirNodeTag.ExternLibBlock:
                continue
            self._analyze_function_block(node)

    def _analyze_function_block(self, fb):
        self.function_block = fb
        for node in fb.nodes:
            self._analyze_stmt(node)

    def _analyze_stmt(self, node):
        kind = node.kind
        if kind == HirNodeTag.Return:
            self._analyze_return(node)
        elif kind == HirNodeTag.Log:
            self._analyze_expr(node.expr)
        elif kind == HirNodeTag.Block:
            for stmt in node.nodes:
                self._analyze_stmt(stmt)
        elif kind == HirNodeTag.LoopBlock:
            for stmt in node.nodes:
                self._analyze_stmt(stmt)
        elif kind == HirNodeTag.Branch:
            self._analyze_branch(node)
        elif kind == HirNodeTag.StoreLocal:
            self._analyze_storelocal(node)
        elif kind == HirNodeTag.Break or kind == HirNodeTag.Continue:
            pass
        else:
            self._analyze_expr(node)

    def _analyze_branch(self, node):
        cond_type = self._analyze_expr(node.condition)
        if cond_type not in [TypeRegistry.BoolType, TypeRegistry.IntType, TypeRegistry.LongType]:
            raise PicoError(
                f"condition should be of type {self.type_registry.get_type(TypeRegistry.BoolType).kind} or {self.type_registry.get_type(TypeRegistry.IntType).kind}",
                node.token)
        if cond_type in [TypeRegistry.IntType, TypeRegistry.LongType]:
            node.condition = BoolCast(node.condition.token, node.condition)
        self._analyze_stmt(node.then_block)
        if node.else_block:
            self._analyze_stmt(node.else_block)

    def _analyze_storelocal(self, node):
        type_id = self._analyze_expr(node.value)
        if not node.symbol.type:
            node.symbol.type = type_id
            node.type_id = type_id
        else:
            result_type = self.type_registry.get_assignment_type(node.symbol.type, type_id)
            if result_type == TypeRegistry.NoneType:
                raise PicoError(
                    f"Cannot assign {self.type_registry.get_type(type_id).kind} to {self.type_registry.get_type(node.symbol.type).kind}",
                    node.token
                )
            if type_id != result_type:
                node.value = Cast(node.value.token, node.value, type_id, result_type)

            node.type_id = result_type

        return node.type_id

    def _analyze_return(self, node):
        tr = self.type_registry
        ret_type = tr.get_ret_type(self.function_block.function_id)

        if node.expr:
            val_type = self._analyze_expr(node.expr)
            result_type = tr.get_assignment_type(ret_type, val_type)

            if result_type == TypeRegistry.NoneType:
                raise PicoError(
                    f"Return type mismatch: expected {tr.get_type(ret_type).kind}, got {tr.get_type(val_type).kind}",
                    node.token
                )

            if val_type != result_type:
                node.expr = Cast(node.token, node.expr, val_type, result_type)

            node.type_id = result_type
        else:
            node.type_id = TypeRegistry.VoidType

    def _analyze_expr(self, node):
        kind = node.kind
        if kind == HirNodeTag.ConstInt:
            return TypeRegistry.IntType
        elif kind == HirNodeTag.ConstBool:
            return TypeRegistry.BoolType
        elif kind == HirNodeTag.ConstStr:
            return TypeRegistry.StrType
        elif kind == HirNodeTag.VarRef:
            return node.symbol.type
        elif kind == HirNodeTag.BinOp:
            return self._analyze_binop(node)
        elif kind == HirNodeTag.Call:
            return self._analyze_call(node)
        elif kind == HirNodeTag.StoreLocal:
            return self._analyze_storelocal(node)
        else:
            raise Exception(f"implementation error: cannot analyze node: {node.kind} yet")

    def _analyze_call(self, node):
        if node.calle.kind != HirNodeTag.VarRef and node.calle.kind != HirNodeTag.StaticAccess:
            raise PicoError("Uncallable expression", node.token)

        if node.calle.kind == HirNodeTag.VarRef:
            function_symbol = node.calle.symbol
            params = function_symbol.params
            return_type = self.type_registry.get_ret_type(function_symbol.type)
        else:
            qualifier_symbol: Symbol = node.calle.qualifier.symbol
            function_symbol = qualifier_symbol.blockRef.resolve(node.calle.name.symbol.name)
            params = function_symbol.params
            return_type = self.type_registry.get_ret_type(function_symbol.type)

        new_args = []
        for arg, param in zip(node.args, params):
            arg_type = self._analyze_expr(arg)
            result_type = self.type_registry.get_assignment_type(param.type,
                                                                 arg_type)
            if result_type == TypeRegistry.NoneType:
                raise PicoError(
                    f"Argument type mismatch: expected {self.type_registry.get_type(param.type).kind}, got {self.type_registry.get_type(arg_type).kind}",
                    node.token
                )
            if arg_type != result_type:
                arg = Cast(arg.token, arg, arg_type, result_type)
            new_args.append(arg)
        node.function_symbol = function_symbol
        node.args = new_args
        return return_type

    def _analyze_binop(self, node):
        left_type = self._analyze_expr(node.lhs)
        right_type = self._analyze_expr(node.rhs)

        tr = self.type_registry

        if node.op_tag in [OpTag.AND, OpTag.OR]:
            result_type = tr.get_logical_type(left_type, right_type)
            if result_type == TypeRegistry.NoneType:
                raise PicoError(
                    f"Error: both operands of '{node.op_tag}' must be boolean, got {tr.get_type(left_type).kind} and {tr.get_type(right_type).kind}"
                    , node.token
                )
            node.type_id = result_type
            return node.type_id

        if node.op_tag in [OpTag.EQ, OpTag.NEQ, OpTag.LT, OpTag.LTE, OpTag.GT, OpTag.GTE]:
            result_type = tr.get_comparison_type(left_type, right_type)
            if result_type == TypeRegistry.NoneType:
                raise PicoError(
                    f"Error: cannot perform '{node.op_tag}' on types {tr.get_type(left_type).kind} and {tr.get_type(right_type).kind}",
                    node.token
                )
            node.type_id = result_type
            return node.type_id

        result_type = tr.get_arithmetic_type(left_type, right_type)
        if result_type == TypeRegistry.NoneType:
            raise PicoError(
                f"Error: cannot perform '{node.op_tag}' on incompatible types {tr.get_type(left_type).kind} and {tr.get_type(right_type).kind}",
                node.token
            )

        if left_type != result_type:
            node.lhs = Cast(node.lhs.token, node.lhs, left_type, result_type)
        if right_type != result_type:
            node.rhs = Cast(node.rhs.token, node.rhs, right_type, result_type)

        node.type_id = result_type
        return node.type_id
