"""GameLang compiler public API."""

from .compiler import CompilationResult, compile_file, compile_source
from .diagnostics import Diagnostic, GameLangError

__all__ = [
    "CompilationResult",
    "Diagnostic",
    "GameLangError",
    "compile_file",
    "compile_source",
]

__version__ = "1.0.0"

