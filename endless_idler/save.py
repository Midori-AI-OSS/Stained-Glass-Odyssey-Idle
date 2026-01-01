from __future__ import annotations

import json
import math
import os
import random
import time

from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from endless_idler.save_codec import as_character_progress_dict
from endless_idler.save_codec import as_character_stats_dict
from endless_idler.save_codec import as_float
from endless_idler.save_codec import as_int
from endless_idler.save_codec import as_int_dict
from endless_idler.save_codec import as_optional_str_list
from endless_idler.save_codec import normalized_character_progress
from endless_idler.save_codec import normalized_character_stats


SAVE_VERSION = 8
DEFAULT_RUN_TOKENS = 20
DEFAULT_CHARACTER_COST = 1
DEFAULT_SHOP_REROLL_COST = 2
DEFAULT_PARTY_LEVEL = 1
DEFAULT_PARTY_LEVEL_UP_COST = 4
DEFAULT_FIGHT_NUMBER = 1
DEFAULT_PARTY_HP_MAX = 100
DEFAULT_PARTY_HP_CURRENT = 100
DEFAULT_PARTY_HP_LAST_IDLE_HEAL_AT = 0.0
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
    fight_number: int = DEFAULT_FIGHT_NUMBER
    party_hp_max: int = DEFAULT_PARTY_HP_MAX
    party_hp_current: int = DEFAULT_PARTY_HP_CURRENT
    party_hp_last_idle_heal_at: float = DEFAULT_PARTY_HP_LAST_IDLE_HEAL_AT
    bar: list[str | None] = field(default_factory=lambda: [None] * BAR_SLOTS)
    onsite: list[str | None] = field(default_factory=lambda: [None] * ONSITE_SLOTS)
    offsite: list[str | None] = field(default_factory=lambda: [None] * OFFSITE_SLOTS)
    standby: list[str | None] = field(default_factory=lambda: [None] * STANDBY_SLOTS)
    stacks: dict[str, int] = field(default_factory=dict)
    character_progress: dict[str, dict[str, float | int]] = field(default_factory=dict)
    character_stats: dict[str, dict[str, float]] = field(default_factory=dict)
    character_initial_stats: dict[str, dict[str, float]] = field(default_factory=dict)
    character_deaths: dict[str, int] = field(default_factory=dict)
    idle_exp_bonus_seconds: float = 0.0
    idle_exp_penalty_seconds: float = 0.0


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

        bonus_seconds = as_float(data.get("idle_exp_bonus_seconds", 0.0), default=0.0)
        penalty_seconds = as_float(data.get("idle_exp_penalty_seconds", 0.0), default=0.0)
        if "idle_exp_bonus_seconds" not in data:
            legacy_bonus = as_float(data.get("idle_exp_bonus_until", 0.0), default=0.0)
            if legacy_bonus > 1_000_000_000:
                bonus_seconds = max(0.0, legacy_bonus - float(time.time()))
            else:
                bonus_seconds = max(0.0, legacy_bonus)
        if "idle_exp_penalty_seconds" not in data:
            legacy_penalty = as_float(data.get("idle_exp_penalty_until", 0.0), default=0.0)
            if legacy_penalty > 1_000_000_000:
                penalty_seconds = max(0.0, legacy_penalty - float(time.time()))
            else:
                penalty_seconds = max(0.0, legacy_penalty)

        save = RunSave(
            version=as_int(data.get("version", SAVE_VERSION), default=SAVE_VERSION),
            tokens=as_int(data.get("tokens", DEFAULT_RUN_TOKENS), default=DEFAULT_RUN_TOKENS),
            party_level=as_int(data.get("party_level", DEFAULT_PARTY_LEVEL), default=DEFAULT_PARTY_LEVEL),
            party_level_up_cost=as_int(
                data.get("party_level_up_cost", DEFAULT_PARTY_LEVEL_UP_COST),
                default=DEFAULT_PARTY_LEVEL_UP_COST,
            ),
            fight_number=as_int(data.get("fight_number", DEFAULT_FIGHT_NUMBER), default=DEFAULT_FIGHT_NUMBER),
            party_hp_max=as_int(data.get("party_hp_max", DEFAULT_PARTY_HP_MAX), default=DEFAULT_PARTY_HP_MAX),
            party_hp_current=as_int(
                data.get("party_hp_current", DEFAULT_PARTY_HP_CURRENT),
                default=DEFAULT_PARTY_HP_CURRENT,
            ),
            party_hp_last_idle_heal_at=as_float(
                data.get("party_hp_last_idle_heal_at", DEFAULT_PARTY_HP_LAST_IDLE_HEAL_AT),
                default=DEFAULT_PARTY_HP_LAST_IDLE_HEAL_AT,
            ),
            bar=as_optional_str_list(data.get("bar", [])),
            onsite=as_optional_str_list(data.get("onsite", [])),
            offsite=as_optional_str_list(data.get("offsite", [])),
            standby=as_optional_str_list(data.get("standby", [])),
            stacks=as_int_dict(data.get("stacks", {})),
            character_progress=as_character_progress_dict(data.get("character_progress", {})),
            character_stats=as_character_stats_dict(data.get("character_stats", {})),
            character_initial_stats=as_character_stats_dict(data.get("character_initial_stats", {})),
            character_deaths=as_int_dict(data.get("character_deaths", {})),
            idle_exp_bonus_seconds=bonus_seconds,
            idle_exp_penalty_seconds=penalty_seconds,
        )
        return _normalized_save(save)

    def save(self, save: RunSave) -> None:
        save = _normalized_save(save)
        payload = {
            "version": save.version,
            "tokens": save.tokens,
            "party_level": save.party_level,
            "party_level_up_cost": save.party_level_up_cost,
            "fight_number": save.fight_number,
            "party_hp_max": save.party_hp_max,
            "party_hp_current": save.party_hp_current,
            "party_hp_last_idle_heal_at": save.party_hp_last_idle_heal_at,
            "bar": save.bar,
            "onsite": save.onsite,
            "offsite": save.offsite,
            "standby": save.standby,
            "stacks": save.stacks,
            "character_progress": save.character_progress,
            "character_stats": save.character_stats,
            "character_initial_stats": save.character_initial_stats,
            "character_deaths": save.character_deaths,
            "idle_exp_bonus_seconds": save.idle_exp_bonus_seconds,
            "idle_exp_penalty_seconds": save.idle_exp_penalty_seconds,
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
    fight_number = max(1, int(getattr(save, "fight_number", DEFAULT_FIGHT_NUMBER)))

    party_hp_max = max(1, int(getattr(save, "party_hp_max", DEFAULT_PARTY_HP_MAX)))
    party_hp_current = max(0, int(getattr(save, "party_hp_current", party_hp_max)))
    party_hp_current = min(party_hp_current, party_hp_max)
    party_hp_last_idle_heal_at = float(max(0.0, float(getattr(save, "party_hp_last_idle_heal_at", 0.0))))

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

    deaths: dict[str, int] = {}
    raw_deaths = getattr(save, "character_deaths", {}) or {}
    if isinstance(raw_deaths, dict):
        for key, value in raw_deaths.items():
            if not isinstance(key, str):
                continue
            char_id = key.strip()
            if not char_id:
                continue
            try:
                count = int(value)
            except (TypeError, ValueError):
                continue
            if count <= 0:
                continue
            deaths[char_id] = count

    return RunSave(
        version=SAVE_VERSION,
        tokens=tokens,
        party_level=party_level,
        party_level_up_cost=party_level_up_cost,
        fight_number=fight_number,
        party_hp_max=party_hp_max,
        party_hp_current=party_hp_current,
        party_hp_last_idle_heal_at=party_hp_last_idle_heal_at,
        bar=deduped_bar,
        onsite=deduped_onsite,
        offsite=deduped_offsite,
        standby=standby,
        stacks=stacks,
        character_progress=normalized_character_progress(save.character_progress),
        character_stats=normalized_character_stats(save.character_stats),
        character_initial_stats=normalized_character_stats(save.character_initial_stats),
        character_deaths=deaths,
        idle_exp_bonus_seconds=float(max(0.0, getattr(save, "idle_exp_bonus_seconds", 0.0))),
        idle_exp_penalty_seconds=float(max(0.0, getattr(save, "idle_exp_penalty_seconds", 0.0))),
    )


def next_party_level_up_cost(*, new_level: int, previous_cost: int) -> int:
    previous_cost = max(0, int(previous_cost))
    new_level = max(1, int(new_level))
    if new_level >= 10:
        return max(1, int(math.ceil(previous_cost * 1.05)))
    return max(1, previous_cost * 4 + 2)


def new_run_save(*, available_char_ids: list[str], rng: random.Random) -> RunSave:
    bar: list[str | None] = [None] * BAR_SLOTS
    available_char_ids = [str(item) for item in available_char_ids if item]
    if available_char_ids:
        count = min(BAR_SLOTS, len(available_char_ids))
        chosen = [str(item) for item in rng.sample(available_char_ids, k=count)]
        bar[: len(chosen)] = chosen

    return RunSave(tokens=DEFAULT_RUN_TOKENS, bar=bar)
