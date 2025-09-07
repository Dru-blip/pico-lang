from enum import Enum


class HirNodeTag(Enum):
    Block = "Block"
    FunctionBlock = "FunctionBlock"
    Return = "Return"
    Log = "Log",
    Cast = "Cast",
    BoolCast = "BoolCast"
    VarRef = "VarRef"
    StoreLocal = "StoreLocal"
    BinOp = "BinOp"
    ConstInt = "ConstInt"


class BlockTag(Enum):
    Global = "Global"
    Function = "Function"
    Local = "Local"


class HirNode:
    def __init__(self, kind: HirNodeTag, **data):
        self.kind = kind
        self.type_id = 0
        self.token = data.get("token")
        self.parent = data.get("parent")
        for k, v in data.items():
            setattr(self, k, v)


class HirBlock(HirNode):
    def __init__(self, kind, name, token, block_tag, scope_depth, parent):
        super().__init__(kind, token=token, parent=parent, name=name, symbols={}, nodes=[], block_tag=block_tag)
        self.scope_depth = scope_depth
        self.name_map = {}

    def add_symbol(self, symbol):
        self.symbols[symbol.name] = symbol

    def add_node(self, node):
        self.nodes.append(node)

    def resolve(self, name):
        temp = self
        while temp:
            symbol = temp.symbols.get(name)
            if symbol:
                return symbol
            temp = temp.parent
        return None


class FunctionBlock(HirBlock):
    def __init__(self, name: str, token=None, symbol=None,
                 type_id=0, parent=None, scope_depth=0):
        super().__init__(HirNodeTag.FunctionBlock,name=name,token=token, parent=parent, scope_depth=scope_depth,block_tag=BlockTag.Function)
        self.kind = HirNodeTag.FunctionBlock
        self.symbol = symbol
        self.type_id = type_id
        self.local_count = 0


class Return(HirNode):
    def __init__(self, token=None, expr=None):
        super().__init__(HirNodeTag.Return, token=token, expr=expr)
        self.expr = expr


class StoreLocal(HirNode):
    def __init__(self, name, token, symbol, value):
        super().__init__(HirNodeTag.StoreLocal, token=token, name=name, symbol=symbol, value=value)


class VarRef(HirNode):
    def __init__(self, token, symbol):
        super().__init__(HirNodeTag.VarRef, token=token, symbol=symbol)


class HirLog(HirNode):
    def __init__(self, token=None, expr=None):
        super().__init__(HirNodeTag.Log, token=token, expr=expr)
        self.expr = expr


class Cast(HirNode):
    def __init__(self, token, expr, from_type, to_type):
        super().__init__(HirNodeTag.Cast, token=token, expr=expr)
        self.from_type = from_type
        self.to_type = to_type


class BinOp(HirNode):
    def __init__(self, token, op_tag, lhs, rhs):
        super().__init__(HirNodeTag.BinOp, token=token, op_tag=op_tag, lhs=lhs, rhs=rhs)


class ConstInt(HirNode):
    def __init__(self, val: int):
        super().__init__(HirNodeTag.ConstInt, val=val)
        self.val = val
