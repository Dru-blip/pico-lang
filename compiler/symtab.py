class SymbolKind:
    Variable = "Variable"
    Function = "Function"
    Parameter = "Parameter"


class Symbol:
    def __init__(self, name, kind, type_id, scope_depth, **extra):
        self.name = name
        self.kind = kind
        self.type = type_id
        self.local_offset = 0  # for local variables
        self.scope_depth = scope_depth
        self.params = []  # for functions
        self.is_defined = False  # for functions

        # assign any extra attributes
        for k, v in extra.items():
            setattr(self, k, v)
