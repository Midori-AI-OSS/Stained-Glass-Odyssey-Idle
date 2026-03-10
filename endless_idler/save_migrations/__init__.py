from __future__ import annotations

import importlib
import pkgutil

from types import ModuleType

from endless_idler.save_migrations.base import MigratableSave
from endless_idler.save_migrations.base import SaveMigration


def _module_names() -> list[str]:
    return [
        name
        for _, name, _ in pkgutil.iter_modules(__path__)
        if name.startswith("migration_")
    ]


def _load_module(module_name: str) -> ModuleType | None:
    try:
        return importlib.import_module(f"{__name__}.{module_name}")
    except ImportError:
        return None


def _discover_migrations() -> tuple[SaveMigration, ...]:
    migrations: list[SaveMigration] = []
    for module_name in sorted(_module_names()):
        module = _load_module(module_name)
        if module is None:
            continue

        candidate = getattr(module, "migration", None)
        if isinstance(candidate, SaveMigration):
            migrations.append(candidate)

    return tuple(
        sorted(
            migrations, key=lambda migration: (migration.order, migration.migration_id)
        )
    )


_MIGRATIONS: tuple[SaveMigration, ...] = _discover_migrations()


def apply_migrations(save: MigratableSave) -> None:
    for migration in _MIGRATIONS:
        migration.migrate(save)


__all__ = ["apply_migrations"]
