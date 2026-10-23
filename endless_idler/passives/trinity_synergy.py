from __future__ import annotations

from typing import Any

from endless_idler.passives._trinity import get_character_passive_modifier
from endless_idler.passives._trinity import get_trinity_mitigation_fraction
from endless_idler.passives._trinity import is_trinity_active
from endless_idler.passives._trinity import sync_stack_ttls
from endless_idler.passives._trinity import update_stack_runtime
from endless_idler.passives.plugin import PassivePlugin
from endless_idler.passives.runtime import PassiveTickContext


def _build_runtime_state(saved_state: dict[str, Any]) -> dict[str, Any]:
    stack_ttls = saved_state.get("stack_ttls", [])
    stack_count = len(stack_ttls) if isinstance(stack_ttls, list) else 0
    return {
        "active": False,
        "stack_count": stack_count,
        "progress_ticks": int(saved_state.get("stack_progress_ticks", 0) or 0),
        "progress": 0.0,
        "countdown_ticks": 30,
        "min_ttl_ticks": min(stack_ttls) if stack_count else 0,
        "mitigation_fraction": 0.0,
        "mitigation_percent": 0.0,
        "owner_passive_modifier": 1.0,
    }


def _tick(context: PassiveTickContext) -> None:
    active = is_trinity_active(context.idle_state)
    stack_ttls, progress_ticks = sync_stack_ttls(
        canonical_state=context.canonical_state,
        runtime_state=context.runtime_state,
        ttl_field="stack_ttls",
        progress_field="stack_progress_ticks",
        active=active,
        tick_count=context.tick_count,
        delta_seconds=context.delta_seconds,
    )

    mitigation_fraction = get_trinity_mitigation_fraction(context.idle_state)
    owner_passive_modifier = get_character_passive_modifier(
        context.idle_state,
        "persona_light_and_dark",
    )
    update_stack_runtime(
        context.runtime_state,
        active=active,
        ttls=stack_ttls if active else [],
        progress_ticks=progress_ticks if active else 0,
    )
    context.runtime_state["mitigation_fraction"] = mitigation_fraction
    context.runtime_state["mitigation_percent"] = mitigation_fraction * 100.0
    context.runtime_state["owner_passive_modifier"] = owner_passive_modifier


passive = PassivePlugin(
    passive_id="trinity_synergy",
    display_name="Trinity Synergy",
    description="Coordinates Trinity's deployed-only idle stack engine and shared mitigation state.",
    save_schema={
        "stack_ttls": list[int],
        "stack_progress_ticks": int,
    },
    tick_order=-100,
    build_runtime_state=_build_runtime_state,
    tick=_tick,
)
