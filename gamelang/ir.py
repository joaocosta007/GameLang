from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .source import SourceSpan, UNKNOWN_SPAN


@dataclass(frozen=True, slots=True)
class IRExpr:
    op: str
    value: Any = None
    args: tuple["IRExpr", ...] = ()
    span: SourceSpan = UNKNOWN_SPAN

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"op": self.op}
        if self.value is not None:
            result["value"] = self.value
        if self.args:
            result["args"] = [arg.to_dict() for arg in self.args]
        result["span"] = self.span.to_dict()
        return result

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "IRExpr":
        span = SourceSpan(**data.get("span", UNKNOWN_SPAN.to_dict()))
        return IRExpr(data["op"], data.get("value"), tuple(IRExpr.from_dict(x) for x in data.get("args", [])), span)


@dataclass(frozen=True, slots=True)
class IRInstruction:
    op: str
    operands: dict[str, Any] = field(default_factory=dict)
    body: tuple["IRInstruction", ...] = ()
    span: SourceSpan = UNKNOWN_SPAN

    def to_dict(self) -> dict[str, Any]:
        def convert(value: Any) -> Any:
            if isinstance(value, IRExpr):
                return {"$expr": value.to_dict()}
            return value
        return {
            "op": self.op,
            "operands": {key: convert(value) for key, value in self.operands.items()},
            "body": [item.to_dict() for item in self.body],
            "span": self.span.to_dict(),
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "IRInstruction":
        def convert(value: Any) -> Any:
            return IRExpr.from_dict(value["$expr"]) if isinstance(value, dict) and "$expr" in value else value
        return IRInstruction(
            data["op"],
            {key: convert(value) for key, value in data.get("operands", {}).items()},
            tuple(IRInstruction.from_dict(x) for x in data.get("body", [])),
            SourceSpan(**data.get("span", UNKNOWN_SPAN.to_dict())),
        )


@dataclass(frozen=True, slots=True)
class IREvent:
    left: str
    right: str
    body: tuple[IRInstruction, ...]
    span: SourceSpan = UNKNOWN_SPAN

    def to_dict(self) -> dict[str, Any]:
        return {
            "left": self.left,
            "right": self.right,
            "body": [item.to_dict() for item in self.body],
            "span": self.span.to_dict(),
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "IREvent":
        return IREvent(data["left"], data["right"], tuple(IRInstruction.from_dict(x) for x in data["body"]), SourceSpan(**data.get("span", UNKNOWN_SPAN.to_dict())))


@dataclass(frozen=True, slots=True)
class IRProgram:
    entities: dict[str, dict[str, int | float]]
    instructions: tuple[IRInstruction, ...]
    events: tuple[IREvent, ...]
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": "GameLang-IR",
            "version": self.version,
            "entities": self.entities,
            "instructions": [item.to_dict() for item in self.instructions],
            "events": [event.to_dict() for event in self.events],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, sort_keys=True)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json() + "\n", encoding="utf-8")

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "IRProgram":
        if data.get("format") != "GameLang-IR":
            raise ValueError("formato de IR invalido")
        return IRProgram(
            data["entities"],
            tuple(IRInstruction.from_dict(x) for x in data.get("instructions", [])),
            tuple(IREvent.from_dict(x) for x in data.get("events", [])),
            data.get("version", "1.0"),
        )

    @staticmethod
    def load(path: str | Path) -> "IRProgram":
        return IRProgram.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

