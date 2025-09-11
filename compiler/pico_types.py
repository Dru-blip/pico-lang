from typing import List

from symtab import Symbol


class TypeKind:
    NoneType = "None"
    Void = "Void"
    Int = "int"
    Bool = "bool"
    Long = "long"
    Str = "Str"
    Function = "function"
    Struct = "Struct"


class TypeObject:
    def __init__(self, kind, *, ret_type=0, params=None, fields=None, id=0):
        self.kind = kind
        self.ret_type = ret_type
        self.params = params or []
        self.fields = fields or []
        self.id = id
        self.is_complete = False  # for structs

    def __str__(self):
        return f"Type<{self.kind}:{self.id}>"


class TypeRegistry:
    _instance = None
    type_counter = 6  # index to start storing types

    # primitive type IDs
    NoneType = 0
    VoidType = 1
    BoolType = 2
    IntType = 3
    LongType = 4
    StrType = 5

    # arithmetic matrix
    _arith_matrix = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 3, 4, 0],
        [0, 0, 0, 4, 4, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    # comparison matrix
    _comp_matrix = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 2, 0, 0, 0],
        [0, 0, 0, 2, 2, 0],
        [0, 0, 0, 2, 2, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    _logical_matrix = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 2, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    _assign_matrix = [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 0, 2, 0, 0, 0],
        [0, 0, 0, 3, 0, 0],
        [0, 0, 0, 4, 4, 0],
        [0, 0, 0, 0, 0, 5],
    ]

    _cast_matrix = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 2, 3, 4, 0],
        [0, 0, 2, 3, 4, 0],
        [0, 0, 2, 3, 4, 0],
        [0, 0, 0, 0, 0, 5],
    ]

    def __init__(self):
        if TypeRegistry._instance:
            return

        self.types = [
            TypeObject(TypeKind.NoneType, id=0),
            TypeObject(TypeKind.Void, id=1),
            TypeObject(TypeKind.Bool, id=2),
            TypeObject(TypeKind.Int, id=3),
            TypeObject(TypeKind.Long, id=4),
            TypeObject(TypeKind.Str, id=5),
        ]

        TypeRegistry._instance = self

    @staticmethod
    def get_instance():
        if TypeRegistry._instance is None:
            TypeRegistry()
        return TypeRegistry._instance

    def add_function(self, ret_type, params=None):
        params = params or []
        for i, t in enumerate(self.types[6:], start=6):
            if not t or t.kind != TypeKind.Function:
                continue
            if t.ret_type != ret_type or len(t.params) != len(params):
                continue
            match = all(tp.type == p.type for tp, p in zip(t.params, params))
            if match:
                return i

        new_type = TypeObject(TypeKind.Function, ret_type=ret_type, params=params, id=TypeRegistry.type_counter)
        self.types.append(new_type)
        TypeRegistry.type_counter += 1
        return new_type.id

    def add_struct(self, fields: List[Symbol]):
        fields = fields or []
        for i, t in enumerate(self.types[6:], start=6):
            if not t or t.kind != TypeKind.Struct:
                continue
            if not t.is_complete:
                t.fields = fields
                return i
            match = all(ft.type == f.type for ft, f in zip(t.fields, fields))
            if match:
                return i
        new_type = TypeObject(TypeKind.Struct, fields=fields, id=TypeRegistry.type_counter)
        self.types.append(new_type)
        TypeRegistry.type_counter += 1
        return new_type.id

    def add_incomplete_struct(self):
        new_type = TypeObject(TypeKind.Struct, id=TypeRegistry.type_counter)
        self.types.append(new_type)
        TypeRegistry.type_counter += 1
        return new_type.id

    def get_ret_type(self, type_id):
        return self.types[type_id].ret_type

    def get_type(self, type_id):
        return self.types[type_id]

    def is_integer_type(self, type_id):
        return type_id == TypeRegistry.IntType or type_id == TypeRegistry.LongType

    @staticmethod
    def get_arithmetic_type(lhs_id: int, rhs_id: int) -> int:
        return TypeRegistry._lookup_matrix(TypeRegistry._arith_matrix, lhs_id, rhs_id)

    @staticmethod
    def get_comparison_type(lhs_id: int, rhs_id: int) -> int:
        return TypeRegistry._lookup_matrix(TypeRegistry._comp_matrix, lhs_id, rhs_id)

    @staticmethod
    def get_logical_type(lhs_id: int, rhs_id: int) -> int:
        return TypeRegistry._lookup_matrix(TypeRegistry._logical_matrix, lhs_id, rhs_id)

    @staticmethod
    def get_cast_type(lhs_id: int, rhs_id: int) -> int:
        return TypeRegistry._lookup_matrix(TypeRegistry._cast_matrix, lhs_id, rhs_id)

    @staticmethod
    def get_assignment_type(expected_id: int, got_id: int) -> int:
        is_compatible = TypeRegistry._lookup_matrix(TypeRegistry._assign_matrix, expected_id, got_id)
        if is_compatible == TypeRegistry.NoneType:
            tr_ = TypeRegistry.get_instance()
            e_type_obj = tr_.get_type(expected_id)
            got_type_obj = tr_.get_type(got_id)
            if e_type_obj.kind != got_type_obj.kind:
                return TypeRegistry.NoneType
            return got_id
        return is_compatible

    @staticmethod
    def _lookup_matrix(matrix, lhs_id: int, rhs_id: int) -> int:
        if lhs_id < 0 or lhs_id >= len(matrix):
            return TypeRegistry.NoneType
        if rhs_id < 0 or rhs_id >= len(matrix[lhs_id]):
            return TypeRegistry.NoneType
        return matrix[lhs_id][rhs_id]
