from __future__ import annotations

from .diagnostics import fail
from .source import SourceSpan
from .tokens import KEYWORDS, Token, TokenKind


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while not self._at_end():
            char = self._peek()
            if char in " \t\r\n":
                self._skip_whitespace()
            elif char == "#" or (char == "/" and self._peek(1) == "/"):
                self._skip_comment()
            elif char.isalpha() or char == "_":
                tokens.append(self._identifier())
            elif char.isdigit():
                tokens.append(self._number())
            elif char == '"':
                tokens.append(self._string())
            else:
                tokens.append(self._operator())
        span = SourceSpan(self.line, self.column, self.line, self.column)
        tokens.append(Token(TokenKind.EOF, "", None, span))
        return tokens

    def _at_end(self) -> bool:
        return self.index >= len(self.source)

    def _peek(self, offset: int = 0) -> str:
        pos = self.index + offset
        return "\0" if pos >= len(self.source) else self.source[pos]

    def _advance(self) -> str:
        char = self.source[self.index]
        self.index += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _span(self, line: int, column: int) -> SourceSpan:
        return SourceSpan(line, column, self.line, self.column)

    def _skip_whitespace(self) -> None:
        while self._peek() in " \t\r\n":
            self._advance()

    def _skip_comment(self) -> None:
        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _identifier(self) -> Token:
        start = self.index
        line, column = self.line, self.column
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        lexeme = self.source[start:self.index]
        kind = KEYWORDS.get(lexeme, TokenKind.IDENT)
        value = lexeme if kind == TokenKind.IDENT else None
        return Token(kind, lexeme, value, self._span(line, column))

    def _number(self) -> Token:
        start = self.index
        line, column = self.line, self.column
        while self._peek().isdigit():
            self._advance()
        is_real = False
        if self._peek() == "." and self._peek(1).isdigit():
            is_real = True
            self._advance()
            while self._peek().isdigit():
                self._advance()
        lexeme = self.source[start:self.index]
        value = float(lexeme) if is_real else int(lexeme)
        return Token(TokenKind.NUMBER, lexeme, value, self._span(line, column))

    def _string(self) -> Token:
        line, column = self.line, self.column
        start = self.index
        self._advance()
        chars: list[str] = []
        escapes = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
        while not self._at_end() and self._peek() != '"':
            if self._peek() == "\n":
                fail("lexico", "L002", "texto nao terminado antes do fim da linha", self._span(line, column))
            char = self._advance()
            if char == "\\":
                if self._at_end():
                    break
                escaped = self._advance()
                if escaped not in escapes:
                    fail("lexico", "L003", f"sequencia de escape desconhecida: \\{escaped}", self._span(line, column))
                chars.append(escapes[escaped])
            else:
                chars.append(char)
        if self._at_end():
            fail("lexico", "L002", "texto nao terminado", self._span(line, column))
        self._advance()
        return Token(TokenKind.STRING, self.source[start:self.index], "".join(chars), self._span(line, column))

    def _operator(self) -> Token:
        line, column = self.line, self.column
        char = self._advance()
        two = char + self._peek()
        two_char = {"==": TokenKind.EQ, "!=": TokenKind.NE, "<=": TokenKind.LE, ">=": TokenKind.GE}
        if two in two_char:
            self._advance()
            return Token(two_char[two], two, None, self._span(line, column))
        one_char = {
            "{": TokenKind.LBRACE, "}": TokenKind.RBRACE,
            "(": TokenKind.LPAREN, ")": TokenKind.RPAREN,
            ";": TokenKind.SEMICOLON, ",": TokenKind.COMMA,
            ".": TokenKind.DOT, "=": TokenKind.ASSIGN,
            "+": TokenKind.PLUS, "-": TokenKind.MINUS,
            "*": TokenKind.STAR, "/": TokenKind.SLASH,
            "%": TokenKind.PERCENT, "<": TokenKind.LT, ">": TokenKind.GT,
        }
        kind = one_char.get(char)
        if kind is None:
            fail("lexico", "L001", f"caractere inesperado: {char!r}", self._span(line, column))
        return Token(kind, char, None, self._span(line, column))


def lex(source: str) -> list[Token]:
    return Lexer(source).tokenize()

