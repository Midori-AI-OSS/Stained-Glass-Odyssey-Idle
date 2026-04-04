"""Shared helpers for Trinity idle passives."""

from __future__ import annotations

import math

from typing import Any


TRINITY_MEMBER_IDS = frozenset(
    {
        "lady_darkness",
        "lady_light",
        "persona_light_and_dark",
    }
)
TRINITY_SYNERGY_PASSIVE_ID = "trinity_synergy"
LADY_LIGHT_PASSIVE_ID = "lady_light_radiant_aegis"
LADY_DARKNESS_PASSIVE_ID = "lady_darkness_eclipsing_veil"

TRINITY_STACK_INTERVAL_TICKS = 30
TRINITY_STACK_TTL_TICKS = 450
TRINITY_SOFT_CAP_THRESHOLD = 0.5
TRINITY_MITIGATION_PER_STACK = 0.0001

LADY_LIGHT_SOURCE_SHARE = 0.5
LADY_LIGHT_STACK_BONUS_PER_STACK = 0.0005

LADY_DARKNESS_BLEED_RATE_PER_STACK = 0.0055
LADY_DARKNESS_HP_FLOOR_FRACTION = 0.3
LADY_DARKNESS_DEFENSE_DIVISOR = 5.0
LADY_DARKNESS_EXP_BONUS_PER_HP_LOST_FRACTION = 5.0


def apply_log_soft_cap(
    value: float,
    *,
    threshold: float = TRINITY_SOFT_CAP_THRESHOLD,
) -> float:
    raw_value = max(0.0, float(value))
    soft_cap_threshold = max(1e-9, float(threshold))
    if raw_value <= soft_cap_threshold:
        return raw_value

    step_size = soft_cap_threshold * 0.05
    excess = raw_value - soft_cap_threshold
    soft_excess = step_size * math.log2(1.0 + (excess / step_size))
    return soft_cap_threshold + soft_excess


def sanitized_counter(value: object) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def sanitized_ttls(value: object) -> list[int]:
    if not isinstance(value, list):
        return []

    ttls: list[int] = []
    for item in value:
        if isinstance(item, bool):
            continue
        if not isinstance(item, int):
            continue
        if item <= 0:
            continue
        ttls.append(item)
    return ttls


def get_character_data(idle_state: object, char_id: str) -> dict[str, Any]:
    getter = getattr(idle_state, "get_char_data", None)
    if not callable(getter):
        return {}
    data = getter(char_id)
    return dict(data) if isinstance(data, dict) else {}


def get_character_passive_modifier(idle_state: object, char_id: str) -> float:
    data = get_character_data(idle_state, char_id)
    try:
        return max(0.0, float(data.get("passive_modifier", 1.0)))
    except (TypeError, ValueError):
        return 1.0


def get_deployed_character_ids(idle_state: object) -> list[str]:
    getter = getattr(idle_state, "get_deployed_character_ids", None)
    if not callable(getter):
        return []
    raw = getter()
    if not isinstance(raw, list):
        return []
    return [str(char_id) for char_id in raw if str(char_id).strip()]


def is_trinity_active(idle_state: object) -> bool:
    deployed = set(get_deployed_character_ids(idle_state))
    return TRINITY_MEMBER_IDS.issubset(deployed)


def get_passive_canonical_state(idle_state: object, passive_id: str) -> dict[str, Any]:
    getter = getattr(idle_state, "get_passive_canonical_state", None)
    if not callable(getter):
        return {}
    state = getter(passive_id)
    return dict(state) if isinstance(state, dict) else {}


def get_effective_exp_multiplier(idle_state: object, char_id: str) -> float:
    getter = getattr(idle_state, "get_effective_exp_multiplier", None)
    if not callable(getter):
        data = get_character_data(idle_state, char_id)
        try:
            return max(0.0, float(data.get("exp_multiplier", 1.0)))
        except (TypeError, ValueError):
            return 1.0
    try:
        return max(0.0, float(getter(char_id)))
    except (TypeError, ValueError):
        return 0.0


def add_exp_multiplier_bonus(idle_state: object, *, char_id: str, bonus: float) -> None:
    adder = getattr(idle_state, "add_passive_exp_multiplier_bonus", None)
    if callable(adder):
        adder(char_id=char_id, bonus=bonus)


def apply_bleed_damage(
    idle_state: object,
    *,
    target_char_id: str,
    raw_damage: float,
) -> float:
    applier = getattr(idle_state, "apply_passive_hp_loss", None)
    if not callable(applier):
        return 0.0
    try:
        return max(
            0.0,
            float(
                applier(
                    target_char_id=target_char_id,
                    raw_damage=raw_damage,
                    hp_floor_fraction=LADY_DARKNESS_HP_FLOOR_FRACTION,
                    defense_divisor=LADY_DARKNESS_DEFENSE_DIVISOR,
                )
            ),
        )
    except (TypeError, ValueError):
        return 0.0


def sync_stack_ttls(
    *,
    canonical_state: dict[str, Any],
    runtime_state: dict[str, Any],
    ttl_field: str,
    progress_field: str,
    active: bool,
    tick_count: int,
    delta_seconds: float,
) -> tuple[list[int], int]:
    ttls = sanitized_ttls(canonical_state.get(ttl_field, []))
    progress_ticks = sanitized_counter(canonical_state.get(progress_field, 0))

    if not active:
        ttls = []
        progress_ticks = 0
    elif (
        delta_seconds > 0.0
        and sanitized_counter(runtime_state.get("last_processed_tick", -1))
        != tick_count
    ):
        next_ttls: list[int] = []
        for ttl in ttls:
            next_ttl = ttl - 1
            if next_ttl > 0:
                next_ttls.append(next_ttl)
        ttls = next_ttls
        progress_ticks += 1
        while progress_ticks >= TRINITY_STACK_INTERVAL_TICKS:
            ttls.append(TRINITY_STACK_TTL_TICKS)
            progress_ticks -= TRINITY_STACK_INTERVAL_TICKS
        runtime_state["last_processed_tick"] = tick_count

    canonical_state[ttl_field] = list(ttls)
    canonical_state[progress_field] = progress_ticks
    return ttls, progress_ticks


def update_stack_runtime(
    runtime_state: dict[str, Any],
    *,
    active: bool,
    ttls: list[int],
    progress_ticks: int,
) -> None:
    clamped_progress = max(0, min(TRINITY_STACK_INTERVAL_TICKS - 1, progress_ticks))
    countdown_ticks = TRINITY_STACK_INTERVAL_TICKS - clamped_progress
    if countdown_ticks <= 0:
        countdown_ticks = TRINITY_STACK_INTERVAL_TICKS

    runtime_state["active"] = bool(active)
    runtime_state["stack_count"] = len(ttls)
    runtime_state["progress_ticks"] = clamped_progress
    runtime_state["progress"] = (
        float(clamped_progress) / float(TRINITY_STACK_INTERVAL_TICKS) if active else 0.0
    )
    runtime_state["countdown_ticks"] = (
        countdown_ticks if active else TRINITY_STACK_INTERVAL_TICKS
    )
    runtime_state["min_ttl_ticks"] = min(ttls) if ttls else 0


def get_trinity_stack_count(idle_state: object) -> int:
    state = get_passive_canonical_state(idle_state, TRINITY_SYNERGY_PASSIVE_ID)
    return len(sanitized_ttls(state.get("stack_ttls", [])))


def get_trinity_mitigation_fraction(idle_state: object) -> float:
    if not is_trinity_active(idle_state):
        return 0.0
    stack_count = get_trinity_stack_count(idle_state)
    passive_modifier = get_character_passive_modifier(
        idle_state, "persona_light_and_dark"
    )
    raw_value = stack_count * TRINITY_MITIGATION_PER_STACK * passive_modifier
    return apply_log_soft_cap(raw_value)
