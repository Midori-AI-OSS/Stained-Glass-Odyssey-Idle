from __future__ import annotations

import json
import math
import os
import random

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from typing import cast

from PySide6.QtCore import QStandardPaths

from endless_idler.blessings.registry import discover_blessing_plugins
from endless_idler.inventory import get_all_items
from endless_idler.inventory import get_item_ids
from endless_idler.save_codec import as_blessings_dict
from endless_idler.save_codec import as_character_progress_dict
from endless_idler.save_codec import as_character_stats_dict
from endless_idler.save_codec import as_float
from endless_idler.save_codec import as_int
from endless_idler.save_codec import as_int_dict
from endless_idler.save_codec import as_optional_str_list
from endless_idler.save_codec import normalized_blessings
from endless_idler.save_codec import normalized_character_progress
from endless_idler.save_codec import normalized_character_stats


SAVE_VERSION = 11
DEFAULT_RUN_TOKENS = 20
DEFAULT_CHARACTER_COST = 1
DEFAULT_SHOP_REROLL_COST = 2
DEFAULT_PARTY_LEVEL = 1
DEFAULT_PARTY_LEVEL_UP_COST = 4
DEFAULT_FIGHT_NUMBER = 1
DEFAULT_PARTY_HP_MAX = 100
DEFAULT_PARTY_HP_CURRENT = 100
DEFAULT_PARTY_HP_LAST_IDLE_HEAL_AT = 0.0
DEFAULT_LAYOUT_TICK_COOLDOWN_SECONDS = 0.0
DEFAULT_LAYOUT_OWNED_ORDERING = "save_order"
ONSITE_SLOTS = 4
OFFSITE_SLOTS = 6
STANDBY_SLOTS = 10
BAR_SLOTS = 6
_LAYOUT_OWNED_ORDERING_VALUES = frozenset(
    {
        "save_order",
        "rarity_desc",
        "alphabetical",
        "recent",
    }
)


def _get_default_blessings() -> dict[str, dict[str, Any]]:
    """Generate default blessing data from registered plugins."""
    defaults: dict[str, dict[str, Any]] = {}
    for plugin in discover_blessing_plugins():
        if not plugin.is_persistent:
            continue

        blessing_defaults: dict[str, Any] = {}
        for field_name, field_type in plugin.save_schema.items():
            if field_type is int:
                blessing_defaults[field_name] = 0
            elif field_type is float:
                blessing_defaults[field_name] = 0.0
            elif field_type is bool:
                if field_name == "unlocked":
                    blessing_defaults[field_name] = plugin.is_unlocked
                else:
                    blessing_defaults[field_name] = False

        defaults[plugin.blessing_id] = blessing_defaults

    return defaults


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
    inventory: dict[str, int] = field(default_factory=dict)
    character_progress: dict[str, dict[str, float | int]] = field(default_factory=dict)
    character_stats: dict[str, dict[str, float]] = field(default_factory=dict)
    character_initial_stats: dict[str, dict[str, float]] = field(default_factory=dict)
    character_deaths: dict[str, int] = field(default_factory=dict)
    blessings: dict[str, dict[str, Any]] = field(default_factory=_get_default_blessings)
    idle_exp_bonus_seconds: float = 0.0
    idle_exp_penalty_seconds: float = 0.0
    idle_shared_exp_percentage: int = 1
    idle_risk_reward_level: int = 0
    winstreak: int = 0
    idle_exp_mult: float = 1.0
    battle_start_time: float = 0.0
    layout_tick_cooldown_seconds: float = DEFAULT_LAYOUT_TICK_COOLDOWN_SECONDS
    layout_owned_ordering: str = DEFAULT_LAYOUT_OWNED_ORDERING


class SaveManager:
    def __init__(self, path: Path | None = None) -> None:
        self._path: Path
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
            loaded_data = cast(object, json.loads(raw))
        except json.JSONDecodeError:
            return None

        if not isinstance(loaded_data, dict):
            return None
        data = cast(dict[str, object], loaded_data)

        save = RunSave(
            version=as_int(data.get("version", SAVE_VERSION), default=SAVE_VERSION),
            tokens=DEFAULT_RUN_TOKENS,
            party_level=as_int(
                data.get("party_level", DEFAULT_PARTY_LEVEL),
                default=DEFAULT_PARTY_LEVEL,
            ),
            party_level_up_cost=as_int(
                data.get("party_level_up_cost", DEFAULT_PARTY_LEVEL_UP_COST),
                default=DEFAULT_PARTY_LEVEL_UP_COST,
            ),
            fight_number=DEFAULT_FIGHT_NUMBER,
            party_hp_max=as_int(
                data.get("party_hp_max", DEFAULT_PARTY_HP_MAX),
                default=DEFAULT_PARTY_HP_MAX,
            ),
            party_hp_current=as_int(
                data.get("party_hp_current", DEFAULT_PARTY_HP_CURRENT),
                default=DEFAULT_PARTY_HP_CURRENT,
            ),
            party_hp_last_idle_heal_at=as_float(
                data.get(
                    "party_hp_last_idle_heal_at", DEFAULT_PARTY_HP_LAST_IDLE_HEAL_AT
                ),
                default=DEFAULT_PARTY_HP_LAST_IDLE_HEAL_AT,
            ),
            onsite=as_optional_str_list(data.get("onsite", [])),
            offsite=as_optional_str_list(data.get("offsite", [])),
            stacks=as_int_dict(data.get("stacks", {})),
            inventory=as_int_dict(data.get("inventory", {})),
            character_progress=as_character_progress_dict(
                data.get("character_progress", {})
            ),
            character_stats=as_character_stats_dict(data.get("character_stats", {})),
            character_initial_stats=as_character_stats_dict(
                data.get("character_initial_stats", {})
            ),
            character_deaths=as_int_dict(data.get("character_deaths", {})),
            blessings=as_blessings_dict(data.get("blessings", {})),
            idle_exp_bonus_seconds=as_float(
                data.get("idle_exp_bonus_seconds", 0.0), default=0.0
            ),
            idle_exp_penalty_seconds=as_float(
                data.get("idle_exp_penalty_seconds", 0.0), default=0.0
            ),
            idle_shared_exp_percentage=as_int(
                data.get("idle_shared_exp_percentage", 1), default=1
            ),
            idle_risk_reward_level=as_int(
                data.get("idle_risk_reward_level", 0), default=0
            ),
            idle_exp_mult=as_float(data.get("idle_exp_mult", 1.0), default=1.0),
            layout_tick_cooldown_seconds=as_float(
                data.get(
                    "layout_tick_cooldown_seconds", DEFAULT_LAYOUT_TICK_COOLDOWN_SECONDS
                ),
                default=DEFAULT_LAYOUT_TICK_COOLDOWN_SECONDS,
            ),
            layout_owned_ordering=_normalize_layout_owned_ordering(
                data.get("layout_owned_ordering", DEFAULT_LAYOUT_OWNED_ORDERING)
            ),
        )
        return _normalized_save(save)

    def save(self, save: RunSave) -> None:
        save = _normalized_save(save)
        payload = {
            "version": save.version,
            "party_level": save.party_level,
            "party_level_up_cost": save.party_level_up_cost,
            "party_hp_max": save.party_hp_max,
            "party_hp_current": save.party_hp_current,
            "party_hp_last_idle_heal_at": save.party_hp_last_idle_heal_at,
            "onsite": save.onsite,
            "offsite": save.offsite,
            "stacks": save.stacks,
            "inventory": save.inventory,
            "character_progress": save.character_progress,
            "character_stats": save.character_stats,
            "character_initial_stats": save.character_initial_stats,
            "character_deaths": save.character_deaths,
            "blessings": save.blessings,
            "idle_exp_bonus_seconds": save.idle_exp_bonus_seconds,
            "idle_exp_penalty_seconds": save.idle_exp_penalty_seconds,
            "idle_shared_exp_percentage": save.idle_shared_exp_percentage,
            "idle_risk_reward_level": save.idle_risk_reward_level,
            "idle_exp_mult": save.idle_exp_mult,
            "layout_tick_cooldown_seconds": save.layout_tick_cooldown_seconds,
            "layout_owned_ordering": save.layout_owned_ordering,
        }

        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        _ = tmp_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )
        _ = tmp_path.replace(self._path)


def _default_save_path() -> Path:
    override = os.environ.get("ENDLESS_IDLER_SAVE_PATH", "").strip()
    if override:
        return Path(override).expanduser()

    home = Path.home()
    if home.exists():
        return home / ".midoriai" / "stainedlgassodysseyidle" / "idlesave.json"

    base = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation
    )
    if not base:
        base = str(Path.cwd())
    return Path(base) / "stainedlgassodysseyidle" / "idlesave.json"


def _normalize_layout_owned_ordering(value: object) -> str:
    normalized = str(value).strip().lower()
    if normalized not in _LAYOUT_OWNED_ORDERING_VALUES:
        return DEFAULT_LAYOUT_OWNED_ORDERING
    return normalized


def _normalized_save(save: RunSave) -> RunSave:
    tokens = max(0, int(save.tokens))
    party_level = max(1, int(save.party_level))
    party_level_up_cost = max(0, int(save.party_level_up_cost))
    fight_number = max(1, int(getattr(save, "fight_number", DEFAULT_FIGHT_NUMBER)))

    party_hp_max = max(1, int(getattr(save, "party_hp_max", DEFAULT_PARTY_HP_MAX)))
    party_hp_current = max(0, int(getattr(save, "party_hp_current", party_hp_max)))
    party_hp_current = min(party_hp_current, party_hp_max)
    party_hp_last_idle_heal_at = float(
        max(0.0, float(getattr(save, "party_hp_last_idle_heal_at", 0.0)))
    )

    onsite = list(save.onsite[:ONSITE_SLOTS])
    onsite.extend([None] * (ONSITE_SLOTS - len(onsite)))

    offsite = list(save.offsite[:OFFSITE_SLOTS])
    offsite.extend([None] * (OFFSITE_SLOTS - len(offsite)))

    raw_standby = [
        item if item else None for item in list(save.standby[:STANDBY_SLOTS])
    ]
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

    party_chars = {
        item for item in (deduped_onsite + deduped_offsite + standby) if item
    }
    stacks: dict[str, int] = {}
    for key, value in save.stacks.items():
        if key in party_chars and value > 0:
            stacks[key] = value

    for char_id in party_chars:
        stacks[char_id] = max(1, int(stacks.get(char_id, 1)))

    item_catalog = get_all_items()
    inventory: dict[str, int] = {}
    for key, value in save.inventory.items():
        item_id = key.strip()
        item_class = item_catalog.get(item_id)
        if not item_id or item_class is None:
            continue
        count = int(value)
        if count <= 0:
            continue
        inventory[item_id] = count

    deaths: dict[str, int] = {}
    for key, value in save.character_deaths.items():
        char_id = key.strip()
        if not char_id:
            continue
        count = int(value)
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
        inventory=inventory,
        character_progress=normalized_character_progress(save.character_progress),
        character_stats=normalized_character_stats(save.character_stats),
        character_initial_stats=normalized_character_stats(
            save.character_initial_stats
        ),
        character_deaths=deaths,
        blessings=normalized_blessings(getattr(save, "blessings", {})),
        idle_exp_bonus_seconds=float(
            max(0.0, getattr(save, "idle_exp_bonus_seconds", 0.0))
        ),
        idle_exp_penalty_seconds=float(
            max(0.0, getattr(save, "idle_exp_penalty_seconds", 0.0))
        ),
        idle_shared_exp_percentage=max(
            1, min(95, int(getattr(save, "idle_shared_exp_percentage", 1)))
        ),
        idle_risk_reward_level=max(
            0, min(150, int(getattr(save, "idle_risk_reward_level", 0)))
        ),
        winstreak=max(0, int(getattr(save, "winstreak", 0))),
        idle_exp_mult=max(1.0, float(getattr(save, "idle_exp_mult", 1.0))),
        battle_start_time=float(max(0.0, getattr(save, "battle_start_time", 0.0))),
        layout_tick_cooldown_seconds=float(
            max(
                0.0,
                float(
                    getattr(
                        save,
                        "layout_tick_cooldown_seconds",
                        DEFAULT_LAYOUT_TICK_COOLDOWN_SECONDS,
                    )
                ),
            )
        ),
        layout_owned_ordering=_normalize_layout_owned_ordering(
            getattr(save, "layout_owned_ordering", DEFAULT_LAYOUT_OWNED_ORDERING)
        ),
    )


def next_party_level_up_cost(*, new_level: int, previous_cost: int) -> int:
    previous_cost = max(0, int(previous_cost))
    new_level = max(1, int(new_level))
    if new_level >= 10:
        return max(1, int(math.ceil(previous_cost * 1.05)))
    return max(1, previous_cost * 4 + 2)


def new_run_save(
    *,
    available_char_ids: list[str] | None = None,
    rng: random.Random | None = None,
) -> RunSave:
    del available_char_ids
    del rng
    return RunSave(tokens=DEFAULT_RUN_TOKENS)


def sanitize_save_characters(*, save: RunSave, allowed_char_ids: set[str]) -> RunSave:
    allowed = {
        str(char_id).strip() for char_id in allowed_char_ids if str(char_id).strip()
    }
    if not allowed:
        return _normalized_save(save)

    def sanitize_slots(values: list[str | None]) -> list[str | None]:
        updated: list[str | None] = []
        for item in values:
            if not item:
                updated.append(None)
                continue
            cleaned = str(item).strip()
            if not cleaned or cleaned not in allowed:
                updated.append(None)
                continue
            updated.append(cleaned)
        return updated

    save.bar = sanitize_slots(list(save.bar))

    save.onsite = sanitize_slots(list(save.onsite))

    save.offsite = sanitize_slots(list(save.offsite))

    save.standby = sanitize_slots(list(save.standby))

    save.stacks = {key: value for key, value in save.stacks.items() if key in allowed}
    save.inventory = {
        key: value
        for key, value in save.inventory.items()
        if key in get_item_ids() and value > 0
    }
    save.character_progress = {
        key: value for key, value in save.character_progress.items() if key in allowed
    }
    save.character_stats = {
        key: value for key, value in save.character_stats.items() if key in allowed
    }
    save.character_initial_stats = {
        key: value
        for key, value in save.character_initial_stats.items()
        if key in allowed
    }
    save.character_deaths = {
        key: value for key, value in save.character_deaths.items() if key in allowed
    }

    return _normalized_save(save)


def reset_character_progress_for_new_run(
    progress_by_id: dict[str, dict[str, float | int]],
) -> dict[str, dict[str, float | int]]:
    reset: dict[str, dict[str, float | int]] = {}
    for char_id, raw in progress_by_id.items():
        try:
            exp_multiplier = max(0.0, float(raw.get("exp_multiplier", 1.0)))
        except (TypeError, ValueError):
            exp_multiplier = 1.0
        try:
            req_multiplier = max(0.0, float(raw.get("req_multiplier", 1.0)))
        except (TypeError, ValueError):
            req_multiplier = 1.0
        try:
            rebirths = max(0, int(raw.get("rebirths", 0)))
        except (TypeError, ValueError):
            rebirths = 0
        try:
            rebirth_power = max(1.0, float(raw.get("rebirth_power", 1.0)))
        except (TypeError, ValueError):
            rebirth_power = 1.0
        try:
            prestige_count = max(0, int(raw.get("prestige_count", 0)))
        except (TypeError, ValueError):
            prestige_count = 0

        reset[char_id] = {
            "level": 1,
            "exp": 0.0,
            "next_exp": 30.0,
            "exp_multiplier": exp_multiplier,
            "req_multiplier": req_multiplier,
            "rebirths": rebirths,
            "rebirth_power": rebirth_power,
            "prestige_count": prestige_count,
            "death_exp_debuff_stacks": 0,
            "death_exp_debuff_until": 0.0,
            "next_vitality_gain_level": 0,
            "next_mitigation_gain_level": 0,
            "max_hp_level_bonus_version": 0,
            "shard_bar_ticks": 0,
        }

    return reset
