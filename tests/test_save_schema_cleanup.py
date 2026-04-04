from __future__ import annotations

import json

from pathlib import Path

import pytest

from endless_idler.save import BAR_SLOTS
from endless_idler.save import DEFAULT_FIGHT_NUMBER
from endless_idler.save import DEFAULT_RUN_TOKENS
from endless_idler.save import RunSave
from endless_idler.save import SaveManager


def test_default_save_path_uses_stainedglassodysseyidle_folder(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("ENDLESS_IDLER_SAVE_PATH", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    manager = SaveManager()
    assert (
        manager.path
        == tmp_path / ".midoriai" / "stainedglassodysseyidle" / "idlesave.json"
    )


def test_old_default_path_is_not_loaded(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("ENDLESS_IDLER_SAVE_PATH", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    old_path = tmp_path / ".midoriai" / "idlesave.json"
    old_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.write_text(json.dumps({"version": 8, "party_level": 9}), encoding="utf-8")

    manager = SaveManager()
    assert manager.path != old_path
    assert manager.load() is None


def test_load_ignores_legacy_run_fields_and_save_strips_them(
    monkeypatch, tmp_path: Path
) -> None:
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
    assert "winstreak" not in rewritten
    assert "battle_start_time" not in rewritten

    assert rewritten["onsite"][0] == "ally"
    assert rewritten["offsite"][0] == "becca"
    assert rewritten["standby"][1] == "ally"


def test_load_ignores_removed_idle_timer_legacy_fields(
    monkeypatch, tmp_path: Path
) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    save_path.write_text(
        json.dumps(
            {
                "version": 10,
                "party_level": 1,
                "idle_exp_bonus_until": 9999999999,
                "idle_exp_penalty_until": 9999999999,
            }
        ),
        encoding="utf-8",
    )

    loaded = SaveManager().load()
    assert loaded is not None
    assert loaded.idle_exp_bonus_seconds == 0.0
    assert loaded.idle_exp_penalty_seconds == 0.0


def test_load_rejects_noncanonical_blessing_payload(
    monkeypatch, tmp_path: Path
) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    canonical = RunSave().blessings
    lunar = dict(canonical["lunar_blessing"])
    lunar["step_start_time"] = 321.0
    canonical["lunar_blessing"] = lunar

    save_path.write_text(
        json.dumps(
            {
                "version": 12,
                "party_level": 1,
                "blessings": canonical,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-canonical fields"):
        _ = SaveManager().load()


def test_current_version_loads_canonical_lunar_blessing(
    monkeypatch, tmp_path: Path
) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    save = RunSave()
    save.blessings["lunar_blessing"] = {
        "steps": 8,
        "unlocked": True,
    }
    SaveManager().save(save)

    loaded = SaveManager().load()
    assert loaded is not None

    lunar = loaded.blessings["lunar_blessing"]
    assert lunar["steps"] == 8
    assert lunar["unlocked"] is True


def test_current_version_round_trips_canonical_passives(
    monkeypatch, tmp_path: Path
) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    save = RunSave()
    SaveManager().save(save)

    payload = json.loads(save_path.read_text(encoding="utf-8"))
    assert payload["passives"] == RunSave().passives

    loaded = SaveManager().load()
    assert loaded is not None
    assert loaded.passives == RunSave().passives


def test_load_rejects_noncanonical_passive_payload_extra_fields(
    monkeypatch, tmp_path: Path
) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    canonical = RunSave().passives
    passive_data = dict(canonical["lady_fire_infernal_momentum"])
    passive_data["runtime_only"] = 321
    canonical["lady_fire_infernal_momentum"] = passive_data

    save_path.write_text(
        json.dumps(
            {
                "version": 12,
                "party_level": 1,
                "passives": canonical,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-canonical fields"):
        _ = SaveManager().load()


def test_load_rejects_unknown_passive_id(monkeypatch, tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    canonical = RunSave().passives
    canonical["unknown_passive"] = {}

    save_path.write_text(
        json.dumps(
            {
                "version": 12,
                "party_level": 1,
                "passives": canonical,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unknown passive ids"):
        _ = SaveManager().load()


def test_load_rejects_missing_passive_payload(monkeypatch, tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    canonical = RunSave().passives
    _ = canonical.pop("lady_fire_infernal_momentum")

    save_path.write_text(
        json.dumps(
            {
                "version": 12,
                "party_level": 1,
                "passives": canonical,
            }
        ),
        encoding="utf-8",
    )

    loaded = SaveManager().load()
    assert loaded is not None
    assert loaded.passives["lady_fire_infernal_momentum"] == {}


def test_load_seeds_new_passive_ids_into_existing_canonical_payload(
    monkeypatch, tmp_path: Path
) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    canonical = RunSave().passives
    _ = canonical.pop("trinity_synergy")
    _ = canonical.pop("lady_light_radiant_aegis")
    _ = canonical.pop("lady_darkness_eclipsing_veil")

    save_path.write_text(
        json.dumps(
            {
                "version": 12,
                "party_level": 1,
                "passives": canonical,
            }
        ),
        encoding="utf-8",
    )

    loaded = SaveManager().load()
    assert loaded is not None
    assert loaded.passives["trinity_synergy"] == {
        "stack_ttls": [],
        "stack_progress_ticks": 0,
    }
    assert loaded.passives["lady_darkness_eclipsing_veil"] == {
        "bleed_stack_ttls": [],
        "bleed_progress_ticks": 0,
    }
    assert loaded.passives["lady_light_radiant_aegis"] == {}


def test_load_rejects_noncanonical_list_int_passive_payload(
    monkeypatch, tmp_path: Path
) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    canonical = RunSave().passives
    canonical["trinity_synergy"] = {
        "stack_ttls": [450, True],
        "stack_progress_ticks": 0,
    }

    save_path.write_text(
        json.dumps(
            {
                "version": 12,
                "party_level": 1,
                "passives": canonical,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must be list\\[int\\]"):
        _ = SaveManager().load()


def test_current_version_round_trips_list_int_passive_schema(
    monkeypatch, tmp_path: Path
) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    save = RunSave()
    save.passives["trinity_synergy"] = {
        "stack_ttls": [449, 420, 13],
        "stack_progress_ticks": 17,
    }
    save.passives["lady_darkness_eclipsing_veil"] = {
        "bleed_stack_ttls": [450, 12],
        "bleed_progress_ticks": 9,
    }
    SaveManager().save(save)

    loaded = SaveManager().load()
    assert loaded is not None
    assert loaded.passives["trinity_synergy"] == {
        "stack_ttls": [449, 420, 13],
        "stack_progress_ticks": 17,
    }
    assert loaded.passives["lady_darkness_eclipsing_veil"] == {
        "bleed_stack_ttls": [450, 12],
        "bleed_progress_ticks": 9,
    }


def test_missing_passives_key_loads_and_rewrites_canonical_defaults(
    monkeypatch, tmp_path: Path
) -> None:
    save_path = tmp_path / "save.json"
    monkeypatch.setenv("ENDLESS_IDLER_SAVE_PATH", str(save_path))

    save_path.write_text(
        json.dumps(
            {
                "version": 12,
                "party_level": 1,
            }
        ),
        encoding="utf-8",
    )

    manager = SaveManager()
    loaded = manager.load()
    assert loaded is not None
    assert loaded.passives == RunSave().passives

    manager.save(loaded)
    rewritten = json.loads(save_path.read_text(encoding="utf-8"))
    assert rewritten["passives"] == RunSave().passives
