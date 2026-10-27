from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .ir import IREvent, IRExpr, IRInstruction, IRProgram


@dataclass(slots=True)
class OptimizationReport:
    counts: dict[str, int] = field(default_factory=lambda: {
        "constant_folding": 0,
        "algebraic_simplification": 0,
        "dead_code_elimination": 0,
    })

    @property
    def total(self) -> int:
        return sum(self.counts.values())


def optimize(program: IRProgram) -> tuple[IRProgram, OptimizationReport]:
    report = OptimizationReport()
    instructions = _instructions(program.instructions, report)
    events = tuple(IREvent(event.left, event.right, _instructions(event.body, report), event.span) for event in program.events)
    return IRProgram(program.entities, instructions, events, program.version), report


def _instructions(items: tuple[IRInstruction, ...], report: OptimizationReport) -> tuple[IRInstruction, ...]:
    result: list[IRInstruction] = []
    for item in items:
        operands = {key: _expr(value, report) if isinstance(value, IRExpr) else value for key, value in item.operands.items()}
        body = _instructions(item.body, report)
        current = IRInstruction(item.op, operands, body, item.span)
        if _is_noop(current):
            report.counts["dead_code_elimination"] += 1
            continue
        if current.op == "repeat" and _const(current.operands["count"]) == 1:
            report.counts["dead_code_elimination"] += 1
            result.extend(current.body)
            continue
        result.append(current)
    return tuple(result)


def _is_noop(item: IRInstruction) -> bool:
    if item.op in {"damage", "heal"}:
        return _const(item.operands["amount"]) == 0
    if item.op == "move":
        value = item.operands["delta"]
        return value.op == "position" and all(_const(x) == 0 for x in value.args)
    if item.op == "repeat":
        return _const(item.operands["count"]) == 0 or not item.body
    return False


def _expr(expression: IRExpr, report: OptimizationReport) -> IRExpr:
    args = tuple(_expr(arg, report) for arg in expression.args)
    current = IRExpr(expression.op, expression.value, args, expression.span)
    simplified = _algebraic(current)
    if simplified is not current:
        report.counts["algebraic_simplification"] += 1
        return simplified
    if args and all(arg.op == "const" for arg in args) and current.op != "property":
        try:
            value = _evaluate_constant(current.op, [arg.value for arg in args])
        except (TypeError, ZeroDivisionError, KeyError):
            return current
        report.counts["constant_folding"] += 1
        return IRExpr("const", value, span=current.span)
    return current


def _algebraic(expression: IRExpr) -> IRExpr:
    if len(expression.args) != 2:
        return expression
    left, right = expression.args
    if expression.op in {"+", "-"} and _const(right) == 0:
        return left
    if expression.op in {"*", "/"} and _const(right) == 1:
        return left
    if expression.op == "*" and _const(left) == 1:
        return right
    if expression.op == "*" and (_const(left) == 0 or _const(right) == 0):
        return IRExpr("const", 0, span=expression.span)
    if expression.op == "+" and _const(left) == 0:
        return right
    return expression


def _const(expression: IRExpr) -> Any | None:
    return expression.value if expression.op == "const" else None


def _evaluate_constant(operator: str, values: list[Any]) -> Any:
    if operator == "position":
        return tuple(values)
    if len(values) == 1:
        return -values[0] if operator == "-" else not values[0]
    left, right = values
    functions = {
        "+": lambda: left + right, "-": lambda: left - right,
        "*": lambda: left * right, "/": lambda: left / right,
        "%": lambda: left % right, "==": lambda: left == right,
        "!=": lambda: left != right, "<": lambda: left < right,
        "<=": lambda: left <= right, ">": lambda: left > right,
        ">=": lambda: left >= right, "and": lambda: left and right,
        "or": lambda: left or right,
    }
    return functions[operator]()

