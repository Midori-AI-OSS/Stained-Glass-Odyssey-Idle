from __future__ import annotations

import json
import random

from pathlib import Path

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
    store.shutdown()


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
