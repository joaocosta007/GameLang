from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


Number = int | float


@dataclass(slots=True)
class EntityState:
    name: str
    properties: dict[str, Number]


@dataclass(slots=True)
class ExecutionResult:
    state: "GameState"
    output: list[str]

    def snapshot(self) -> dict[str, object]:
        return {
            "entities": {
                name: dict(sorted(entity.properties.items()))
                for name, entity in sorted(self.state.entities.items())
            },
            "output": list(self.output),
        }


@dataclass(slots=True)
class GameState:
    entities: dict[str, EntityState] = field(default_factory=dict)
    output: list[str] = field(default_factory=list)
    events: list[tuple[str, str, Callable[["GameState"], None]]] = field(default_factory=list)

    def add_entity(self, name: str, properties: dict[str, Number]) -> None:
        self.entities[name] = EntityState(name, dict(properties))

    def add_event(self, left: str, right: str, handler: Callable[["GameState"], None]) -> None:
        self.events.append((left, right, handler))

    def property(self, qualified_name: str) -> Number:
        entity, prop = qualified_name.split(".", 1)
        return self.entities[entity].properties[prop]

    def damage(self, entity: str, amount: Number) -> None:
        self.entities[entity].properties["health"] -= amount

    def heal(self, entity: str, amount: Number) -> None:
        self.entities[entity].properties["health"] += amount

    def move(self, entity: str, delta: tuple[Number, Number]) -> None:
        self.entities[entity].properties["x"] += delta[0]
        self.entities[entity].properties["y"] += delta[1]

    def emit(self, value: object) -> None:
        self.output.append(format_value(value))

    def touch(self, left: str, right: str) -> None:
        for expected_left, expected_right, handler in self.events:
            if (expected_left == left and expected_right == right) or (expected_left == right and expected_right == left):
                handler(self)


def format_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, tuple) and len(value) == 2:
        return f"({format_value(value[0])}, {format_value(value[1])})"
    return str(value)

