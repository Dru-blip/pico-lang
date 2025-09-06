from enum import Enum, auto

class HirNodeTag(Enum):
    Block = "Block"
    FunctionBlock = "FunctionBlock"
    Return = "Return"
    ConstInt = "ConstInt"


class HirNode:
    def __init__(self, kind: HirNodeTag, **data):
        self.kind = kind
        self.type_id = 0
        self.token = data.get("token")
        self.parent = data.get("parent")
        for k, v in data.items():
            setattr(self, k, v)


class HirBlock(HirNode):
    def __init__(self, name: str, token=None, parent=None, scope_depth=0):
        super().__init__(HirNodeTag.Block,
                         token=token,
                         parent=parent,
                         name=name,
                         symbols={},
                         nodes=[])
        self.scope_depth = scope_depth

    def add_node(self, node: "HirNode"):
        self.nodes.append(node)


class FunctionBlock(HirBlock):
    def __init__(self, name: str, token=None, symbol=None,
                 type_id=0, parent=None, scope_depth=0):
        super().__init__(name, token, parent, scope_depth)
        self.kind = HirNodeTag.FunctionBlock
        self.symbol = symbol
        self.type_id = type_id


class Return(HirNode):
    def __init__(self, token=None, expr=None):
        super().__init__(HirNodeTag.Return, token=token, expr=expr)
        self.expr = expr


class ConstInt(HirNode):
    def __init__(self, val: int):
        super().__init__(HirNodeTag.ConstInt, val=val)
        self.val = val
