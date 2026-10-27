from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import ast as ast_module
from .compiler import compile_file
from .diagnostics import GameLangError
from .interpreter import run
from .lexer import lex


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gamelang", description="Compilador da linguagem GameLang")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "tokens", "ast", "ir", "run", "compile"):
        item = sub.add_parser(command)
        item.add_argument("source", type=Path)
        if command in {"ir", "run", "compile"}:
            item.add_argument("--optimize", action="store_true", help="aplica otimizacoes na IR")
        if command == "run":
            item.add_argument("--touch", action="append", default=[], metavar="A,B")
            item.add_argument("--json", action="store_true", help="imprime estado final em JSON")
        if command in {"ir", "compile"}:
            item.add_argument("-o", "--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "tokens":
            data = [token.to_dict() for token in lex(args.source.read_text(encoding="utf-8"))]
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        result = compile_file(args.source, optimize_ir=getattr(args, "optimize", False))
        if args.command == "check":
            print(f"OK: {args.source}")
        elif args.command == "ast":
            print(json.dumps(ast_module.to_dict(result.ast), ensure_ascii=False, indent=2))
        elif args.command == "ir":
            text = result.ir.to_json() + "\n"
            if args.output:
                args.output.write_text(text, encoding="utf-8")
            else:
                print(text, end="")
        elif args.command == "compile":
            output = args.output or args.source.with_suffix(".py")
            output.write_text(result.python, encoding="utf-8")
            print(output)
        elif args.command == "run":
            touches = [_parse_touch(item, parser) for item in args.touch]
            execution = run(result.ir, touches)
            for line in execution.output:
                print(line)
            if args.json:
                print(json.dumps(execution.snapshot(), ensure_ascii=False, sort_keys=True))
        if result.optimization_report and result.optimization_report.total:
            counts = result.optimization_report.counts
            summary = ", ".join(f"{name}={count}" for name, count in counts.items())
            print(f"otimizacoes: {summary}", file=sys.stderr)
        return 0
    except GameLangError as error:
        print(error.diagnostic.format(str(args.source)), file=sys.stderr)
        return 1
    except OSError as error:
        print(f"erro de arquivo: {error}", file=sys.stderr)
        return 2


def _parse_touch(value: str, parser: argparse.ArgumentParser) -> tuple[str, str]:
    parts = value.split(",")
    if len(parts) != 2 or not all(parts):
        parser.error("--touch exige dois nomes separados por virgula, por exemplo player,enemy")
    return parts[0], parts[1]

