from __future__ import annotations

import random

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


class RunSaveStore:
    def __init__(
        self,
        *,
        plugins: list[CharacterPlugin],
        save_manager: SaveManager | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self._plugins = list(plugins)
        self._allowed_char_ids = {
            plugin.char_id
            for plugin in self._plugins
            if isinstance(getattr(plugin, "char_id", None), str)
        }
        self._save_manager = save_manager or SaveManager()
        self._rng = rng or random.Random()
        self._current: RunSave | None = None

    @property
    def path(self) -> Path:
        return self._save_manager.path

    @property
    def current(self) -> RunSave:
        if self._current is None:
            return self.load_or_create()
        return self._current

    def load_or_create(self) -> RunSave:
        loaded = self._save_manager.load()
        is_new_save = loaded is None
        save = loaded or new_run_save()
        save = sanitize_save_characters(save=save, allowed_char_ids=self._allowed_char_ids)
        if is_new_save and should_bootstrap_party(save):
            bootstrap_party(save=save, plugins=self._plugins, rng=self._rng)

        if self._current is None:
            self._current = save
        else:
            self._copy_save(source=save, target=self._current)

        self.persist()
        return self.current

    def persist(self) -> None:
        current = self.current
        normalized = self._normalized_copy(current)
        self._copy_save(source=normalized, target=current)
        self._save_manager.save(current)

    def backup_current(self) -> Path:
        self.persist()
        source = self.path
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        backup_path = self._backup_path_for(timestamp)
        copy2(source, backup_path)
        return backup_path

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
            candidate = self.path.with_name(f"{stem}.{timestamp}.backup{suffix_text}{suffix}")
            if not candidate.exists():
                return candidate
            index += 1

    @staticmethod
    def _copy_save(*, source: RunSave, target: RunSave) -> None:
        for field in fields(RunSave):
            setattr(target, field.name, deepcopy(getattr(source, field.name)))
