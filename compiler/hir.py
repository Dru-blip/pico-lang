from enum import Enum
from typing import List

from symtab import Symbol


class HirNodeTag(Enum):
    Block = "Block"
    Module = "Module"
    FunctionBlock = "FunctionBlock"
    Branch = "Branch"
    LoopBlock = "LoopBlock"
    ExternLibBlock = "ExternLibBlock"

    StructDecl = "StructDecl"
    CreateStruct = "CreateStruct"
    FieldValue = "FieldValue"
    FieldAccess = "FieldAccess"
    StaticAccess = "StaticAccess"
    StoreField = "StoreField"
    Break = "Break"
    Continue = "Continue"
    Return = "Return"
    Log = "Log",
    Cast = "Cast",
    UnOp = "UnOp"
    BoolCast = "BoolCast"
    VarRef = "VarRef"
    StoreLocal = "StoreLocal"
    BinOp = "BinOp"
    ConstInt = "ConstInt"
    ConstStr = "ConstStr"
    ConstBool = "ConstBool"
    Call = "Call"


class BlockTag(Enum):
    Global = "Global"
    Function = "Function"
    Local = "Local"
    Module = "Module"


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

    def resolve(self, name) -> Symbol | None:
        temp = self
        while temp:
            symbol = temp.symbols.get(name)
            if symbol:
                return symbol
            temp = temp.parent
        return None


class HirModule(HirBlock):
    def __init__(self, name, token, parent=None, scope_depth=0):
        super().__init__(HirNodeTag.Module, name=name, token=token, parent=parent, scope_depth=scope_depth,
                         block_tag=BlockTag.Module)


class HirExternalLibBlock(HirModule):
    def __init__(self, token, lib_prefix, symbol, symbols: List[Symbol]):
        super().__init__(name=lib_prefix, token=token)
        self.kind = HirNodeTag.ExternLibBlock
        self.symbol = symbol
        for symbol in symbols:
            self.add_symbol(symbol)
        self.symbol.blockRef = self


class FunctionBlock(HirBlock):
    def __init__(self, function_id: int, name: str, token=None, symbol=None,
                 type_id=0, parent=None, scope_depth=0):
        super().__init__(HirNodeTag.FunctionBlock, name=name, token=token, parent=parent, scope_depth=scope_depth,
                         block_tag=BlockTag.Function)
        self.function_id = function_id
        self.kind = HirNodeTag.FunctionBlock
        self.symbol = symbol
        self.type_id = type_id
        self.local_count = 0


class LoopBlock(HirBlock):
    def __init__(self, name: str, loop_id: int, token=None, parent=None, scope_depth=0):
        super().__init__(HirNodeTag.LoopBlock,
                         name=name,
                         token=token,
                         parent=parent,
                         scope_depth=scope_depth,
                         block_tag=BlockTag.Local
                         )
        self.loop_id = loop_id
        self.kind = HirNodeTag.LoopBlock


class Branch(HirNode):
    def __init__(self, token, condition, then_block, else_block, merge_label):
        super().__init__(
            HirNodeTag.Branch,
            token=token,
            condition=condition,
            then_block=then_block,
            else_block=else_block,
            merge_label=merge_label,
        )


class Return(HirNode):
    def __init__(self, token=None, expr=None):
        super().__init__(HirNodeTag.Return, token=token, expr=expr)
        self.expr = expr


class Continue(HirNode):
    def __init__(self, token=None, loop_id=-1):
        super().__init__(HirNodeTag.Continue, token=token)
        self.loop_id = loop_id


class Break(HirNode):
    def __init__(self, token=None, loop_id=-1):
        super().__init__(HirNodeTag.Break, token=token)
        self.loop_id = loop_id


class StoreLocal(HirNode):
    def __init__(self, name, token, symbol, value):
        super().__init__(HirNodeTag.StoreLocal, token=token, name=name, symbol=symbol, value=value)


class VarRef(HirNode):
    def __init__(self, token, name, symbol=None):
        super().__init__(HirNodeTag.VarRef, token=token, name=name, symbol=symbol)


class HirLog(HirNode):
    def __init__(self, token=None, expr=None):
        super().__init__(HirNodeTag.Log, token=token, expr=expr)
        self.expr = expr


class Cast(HirNode):
    def __init__(self, token, expr, from_type, to_type):
        super().__init__(HirNodeTag.Cast, token=token, expr=expr)
        self.from_type = from_type
        self.to_type = to_type


class BoolCast(HirNode):
    def __init__(self, token, expr):
        super().__init__(HirNodeTag.Cast, token=token, expr=expr)


class StaticAccess(HirNode):
    def __init__(self, token, qualifier, name):
        super().__init__(HirNodeTag.StaticAccess, token=token, qualifier=qualifier, name=name)


class FieldAccess(HirNode):
    def __init__(self, token, obj, target):
        super().__init__(HirNodeTag.FieldAccess, token=token, obj=obj, target=target)
        self.field_index = -1  # set by sema


class CreateStruct(HirNode):
    def __init__(self, token, name, values):
        super().__init__(HirNodeTag.CreateStruct, token=token, name=name, values=values)
        self.symbol = None


class FieldValue(HirNode):
    def __init__(self, name, value):
        super().__init__(HirNodeTag.FieldValue, token=name, name=name, value=value)
        self.field_index = -1  # set by sema


class StoreField(HirNode):
    def __init__(self, token, obj, field_name, value):
        super().__init__(HirNodeTag.StoreField,
                         token=token,
                         obj=obj,
                         field_name=field_name,
                         value=value)
        self.field_index = -1  # resolved during sema
        self.symbol = None  # field symbol


class Call(HirNode):
    def __init__(self, token, calle, args):
        super().__init__(HirNodeTag.Call, token=token, calle=calle, args=args)
        self.function_symbol = None  # filled by sema


class BinOp(HirNode):
    def __init__(self, token, op_tag, lhs, rhs):
        super().__init__(HirNodeTag.BinOp, token=token, op_tag=op_tag, lhs=lhs, rhs=rhs)


class UnOp(HirNode):
    def __init__(self, token, op_tag, expr):
        super().__init__(HirNodeTag.UnOp, token=token, op_tag=op_tag, expr=expr)


class ConstInt(HirNode):
    def __init__(self, val: int):
        super().__init__(HirNodeTag.ConstInt, val=val)
        self.val = val


class ConstStr(HirNode):
    def __init__(self, val: str):
        super().__init__(HirNodeTag.ConstStr, val=val)
        self.val = val


class ConstBool(HirNode):
    def __init__(self, val: bool):
        super().__init__(HirNodeTag.ConstBool, val=val)
