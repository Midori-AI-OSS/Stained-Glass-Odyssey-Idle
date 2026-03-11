from __future__ import annotations

import logging
import random

from collections.abc import Callable
from copy import deepcopy
from dataclasses import fields
from datetime import datetime
from datetime import timezone
from pathlib import Path
from shutil import copy2

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.save import RunSave
from endless_idler.save import SaveManager
from endless_idler.save import new_run_save
from endless_idler.save import sanitize_save_characters
from endless_idler.save_bootstrap import bootstrap_party
from endless_idler.save_bootstrap import should_bootstrap_party
from endless_idler.save_queue import AsyncSaveQueue

logger = logging.getLogger(__name__)


class RunSaveStore:
    def __init__(
        self,
        *,
        plugins: list[CharacterPlugin],
        save_manager: SaveManager | None = None,
        rng: random.Random | None = None,
        persist_interval_seconds: float = 0.0,
        time_fn: Callable[[], float] | None = None,
    ) -> None:
        del persist_interval_seconds
        del time_fn
        self._plugins = list(plugins)
        self._allowed_char_ids = {
            plugin.char_id
            for plugin in self._plugins
            if isinstance(getattr(plugin, "char_id", None), str)
        }
        self._save_manager = save_manager or SaveManager()
        self._rng = rng or random.Random()
        self._current: RunSave | None = None
        self._save_queue = AsyncSaveQueue()

    @property
    def path(self) -> Path:
        return self._save_manager.path

    @property
    def current(self) -> RunSave:
        if self._current is None:
            return self.load_or_create()
        return self._current

    def load_or_create(self) -> RunSave:
        try:
            return self._load_or_create_once()
        except Exception as exc:
            logger.exception(
                "Startup save load/create failed; attempting crash backup recovery.",
            )
            self._recover_startup_save_after_failure(cause=exc)
            return self.current

    def persist(self, *, force: bool = False) -> None:
        current = self.current
        snapshot = self._normalized_copy(current)

        def _write_snapshot() -> None:
            self._save_manager.save(snapshot)

        self._save_queue.enqueue(_write_snapshot)
        if force:
            self._save_queue.flush()
            self._copy_save(source=snapshot, target=current)

    def backup_current(self) -> Path:
        self.persist(force=True)
        source = self.path
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        backup_path = self._backup_path_for(timestamp)
        copy2(source, backup_path)
        return backup_path

    def shutdown(self) -> None:
        self.persist(force=True)
        self._save_queue.shutdown()

    def delete_active_save(self) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            return

    def _normalized_copy(self, save: RunSave) -> RunSave:
        return sanitize_save_characters(
            save=deepcopy(save),
            allowed_char_ids=self._allowed_char_ids,
        )

    def _backup_path_for(self, timestamp: str) -> Path:
        suffix = self.path.suffix or ".json"
        stem = self.path.name[: -len(suffix)] if self.path.suffix else self.path.name
        index = 0
        while True:
            suffix_text = f".{index}" if index else ""
            candidate = self.path.with_name(
                f"{stem}.{timestamp}.backup{suffix_text}{suffix}"
            )
            if not candidate.exists():
                return candidate
            index += 1

    def _crash_backup_path_for(self, timestamp: str) -> Path:
        suffix = self.path.suffix or ".json"
        stem = self.path.name[: -len(suffix)] if self.path.suffix else self.path.name
        index = 0
        while True:
            suffix_text = f".{index}" if index else ""
            candidate = self.path.with_name(
                f"{stem}.{timestamp}.crash.backup{suffix_text}{suffix}"
            )
            if not candidate.exists():
                return candidate
            index += 1

    def _load_or_create_once(self) -> RunSave:
        loaded = self._save_manager.load()
        save = self._new_startup_save(loaded=loaded)
        self._set_current(save=save)
        self.persist(force=True)
        return self.current

    def _new_startup_save(self, *, loaded: RunSave | None) -> RunSave:
        is_new_save = loaded is None
        save = loaded or new_run_save()
        save = sanitize_save_characters(
            save=save, allowed_char_ids=self._allowed_char_ids
        )
        if is_new_save and should_bootstrap_party(save):
            bootstrap_party(save=save, plugins=self._plugins, rng=self._rng)
        return save

    def _set_current(self, *, save: RunSave) -> None:
        if self._current is None:
            self._current = save
            return
        self._copy_save(source=save, target=self._current)

    def _recover_startup_save_after_failure(self, *, cause: Exception) -> None:
        backup_path = self._backup_startup_save_or_raise(cause=cause)
        if backup_path is not None:
            logger.warning(
                "Created startup crash backup at %s before resetting save.",
                backup_path,
            )
        else:
            logger.warning(
                "Startup recovery: no existing save file found; creating fresh save.",
            )

        fresh = self._new_startup_save(loaded=None)
        self._set_current(save=fresh)
        self.persist(force=True)
        logger.warning("Startup save recovery completed with fresh canonical save.")

    def _backup_startup_save_or_raise(self, *, cause: Exception) -> Path | None:
        if not self.path.exists():
            return None

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        backup_path = self._crash_backup_path_for(timestamp)
        try:
            copy2(self.path, backup_path)
        except OSError as backup_error:
            logger.exception(
                "Startup recovery failed: unable to backup %s to %s.",
                self.path,
                backup_path,
            )
            raise RuntimeError(
                "Startup save recovery aborted because backup failed; "
                "the active save was left untouched."
            ) from backup_error
        logger.error("Recovered from startup save error: %s", cause)
        return backup_path

    @staticmethod
    def _copy_save(*, source: RunSave, target: RunSave) -> None:
        for field in fields(RunSave):
            setattr(target, field.name, deepcopy(getattr(source, field.name)))
