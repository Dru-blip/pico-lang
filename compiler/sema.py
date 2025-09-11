# semantic analyzer
from hir import Cast, HirNodeTag, BoolCast
from pico_ast import OpTag, NodeTag, NamedType
from pico_error import PicoError
from pico_types import TypeRegistry, TypeKind
from symtab import Symbol, SymbolKind


class Sema:
    def __init__(self, block):
        self.block = block
        self.type_registry: TypeRegistry = TypeRegistry.get_instance()
        self.function_block = None
        self.current_block = None

    def analyze(self):
        for node in self.block.nodes:
            if node.kind == HirNodeTag.ExternLibBlock:
                continue
            self._analyze_function_block(node)

    def _analyze_function_block(self, fb):
        self.function_block = fb
        self.current_block = fb
        for node in fb.nodes:
            self._analyze_stmt(node)

    def _analyze_stmt(self, node):
        kind = node.kind
        if kind == HirNodeTag.Return:
            self._analyze_return(node)
        elif kind == HirNodeTag.Log:
            self._analyze_expr(node.expr)
        elif kind == HirNodeTag.Block:
            self.current_block = node
            for stmt in node.nodes:
                self._analyze_stmt(stmt)
            self.current_block = self.current_block.parent
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
        if node.symbol is None:
            sym = self.current_block.resolve(node.name)
            if not sym:
                raise PicoError(f"undeclared identifier {node.name}", node.token)
            node.symbol = sym

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
        ret_type = tr.get_ret_type(self.function_block.type_id)

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
            if node.symbol is None:
                sym = self.current_block.resolve(node.name)
                if isinstance(sym.type, NamedType):
                    sym.type = self._transform_type(sym.type)
                if not sym:
                    raise PicoError(f"undeclared identifier {node.name}", node.token)
                node.symbol = sym
            return node.symbol.type
        elif kind == HirNodeTag.BinOp:
            return self._analyze_binop(node)
        elif kind == HirNodeTag.Call:
            return self._analyze_call(node)
        elif kind == HirNodeTag.StoreLocal:
            return self._analyze_storelocal(node)
        elif kind == HirNodeTag.CreateStruct:
            return self._analyze_create_struct(node)
        elif kind == HirNodeTag.FieldAccess:
            obj_type_id = self._analyze_expr(node.obj)
            obj_type = self.type_registry.get_type(obj_type_id)
            if obj_type.kind != TypeKind.Struct:
                raise PicoError(f"invalid field access of {obj_type.kind}", node.token)
            result = next(
                ((i, sym) for i, sym in enumerate(obj_type.fields) if node.target.value == sym.name),
                (None, None)
            )
            match_idx, match_sym = result
            if not match_sym:
                raise PicoError(f"invalid field access", node.target)
            node.field_index = match_sym.field_index
            node.type_id = match_sym.type
            return match_sym.type
        elif kind == HirNodeTag.Cast:
            from_type = self._analyze_expr(node.expr)
            node.from_type = from_type
            result_type = self.type_registry.get_cast_type(from_type, node.to_type)
            if result_type == TypeRegistry.NoneType:
                raise PicoError(
                    f"invalid type cast {self.type_registry.get_type(from_type).kind} to {self.type_registry.get_type(node.to_type).kind}",
                    node.token)
            return node.to_type
        else:
            raise Exception(f"implementation error: cannot analyze node: {node.kind} yet")

    def _analyze_create_struct(self, node):
        if node.name.kind != HirNodeTag.VarRef:
            raise PicoError("Invalid struct literal", node.token)

        if node.name.symbol is None:
            sym = self.current_block.resolve(node.name.name)
            if not sym:
                raise PicoError(f"undeclared struct {node.name.name}", node.token)
            node.name.symbol = sym

        if node.name.symbol.kind != SymbolKind.Struct:
            raise PicoError("Invalid struct literal", node.token)
        field_symbols = node.name.symbol.fields
        for i, field in enumerate(node.values):
            result = next(
                ((i, sym) for i, sym in enumerate(field_symbols) if field.name.value == sym.name),
                (None, None)
            )
            match_index, match_sym = result
            if not match_sym:
                raise PicoError(f"unknown field name {field.name.value} in struct {node.name.symbol.name}", field.name)
            field_type = self._analyze_expr(field.value)
            result_type = self.type_registry.get_assignment_type(field_type,
                                                                 match_sym.type)
            if result_type == TypeRegistry.NoneType:
                raise PicoError(
                    f"Field type mismatch: expected {self.type_registry.get_type(match_sym.type).kind} got {self.type_registry.get_type(field_type).kind}",
                    field.name)
            field.field_index = match_sym.field_index
        return node.name.symbol.type

    def _analyze_call(self, node):
        if node.calle.kind != HirNodeTag.VarRef and node.calle.kind != HirNodeTag.StaticAccess:
            raise PicoError("Uncallable expression", node.token)

        if node.calle.kind == HirNodeTag.VarRef:
            if node.calle.symbol is None:
                sym = self.current_block.resolve(node.calle.name)
                if not sym:
                    raise PicoError(f"undeclared function {node.calle.name}", node.token)
                node.calle.symbol = sym

            function_symbol = node.calle.symbol
            if function_symbol.kind != SymbolKind.Function:
                raise PicoError(f"{node.calle.name} is not a function", node.token)
            params = function_symbol.params
            return_type = self.type_registry.get_ret_type(function_symbol.type)
        else:
            if node.calle.qualifier.symbol is None:
                qual_sym = self.current_block.resolve(node.calle.qualifier.name)
                if not qual_sym:
                    raise PicoError(f"undeclared identifier {node.calle.qualifier.name}", node.token)
                node.calle.qualifier.symbol = qual_sym

            if node.calle.name.symbol is None:
                name_sym = node.calle.qualifier.symbol.blockRef.resolve(node.calle.name.name)
                if not name_sym:
                    raise PicoError(f"undeclared function {node.calle.name.name}", node.token)
                node.calle.name.symbol = name_sym

            qualifier_symbol: Symbol = node.calle.qualifier.symbol
            function_symbol = node.calle.name.symbol
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
        node.type_id = return_type
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
                type_symbol = self.block.resolve(type_node.name)
                if not type_symbol:
                    raise PicoError(f"Unknown type {type_node.name}", type_node.token)
                if type_symbol.kind != SymbolKind.Struct:
                    raise PicoError(f"Unknown type {type_node.name}", type_node.token)
                return type_symbol.type

        raise PicoError(f"Unknown type {type_node.name}", type_node.token)
