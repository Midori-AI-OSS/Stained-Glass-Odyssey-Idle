from __future__ import annotations

import json

from pathlib import Path

from endless_idler.save import BAR_SLOTS
from endless_idler.save import DEFAULT_FIGHT_NUMBER
from endless_idler.save import DEFAULT_RUN_TOKENS
from endless_idler.save import SaveManager


def test_default_save_path_uses_stainedlgassodysseyidle_folder(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("ENDLESS_IDLER_SAVE_PATH", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    manager = SaveManager()
    assert manager.path == tmp_path / ".midoriai" / "stainedlgassodysseyidle" / "idlesave.json"


def test_old_default_path_is_not_loaded(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("ENDLESS_IDLER_SAVE_PATH", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    old_path = tmp_path / ".midoriai" / "idlesave.json"
    old_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.write_text(json.dumps({"version": 8, "party_level": 9}), encoding="utf-8")

    manager = SaveManager()
    assert manager.path != old_path
    assert manager.load() is None


def test_load_ignores_legacy_run_fields_and_save_strips_them(monkeypatch, tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    raw_payload = {
        "version": 8,
        "tokens": 999,
        "fight_number": 42,
        "bar": ["ally", "becca", None, None, None, None],
        "standby": [None, "ally", None, None, None, None, None, None, None, None],
        "onsite": ["ally", None, None, None],
        "offsite": ["becca", None, None, None, None, None],
        "stacks": {"ally": 3, "becca": 2},
        "winstreak": 11,
        "battle_start_time": 12345.0,
        "party_level": 5,
    }
    save_path.write_text(json.dumps(raw_payload), encoding="utf-8")

    manager = SaveManager()
    loaded = manager.load()
    assert loaded is not None

    # Legacy run fields are intentionally ignored on load.
    assert loaded.tokens == DEFAULT_RUN_TOKENS
    assert loaded.fight_number == DEFAULT_FIGHT_NUMBER
    assert loaded.bar == [None] * BAR_SLOTS

    manager.save(loaded)
    rewritten = json.loads(save_path.read_text(encoding="utf-8"))

    assert "tokens" not in rewritten
    assert "fight_number" not in rewritten
    assert "bar" not in rewritten
    assert "standby" not in rewritten
    assert "winstreak" not in rewritten
    assert "battle_start_time" not in rewritten

    assert rewritten["onsite"][0] == "ally"
    assert rewritten["offsite"][0] == "becca"
