from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .source import SourceSpan


class TokenKind(str, Enum):
    EOF = "EOF"
    IDENT = "IDENT"
    NUMBER = "NUMBER"
    STRING = "STRING"
    ENTITY = "entity"
    WHEN = "when"
    TOUCHES = "touches"
    DAMAGE = "damage"
    BY = "by"
    HEAL = "heal"
    MOVE = "move"
    REPEAT = "repeat"
    PRINT = "print"
    TRUE = "true"
    FALSE = "false"
    AND = "and"
    OR = "or"
    NOT = "not"
    LBRACE = "{"
    RBRACE = "}"
    LPAREN = "("
    RPAREN = ")"
    SEMICOLON = ";"
    COMMA = ","
    DOT = "."
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    PERCENT = "%"
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="


KEYWORDS = {kind.value: kind for kind in TokenKind if kind.value.isalpha()}


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    lexeme: str
    value: Any
    span: SourceSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "lexeme": self.lexeme,
            "value": self.value,
            "span": self.span.to_dict(),
        }

