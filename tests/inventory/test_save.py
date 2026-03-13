from __future__ import annotations

import json

from pathlib import Path
from typing import cast

from endless_idler.save import RunSave
from endless_idler.save import SaveManager
from endless_idler.save import STANDBY_SLOTS
from endless_idler.save import sanitize_save_characters


def test_inventory_round_trips_through_save_manager(tmp_path: Path) -> None:
    save_path = tmp_path / "inventory-save.json"
    manager = SaveManager(path=save_path)
    manager.save(
        RunSave(
            inventory={
                "health_potion": 4,
                "power_stone": 2,
            }
        )
    )

    payload = cast(dict[str, object], json.loads(save_path.read_text(encoding="utf-8")))
    assert payload["inventory"] == {"health_potion": 4, "power_stone": 2}

    loaded = manager.load()
    assert loaded is not None
    assert loaded.inventory == {"health_potion": 4, "power_stone": 2}


def test_inventory_normalization_strips_unknown_or_invalid_items(
    tmp_path: Path,
) -> None:
    save_path = tmp_path / "inventory-save.json"
    _ = save_path.write_text(
        json.dumps(
            {
                "version": 10,
                "party_level": 1,
                "party_level_up_cost": 4,
                "party_hp_max": 100,
                "party_hp_current": 100,
                "inventory": {
                    "health_potion": 3,
                    "unknown_item": 8,
                    "fire_shard": 0,
                    " ": 10,
                },
            }
        ),
        encoding="utf-8",
    )

    loaded = SaveManager(path=save_path).load()

    assert loaded is not None
    assert loaded.inventory == {"health_potion": 3}


def test_inventory_normalization_keeps_positive_counts(tmp_path: Path) -> None:
    save_path = tmp_path / "inventory-count-save.json"
    manager = SaveManager(path=save_path)
    manager.save(RunSave(inventory={"radiant_shield": 9, "glass_fragment": 1500}))

    loaded = manager.load()

    assert loaded is not None
    assert loaded.inventory == {"radiant_shield": 9, "glass_fragment": 1500}


def test_sanitize_save_characters_preserves_only_allowed_items() -> None:
    save = RunSave(
        onsite=["ally", None, None, None],
        inventory={
            "health_potion": 5,
            "fake_item": 2,
            "power_stone": 0,
        },
    )

    sanitized = sanitize_save_characters(save=save, allowed_char_ids={"ally"})

    assert sanitized.inventory == {"health_potion": 5}


def test_sanitize_reserved_standby_slot_does_not_prune_character_data() -> None:
    standby: list[str | None] = [None] * STANDBY_SLOTS
    standby[0] = "ally"
    save = RunSave(
        standby=standby,
        character_progress={"ally": {"level": 7, "exp": 56.0, "next_exp": 90.0}},
        character_stats={"ally": {"attack": 42.0}},
        character_initial_stats={"ally": {"attack": 21.0}},
        character_deaths={"ally": 3},
    )

    sanitized = sanitize_save_characters(save=save, allowed_char_ids={"someone_else"})

    assert "ally" in sanitized.character_progress
    assert "ally" in sanitized.character_stats
    assert "ally" in sanitized.character_initial_stats
    assert sanitized.character_deaths.get("ally") == 3
