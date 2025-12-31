from __future__ import annotations

import os
import json
import math

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from PySide6.QtCore import QStandardPaths


SAVE_VERSION = 3
DEFAULT_RUN_TOKENS = 20
DEFAULT_CHARACTER_COST = 1
DEFAULT_PARTY_LEVEL = 1
DEFAULT_PARTY_LEVEL_UP_COST = 4
ONSITE_SLOTS = 4
OFFSITE_SLOTS = 6
STANDBY_SLOTS = 10
BAR_SLOTS = 6


@dataclass(slots=True)
class RunSave:
    version: int = SAVE_VERSION
    tokens: int = DEFAULT_RUN_TOKENS
    party_level: int = DEFAULT_PARTY_LEVEL
    party_level_up_cost: int = DEFAULT_PARTY_LEVEL_UP_COST
    bar: list[str | None] = field(default_factory=lambda: [None] * BAR_SLOTS)
    onsite: list[str | None] = field(default_factory=lambda: [None] * ONSITE_SLOTS)
    offsite: list[str | None] = field(default_factory=lambda: [None] * OFFSITE_SLOTS)
    standby: list[str | None] = field(default_factory=lambda: [None] * STANDBY_SLOTS)
    stacks: dict[str, int] = field(default_factory=dict)
    character_progress: dict[str, dict[str, float | int]] = field(default_factory=dict)
    idle_exp_bonus_until: float = 0.0
    idle_exp_penalty_until: float = 0.0


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
            party_level=_as_int(data.get("party_level", DEFAULT_PARTY_LEVEL), default=DEFAULT_PARTY_LEVEL),
            party_level_up_cost=_as_int(
                data.get("party_level_up_cost", DEFAULT_PARTY_LEVEL_UP_COST),
                default=DEFAULT_PARTY_LEVEL_UP_COST,
            ),
            bar=_as_optional_str_list(data.get("bar", [])),
            onsite=_as_optional_str_list(data.get("onsite", [])),
            offsite=_as_optional_str_list(data.get("offsite", [])),
            standby=_as_optional_str_list(data.get("standby", [])),
            stacks=_as_int_dict(data.get("stacks", {})),
            character_progress=_as_character_progress_dict(data.get("character_progress", {})),
            idle_exp_bonus_until=_as_float(data.get("idle_exp_bonus_until", 0.0), default=0.0),
            idle_exp_penalty_until=_as_float(data.get("idle_exp_penalty_until", 0.0), default=0.0),
        )
        return _normalized_save(save)

    def save(self, save: RunSave) -> None:
        save = _normalized_save(save)
        payload = {
            "version": save.version,
            "tokens": save.tokens,
            "party_level": save.party_level,
            "party_level_up_cost": save.party_level_up_cost,
            "bar": save.bar,
            "onsite": save.onsite,
            "offsite": save.offsite,
            "standby": save.standby,
            "stacks": save.stacks,
            "character_progress": save.character_progress,
            "idle_exp_bonus_until": save.idle_exp_bonus_until,
            "idle_exp_penalty_until": save.idle_exp_penalty_until,
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
    party_level = max(1, int(save.party_level))
    party_level_up_cost = max(0, int(save.party_level_up_cost))

    onsite = list(save.onsite[:ONSITE_SLOTS])
    onsite.extend([None] * (ONSITE_SLOTS - len(onsite)))

    offsite = list(save.offsite[:OFFSITE_SLOTS])
    offsite.extend([None] * (OFFSITE_SLOTS - len(offsite)))

    raw_standby = [item if item else None for item in list(save.standby[:STANDBY_SLOTS])]
    raw_standby.extend([None] * (STANDBY_SLOTS - len(raw_standby)))
    standby: list[str | None] = [None] * STANDBY_SLOTS
    for item in raw_standby:
        if not item:
            continue
        try:
            target = next(
                index
                for index in range(1, max(1, STANDBY_SLOTS - 1))
                if standby[index] is None
            )
        except StopIteration:
            break
        standby[target] = item
    if standby:
        standby[0] = None
        standby[-1] = None

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

    party_chars = {item for item in (deduped_onsite + deduped_offsite + standby) if item}
    stacks: dict[str, int] = {}
    for key, value in save.stacks.items():
        if key in party_chars and isinstance(value, int) and value > 0:
            stacks[key] = value

    for char_id in party_chars:
        stacks[char_id] = max(1, int(stacks.get(char_id, 1)))

    return RunSave(
        version=SAVE_VERSION,
        tokens=tokens,
        party_level=party_level,
        party_level_up_cost=party_level_up_cost,
        bar=deduped_bar,
        onsite=deduped_onsite,
        offsite=deduped_offsite,
        standby=standby,
        stacks=stacks,
        character_progress=_normalized_character_progress(save.character_progress),
        idle_exp_bonus_until=float(max(0.0, save.idle_exp_bonus_until)),
        idle_exp_penalty_until=float(max(0.0, save.idle_exp_penalty_until)),
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


def _as_float(value: object, *, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return float(default)


def _as_character_progress_dict(value: object) -> dict[str, dict[str, float | int]]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, dict[str, float | int]] = {}
    for key, raw_progress in value.items():
        if not isinstance(key, str):
            continue
        char_id = key.strip()
        if not char_id:
            continue
        if not isinstance(raw_progress, dict):
            continue

        level = _as_int(raw_progress.get("level", 1), default=1)
        exp = _as_float(raw_progress.get("exp", 0.0), default=0.0)
        next_exp = _as_float(raw_progress.get("next_exp", 30.0), default=30.0)

        progress: dict[str, float | int] = {
            "level": max(1, level),
            "exp": float(max(0.0, exp)),
            "next_exp": float(max(1.0, next_exp)),
        }
        result[char_id] = progress
    return result


def _normalized_character_progress(
    value: dict[str, dict[str, float | int]],
) -> dict[str, dict[str, float | int]]:
    normalized: dict[str, dict[str, float | int]] = {}
    for key, raw in value.items():
        if not isinstance(key, str):
            continue
        char_id = key.strip()
        if not char_id:
            continue
        if not isinstance(raw, dict):
            continue

        level = _as_int(raw.get("level", 1), default=1)
        exp = _as_float(raw.get("exp", 0.0), default=0.0)
        next_exp = _as_float(raw.get("next_exp", 30.0), default=30.0)
        normalized[char_id] = {
            "level": max(1, level),
            "exp": float(max(0.0, exp)),
            "next_exp": float(max(1.0, next_exp)),
        }
    return normalized


def next_party_level_up_cost(*, new_level: int, previous_cost: int) -> int:
    previous_cost = max(0, int(previous_cost))
    new_level = max(1, int(new_level))
    if new_level >= 10:
        return max(1, int(math.ceil(previous_cost * 1.05)))
    return max(1, previous_cost * 4 + 2)
