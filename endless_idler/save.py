from __future__ import annotations

import json
import os

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from PySide6.QtCore import QStandardPaths


SAVE_VERSION = 1
DEFAULT_RUN_TOKENS = 20
DEFAULT_CHARACTER_COST = 1
ONSITE_SLOTS = 4
OFFSITE_SLOTS = 10
BAR_SLOTS = 6


@dataclass(slots=True)
class RunSave:
    version: int = SAVE_VERSION
    tokens: int = DEFAULT_RUN_TOKENS
    bar: list[str | None] = field(default_factory=lambda: [None] * BAR_SLOTS)
    onsite: list[str | None] = field(default_factory=lambda: [None] * ONSITE_SLOTS)
    offsite: list[str | None] = field(default_factory=lambda: [None] * OFFSITE_SLOTS)
    stacks: dict[str, int] = field(default_factory=dict)


class SaveManager:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _default_save_path()

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> RunSave | None:
        try:
            raw = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except OSError:
            return None

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        save = RunSave(
            version=_as_int(data.get("version", SAVE_VERSION), default=SAVE_VERSION),
            tokens=_as_int(data.get("tokens", DEFAULT_RUN_TOKENS), default=DEFAULT_RUN_TOKENS),
            bar=_as_optional_str_list(data.get("bar", [])),
            onsite=_as_optional_str_list(data.get("onsite", [])),
            offsite=_as_optional_str_list(data.get("offsite", [])),
            stacks=_as_int_dict(data.get("stacks", {})),
        )
        return _normalized_save(save)

    def save(self, save: RunSave) -> None:
        save = _normalized_save(save)
        payload = {
            "version": save.version,
            "tokens": save.tokens,
            "bar": save.bar,
            "onsite": save.onsite,
            "offsite": save.offsite,
            "stacks": save.stacks,
        }

        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp_path.replace(self._path)


def _default_save_path() -> Path:
    override = os.environ.get("ENDLESS_IDLER_SAVE_PATH", "").strip()
    if override:
        return Path(override).expanduser()

    home = Path.home()
    if home.exists():
        return home / ".midoriai" / "idlesave.json"

    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if not base:
        base = str(Path.cwd())
    return Path(base) / "idlesave.json"


def _normalized_save(save: RunSave) -> RunSave:
    tokens = max(0, int(save.tokens))

    onsite = list(save.onsite[:ONSITE_SLOTS])
    onsite.extend([None] * (ONSITE_SLOTS - len(onsite)))

    offsite = list(save.offsite[:OFFSITE_SLOTS])
    offsite.extend([None] * (OFFSITE_SLOTS - len(offsite)))

    bar = list(save.bar[:BAR_SLOTS])
    bar.extend([None] * (BAR_SLOTS - len(bar)))

    seen: set[str] = set()
    deduped_onsite: list[str | None] = []
    for item in onsite:
        if not item:
            deduped_onsite.append(None)
            continue
        if item in seen:
            deduped_onsite.append(None)
            continue
        seen.add(item)
        deduped_onsite.append(item)

    deduped_offsite: list[str | None] = []
    for item in offsite:
        if not item:
            deduped_offsite.append(None)
            continue
        if item in seen:
            deduped_offsite.append(None)
            continue
        seen.add(item)
        deduped_offsite.append(item)

    deduped_bar: list[str | None] = []
    for item in bar:
        deduped_bar.append(item if item else None)

    party_chars = {item for item in (deduped_onsite + deduped_offsite) if item}
    stacks: dict[str, int] = {}
    for key, value in save.stacks.items():
        if key in party_chars and isinstance(value, int) and value > 0:
            stacks[key] = value

    for char_id in party_chars:
        stacks[char_id] = max(1, int(stacks.get(char_id, 1)))

    return RunSave(
        version=SAVE_VERSION,
        tokens=tokens,
        bar=deduped_bar,
        onsite=deduped_onsite,
        offsite=deduped_offsite,
        stacks=stacks,
    )


def _as_int(value: object, *, default: int) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _as_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            stripped = item.strip()
            if stripped:
                result.append(stripped)
    return result


def _as_optional_str_list(value: object) -> list[str | None]:
    if not isinstance(value, list):
        return []
    result: list[str | None] = []
    for item in value:
        if item is None:
            result.append(None)
        elif isinstance(item, str):
            stripped = item.strip()
            result.append(stripped if stripped else None)
    return result


def _as_int_dict(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, int] = {}
    for key, raw in value.items():
        if not isinstance(key, str):
            continue
        stripped = key.strip()
        if not stripped:
            continue
        try:
            number = int(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        if number <= 0:
            continue
        result[stripped] = number
    return result
