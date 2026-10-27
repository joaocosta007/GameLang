from __future__ import annotations

from typing import Any, Iterable

from .ir import IRExpr, IRInstruction, IRProgram
from .runtime import ExecutionResult, GameState


def run(program: IRProgram, touches: Iterable[tuple[str, str]] = ()) -> ExecutionResult:
    state = GameState()
    for name, properties in program.entities.items():
        state.add_entity(name, properties)
    for event in program.events:
        state.add_event(event.left, event.right, lambda current, body=event.body: _execute(body, current))
    _execute(program.instructions, state)
    for left, right in touches:
        state.touch(left, right)
    return ExecutionResult(state, list(state.output))


def _execute(instructions: tuple[IRInstruction, ...], state: GameState) -> None:
    for instruction in instructions:
        if instruction.op == "damage":
            state.damage(instruction.operands["entity"], _eval(instruction.operands["amount"], state))
        elif instruction.op == "heal":
            state.heal(instruction.operands["entity"], _eval(instruction.operands["amount"], state))
        elif instruction.op == "move":
            state.move(instruction.operands["entity"], _eval(instruction.operands["delta"], state))
        elif instruction.op == "print":
            state.emit(_eval(instruction.operands["value"], state))
        elif instruction.op == "repeat":
            for _ in range(_eval(instruction.operands["count"], state)):
                _execute(instruction.body, state)
        else:
            raise RuntimeError(f"instrucao IR desconhecida: {instruction.op}")


def _eval(expression: IRExpr, state: GameState) -> Any:
    if expression.op == "const":
        if isinstance(expression.value, list):
            return tuple(expression.value)
        return expression.value
    if expression.op == "property":
        return state.property(expression.value)
    values = [_eval(item, state) for item in expression.args]
    if expression.op == "position":
        return tuple(values)
    if len(values) == 1:
        return -values[0] if expression.op == "-" else not values[0]
    left, right = values
    operations = {
        "+": lambda: left + right, "-": lambda: left - right,
        "*": lambda: left * right, "/": lambda: left / right,
        "%": lambda: left % right, "==": lambda: left == right,
        "!=": lambda: left != right, "<": lambda: left < right,
        "<=": lambda: left <= right, ">": lambda: left > right,
        ">=": lambda: left >= right, "and": lambda: left and right,
        "or": lambda: left or right,
    }
    return operations[expression.op]()

