from __future__ import annotations

from typing import Any
from typing import cast

from endless_idler.save import RunSave


def apply_idle_runtime_snapshot_to_save(
    *,
    save: RunSave,
    snapshot: dict[str, object],
) -> None:
    progress = _copy_nested_dict(snapshot.get("progress"))
    if progress is not None:
        save.character_progress = progress
    stats = _copy_nested_dict(snapshot.get("character_stats"))
    if stats is not None:
        save.character_stats = stats
    initial_stats = _copy_nested_dict(snapshot.get("initial_stats"))
    if initial_stats is not None:
        save.character_initial_stats = initial_stats
    blessings = _copy_nested_dict(snapshot.get("blessings"))
    if blessings is not None:
        save.blessings = blessings
    passives = _copy_nested_dict(snapshot.get("passives"))
    if passives is not None:
        save.passives = passives
    save.idle_exp_bonus_seconds = _coerce_float(
        snapshot.get("exp_bonus_seconds", 0.0),
        0.0,
    )
    save.idle_exp_penalty_seconds = _coerce_float(
        snapshot.get("exp_penalty_seconds", 0.0),
        0.0,
    )
    save.idle_shared_exp_percentage = max(
        1,
        min(95, _coerce_int(snapshot.get("shared_exp_percentage", 1), 1)),
    )
    save.idle_risk_reward_level = max(
        0,
        min(150, _coerce_int(snapshot.get("risk_reward_level", 0), 0)),
    )
    inventory = _copy_inventory(snapshot.get("inventory"))
    if inventory is not None:
        save.inventory.clear()
        save.inventory.update(inventory)


def _copy_nested_dict(raw: object) -> dict[str, dict[str, Any]] | None:
    if not isinstance(raw, dict):
        return None
    raw_dict = cast(dict[object, object], raw)
    return {
        str(item_id): dict(cast(dict[str, Any], data))
        for item_id, data in raw_dict.items()
        if isinstance(item_id, str) and isinstance(data, dict)
    }


def _copy_inventory(raw: object) -> dict[str, int] | None:
    if not isinstance(raw, dict):
        return None
    raw_dict = cast(dict[object, object], raw)
    return {
        str(item_id): _coerce_inventory_count(count)
        for item_id, count in raw_dict.items()
        if isinstance(item_id, str)
    }


def _coerce_inventory_count(value: object) -> int:
    if isinstance(value, bool):
        return max(0, int(value))
    if isinstance(value, int | float | str):
        try:
            return max(0, int(value))
        except ValueError:
            return 0
    return 0


def _coerce_float(value: object, default: float) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, int | float):
        return max(0.0, float(value))
    if isinstance(value, str):
        try:
            return max(0.0, float(value))
        except ValueError:
            return default
    return default


def _coerce_int(value: object, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default
