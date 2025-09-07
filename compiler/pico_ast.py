from enum import Enum
from typing import Any, Optional, List


class OpTag:
    OR = "OR"
    AND = "AND"
    EQ = "EQ"
    NEQ = "NEQ"
    LT = "LT"
    LTE = "LTE"
    GT = "GT"
    GTE = "GTE"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"

    BAND = "BAND"
    BOR = "BOR"
    BXOR = "XOR"
    SHL = "SHL"
    SHR = "SHR"


class NodeTag(str, Enum):
    NamedType = "NamedType"

    IntLiteral = "IntLiteral"
    Identifier = "Identifier"

    BinOp = "BinOp"

    Not = "Not"

    Assignment = "Assignment"

    Return = "Return"
    ExprStmt = "ExprStmt"
    Log = "Log",
    Block = "Block"

    Param = "Param"
    VarDecl = "VarDecl"
    FunctionDeclaration = "FunctionDeclaration"
    FunctionPrototype = "FunctionPrototype"


class Node:
    def __init__(self, tag: NodeTag, token: Optional[Any] = None, **props: Any):
        self.tag = tag
        self.token = token
        for k, v in props.items():
            setattr(self, k, v)


class Program:
    def __init__(self, nodes: Optional[list] = None):
        self.kind = "Program"
        self.nodes = nodes or []


class NamedType(Node):
    def __init__(self, token, name: str):
        super().__init__(NodeTag.NamedType, token=token, name=name)


class Decl(Node):
    def __init__(self, tag: NodeTag, **props):
        super().__init__(tag, **props)


class Param(Node):
    def __init__(self, token, name: str, type_node):
        super().__init__(NodeTag.Param, token=token, name=name, type=type_node)


class FunctionPrototype(Decl):
    def __init__(self, token, name: str, return_type, params: list):
        super().__init__(
            NodeTag.FunctionPrototype,
            token=token,
            name=name,
            returnType=return_type,
            params=params
        )


class FunctionDeclaration(Decl):
    def __init__(self, proto: FunctionPrototype, body):
        super().__init__(
            NodeTag.FunctionDeclaration,
            proto=proto,
            body=body
        )


class VarDecl(Decl):
    def __init__(self, token, name, type_, init=None):
        super().__init__(NodeTag.VarDecl, token=token, name=name, type_=type_, init=init)


class Stmt(Node):
    def __init__(self, tag: NodeTag, **props):
        super().__init__(tag, **props)


class Log(Stmt):
    def __init__(self, token, expr=None):
        super().__init__(NodeTag.Log, token=token, expr=expr)


class Return(Stmt):
    def __init__(self, token, expr=None):
        super().__init__(NodeTag.Return, token=token, expr=expr)


class ExprStmt(Stmt):
    def __init__(self, token, expr=None):
        super().__init__(NodeTag.ExprStmt, token=token, expr=expr)


class Block(Stmt):
    def __init__(self, token, stmts: List[Node]):
        super().__init__(NodeTag.Block, token=token, stmts=stmts)


class Expr(Node):
    def __init__(self, tag: NodeTag, **props):
        super().__init__(tag, **props)


class Assignment(Expr):
    def __init__(self, token, target, val):
        super().__init__(NodeTag.Assignment, token=token, target=target, val=val)


class IntLiteral(Expr):
    def __init__(self, value: int):
        super().__init__(NodeTag.IntLiteral, value=value)


class Identifier(Expr):
    def __init__(self, name: str, token=None):
        super().__init__(NodeTag.Identifier, name=name, token=token)


class BinOp(Expr):
    def __init__(self, token, op_tag, lhs, rhs):
        super().__init__(NodeTag.BinOp, token=token, op_tag=op_tag, lhs=lhs, rhs=rhs)
