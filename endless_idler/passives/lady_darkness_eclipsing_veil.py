from __future__ import annotations

from typing import Any

from endless_idler.passives._trinity import LADY_DARKNESS_BLEED_RATE_PER_STACK
from endless_idler.passives._trinity import LADY_DARKNESS_EXP_BONUS_PER_HP_LOST_FRACTION
from endless_idler.passives._trinity import add_exp_multiplier_bonus
from endless_idler.passives._trinity import apply_bleed_damage
from endless_idler.passives._trinity import apply_log_soft_cap
from endless_idler.passives._trinity import get_character_data
from endless_idler.passives._trinity import get_character_passive_modifier
from endless_idler.passives._trinity import get_deployed_character_ids
from endless_idler.passives._trinity import get_trinity_mitigation_fraction
from endless_idler.passives._trinity import is_trinity_active
from endless_idler.passives._trinity import sync_stack_ttls
from endless_idler.passives._trinity import update_stack_runtime
from endless_idler.passives.plugin import PassivePlugin
from endless_idler.passives.runtime import PassiveTickContext


def _build_runtime_state(saved_state: dict[str, Any]) -> dict[str, Any]:
    stack_ttls = saved_state.get("bleed_stack_ttls", [])
    stack_count = len(stack_ttls) if isinstance(stack_ttls, list) else 0
    return {
        "active": False,
        "stack_count": stack_count,
        "progress_ticks": int(saved_state.get("bleed_progress_ticks", 0) or 0),
        "progress": 0.0,
        "countdown_ticks": 30,
        "min_ttl_ticks": min(stack_ttls) if stack_count else 0,
        "bleed_rate_fraction": 0.0,
        "hp_loss_fraction": 0.0,
        "exp_multiplier_bonus": 0.0,
        "bonus_tick": -1,
        "owner_passive_modifier": 1.0,
        "trinity_mitigation_fraction": 0.0,
    }


def _tick(context: PassiveTickContext) -> None:
    active = is_trinity_active(context.idle_state)
    stack_ttls, progress_ticks = sync_stack_ttls(
        canonical_state=context.canonical_state,
        runtime_state=context.runtime_state,
        ttl_field="bleed_stack_ttls",
        progress_field="bleed_progress_ticks",
        active=active,
        tick_count=context.tick_count,
        delta_seconds=context.delta_seconds,
    )

    owner_passive_modifier = get_character_passive_modifier(
        context.idle_state,
        "lady_darkness",
    )
    trinity_mitigation_fraction = get_trinity_mitigation_fraction(context.idle_state)

    hp_loss_fraction = 0.0
    exp_multiplier_bonus = 0.0
    if active and context.delta_seconds > 0.0:
        bleed_rate_fraction = (
            len(stack_ttls)
            * LADY_DARKNESS_BLEED_RATE_PER_STACK
            * owner_passive_modifier
            * max(0.0, 1.0 - trinity_mitigation_fraction)
        )
        for target_char_id in get_deployed_character_ids(context.idle_state):
            if target_char_id == "lady_darkness":
                continue
            target = get_character_data(context.idle_state, target_char_id)
            try:
                target_max_hp = max(1.0, float(target.get("max_hp", 1.0)))
            except (TypeError, ValueError):
                target_max_hp = 1.0
            raw_damage = target_max_hp * bleed_rate_fraction
            applied_damage = apply_bleed_damage(
                context.idle_state,
                target_char_id=target_char_id,
                raw_damage=raw_damage,
            )
            hp_loss_fraction += applied_damage / target_max_hp

        exp_multiplier_bonus = apply_log_soft_cap(
            hp_loss_fraction
            * LADY_DARKNESS_EXP_BONUS_PER_HP_LOST_FRACTION
            * owner_passive_modifier,
        )
        context.runtime_state["bonus_tick"] = context.tick_count
        context.runtime_state["exp_multiplier_bonus"] = exp_multiplier_bonus
        context.runtime_state["hp_loss_fraction"] = hp_loss_fraction
    elif not active:
        context.runtime_state["bonus_tick"] = -1
        context.runtime_state["exp_multiplier_bonus"] = 0.0
        context.runtime_state["hp_loss_fraction"] = 0.0

    update_stack_runtime(
        context.runtime_state,
        active=active,
        ttls=stack_ttls if active else [],
        progress_ticks=progress_ticks if active else 0,
    )
    context.runtime_state["bleed_rate_fraction"] = (
        len(stack_ttls)
        * LADY_DARKNESS_BLEED_RATE_PER_STACK
        * owner_passive_modifier
        * max(0.0, 1.0 - trinity_mitigation_fraction)
        if active
        else 0.0
    )
    context.runtime_state["owner_passive_modifier"] = owner_passive_modifier
    context.runtime_state["trinity_mitigation_fraction"] = trinity_mitigation_fraction

    bonus_tick = int(context.runtime_state.get("bonus_tick", -1) or -1)
    if active and bonus_tick == context.tick_count:
        add_exp_multiplier_bonus(
            context.idle_state,
            char_id="lady_darkness",
            bonus=float(
                max(0.0, context.runtime_state.get("exp_multiplier_bonus", 0.0))
            ),
        )


passive = PassivePlugin(
    passive_id="lady_darkness_eclipsing_veil",
    display_name="Lady Darkness Eclipsing Veil",
    description="Builds Trinity's Darkness-side bleed pool and turns real bleed damage into a temporary EXP multiplier bonus.",
    save_schema={
        "bleed_stack_ttls": list[int],
        "bleed_progress_ticks": int,
    },
    tick_order=-50,
    build_runtime_state=_build_runtime_state,
    tick=_tick,
)
