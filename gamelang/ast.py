from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any

from .source import SourceSpan


@dataclass(frozen=True, slots=True)
class Node:
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Expr(Node):
    pass


@dataclass(frozen=True, slots=True)
class Literal(Expr):
    value: Any


@dataclass(frozen=True, slots=True)
class PropertyRef(Expr):
    entity: str
    property: str


@dataclass(frozen=True, slots=True)
class Unary(Expr):
    operator: str
    operand: Expr


@dataclass(frozen=True, slots=True)
class Binary(Expr):
    left: Expr
    operator: str
    right: Expr


@dataclass(frozen=True, slots=True)
class Position(Expr):
    x: Expr
    y: Expr


@dataclass(frozen=True, slots=True)
class Statement(Node):
    pass


@dataclass(frozen=True, slots=True)
class Damage(Statement):
    entity: str
    amount: Expr


@dataclass(frozen=True, slots=True)
class Heal(Statement):
    entity: str
    amount: Expr


@dataclass(frozen=True, slots=True)
class Move(Statement):
    entity: str
    delta: Expr


@dataclass(frozen=True, slots=True)
class Print(Statement):
    value: Expr


@dataclass(frozen=True, slots=True)
class Repeat(Statement):
    count: Expr
    body: tuple[Statement, ...]


@dataclass(frozen=True, slots=True)
class EntityDecl(Node):
    name: str
    properties: tuple[tuple[str, Expr, SourceSpan], ...]


@dataclass(frozen=True, slots=True)
class EventDecl(Node):
    left: str
    right: str
    body: tuple[Statement, ...]


@dataclass(frozen=True, slots=True)
class Program(Node):
    entities: tuple[EntityDecl, ...]
    events: tuple[EventDecl, ...]
    statements: tuple[Statement, ...]


def to_dict(value: Any) -> Any:
    if isinstance(value, SourceSpan):
        return value.to_dict()
    if is_dataclass(value):
        result = {"kind": value.__class__.__name__}
        for field in fields(value):
            result[field.name] = to_dict(getattr(value, field.name))
        return result
    if isinstance(value, tuple):
        return [to_dict(item) for item in value]
    return value

