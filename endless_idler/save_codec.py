"""Serialization helpers used by the save system.

These helpers normalize loosely typed payload data before `RunSave` objects are
constructed. `as_int_dict()` is shared by character stacks, death counters, and
the inventory item stack map.
"""

from __future__ import annotations

from typing import Any


def as_int(value: object, *, default: int) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return default
        try:
            return int(stripped)
        except ValueError:
            return default
    return default


def as_float(value: object, *, default: float) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return float(default)
        try:
            return float(stripped)
        except ValueError:
            return float(default)
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
        rebirth_power = as_float(raw_progress.get("rebirth_power", 1.0), default=1.0)
        prestige_count = as_int(raw_progress.get("prestige_count", 0), default=0)
        death_stacks = as_int(raw_progress.get("death_exp_debuff_stacks", 0), default=0)
        death_until = as_float(
            raw_progress.get("death_exp_debuff_until", 0.0), default=0.0
        )
        next_vitality_gain_level = as_int(
            raw_progress.get("next_vitality_gain_level", 0), default=0
        )
        next_mitigation_gain_level = as_int(
            raw_progress.get("next_mitigation_gain_level", 0), default=0
        )
        max_hp_level_bonus_version = as_int(
            raw_progress.get("max_hp_level_bonus_version", 0), default=0
        )
        shard_bar_ticks = as_int(raw_progress.get("shard_bar_ticks", 0), default=0)

        progress: dict[str, float | int] = {
            "level": max(1, level),
            "exp": float(max(0.0, exp)),
            "next_exp": float(max(1.0, next_exp)),
            "exp_multiplier": float(max(0.0, exp_multiplier)),
            "req_multiplier": float(max(0.0, req_multiplier)),
            "rebirths": max(0, rebirths),
            "rebirth_power": float(max(1.0, rebirth_power)),
            "prestige_count": max(0, prestige_count),
            "death_exp_debuff_stacks": max(0, death_stacks),
            "death_exp_debuff_until": float(max(0.0, death_until)),
            "next_vitality_gain_level": max(0, next_vitality_gain_level),
            "next_mitigation_gain_level": max(0, next_mitigation_gain_level),
            "max_hp_level_bonus_version": max(0, max_hp_level_bonus_version),
            "shard_bar_ticks": max(0, shard_bar_ticks),
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
        rebirth_power = as_float(raw.get("rebirth_power", 1.0), default=1.0)
        prestige_count = as_int(raw.get("prestige_count", 0), default=0)
        death_stacks = as_int(raw.get("death_exp_debuff_stacks", 0), default=0)
        death_until = as_float(raw.get("death_exp_debuff_until", 0.0), default=0.0)
        next_vitality_gain_level = as_int(
            raw.get("next_vitality_gain_level", 0), default=0
        )
        next_mitigation_gain_level = as_int(
            raw.get("next_mitigation_gain_level", 0), default=0
        )
        max_hp_level_bonus_version = as_int(
            raw.get("max_hp_level_bonus_version", 0), default=0
        )
        shard_bar_ticks = as_int(raw.get("shard_bar_ticks", 0), default=0)
        normalized[char_id] = {
            "level": max(1, level),
            "exp": float(max(0.0, exp)),
            "next_exp": float(max(1.0, next_exp)),
            "exp_multiplier": float(max(0.0, exp_multiplier)),
            "req_multiplier": float(max(0.0, req_multiplier)),
            "rebirths": max(0, rebirths),
            "rebirth_power": float(max(1.0, rebirth_power)),
            "prestige_count": max(0, prestige_count),
            "death_exp_debuff_stacks": max(0, death_stacks),
            "death_exp_debuff_until": float(max(0.0, death_until)),
            "next_vitality_gain_level": max(0, next_vitality_gain_level),
            "next_mitigation_gain_level": max(0, next_mitigation_gain_level),
            "max_hp_level_bonus_version": max(0, max_hp_level_bonus_version),
            "shard_bar_ticks": max(0, shard_bar_ticks),
        }
    return normalized


def _default_blessings() -> dict[str, dict[str, Any]]:
    """Generate default blessings from plugin discovery."""
    from endless_idler.blessings.registry import discover_blessing_plugins

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
                blessing_defaults[field_name] = (
                    plugin.is_unlocked if field_name == "unlocked" else False
                )

        defaults[plugin.blessing_id] = blessing_defaults

    return defaults


def as_blessings_dict(value: object) -> dict[str, dict[str, Any]]:
    """Validate and normalize canonical blessings data using plugin schemas."""
    from endless_idler.blessings.registry import discover_blessing_plugins

    if not isinstance(value, dict):
        raise ValueError("Blessings payload must be a dictionary.")
    if not value:
        return _default_blessings()

    result: dict[str, dict[str, Any]] = {}
    persistent_plugins = [
        plugin for plugin in discover_blessing_plugins() if plugin.is_persistent
    ]
    plugin_by_id = {plugin.blessing_id: plugin for plugin in persistent_plugins}
    unknown_ids = sorted(
        blessing_id
        for blessing_id in value
        if isinstance(blessing_id, str) and blessing_id not in plugin_by_id
    )
    if unknown_ids:
        raise ValueError(f"Unknown blessing ids in payload: {unknown_ids}")

    for plugin in persistent_plugins:
        if plugin.blessing_id not in value:
            raise ValueError(
                f"Missing blessing payload for persistent blessing '{plugin.blessing_id}'."
            )
        raw_blessing = value.get(plugin.blessing_id)
        if not isinstance(raw_blessing, dict):
            raise ValueError(
                f"Blessing '{plugin.blessing_id}' payload must be a dictionary."
            )

        normalized: dict[str, Any] = {}
        expected_fields = set(plugin.save_schema)
        actual_fields = {key for key in raw_blessing if isinstance(key, str)}
        extra_fields = sorted(actual_fields - expected_fields)
        missing_fields = sorted(expected_fields - actual_fields)
        if extra_fields or missing_fields:
            raise ValueError(
                f"Blessing '{plugin.blessing_id}' has non-canonical fields. "
                f"missing={missing_fields}, extra={extra_fields}"
            )
        for field_name, field_type in plugin.save_schema.items():
            raw_value = raw_blessing[field_name]

            if field_type is int:
                if isinstance(raw_value, bool) or not isinstance(raw_value, int):
                    raise ValueError(
                        f"Blessing '{plugin.blessing_id}.{field_name}' must be int."
                    )
                if raw_value < 0:
                    raise ValueError(
                        f"Blessing '{plugin.blessing_id}.{field_name}' must be >= 0."
                    )
                normalized[field_name] = raw_value
            elif field_type is float:
                if isinstance(raw_value, bool) or not isinstance(raw_value, int | float):
                    raise ValueError(
                        f"Blessing '{plugin.blessing_id}.{field_name}' must be float."
                    )
                if float(raw_value) < 0.0:
                    raise ValueError(
                        f"Blessing '{plugin.blessing_id}.{field_name}' must be >= 0.0."
                    )
                normalized[field_name] = float(raw_value)
            elif field_type is bool:
                if not isinstance(raw_value, bool):
                    raise ValueError(
                        f"Blessing '{plugin.blessing_id}.{field_name}' must be bool."
                    )
                normalized[field_name] = raw_value

        result[plugin.blessing_id] = normalized

    return result


def normalized_blessings(
    value: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Normalize and validate blessings data using plugin schemas.

    Ensures all persistent blessings exist with proper types.
    """
    from endless_idler.blessings.registry import discover_blessing_plugins

    defaults = _default_blessings()
    result: dict[str, dict[str, Any]] = {}

    for plugin in discover_blessing_plugins():
        if not plugin.is_persistent:
            continue

        raw = value.get(plugin.blessing_id, {})
        if not isinstance(raw, dict):
            result[plugin.blessing_id] = defaults.get(plugin.blessing_id, {}).copy()
            continue

        normalized: dict[str, Any] = {}
        for field_name, field_type in plugin.save_schema.items():
            raw_value = raw.get(field_name)

            if field_type is int:
                normalized[field_name] = max(0, as_int(raw_value, default=0))
            elif field_type is float:
                normalized[field_name] = max(0.0, as_float(raw_value, default=0.0))
            elif field_type is bool:
                if field_name == "unlocked":
                    normalized[field_name] = (
                        bool(raw_value) if raw_value is not None else plugin.is_unlocked
                    )
                else:
                    normalized[field_name] = (
                        bool(raw_value) if raw_value is not None else False
                    )

        result[plugin.blessing_id] = normalized

    return result


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
