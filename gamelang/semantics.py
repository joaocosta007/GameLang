from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from . import ast
from .diagnostics import fail


class Type(str, Enum):
    INTEGER = "inteiro"
    REAL = "real"
    BOOLEAN = "booleano"
    TEXT = "texto"
    POSITION = "posicao"


NUMERIC = {Type.INTEGER, Type.REAL}


@dataclass(frozen=True, slots=True)
class SemanticModel:
    entities: dict[str, dict[str, Type]]
    constants: dict[str, dict[str, int | float]]


class Analyzer:
    def __init__(self, program: ast.Program):
        self.program = program
        self.entities: dict[str, dict[str, Type]] = {}
        self.constants: dict[str, dict[str, int | float]] = {}

    def analyze(self) -> SemanticModel:
        self._declare_entities()
        for event in self.program.events:
            self._require_entity(event.left, event.span)
            self._require_entity(event.right, event.span)
            self._statements(event.body)
        self._statements(self.program.statements)
        return SemanticModel(self.entities, self.constants)

    def _declare_entities(self) -> None:
        for entity in self.program.entities:
            if entity.name in self.entities:
                fail("semantico", "S001", f"entidade duplicada: {entity.name}", entity.span)
            properties: dict[str, Type] = {}
            values: dict[str, int | float] = {}
            self.entities[entity.name] = properties
            self.constants[entity.name] = values
            for name, expression, span in entity.properties:
                if name in properties:
                    fail("semantico", "S002", f"propriedade duplicada: {entity.name}.{name}", span)
                value_type = self._expr(expression)
                if value_type not in NUMERIC:
                    fail("semantico", "S003", f"propriedades devem ser numericas; {entity.name}.{name} recebeu {value_type.value}", expression.span)
                constant = constant_value(expression)
                if constant is None or isinstance(constant, bool):
                    fail("semantico", "S004", f"valor inicial de {entity.name}.{name} deve ser uma expressao numerica constante", expression.span)
                properties[name] = value_type
                values[name] = constant

    def _statements(self, statements: tuple[ast.Statement, ...]) -> None:
        for statement in statements:
            if isinstance(statement, (ast.Damage, ast.Heal)):
                self._require_entity(statement.entity, statement.span)
                self._require_property(statement.entity, "health", statement.span)
                if self._expr(statement.amount) not in NUMERIC:
                    fail("semantico", "S011", "a quantidade de dano ou cura deve ser numerica", statement.amount.span)
            elif isinstance(statement, ast.Move):
                self._require_entity(statement.entity, statement.span)
                self._require_property(statement.entity, "x", statement.span)
                self._require_property(statement.entity, "y", statement.span)
                if self._expr(statement.delta) != Type.POSITION:
                    fail("semantico", "S012", "movimento exige uma posicao no formato (x, y)", statement.delta.span)
            elif isinstance(statement, ast.Print):
                self._expr(statement.value)
            elif isinstance(statement, ast.Repeat):
                if self._expr(statement.count) != Type.INTEGER:
                    fail("semantico", "S013", "a contagem de 'repeat' deve ser inteira", statement.count.span)
                count = constant_value(statement.count)
                if isinstance(count, int) and not isinstance(count, bool) and count < 0:
                    fail("semantico", "S014", "a contagem de 'repeat' nao pode ser negativa", statement.count.span)
                self._statements(statement.body)

    def _expr(self, expression: ast.Expr) -> Type:
        if isinstance(expression, ast.Literal):
            if isinstance(expression.value, bool):
                return Type.BOOLEAN
            if isinstance(expression.value, int):
                return Type.INTEGER
            if isinstance(expression.value, float):
                return Type.REAL
            return Type.TEXT
        if isinstance(expression, ast.PropertyRef):
            self._require_entity(expression.entity, expression.span)
            return self._require_property(expression.entity, expression.property, expression.span)
        if isinstance(expression, ast.Position):
            if self._expr(expression.x) not in NUMERIC or self._expr(expression.y) not in NUMERIC:
                fail("semantico", "S020", "os componentes de uma posicao devem ser numericos", expression.span)
            return Type.POSITION
        if isinstance(expression, ast.Unary):
            operand = self._expr(expression.operand)
            if expression.operator == "-" and operand in NUMERIC:
                return operand
            if expression.operator == "not" and operand == Type.BOOLEAN:
                return Type.BOOLEAN
            fail("semantico", "S021", f"operador '{expression.operator}' incompativel com {operand.value}", expression.span)
        if isinstance(expression, ast.Binary):
            left = self._expr(expression.left)
            right = self._expr(expression.right)
            op = expression.operator
            if op in {"+", "-", "*", "/", "%"}:
                if op == "+" and left == right == Type.TEXT:
                    return Type.TEXT
                if left in NUMERIC and right in NUMERIC:
                    return Type.REAL if Type.REAL in {left, right} or op == "/" else Type.INTEGER
            elif op in {"<", "<=", ">", ">="} and left in NUMERIC and right in NUMERIC:
                return Type.BOOLEAN
            elif op in {"==", "!="} and (left == right or left in NUMERIC and right in NUMERIC):
                return Type.BOOLEAN
            elif op in {"and", "or"} and left == right == Type.BOOLEAN:
                return Type.BOOLEAN
            fail("semantico", "S022", f"operacao '{op}' incompativel entre {left.value} e {right.value}", expression.span)
        raise AssertionError(f"expressao desconhecida: {expression!r}")

    def _require_entity(self, name: str, span) -> dict[str, Type]:
        if name not in self.entities:
            fail("semantico", "S005", f"entidade inexistente: {name}", span)
        return self.entities[name]

    def _require_property(self, entity: str, prop: str, span) -> Type:
        properties = self._require_entity(entity, span)
        if prop not in properties:
            fail("semantico", "S006", f"propriedade inexistente: {entity}.{prop}", span)
        return properties[prop]


def constant_value(expression: ast.Expr) -> Any | None:
    if isinstance(expression, ast.Literal):
        return expression.value
    if isinstance(expression, ast.Unary):
        value = constant_value(expression.operand)
        if value is None:
            return None
        try:
            return -value if expression.operator == "-" else not value
        except (TypeError, ZeroDivisionError):
            return None
    if isinstance(expression, ast.Binary):
        left = constant_value(expression.left)
        right = constant_value(expression.right)
        if left is None or right is None:
            return None
        try:
            return _apply_binary(expression.operator, left, right)
        except (TypeError, ZeroDivisionError):
            return None
    if isinstance(expression, ast.Position):
        x = constant_value(expression.x)
        y = constant_value(expression.y)
        return None if x is None or y is None else (x, y)
    return None


def _apply_binary(operator: str, left: Any, right: Any) -> Any:
    operations = {
        "+": lambda: left + right, "-": lambda: left - right,
        "*": lambda: left * right, "/": lambda: left / right,
        "%": lambda: left % right, "==": lambda: left == right,
        "!=": lambda: left != right, "<": lambda: left < right,
        "<=": lambda: left <= right, ">": lambda: left > right,
        ">=": lambda: left >= right, "and": lambda: left and right,
        "or": lambda: left or right,
    }
    return operations[operator]()


def analyze(program: ast.Program) -> SemanticModel:
    return Analyzer(program).analyze()

