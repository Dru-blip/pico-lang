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
    Assignment, BinOp, Log, VarDecl, ExprStmt, IfStmt, LoopStmt, Continue, Break, Call, StrLiteral, ExternLibBlock,
    BoolLiteral, StaticAccess, StructDecl, StructField, StructLiteral, FieldValue, FieldAccess,
)
from pico_error import PicoSyntaxError
from tokenizer import Tokenizer, TokenTag


class OperatorKind:
    Infix = "infix"
    Assign = "assign"
    Postfix = "postfix"


class Operator:
    def __init__(self, kind, lbp, rbp, op_tag, node):
        self.kind = kind
        self.lbp = lbp
        self.rbp = rbp
        self.op_tag = op_tag
        self.node = node


class Parser:
    def __init__(self, filename: str, source: str):
        self.filename = filename
        self.source = source
        self.tokens = Tokenizer.tokenize(source, filename)
        self.pos = 0
        self.current_token = self.tokens[0]

        self.operator_table = {
            TokenTag.EQUAL: Operator(OperatorKind.Assign, 1, 1, OpTag.Assign, Assignment),
            TokenTag.PIPE_PIPE: Operator(OperatorKind.Infix, 28, 29, OpTag.OR, BinOp),
            TokenTag.AMPERSAND_AMPERSAND: Operator(OperatorKind.Infix, 30, 31, OpTag.AND, BinOp),

            TokenTag.PIPE: Operator(OperatorKind.Infix, 34, 35, OpTag.BOR, BinOp),
            TokenTag.CARET: Operator(OperatorKind.Infix, 36, 37, OpTag.BXOR, BinOp),
            TokenTag.AMPERSAND: Operator(OperatorKind.Infix, 38, 39, OpTag.BAND, BinOp),

            TokenTag.EQUAL_EQUAL: Operator(OperatorKind.Infix, 40, 41, OpTag.EQ, BinOp),
            TokenTag.NOT_EQUAL: Operator(OperatorKind.Infix, 40, 41, OpTag.NEQ, BinOp),

            TokenTag.LESS: Operator(OperatorKind.Infix, 45, 46, OpTag.LT, BinOp),
            TokenTag.LESS_EQUAL: Operator(OperatorKind.Infix, 45, 46, OpTag.LTE, BinOp),
            TokenTag.GREATER: Operator(OperatorKind.Infix, 45, 46, OpTag.GT, BinOp),
            TokenTag.GREATER_EQUAL: Operator(OperatorKind.Infix, 45, 46, OpTag.GTE, BinOp),

            TokenTag.LESS_LESS: Operator(OperatorKind.Infix, 47, 48, OpTag.SHL, BinOp),
            TokenTag.GREATER_GREATER: Operator(OperatorKind.Infix, 47, 48, OpTag.SHR, BinOp),

            TokenTag.PLUS: Operator(OperatorKind.Infix, 50, 51, OpTag.ADD, BinOp),
            TokenTag.MINUS: Operator(OperatorKind.Infix, 50, 51, OpTag.SUB, BinOp),
            TokenTag.ASTERISK: Operator(OperatorKind.Infix, 55, 56, OpTag.MUL, BinOp),
            TokenTag.SLASH: Operator(OperatorKind.Infix, 55, 56, OpTag.DIV, BinOp),
            TokenTag.MODULUS: Operator(OperatorKind.Infix, 55, 56, OpTag.MOD, BinOp),

            TokenTag.COLON_COLON: Operator(OperatorKind.Postfix, 97, 98, OpTag.StaticAccess, StaticAccess),
            TokenTag.LPAREN: Operator(OperatorKind.Postfix, 99, 100, OpTag.Call, Call),
            TokenTag.LBRACE: Operator(OperatorKind.Postfix, 99, 100, OpTag.StructLiteral, StructLiteral),
            TokenTag.DOT: Operator(OperatorKind.Postfix, 99, 100, OpTag.FieldAccess, FieldAccess),
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
            raise PicoSyntaxError(f"expected {tag.lower()}, but got {self.current_token.tag.lower()}",
                                  self.tokens[self.pos - 1])
        return self._next_token()

    def _check(self, tag):
        return self.current_token.tag == tag

    def parse_nodes(self):
        nodes = []
        while self.current_token.tag != TokenTag.EOF:
            nodes.append(self._parse_decl())
        return nodes

    def _parse_decl(self):
        if self._check(TokenTag.KW_EXTERN):
            return self._parse_extern_lib_block()
        if self._check(TokenTag.KW_FN):
            return self._parse_function_declaration()
        if self._check(TokenTag.KW_STRUCT):
            return self._parse_struct_decl()

        raise PicoSyntaxError("invalid syntax", self.current_token)

    def _parse_struct_decl(self):
        main_token = self._next_token()
        name = self._expect_token(TokenTag.ID)
        self._expect_token(TokenTag.LBRACE)
        fields = []
        while not self._check(TokenTag.RBRACE):
            field_token = self.current_token
            field_type = self._parse_type_expr()
            field_name = self._expect_token(TokenTag.ID)
            fields.append(StructField(field_token, field_type, field_name))
            self._expect_token(TokenTag.SEMICOLON)
        self._next_token()
        return StructDecl(main_token, name.value, fields)

    def _parse_extern_lib_block(self):
        main_token = self._next_token()
        decls = []
        self._expect_token(TokenTag.AT)
        self._expect_token(TokenTag.ID)
        self._expect_token(TokenTag.EQUAL)
        lib_name = self._expect_token(TokenTag.STR_LIT).value
        self._expect_token(TokenTag.LBRACE)
        while not self._check(TokenTag.RBRACE):
            decls.append(self._parse_function_proto())
            self._expect_token(TokenTag.SEMICOLON)
        self._expect_token(TokenTag.RBRACE)
        return ExternLibBlock(main_token, lib_name, decls)

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

    def _parse_variable_decl(self):
        main_token = self._next_token()
        ident_token = self._expect_token(TokenTag.ID)
        if self._check(TokenTag.COLON):
            var_type = self._parse_type_expr()
        else:
            var_type = None
        init = None
        if self._check(TokenTag.EQUAL):
            self._advance()
            init = self._parse_expr(0)

        self._expect_token(TokenTag.SEMICOLON)
        return VarDecl(main_token, ident_token.value, var_type, init)

    def _parse_stmt(self):
        if self._check(TokenTag.KW_RETURN):
            return self._parse_return()
        elif self._check(TokenTag.LBRACE):
            return self._parse_block()
        elif self._check(TokenTag.KW_LOG):
            return self._parse_log()
        elif self._check(TokenTag.KW_LET):
            return self._parse_variable_decl()
        elif self._check(TokenTag.KW_IF):
            return self._parse_if_stmt()
        elif self._check(TokenTag.KW_LOOP):
            return self._parse_loop_stmt()
        elif self._check(TokenTag.KW_CONTINUE):
            return self._parse_continue()
        elif self._check(TokenTag.KW_BREAK):
            return self._parse_break()
        else:
            main_token = self.current_token
            expr = self._parse_expr()
            self._expect_token(TokenTag.SEMICOLON)
            return ExprStmt(main_token, expr)

    def _parse_loop_stmt(self):
        main_token = self._next_token()
        body = self._parse_block()
        return LoopStmt(main_token, body)

    def _parse_block(self):
        main_token = self._expect_token(TokenTag.LBRACE)
        stmts = []
        while not self._check(TokenTag.RBRACE):
            stmts.append(self._parse_stmt())
        self._advance()
        return Block(main_token, stmts)

    def _parse_if_stmt(self):
        main_token = self._expect_token(TokenTag.KW_IF)
        self._expect_token(TokenTag.LPAREN)
        condition = self._parse_expr(0)
        self._expect_token(TokenTag.RPAREN)
        then_stmt = self._parse_stmt()
        else_stmt = None
        if self._check(TokenTag.KW_ELSE):
            self._advance()
            else_stmt = self._parse_stmt()
        return IfStmt(main_token, condition, then_stmt, else_stmt)

    def _parse_continue(self):
        main = self._next_token()
        self._expect_token(TokenTag.SEMICOLON)
        return Continue(main)

    def _parse_break(self):
        main = self._next_token()
        self._expect_token(TokenTag.SEMICOLON)
        return Break(main)

    def _parse_return(self):
        main_token = self._next_token()
        if not self._check(TokenTag.SEMICOLON):
            expr = self._parse_expr()
        else:
            expr = None

        self._expect_token(TokenTag.SEMICOLON)
        return Return(main_token, expr)

    def _parse_log(self):
        main_token = self._next_token()
        expr = self._parse_expr()
        self._expect_token(TokenTag.SEMICOLON)
        return Log(main_token, expr)

    def _parse_expr(self, min_bp=0):
        lhs = self._parse_primary_expr()
        while True:
            op_info = self.operator_table.get(self.current_token.tag)
            if not op_info or op_info.lbp < min_bp:
                break
            if op_info.kind == OperatorKind.Postfix:
                lhs = self._parse_postfix_expr(op_info.op_tag, lhs)
                continue
            op_token = self._next_token()
            rhs = self._parse_expr(op_info.rbp)
            lhs = op_info.node(op_token, op_info.op_tag, lhs, rhs)
        return lhs

    def _parse_postfix_expr(self, op_tag, lhs):
        main_token = self.current_token
        if op_tag == OpTag.Call:
            self._advance()
            args = self._parse_call_args()
            return Call(main_token, lhs, args)
        if op_tag == OpTag.StaticAccess:
            self._advance()
            name = self._parse_primary_expr()
            return StaticAccess(main_token, lhs, name)
        if op_tag == OpTag.StructLiteral:
            self._advance()
            field_values = []
            while not self._check(TokenTag.RBRACE):
                self._expect_token(TokenTag.DOT)
                name = self._expect_token(TokenTag.ID)
                self._expect_token(TokenTag.EQUAL)
                value = self._parse_expr()
                if self._check(TokenTag.COMMA):
                    self._expect_token(TokenTag.COMMA)
                field_values.append(FieldValue(name, value))
            self._advance()
            return StructLiteral(main_token, lhs, field_values)
        if op_tag == OpTag.FieldAccess:
            self._advance()
            target = self._expect_token(TokenTag.ID)
            return FieldAccess(main_token, lhs, target)
        return None

    def _parse_call_args(self):
        args = []
        while not self._check(TokenTag.RPAREN):
            args.append(self._parse_expr())
            if self._check(TokenTag.COMMA):
                self._advance()
        self._advance()
        return args

    def _parse_primary_expr(self):
        token = self._next_token()
        if token.tag == TokenTag.INT_LIT:
            return IntLiteral(int(token.value))
        elif token.tag == TokenTag.STR_LIT:
            return StrLiteral(token.value)
        elif token.tag == TokenTag.KW_TRUE:
            return BoolLiteral(True)
        elif token.tag == TokenTag.KW_FALSE:
            return BoolLiteral(False)
        elif token.tag == TokenTag.ID:
            return Identifier(token.value, token)
        else:
            raise PicoSyntaxError("invalid syntax", self.tokens[self.pos - 2])

    def _parse_type_expr(self):
        token = self._next_token()
        if token.tag == TokenTag.ID:
            return NamedType(token, token.value)
        else:
            raise PicoSyntaxError("unknown type specifier", token)
