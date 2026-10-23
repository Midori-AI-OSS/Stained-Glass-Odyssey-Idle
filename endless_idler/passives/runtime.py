"""Passive runtime helpers for idle execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from endless_idler.passives.plugin import PassivePlugin
from endless_idler.passives.registry import get_passive_by_id
from endless_idler.save_codec import normalized_passives


@dataclass(slots=True)
class PassiveTickContext:
    passive_id: str
    plugin: PassivePlugin
    canonical_state: dict[str, Any]
    runtime_state: dict[str, Any]
    idle_state: object
    delta_seconds: float
    tick_count: int
    elapsed_seconds: float


def _default_canonical_state(plugin: PassivePlugin) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for field_name, field_type in plugin.save_schema.items():
        if field_type is int:
            defaults[field_name] = 0
        elif field_type is float:
            defaults[field_name] = 0.0
        elif field_type is bool:
            defaults[field_name] = False
        elif field_type == list[int]:
            defaults[field_name] = []
    return defaults


def _is_stateful_passive(
    *,
    plugin: PassivePlugin,
    canonical_state: dict[str, Any],
    runtime_state: dict[str, Any] | None,
) -> bool:
    defaults = _default_canonical_state(plugin)
    if canonical_state != defaults:
        return True
    return bool(runtime_state)


def _ordered_passive_ids_to_tick(
    *,
    active_passive_ids: list[str],
    canonical_passives: dict[str, dict[str, Any]],
    runtime_passives: dict[str, dict[str, Any]],
) -> list[str]:
    order: list[str] = []
    seen: set[str] = set()

    for passive_id in active_passive_ids:
        if passive_id in seen:
            continue
        seen.add(passive_id)
        order.append(passive_id)

    for passive_id, canonical_state in canonical_passives.items():
        if passive_id in seen:
            continue
        plugin = get_passive_by_id(passive_id)
        if plugin is None:
            continue
        runtime_state = runtime_passives.get(passive_id)
        if not _is_stateful_passive(
            plugin=plugin,
            canonical_state=canonical_state
            if isinstance(canonical_state, dict)
            else {},
            runtime_state=runtime_state if isinstance(runtime_state, dict) else None,
        ):
            continue
        seen.add(passive_id)
        order.append(passive_id)

    indexed_order = {passive_id: index for index, passive_id in enumerate(order)}
    return sorted(
        order,
        key=lambda passive_id: (
            int(getattr(get_passive_by_id(passive_id), "tick_order", 0) or 0),
            indexed_order[passive_id],
        ),
    )


def resolve_active_passive_ids(
    *,
    char_ids: list[str],
    offsite_ids: list[str],
    standby_ids: list[str],
    plugins_by_id: dict[str, object],
) -> list[str]:
    active_ids: list[str] = []
    seen: set[str] = set()
    for char_id in list(dict.fromkeys([*char_ids, *offsite_ids, *standby_ids])):
        plugin = plugins_by_id.get(char_id)
        raw_passives = getattr(plugin, "passives", [])
        if not isinstance(raw_passives, list):
            continue
        for raw_passive_id in raw_passives:
            passive_id = str(raw_passive_id or "").strip()
            if not passive_id or passive_id in seen:
                continue
            if get_passive_by_id(passive_id) is None:
                continue
            seen.add(passive_id)
            active_ids.append(passive_id)
    return active_ids


def initialize_passive_state(
    *,
    passives_data: dict[str, dict[str, Any]] | None,
    active_passive_ids: list[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    canonical = normalized_passives(dict(passives_data or {}))
    runtime: dict[str, dict[str, Any]] = {}
    for passive_id in active_passive_ids:
        plugin = get_passive_by_id(passive_id)
        if plugin is None:
            continue
        state = plugin.build_runtime_state(dict(canonical.get(passive_id, {})))
        runtime[passive_id] = dict(state) if isinstance(state, dict) else {}
    return canonical, runtime


def tick_active_passives(
    *,
    active_passive_ids: list[str],
    canonical_passives: dict[str, dict[str, Any]],
    runtime_passives: dict[str, dict[str, Any]],
    idle_state: object,
    delta_seconds: float,
    tick_count: int,
    elapsed_seconds: float,
) -> None:
    passive_ids_to_tick = _ordered_passive_ids_to_tick(
        active_passive_ids=active_passive_ids,
        canonical_passives=canonical_passives,
        runtime_passives=runtime_passives,
    )

    for passive_id in passive_ids_to_tick:
        plugin = get_passive_by_id(passive_id)
        if plugin is None:
            continue
        canonical_state = canonical_passives.setdefault(passive_id, {})
        runtime_state = runtime_passives.get(passive_id)
        if not isinstance(runtime_state, dict):
            runtime_state = plugin.build_runtime_state(dict(canonical_state))
            runtime_state = (
                dict(runtime_state) if isinstance(runtime_state, dict) else {}
            )
            runtime_passives[passive_id] = runtime_state
        plugin.tick(
            PassiveTickContext(
                passive_id=passive_id,
                plugin=plugin,
                canonical_state=canonical_state,
                runtime_state=runtime_state,
                idle_state=idle_state,
                delta_seconds=float(max(0.0, delta_seconds)),
                tick_count=max(0, int(tick_count)),
                elapsed_seconds=float(max(0.0, elapsed_seconds)),
            )
        )


def export_passives(
    *,
    canonical_passives: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return normalized_passives(dict(canonical_passives or {}))


def export_active_passive_runtime(
    *,
    active_passive_ids: list[str],
    runtime_passives: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    for passive_id in active_passive_ids:
        raw = runtime_passives.get(passive_id, {})
        payload[passive_id] = dict(raw) if isinstance(raw, dict) else {}
    return payload
