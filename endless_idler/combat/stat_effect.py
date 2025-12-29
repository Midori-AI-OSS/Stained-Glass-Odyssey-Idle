from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StatEffect:
    """Represents a temporary effect that modifies stats."""

    name: str
    stat_modifiers: dict[str, int | float]
    duration: int = -1
    source: str = "unknown"

    def is_expired(self) -> bool:
        return self.duration == 0

    def tick(self) -> None:
        if self.duration > 0:
            self.duration -= 1

