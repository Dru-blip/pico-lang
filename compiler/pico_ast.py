from enum import Enum
from typing import Any, Optional, List


class OpTag:
    Assign = "Assign"
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

    Call = "Call"


class NodeTag(str, Enum):
    NamedType = "NamedType"

    IntLiteral = "IntLiteral"
    Identifier = "Identifier"
    StrLiteral = "StrLiteral"

    BinOp = "BinOp"

    Not = "Not"

    Assignment = "Assignment"
    Call = "Call"

    If = "If"
    LoopStmt = "LoopStmt"

    Break = "Break"
    Continue = "Continue"
    Return = "Return"
    ExprStmt = "ExprStmt"
    Log = "Log",
    Block = "Block"

    Param = "Param"
    VarDecl = "VarDecl"
    FunctionDeclaration = "FunctionDeclaration"
    FunctionPrototype = "FunctionPrototype"
    ExternLibBlock = "ExternLibBlock"


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


class ExternLibBlock(Decl):
    def __init__(self, token, libname: str, lib_prefix: str, decls: List[Decl]):
        super().__init__(
            NodeTag.ExternLibBlock,
            token=token,
            libname=libname,
            lib_prefix=lib_prefix,
            decls=decls,
        )


class VarDecl(Decl):
    def __init__(self, token, name, type_, init=None):
        super().__init__(NodeTag.VarDecl, token=token, name=name, type_=type_, init=init)


class Stmt(Node):
    def __init__(self, tag: NodeTag, **props):
        super().__init__(tag, **props)


class LoopStmt(Stmt):
    def __init__(self, token, body):
        super().__init__(NodeTag.LoopStmt, token=token, body=body)


class IfStmt(Node):
    def __init__(self, token, condition, then_stmt, else_stmt=None):
        super().__init__(NodeTag.If, token=token, condition=condition, then_stmt=then_stmt, else_stmt=else_stmt)


class Log(Stmt):
    def __init__(self, token, expr=None):
        super().__init__(NodeTag.Log, token=token, expr=expr)


class Return(Stmt):
    def __init__(self, token, expr=None):
        super().__init__(NodeTag.Return, token=token, expr=expr)


class Break(Stmt):
    def __init__(self, token):
        super().__init__(NodeTag.Break, token=token)


class Continue(Stmt):
    def __init__(self, token):
        super().__init__(NodeTag.Continue, token=token)


class ExprStmt(Stmt):
    def __init__(self, token, expr=None):
        super().__init__(NodeTag.ExprStmt, token=token, expr=expr)


class Block(Stmt):
    def __init__(self, token, stmts: List[Node]):
        super().__init__(NodeTag.Block, token=token, stmts=stmts)


class Expr(Node):
    def __init__(self, tag: NodeTag, **props):
        super().__init__(tag, **props)


class Call(Expr):
    def __init__(self, token, calle, args: List[Expr]):
        super().__init__(NodeTag.Call, token=token, calle=calle, args=args)


class Assignment(Expr):
    def __init__(self, token, op_tag, target, val):
        super().__init__(NodeTag.Assignment, op_tag=op_tag, token=token, target=target, val=val)


class IntLiteral(Expr):
    def __init__(self, value: int):
        super().__init__(NodeTag.IntLiteral, value=value)


class StrLiteral(Expr):
    def __init__(self, value: str):
        super().__init__(NodeTag.StrLiteral, value=value)


class Identifier(Expr):
    def __init__(self, name: str, token=None):
        super().__init__(NodeTag.Identifier, name=name, token=token)


class BinOp(Expr):
    def __init__(self, token, op_tag, lhs, rhs):
        super().__init__(NodeTag.BinOp, token=token, op_tag=op_tag, lhs=lhs, rhs=rhs)
