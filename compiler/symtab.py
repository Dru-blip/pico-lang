from enum import Enum


class SymbolKind:
    Variable = "Variable"
    Function = "Function"
    Struct = "Struct"
    Parameter = "Parameter"
    Module = "Module"
    StructField = "StructField"


class Linkage(Enum):
    External = "External"
    Internal = "Internal"


class Symbol:
    def __init__(self, name, kind, type_id, scope_depth=0, **extra):
        self.name = name
        self.kind = kind
        self.type = type_id
        self.function_id = 0  # only for function symbol, will later be filled by sema or hirgen
        self.local_offset = 0  # for local variables
        self.scope_depth = scope_depth
        self.params = []  # for functions
        self.is_defined = False  # for functions
        self.lib_prefix = None  # filled in hirgen
        self.linkage = Linkage.Internal  # for functions
        self.lib_name = None
        self.blockRef = None  # for modules
        self.fields = []  # for structs
        self.field_index = -1

        # assign any extra attributes
        for k, v in extra.items():
            setattr(self, k, v)

    def __str__(self):
        parts = [
            f"name={self.name}",
            f"kind={self.kind}",
            f"type={self.type}",
            f"scope_depth={self.scope_depth}",
        ]

        if self.kind == SymbolKind.Function:
            parts.extend([
                f"function_id={self.function_id}",
                f"params={[p.name for p in self.params]}",
                f"is_defined={self.is_defined}",
                f"linkage={self.linkage.value}",
                f"lib_prefix={self.lib_prefix}",
                f"lib_name={self.lib_name}"
            ])
        elif self.kind == SymbolKind.Variable or self.kind == SymbolKind.Parameter:
            parts.append(f"local_offset={self.local_offset}")

        return f"<Symbol {' | '.join(parts)}>"
