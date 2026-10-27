from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import ast
from .backend_python import generate_python
from .ir import IRProgram
from .lexer import lex
from .lowering import lower
from .optimizer import OptimizationReport, optimize
from .parser import parse
from .semantics import SemanticModel, analyze
from .tokens import Token


@dataclass(frozen=True, slots=True)
class CompilationResult:
    tokens: list[Token]
    ast: ast.Program
    semantics: SemanticModel
    ir: IRProgram
    python: str
    optimization_report: OptimizationReport | None


def compile_source(source: str, *, optimize_ir: bool = False) -> CompilationResult:
    tokens = lex(source)
    tree = parse(tokens)
    semantics = analyze(tree)
    ir = lower(tree, semantics)
    report = None
    if optimize_ir:
        ir, report = optimize(ir)
    return CompilationResult(tokens, tree, semantics, ir, generate_python(ir), report)


def compile_file(path: str | Path, *, optimize_ir: bool = False) -> CompilationResult:
    return compile_source(Path(path).read_text(encoding="utf-8"), optimize_ir=optimize_ir)

