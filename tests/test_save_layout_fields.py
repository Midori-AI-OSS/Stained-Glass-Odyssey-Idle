from __future__ import annotations

import json

from pathlib import Path

from endless_idler.save import DEFAULT_LAYOUT_OWNED_ORDERING
from endless_idler.save import RunSave
from endless_idler.save import SaveManager


def test_layout_fields_round_trip(monkeypatch, tmp_path: Path) -> None:
    save_path = tmp_path / "layout-save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    save = RunSave(
        layout_tick_cooldown_seconds=3.25,
        layout_owned_ordering="alphabetical",
    )
    manager = SaveManager()
    manager.save(save)

    payload = json.loads(save_path.read_text(encoding="utf-8"))
    assert payload["layout_tick_cooldown_seconds"] == 3.25
    assert payload["layout_owned_ordering"] == "alphabetical"

    loaded = manager.load()
    assert loaded is not None
    assert loaded.layout_tick_cooldown_seconds == 3.25
    assert loaded.layout_owned_ordering == "alphabetical"


def test_layout_fields_normalize_invalid_values(monkeypatch, tmp_path: Path) -> None:
    save_path = tmp_path / "layout-save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    save_path.write_text(
        json.dumps(
            {
                "version": 10,
                "party_level": 1,
                "party_level_up_cost": 4,
                "party_hp_max": 100,
                "party_hp_current": 100,
                "layout_tick_cooldown_seconds": -42.0,
                "layout_owned_ordering": "not-a-valid-order",
            }
        ),
        encoding="utf-8",
    )

    loaded = SaveManager().load()
    assert loaded is not None
    assert loaded.layout_tick_cooldown_seconds == 0.0
    assert loaded.layout_owned_ordering == DEFAULT_LAYOUT_OWNED_ORDERING
