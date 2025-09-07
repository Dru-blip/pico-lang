from tokenizer import Tokenizer, TokenTag
from pico_ast import (
    FunctionPrototype,
    FunctionDeclaration,
    Block,
    OpTag,
    Return,
    IntLiteral,
    Identifier,
    NamedType,
    Param,
    Program,
    Assignment, BinOp,
)


class OperatorKind:
    Infix = "infix"
    Assign = "assign"


class Operator:
    def __init__(self, kind, lbp, rbp, op_tag):
        self.kind = kind
        self.lbp = lbp
        self.rbp = rbp
        self.op_tag = op_tag


class Parser:
    def __init__(self, filename: str, source: str):
        self.filename = filename
        self.source = source
        self.tokens = Tokenizer.tokenize(source, filename)
        self.pos = 0
        self.current_token = self.tokens[0]

        self.operator_table = {
            # TokenTag.EQUAL: Operator(OperatorKind.Assign, 1, 1, OpTag.ASSIGN),
            TokenTag.PIPE_PIPE: Operator(OperatorKind.Infix, 28, 29, OpTag.OR),
            TokenTag.AMPERSAND_AMPERSAND: Operator(OperatorKind.Infix, 30, 31, OpTag.AND),

            TokenTag.EQUAL_EQUAL: Operator(OperatorKind.Infix, 45, 46, OpTag.EQ),
            TokenTag.NOT_EQUAL: Operator(OperatorKind.Infix, 45, 46, OpTag.NEQ),
            TokenTag.LESS: Operator(OperatorKind.Infix, 45, 46, OpTag.LT),
            TokenTag.LESS_EQUAL: Operator(OperatorKind.Infix, 45, 46, OpTag.LTE),
            TokenTag.GREATER: Operator(OperatorKind.Infix, 45, 46, OpTag.GT),
            TokenTag.GREATER_EQUAL: Operator(OperatorKind.Infix, 45, 46, OpTag.GTE),

            TokenTag.PLUS: Operator(OperatorKind.Infix, 50, 51, OpTag.ADD),
            TokenTag.MINUS: Operator(OperatorKind.Infix, 50, 51, OpTag.SUB),
            TokenTag.ASTERISK: Operator(OperatorKind.Infix, 55, 56, OpTag.MUL),
            TokenTag.SLASH: Operator(OperatorKind.Infix, 55, 56, OpTag.DIV),
            TokenTag.MODULUS: Operator(OperatorKind.Infix, 55, 56, OpTag.MOD),
        }

    @staticmethod
    def parse(filename, source):
        return Program(Parser(filename, source).parse_nodes())

    def _advance(self):
        if self.pos + 1 >= len(self.tokens):
            return self.pos
        self.pos += 1
        self.current_token = self.tokens[self.pos]
        return self.pos - 1

    def _next_token(self):
        return self.tokens[self._advance()]

    def _eat_token(self, tag):
        if self.current_token.tag == tag:
            return self._next_token()
        return None

    def _expect_token(self, tag):
        if self.current_token.tag != tag:
            raise SyntaxError(
                f"expected {tag}, but got {self.current_token.tag}"
            )
        return self._next_token()

    def _check(self, tag):
        return self.current_token.tag == tag

    def parse_nodes(self):
        nodes = []
        while self.current_token.tag != TokenTag.EOF:
            nodes.append(self._parse_function_declaration())
        return nodes

    def _parse_function_declaration(self):
        proto = self._parse_function_proto()
        if self._check(TokenTag.SEMICOLON):
            self._advance()
            body = None
        else:
            body = self._parse_block()
        return FunctionDeclaration(proto, body)

    def _parse_function_proto(self):
        main_token = self._next_token()
        ident_token = self._expect_token(TokenTag.ID)
        params = []
        self._expect_token(TokenTag.LPAREN)
        while not self._check(TokenTag.RPAREN):
            param_type = self._parse_type_expr()
            param_name = self._expect_token(TokenTag.ID)
            if self._check(TokenTag.COMMA):
                self._advance()
            params.append(Param(param_name, param_name.value, param_type))
        self._expect_token(TokenTag.RPAREN)
        return_type = self._parse_type_expr()
        return FunctionPrototype(main_token, ident_token.value, return_type, params)

    def _parse_block(self):
        main_token = self._expect_token(TokenTag.LBRACE)
        stmts = []
        while not self._check(TokenTag.RBRACE):
            stmts.append(self._parse_stmt())
        self._advance()
        return Block(main_token, stmts)

    def _parse_stmt(self):
        if self._check(TokenTag.KW_RETURN):
            return self._parse_return()
        elif self._check(TokenTag.LBRACE):
            return self._parse_block()
        else:
            raise SyntaxError(f"unexpected token in statement: {self.current_token.tag}")

    def _parse_return(self):
        main_token = self._next_token()
        expr = self._parse_expr()
        self._expect_token(TokenTag.SEMICOLON)
        return Return(main_token, expr)

    def _parse_expr(self, min_bp=0):
        lhs = self._parse_primary_expr()
        while True:
            op_info = self.operator_table.get(self.current_token.tag)
            if not op_info or op_info.lbp < min_bp:
                break
            op_token = self._next_token()
            rhs = self._parse_expr(op_info.rbp)
            lhs = BinOp(op_token, op_info.op_tag, lhs, rhs)
        return lhs

    def _parse_primary_expr(self):
        token = self._next_token()
        if token.tag == TokenTag.INT_LIT:
            return IntLiteral(int(token.value))
        elif token.tag == TokenTag.ID:
            return Identifier(token.value, token)
        else:
            raise SyntaxError(f"invalid primary expression: {token.tag}")

    def _parse_type_expr(self):
        token = self._next_token()
        if token.tag == TokenTag.ID:
            return NamedType(token, token.value)
        else:
            raise SyntaxError("unknown type specifier")
