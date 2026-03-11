from __future__ import annotations

import json
import random

from pathlib import Path

import pytest

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.run_save_store import RunSaveStore
from endless_idler.save import SaveManager


def _plugin(char_id: str, placement: str) -> CharacterPlugin:
    return CharacterPlugin(
        char_id=char_id, display_name=char_id.title(), placement=placement
    )


def _trinity_plugins() -> list[CharacterPlugin]:
    return [
        _plugin("lady_darkness", "onsite"),
        _plugin("lady_light", "offsite"),
        _plugin("persona_light_and_dark", "both"),
    ]


def test_run_save_store_load_or_create_bootstraps_new_save(tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    store = RunSaveStore(
        plugins=_trinity_plugins(),
        save_manager=SaveManager(path=save_path),
        rng=random.Random(7),
    )

    save = store.load_or_create()

    assigned = [item for item in [*save.onsite, *save.offsite] if item]
    assert len(assigned) == 3
    assert set(assigned) == {"lady_darkness", "lady_light", "persona_light_and_dark"}
    assert save_path.exists()
    assert not list(tmp_path.glob("save.*.crash.backup*.json"))
    store.shutdown()


def test_run_save_store_startup_load_exception_creates_crash_backup_and_resets(
    tmp_path: Path,
) -> None:
    save_path = tmp_path / "save.json"
    save_path.write_text(
        json.dumps(
            {
                "version": 12,
                "party_level": 99,
                "blessings": {
                    "lunar_blessing": {
                        "steps": 4,
                        "unlocked": True,
                        "step_start_time": 321.0,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    store = RunSaveStore(
        plugins=_trinity_plugins(),
        save_manager=SaveManager(path=save_path),
        rng=random.Random(13),
    )

    save = store.load_or_create()

    crash_backups = sorted(tmp_path.glob("save.*.crash.backup*.json"))
    assert len(crash_backups) == 1

    backed_up_payload = json.loads(crash_backups[0].read_text(encoding="utf-8"))
    assert backed_up_payload["party_level"] == 99
    assert (
        backed_up_payload["blessings"]["lunar_blessing"]["step_start_time"] == 321.0
    )

    rewritten_payload = json.loads(save_path.read_text(encoding="utf-8"))
    assert rewritten_payload["party_level"] == 1
    assert set(rewritten_payload["blessings"]["lunar_blessing"]) == {"steps", "unlocked"}
    assert save.party_level == 1
    store.shutdown()


def test_run_save_store_startup_backup_failure_raises_and_preserves_save(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    save_path = tmp_path / "save.json"
    original_payload = json.dumps(
        {
            "version": 12,
            "party_level": 77,
            "blessings": {
                "lunar_blessing": {
                    "steps": 1,
                    "unlocked": True,
                    "step_start_time": 12.0,
                }
            },
        }
    )
    save_path.write_text(original_payload, encoding="utf-8")
    store = RunSaveStore(
        plugins=_trinity_plugins(),
        save_manager=SaveManager(path=save_path),
    )

    def _raise_copy_error(*_args: object, **_kwargs: object) -> None:
        raise OSError("copy failed")

    monkeypatch.setattr("endless_idler.run_save_store.copy2", _raise_copy_error)

    try:
        with pytest.raises(
            RuntimeError, match="Startup save recovery aborted because backup failed"
        ):
            _ = store.load_or_create()
    finally:
        store._save_queue.shutdown()

    assert save_path.read_text(encoding="utf-8") == original_payload
    assert not list(tmp_path.glob("save.*.crash.backup*.json"))


def test_run_save_store_backup_current_creates_collision_safe_files(
    tmp_path: Path,
) -> None:
    save_path = tmp_path / "save.json"
    store = RunSaveStore(
        plugins=_trinity_plugins(),
        save_manager=SaveManager(path=save_path),
        rng=random.Random(3),
    )
    save = store.load_or_create()
    save.party_level = 7

    backup_one = store.backup_current()
    backup_two = store.backup_current()

    assert backup_one.exists()
    assert backup_two.exists()
    assert backup_one != backup_two
    assert json.loads(backup_one.read_text(encoding="utf-8"))["party_level"] == 7
    store.shutdown()


def test_run_save_store_delete_active_save_removes_file(tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    store = RunSaveStore(
        plugins=_trinity_plugins(),
        save_manager=SaveManager(path=save_path),
    )
    _ = store.load_or_create()

    assert save_path.exists()
    store.delete_active_save()
    assert not save_path.exists()
    store.shutdown()


def test_run_save_store_persist_uses_async_queue_until_flushed(tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    store = RunSaveStore(
        plugins=_trinity_plugins(),
        save_manager=SaveManager(path=save_path),
    )
    _ = store.load_or_create()

    store.current.party_level = 9
    store.persist(force=False)

    payload_before_flush = json.loads(save_path.read_text(encoding="utf-8"))
    assert payload_before_flush["party_level"] in {1, 9}

    store.persist(force=True)
    payload_after_flush = json.loads(save_path.read_text(encoding="utf-8"))
    assert payload_after_flush["party_level"] == 9
    store.shutdown()
