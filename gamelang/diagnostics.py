from __future__ import annotations

from dataclasses import dataclass

from .source import SourceSpan


@dataclass(frozen=True, slots=True)
class Diagnostic:
    phase: str
    message: str
    span: SourceSpan
    code: str

    def format(self, filename: str = "<entrada>") -> str:
        return (
            f"{filename}:{self.span.line}:{self.span.column}: "
            f"erro {self.phase} [{self.code}]: {self.message}"
        )


class GameLangError(Exception):
    def __init__(self, diagnostic: Diagnostic):
        self.diagnostic = diagnostic
        super().__init__(diagnostic.message)


def fail(phase: str, code: str, message: str, span: SourceSpan) -> "None":
    raise GameLangError(Diagnostic(phase, message, span, code))

