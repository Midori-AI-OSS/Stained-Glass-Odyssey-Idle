from __future__ import annotations

import json
import random

from pathlib import Path

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.run_save_store import RunSaveStore
from endless_idler.save import SaveManager


def _plugin(char_id: str, placement: str) -> CharacterPlugin:
    return CharacterPlugin(char_id=char_id, display_name=char_id.title(), placement=placement)


def test_run_save_store_load_or_create_bootstraps_new_save(tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    store = RunSaveStore(
        plugins=[
            _plugin("lady_darkness", "onsite"),
            _plugin("persona_light_and_dark", "both"),
        ],
        save_manager=SaveManager(path=save_path),
        rng=random.Random(7),
    )

    save = store.load_or_create()

    assigned = [item for item in [*save.onsite, *save.offsite] if item]
    assert len(assigned) == 1
    assert assigned[0] in {"lady_darkness", "persona_light_and_dark"}
    assert save_path.exists()


def test_run_save_store_backup_current_creates_collision_safe_files(tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    store = RunSaveStore(
        plugins=[_plugin("lady_darkness", "onsite")],
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


def test_run_save_store_delete_active_save_removes_file(tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    store = RunSaveStore(
        plugins=[_plugin("lady_darkness", "onsite")],
        save_manager=SaveManager(path=save_path),
    )
    store.load_or_create()

    assert save_path.exists()
    store.delete_active_save()
    assert not save_path.exists()
