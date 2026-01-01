from __future__ import annotations

def as_int(value: object, *, default: int) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def as_float(value: object, *, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return float(default)


def as_str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            stripped = item.strip()
            if stripped:
                result.append(stripped)
    return result


def as_optional_str_list(value: object) -> list[str | None]:
    if not isinstance(value, list):
        return []
    result: list[str | None] = []
    for item in value:
        if isinstance(item, str):
            stripped = item.strip()
            result.append(stripped if stripped else None)
        else:
            result.append(None)
    return result


def as_int_dict(value: object) -> dict[str, int]:
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


def as_character_progress_dict(value: object) -> dict[str, dict[str, float | int]]:
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

        level = as_int(raw_progress.get("level", 1), default=1)
        exp = as_float(raw_progress.get("exp", 0.0), default=0.0)
        next_exp = as_float(raw_progress.get("next_exp", 30.0), default=30.0)
        exp_multiplier = as_float(raw_progress.get("exp_multiplier", 1.0), default=1.0)
        req_multiplier = as_float(raw_progress.get("req_multiplier", 1.0), default=1.0)
        rebirths = as_int(raw_progress.get("rebirths", 0), default=0)
        death_stacks = as_int(raw_progress.get("death_exp_debuff_stacks", 0), default=0)
        death_until = as_float(raw_progress.get("death_exp_debuff_until", 0.0), default=0.0)
        next_vitality_gain_level = as_int(raw_progress.get("next_vitality_gain_level", 0), default=0)
        next_mitigation_gain_level = as_int(raw_progress.get("next_mitigation_gain_level", 0), default=0)

        progress: dict[str, float | int] = {
            "level": max(1, level),
            "exp": float(max(0.0, exp)),
            "next_exp": float(max(1.0, next_exp)),
            "exp_multiplier": float(max(0.0, exp_multiplier)),
            "req_multiplier": float(max(0.0, req_multiplier)),
            "rebirths": max(0, rebirths),
            "death_exp_debuff_stacks": max(0, death_stacks),
            "death_exp_debuff_until": float(max(0.0, death_until)),
            "next_vitality_gain_level": max(0, next_vitality_gain_level),
            "next_mitigation_gain_level": max(0, next_mitigation_gain_level),
        }
        result[char_id] = progress
    return result


def as_character_stats_dict(value: object) -> dict[str, dict[str, float]]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, dict[str, float]] = {}
    for key, raw_stats in value.items():
        if not isinstance(key, str):
            continue
        char_id = key.strip()
        if not char_id:
            continue
        if not isinstance(raw_stats, dict):
            continue
        stats: dict[str, float] = {}
        for stat_key, raw in raw_stats.items():
            if not isinstance(stat_key, str):
                continue
            stat_name = stat_key.strip()
            if not stat_name:
                continue
            try:
                stats[stat_name] = float(raw)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                continue
        result[char_id] = stats
    return result


def normalized_character_progress(
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

        level = as_int(raw.get("level", 1), default=1)
        exp = as_float(raw.get("exp", 0.0), default=0.0)
        next_exp = as_float(raw.get("next_exp", 30.0), default=30.0)
        exp_multiplier = as_float(raw.get("exp_multiplier", 1.0), default=1.0)
        req_multiplier = as_float(raw.get("req_multiplier", 1.0), default=1.0)
        rebirths = as_int(raw.get("rebirths", 0), default=0)
        death_stacks = as_int(raw.get("death_exp_debuff_stacks", 0), default=0)
        death_until = as_float(raw.get("death_exp_debuff_until", 0.0), default=0.0)
        next_vitality_gain_level = as_int(raw.get("next_vitality_gain_level", 0), default=0)
        next_mitigation_gain_level = as_int(raw.get("next_mitigation_gain_level", 0), default=0)
        normalized[char_id] = {
            "level": max(1, level),
            "exp": float(max(0.0, exp)),
            "next_exp": float(max(1.0, next_exp)),
            "exp_multiplier": float(max(0.0, exp_multiplier)),
            "req_multiplier": float(max(0.0, req_multiplier)),
            "rebirths": max(0, rebirths),
            "death_exp_debuff_stacks": max(0, death_stacks),
            "death_exp_debuff_until": float(max(0.0, death_until)),
            "next_vitality_gain_level": max(0, next_vitality_gain_level),
            "next_mitigation_gain_level": max(0, next_mitigation_gain_level),
        }
    return normalized


def normalized_character_stats(
    value: dict[str, dict[str, float]],
    *,
    party_chars: set[str] | None = None,
) -> dict[str, dict[str, float]]:
    normalized: dict[str, dict[str, float]] = {}
    for key, raw in value.items():
        if not isinstance(key, str):
            continue
        char_id = key.strip()
        if not char_id:
            continue
        if party_chars is not None and char_id not in party_chars:
            continue
        if not isinstance(raw, dict):
            continue
        stats: dict[str, float] = {}
        for stat_key, stat_value in raw.items():
            if not isinstance(stat_key, str):
                continue
            name = stat_key.strip()
            if not name:
                continue
            try:
                number = float(stat_value)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                continue
            stats[name] = number
        normalized[char_id] = stats
    return normalized
