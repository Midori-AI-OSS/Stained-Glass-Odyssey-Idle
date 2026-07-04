from __future__ import annotations

from typing import Any

from endless_idler.passives._trinity import LADY_LIGHT_SOURCE_SHARE
from endless_idler.passives._trinity import LADY_LIGHT_STACK_BONUS_PER_STACK
from endless_idler.passives._trinity import add_exp_multiplier_bonus
from endless_idler.passives._trinity import apply_log_soft_cap
from endless_idler.passives._trinity import get_character_passive_modifier
from endless_idler.passives._trinity import get_effective_exp_multiplier
from endless_idler.passives._trinity import get_trinity_stack_count
from endless_idler.passives._trinity import is_trinity_active
from endless_idler.passives.plugin import PassivePlugin
from endless_idler.passives.runtime import PassiveTickContext


def _build_runtime_state(_saved_state: dict[str, Any]) -> dict[str, Any]:
    return {
        "active": False,
        "source_dark_exp_multiplier": 0.0,
        "source_persona_exp_multiplier": 0.0,
        "base_transfer": 0.0,
        "stack_bonus_fraction": 0.0,
        "exp_multiplier_bonus": 0.0,
        "owner_passive_modifier": 1.0,
        "trinity_stack_count": 0,
    }


def _tick(context: PassiveTickContext) -> None:
    active = is_trinity_active(context.idle_state)
    owner_passive_modifier = get_character_passive_modifier(
        context.idle_state,
        "lady_light",
    )
    if not active:
        context.runtime_state["active"] = False
        context.runtime_state["source_dark_exp_multiplier"] = 0.0
        context.runtime_state["source_persona_exp_multiplier"] = 0.0
        context.runtime_state["base_transfer"] = 0.0
        context.runtime_state["stack_bonus_fraction"] = 0.0
        context.runtime_state["exp_multiplier_bonus"] = 0.0
        context.runtime_state["owner_passive_modifier"] = owner_passive_modifier
        context.runtime_state["trinity_stack_count"] = 0
        return

    dark_exp_multiplier = get_effective_exp_multiplier(
        context.idle_state,
        "lady_darkness",
    )
    persona_exp_multiplier = get_effective_exp_multiplier(
        context.idle_state,
        "persona_light_and_dark",
    )
    trinity_stack_count = get_trinity_stack_count(context.idle_state)
    base_transfer = (
        dark_exp_multiplier * LADY_LIGHT_SOURCE_SHARE
        + persona_exp_multiplier * LADY_LIGHT_SOURCE_SHARE
    )
    stack_bonus_fraction = apply_log_soft_cap(
        trinity_stack_count * LADY_LIGHT_STACK_BONUS_PER_STACK * owner_passive_modifier,
    )
    exp_multiplier_bonus = (
        base_transfer * owner_passive_modifier * (1.0 + stack_bonus_fraction)
    )
    add_exp_multiplier_bonus(
        context.idle_state,
        char_id="lady_light",
        bonus=exp_multiplier_bonus,
    )

    context.runtime_state["active"] = True
    context.runtime_state["source_dark_exp_multiplier"] = dark_exp_multiplier
    context.runtime_state["source_persona_exp_multiplier"] = persona_exp_multiplier
    context.runtime_state["base_transfer"] = base_transfer
    context.runtime_state["stack_bonus_fraction"] = stack_bonus_fraction
    context.runtime_state["exp_multiplier_bonus"] = exp_multiplier_bonus
    context.runtime_state["owner_passive_modifier"] = owner_passive_modifier
    context.runtime_state["trinity_stack_count"] = trinity_stack_count


passive = PassivePlugin(
    passive_id="lady_light_radiant_aegis",
    display_name="Lady Light Radiant Aegis",
    description="Transfers Trinity-linked EXP multiplier power into Lady Light while the trio remains deployed.",
    tick_order=0,
    build_runtime_state=_build_runtime_state,
    tick=_tick,
)
