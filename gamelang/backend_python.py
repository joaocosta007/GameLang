from __future__ import annotations

from .ir import IRExpr, IRInstruction, IRProgram


def generate_python(program: IRProgram) -> str:
    lines = [
        '"""Codigo gerado automaticamente pelo compilador GameLang."""',
        "from __future__ import annotations",
        "",
        "import argparse",
        "import json",
        "import sys",
        "from pathlib import Path",
        "",
        "_origin = Path(globals().get('__file__', Path.cwd())).resolve().parent",
        "for _candidate in (_origin, *_origin.parents):",
        "    if (_candidate / 'gamelang').is_dir():",
        "        sys.path.insert(0, str(_candidate))",
        "        break",
        "",
        "from gamelang.runtime import ExecutionResult, GameState",
        "",
        "",
        "def run(touches=None):",
        "    state = GameState()",
    ]
    for name, properties in program.entities.items():
        lines.append(f"    state.add_entity({name!r}, {properties!r})")
    if not program.entities:
        lines.append("    pass")
    for index, event in enumerate(program.events):
        lines.extend(["", f"    def _event_{index}(state):"])
        lines.extend(_instructions(event.body, 8) or ["        pass"])
        lines.append(f"    state.add_event({event.left!r}, {event.right!r}, _event_{index})")
    lines.extend(_instructions(program.instructions, 4))
    lines.extend([
        "    for left, right in touches or []:",
        "        state.touch(left, right)",
        "    return ExecutionResult(state, list(state.output))",
        "",
        "",
        "def main():",
        "    parser = argparse.ArgumentParser(description='Programa gerado a partir de GameLang')",
        "    parser.add_argument('--touch', action='append', default=[], metavar='A,B')",
        "    parser.add_argument('--state-json', action='store_true')",
        "    args = parser.parse_args()",
        "    touches = [tuple(item.split(',', 1)) for item in args.touch]",
        "    result = run(touches)",
        "    for line in result.output:",
        "        print(line)",
        "    if args.state_json:",
        "        print(json.dumps(result.snapshot(), ensure_ascii=False, sort_keys=True))",
        "",
        "",
        "if __name__ == '__main__':",
        "    main()",
        "",
    ])
    return "\n".join(lines)


def _instructions(instructions: tuple[IRInstruction, ...], indent: int) -> list[str]:
    pad = " " * indent
    lines: list[str] = []
    for item in instructions:
        if item.op == "damage":
            lines.append(f"{pad}state.damage({item.operands['entity']!r}, {_expr(item.operands['amount'])})")
        elif item.op == "heal":
            lines.append(f"{pad}state.heal({item.operands['entity']!r}, {_expr(item.operands['amount'])})")
        elif item.op == "move":
            lines.append(f"{pad}state.move({item.operands['entity']!r}, {_expr(item.operands['delta'])})")
        elif item.op == "print":
            lines.append(f"{pad}state.emit({_expr(item.operands['value'])})")
        elif item.op == "repeat":
            lines.append(f"{pad}for _ in range({_expr(item.operands['count'])}):")
            lines.extend(_instructions(item.body, indent + 4) or [" " * (indent + 4) + "pass"])
    return lines


def _expr(expression: IRExpr) -> str:
    if expression.op == "const":
        value = tuple(expression.value) if isinstance(expression.value, list) else expression.value
        return repr(value)
    if expression.op == "property":
        return f"state.property({expression.value!r})"
    if expression.op == "position":
        return f"({_expr(expression.args[0])}, {_expr(expression.args[1])})"
    if len(expression.args) == 1:
        operator = "not " if expression.op == "not" else "-"
        return f"({operator}{_expr(expression.args[0])})"
    return f"({_expr(expression.args[0])} {expression.op} {_expr(expression.args[1])})"

