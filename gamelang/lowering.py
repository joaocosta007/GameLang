from __future__ import annotations

from . import ast
from .ir import IREvent, IRExpr, IRInstruction, IRProgram
from .semantics import SemanticModel


def lower(program: ast.Program, model: SemanticModel) -> IRProgram:
    return IRProgram(
        entities={name: dict(values) for name, values in model.constants.items()},
        instructions=tuple(_statement(item) for item in program.statements),
        events=tuple(IREvent(item.left, item.right, tuple(_statement(x) for x in item.body), item.span) for item in program.events),
    )


def _statement(statement: ast.Statement) -> IRInstruction:
    if isinstance(statement, ast.Damage):
        return IRInstruction("damage", {"entity": statement.entity, "amount": _expr(statement.amount)}, span=statement.span)
    if isinstance(statement, ast.Heal):
        return IRInstruction("heal", {"entity": statement.entity, "amount": _expr(statement.amount)}, span=statement.span)
    if isinstance(statement, ast.Move):
        return IRInstruction("move", {"entity": statement.entity, "delta": _expr(statement.delta)}, span=statement.span)
    if isinstance(statement, ast.Print):
        return IRInstruction("print", {"value": _expr(statement.value)}, span=statement.span)
    if isinstance(statement, ast.Repeat):
        return IRInstruction("repeat", {"count": _expr(statement.count)}, tuple(_statement(x) for x in statement.body), statement.span)
    raise AssertionError(statement)


def _expr(expression: ast.Expr) -> IRExpr:
    if isinstance(expression, ast.Literal):
        return IRExpr("const", expression.value, span=expression.span)
    if isinstance(expression, ast.PropertyRef):
        return IRExpr("property", f"{expression.entity}.{expression.property}", span=expression.span)
    if isinstance(expression, ast.Unary):
        return IRExpr(expression.operator, args=(_expr(expression.operand),), span=expression.span)
    if isinstance(expression, ast.Binary):
        return IRExpr(expression.operator, args=(_expr(expression.left), _expr(expression.right)), span=expression.span)
    if isinstance(expression, ast.Position):
        return IRExpr("position", args=(_expr(expression.x), _expr(expression.y)), span=expression.span)
    raise AssertionError(expression)

