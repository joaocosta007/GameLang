from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class SourceSpan:
    line: int
    column: int
    end_line: int
    end_column: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)

    @staticmethod
    def merge(first: "SourceSpan", last: "SourceSpan") -> "SourceSpan":
        return SourceSpan(first.line, first.column, last.end_line, last.end_column)


UNKNOWN_SPAN = SourceSpan(1, 1, 1, 1)

