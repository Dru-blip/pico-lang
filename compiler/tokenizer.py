from dataclasses import dataclass
from enum import Enum
from typing import List, Dict


class TokenTag(str, Enum):
    UNKNOWN = "UNKNOWN"
    EOF = "EOF"
    ID = "ID"
    INT_LIT = "INT_LIT"
    LONG_LIT = "LONG_LIT"
    STR_LIT = "STR_LIT"

    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"

    PLUS = "PLUS"
    PLUS_PLUS = "PLUS_PLUS"
    PLUS_EQUAL = "PLUS_EQUAL"

    MINUS = "MINUS"
    MINUS_MINUS = "MINUS_MINUS"
    MINUS_EQUAL = "MINUS_EQUAL"

    ASTERISK = "ASTERISK"
    ASTERISK_EQUAL = "ASTERISK_EQUAL"
    SLASH = "SLASH"
    SLASH_EQUAL = "SLASH_EQUAL"

    MODULUS = "MODULUS"
    MODULUS_EQUAL = "MODULUS_EQUAL"

    LESS = "LESS"
    LESS_LESS = "LESS_LESS"
    LESS_EQUAL = "LESS_EQUAL"

    GREATER = "GREATER"
    GREATER_GREATER = "GREATER_GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"

    EQUAL = "EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    NOT = "NOT"
    NOT_EQUAL = "NOT_EQUAL"

    AMPERSAND = "AMPERSAND"
    AMPERSAND_AMPERSAND = "AMPERSAND_AMPERSAND"

    PIPE = "PIPE"
    PIPE_PIPE = "PIPE_PIPE"

    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    COLON = "COLON",
    COLON_COLON = "COLON_COLON"

    CARET = "CARET"
    AT = "AT"
    DOT = "DOT"

    KW_FN = "KW_FN"
    KW_LET = "KW_LET"
    KW_LOG = "KW_LOG",
    KW_RETURN = "KW_RETURN"
    KW_IF = "KW_IF"
    KW_ELSE = "KW_ELSE"
    KW_WHILE = "KW_WHILE"
    KW_LOOP = "KW_LOOP"
    KW_BREAK = "KW_BREAK"
    KW_CONTINUE = "KW_CONTINUE"
    KW_DO = "KW_DO"
    KW_EXTERN = "KW_EXTERN"
    KW_TRUE = "KW_TRUE",
    KW_FALSE = "KW_FALSE"
    KW_STRUCT = "KW_STRUCT"


@dataclass
class Location:
    line: int
    col: int
    start: int
    end: int


@dataclass
class Token:
    tag: TokenTag
    value: str
    loc: Location
    line_start: int

    def __str__(self):
        return f'Token({self.tag}, "{self.value}", line={self.loc.line}, col={self.loc.col})'


class Tokenizer:
    keywords: Dict[str, TokenTag] = {
        "fn": TokenTag.KW_FN,
        "let": TokenTag.KW_LET,
        "return": TokenTag.KW_RETURN,
        "log": TokenTag.KW_LOG,
        "if": TokenTag.KW_IF,
        "else": TokenTag.KW_ELSE,
        "while": TokenTag.KW_WHILE,
        "loop": TokenTag.KW_LOOP,
        "do": TokenTag.KW_DO,
        "break": TokenTag.KW_BREAK,
        "extern": TokenTag.KW_EXTERN,
        "continue": TokenTag.KW_CONTINUE,
        "true": TokenTag.KW_TRUE,
        "false": TokenTag.KW_FALSE,
        "struct": TokenTag.KW_STRUCT,
    }

    def __init__(self, source: str, filename: str):
        self.source = source
        self.filename = filename

        self.pos = 0
        self.line = 1
        self.col = 1
        self.line_start = 0

    @staticmethod
    def tokenize(source: str, filename: str) -> List[Token]:
        return Tokenizer(source, filename).tokenize_all()

    def _current(self) -> str:
        return "\0" if self.pos >= len(self.source) else self.source[self.pos]

    def _check(self, target: str) -> bool:
        return self.pos < len(self.source) and self.source[self.pos] == target

    def _is_end(self) -> bool:
        return self.pos > len(self.source)

    def _advance(self):
        self.pos += 1
        self.col += 1

    def _skip_whitespace(self):
        while True:
            c = self._current()
            if c in ("\t", " ", "\r"):
                self._advance()
                continue
            if c == "\n":
                self.pos += 1
                self.line += 1
                self.col = 1
                self.line_start = self.pos
                continue
            break

    def _next(self) -> Token:
        self._skip_whitespace()

        tok = Token(
            tag=TokenTag.UNKNOWN,
            value="",
            loc=Location(
                line=self.line,
                col=self.col,
                start=self.pos,
                end=self.pos + 1,
            ),
            line_start=self.line_start,
        )

        c = self._current()

        match c:
            case "\0":
                tok.tag = TokenTag.EOF
                self._advance()
            case "{":
                tok.tag = TokenTag.LBRACE
                self._advance()
            case "}":
                tok.tag = TokenTag.RBRACE
                self._advance()
            case "(":
                tok.tag = TokenTag.LPAREN
                self._advance()
            case ")":
                tok.tag = TokenTag.RPAREN
                self._advance()
            case ";":
                tok.tag = TokenTag.SEMICOLON
                self._advance()
            case "+":
                self._advance()
                if self._check("+"):
                    self._advance()
                    tok.tag = TokenTag.PLUS_PLUS
                elif self._check("="):
                    self._advance()
                    tok.tag = TokenTag.PLUS_EQUAL
                else:
                    tok.tag = TokenTag.PLUS
            case "-":
                self._advance()
                if self._check("-"):
                    self._advance()
                    tok.tag = TokenTag.MINUS_MINUS
                elif self._check("="):
                    self._advance()
                    tok.tag = TokenTag.MINUS_EQUAL
                else:
                    tok.tag = TokenTag.MINUS
            case "*":
                self._advance()
                if self._check("="):
                    self._advance()
                    tok.tag = TokenTag.ASTERISK_EQUAL
                else:
                    tok.tag = TokenTag.ASTERISK
            case "/":
                self._advance()
                if self._check("="):
                    self._advance()
                    tok.tag = TokenTag.SLASH_EQUAL
                else:
                    tok.tag = TokenTag.SLASH
            case "%":
                self._advance()
                if self._check("="):
                    self._advance()
                    tok.tag = TokenTag.MODULUS_EQUAL
                else:
                    tok.tag = TokenTag.MODULUS
            case "<":
                self._advance()
                if self._check("="):
                    self._advance()
                    tok.tag = TokenTag.LESS_EQUAL
                if self._check("<"):
                    self._advance()
                    tok.tag = TokenTag.LESS_LESS
                else:
                    tok.tag = TokenTag.LESS
            case ">":
                self._advance()
                if self._check("="):
                    self._advance()
                    tok.tag = TokenTag.GREATER_EQUAL
                if self._check(">"):
                    self._advance()
                    tok.tag = TokenTag.GREATER_GREATER
                else:
                    tok.tag = TokenTag.GREATER
            case "=":
                self._advance()
                if self._check("="):
                    self._advance()
                    tok.tag = TokenTag.EQUAL_EQUAL
                else:
                    tok.tag = TokenTag.EQUAL
            case "&":
                self._advance()
                if self._check("&"):
                    self._advance()
                    tok.tag = TokenTag.AMPERSAND_AMPERSAND
                else:
                    tok.tag = TokenTag.AMPERSAND
            case "|":
                self._advance()
                if self._check("|"):
                    self._advance()
                    tok.tag = TokenTag.PIPE_PIPE
                else:
                    tok.tag = TokenTag.PIPE
            case "!":
                self._advance()
                if self._check("="):
                    self._advance()
                    tok.tag = TokenTag.NOT_EQUAL
                else:
                    tok.tag = TokenTag.NOT
            case ",":
                self._advance()
                tok.tag = TokenTag.COMMA
            case "^":
                self._advance()
                tok.tag = TokenTag.CARET
            case ":":
                self._advance()
                if self._check(":"):
                    self._advance()
                    tok.tag = TokenTag.COLON_COLON
                else:
                    tok.tag = TokenTag.COLON
            case "@":
                self._advance()
                tok.tag = TokenTag.AT
            case ".":
                self._advance()
                tok.tag = TokenTag.DOT
            case '"':
                self._advance()
                value_chars = []

                while True:
                    c = self._current()
                    if c == '"':
                        self._advance()
                        break
                    elif c == "\\":
                        self._advance()
                        esc = self._current()
                        if esc == "n":
                            value_chars.append("\n")
                        elif esc == "t":
                            value_chars.append("\t")
                        elif esc == "r":
                            value_chars.append("\r")
                        elif esc == "\\":
                            value_chars.append("\\")
                        elif esc == '"':
                            value_chars.append('"')
                        else:
                            raise ValueError(
                                f"Unknown escape sequence '\\{esc}' "
                                f"at line {self.line}, col {self.col}"
                            )
                        self._advance()
                    elif c == "\0":
                        raise ValueError(
                            f"Unterminated string literal starting at line {self.line}, col {self.col}"
                        )
                    else:
                        value_chars.append(c)
                        self._advance()

                tok.tag = TokenTag.STR_LIT
                tok.value = "".join(value_chars)
            case _:
                if c.isdigit():
                    start = self.pos
                    while self._current().isdigit():
                        self._advance()
                    if self._current() in ("l", "L"):
                        self._advance()
                        tok.tag = TokenTag.LONG_LIT
                    else:
                        tok.tag = TokenTag.INT_LIT
                    tok.value = self.source[start:self.pos]
                elif c.isalpha() or c == "_":
                    start = self.pos
                    while self._current().isalnum() or self._current() == "_":
                        self._advance()
                    value = self.source[start:self.pos]
                    tok.tag = self.keywords.get(value, TokenTag.ID)
                    tok.value = value
                else:
                    raise ValueError(
                        f"Unknown character '{c}' at line {self.line}, col {self.col}"
                    )

        tok.loc.end = self.pos
        return tok

    def tokenize_all(self) -> List[Token]:
        tokens = []
        while not self._is_end():
            tokens.append(self._next())
        return tokens
