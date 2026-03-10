from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType
from typing import Any

import endless_idler.save_migrations as save_migrations

from endless_idler.save_migrations.base import SaveMigration


@dataclass
class _FakeSave:
    version: int = 12
    blessings: dict[str, dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        if self.blessings is None:
            self.blessings = {}


def test_discovery_finds_existing_migration_module() -> None:
    discovered = save_migrations._discover_migrations()
    migration_ids = {migration.migration_id for migration in discovered}
    assert "v12_lunar_legacy_reset" in migration_ids


def test_discovery_orders_by_order_then_migration_id(monkeypatch) -> None:
    module_a = ModuleType("migration_a")
    module_b = ModuleType("migration_b")
    module_z = ModuleType("migration_z")

    module_a.migration = SaveMigration(
        migration_id="b_same_order",
        order=100,
        migrate=lambda _save: None,
    )
    module_b.migration = SaveMigration(
        migration_id="a_same_order",
        order=100,
        migrate=lambda _save: None,
    )
    module_z.migration = SaveMigration(
        migration_id="z_lower_order",
        order=50,
        migrate=lambda _save: None,
    )

    modules = {
        "migration_z": module_z,
        "migration_b": module_b,
        "migration_a": module_a,
    }

    monkeypatch.setattr(
        save_migrations,
        "_module_names",
        lambda: ["migration_z", "migration_b", "migration_a"],
    )
    monkeypatch.setattr(save_migrations, "_load_module", modules.get)

    discovered = save_migrations._discover_migrations()
    assert [migration.migration_id for migration in discovered] == [
        "z_lower_order",
        "a_same_order",
        "b_same_order",
    ]


def test_apply_migrations_invokes_migrations_in_expected_order(monkeypatch) -> None:
    calls: list[str] = []

    migrations = (
        SaveMigration(
            migration_id="second",
            order=20,
            migrate=lambda _save: calls.append("second"),
        ),
        SaveMigration(
            migration_id="first", order=10, migrate=lambda _save: calls.append("first")
        ),
    )

    monkeypatch.setattr(
        save_migrations,
        "_MIGRATIONS",
        tuple(
            sorted(
                migrations,
                key=lambda migration: (migration.order, migration.migration_id),
            )
        ),
    )

    save_migrations.apply_migrations(_FakeSave())
    assert calls == ["first", "second"]


def test_lunar_migration_still_applies_for_pre_v12_saves() -> None:
    save = _FakeSave(
        version=11,
        blessings={
            "lunar_blessing": {
                "steps": 123,
                "total_minutes": 456,
                "last_tick_time": 789.0,
                "step_start_time": 321.0,
                "unlocked": False,
            }
        },
    )

    save_migrations.apply_migrations(save)

    lunar = save.blessings["lunar_blessing"]
    assert lunar["steps"] == 0
    assert lunar["total_minutes"] == 0
    assert lunar["last_tick_time"] == 0.0
    assert lunar["step_start_time"] == 0.0
    assert lunar["unlocked"] is False
