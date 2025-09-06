class TypeKind:
    NoneType = "None"
    Void = "Void"
    Int = "int"
    Long = "long"
    Function = "function"


class TypeObject:
    def __init__(self, kind, *, size=0, align=0, ret_type=0, params=None, id=0):
        self.kind = kind
        self.size = size
        self.align = align
        self.ret_type = ret_type
        self.params = params or []
        self.id = id


class TypeRegistry:
    _instance = None
    type_counter = 4  # index to start storing types

    # primitive type IDs
    NoneType = 0
    VoidType = 1
    IntType = 2
    LongType = 3

    def __init__(self):
        if TypeRegistry._instance:
            return

        self.types = [
            TypeObject(TypeKind.NoneType, size=0, align=0, id=0),
            TypeObject(TypeKind.Void, size=0, align=0, id=1),
            TypeObject(TypeKind.Int, size=4, align=4, id=2),
            TypeObject(TypeKind.Long, size=8, align=8, id=3),
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

    def get_common_type(self, a_type_id, b_type_id):
        if a_type_id == b_type_id:
            return a_type_id

        atype = self.types[a_type_id]
        btype = self.types[b_type_id]

        if not atype or not btype:
            return TypeRegistry.NoneType

        if (atype.kind == TypeKind.Int and btype.kind == TypeKind.Long) or \
           (atype.kind == TypeKind.Long and btype.kind == TypeKind.Int):
            return TypeRegistry.LongType

        return TypeRegistry.NoneType
