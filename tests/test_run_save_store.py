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


def test_run_save_store_persist_debounces_routine_flushes(tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    now = 100.0

    def _time_fn() -> float:
        return now

    store = RunSaveStore(
        plugins=_trinity_plugins(),
        save_manager=SaveManager(path=save_path),
        persist_interval_seconds=15.0,
        time_fn=_time_fn,
    )
    _ = store.load_or_create()
    initial_mtime = save_path.stat().st_mtime_ns

    now = 105.0
    store.current.party_level = 2
    store.persist()
    assert save_path.stat().st_mtime_ns == initial_mtime

    now = 116.0
    store.persist()
    assert save_path.stat().st_mtime_ns != initial_mtime


def test_run_save_store_persist_skips_normalization_when_debounced(
    tmp_path: Path,
) -> None:
    save_path = tmp_path / "save.json"
    now = 300.0

    def _time_fn() -> float:
        return now

    store = RunSaveStore(
        plugins=_trinity_plugins(),
        save_manager=SaveManager(path=save_path),
        persist_interval_seconds=15.0,
        time_fn=_time_fn,
    )
    _ = store.load_or_create()

    calls = 0
    original_normalized_copy = store._normalized_copy

    def _counting_normalized_copy(save):  # type: ignore[no-untyped-def]
        nonlocal calls
        calls += 1
        return original_normalized_copy(save)

    store._normalized_copy = _counting_normalized_copy  # type: ignore[method-assign]

    now = 305.0
    store.current.party_level = 2
    store.persist()
    assert calls == 0

    now = 316.0
    store.persist()
    assert calls == 1


def test_run_save_store_persist_force_flushes_immediately(tmp_path: Path) -> None:
    save_path = tmp_path / "save.json"
    now = 200.0

    def _time_fn() -> float:
        return now

    store = RunSaveStore(
        plugins=_trinity_plugins(),
        save_manager=SaveManager(path=save_path),
        persist_interval_seconds=15.0,
        time_fn=_time_fn,
    )
    _ = store.load_or_create()

    now = 205.0
    store.current.party_level = 9
    store.persist(force=True)

    payload = json.loads(save_path.read_text(encoding="utf-8"))
    assert payload["party_level"] == 9
