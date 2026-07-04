from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Protocol


class MigratableSave(Protocol):
    version: int
    blessings: dict[str, dict[str, Any]]


MigrationFn = Callable[[MigratableSave], None]


@dataclass(frozen=True, slots=True)
class SaveMigration:
    migration_id: str
    order: int
    migrate: MigrationFn
