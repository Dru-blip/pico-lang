class TypeKind:
    NoneType = "None"
    Void = "Void"
    Int = "int"
    Bool = "bool"
    Long = "long"
    Str = "Str"
    Function = "function"


class TypeObject:
    def __init__(self, kind, *, ret_type=0, params=None, id=0):
        self.kind = kind
        self.ret_type = ret_type
        self.params = params or []
        self.id = id


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
        # check for existing function type
        for i, t in enumerate(self.types[4:], start=4):
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

    def get_ret_type(self, type_id):
        return self.types[type_id].ret_type

    def get_type(self, type_id):
        return self.types[type_id]

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
    def get_assignment_type(expected_id: int, got_id: int) -> int:
        return TypeRegistry._lookup_matrix(TypeRegistry._assign_matrix, expected_id, got_id)

    @staticmethod
    def _lookup_matrix(matrix, lhs_id: int, rhs_id: int) -> int:
        if lhs_id < 0 or lhs_id >= len(matrix):
            return TypeRegistry.NoneType
        if rhs_id < 0 or rhs_id >= len(matrix[lhs_id]):
            return TypeRegistry.NoneType
        return matrix[lhs_id][rhs_id]
