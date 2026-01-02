from __future__ import annotations

import math

from endless_idler.ui.battle.sim import Combatant


MIN_REMAINING_HP_FRACTION: float = 0.20


def min_hp_for_max_hp(*, max_hp: int, min_remaining_fraction: float = MIN_REMAINING_HP_FRACTION) -> int:
    return max(1, int(math.ceil(max(0.0, float(min_remaining_fraction)) * max(1, int(max_hp)))))


def reduce_hp_percent_of_max(
    combatant: Combatant,
    *,
    percent: float,
    min_remaining_fraction: float = MIN_REMAINING_HP_FRACTION,
) -> int:
    max_hp = max(1, int(combatant.max_hp))
    current = max(0, int(combatant.stats.hp))
    min_hp = min_hp_for_max_hp(max_hp=max_hp, min_remaining_fraction=min_remaining_fraction)
    if current <= min_hp:
        return 0

    desired = int(math.ceil(max(0.0, float(percent)) * max_hp))
    removable = max(0, current - min_hp)
    removed = min(removable, max(0, desired))
    if removed <= 0:
        return 0

    combatant.stats.hp = current - removed
    return removed


def heal_amount(combatant: Combatant, *, amount: int) -> int:
    amount = max(0, int(amount))
    if amount <= 0:
        return 0

    max_hp = max(1, int(combatant.max_hp))
    current = max(0, int(combatant.stats.hp))
    if current >= max_hp:
        return 0

    healed = min(amount, max_hp - current)
    combatant.stats.hp = current + healed
    return healed


def apply_dark_sacrifice(
    *,
    onsite_allies: list[Combatant],
    offsite_allies: list[Combatant],
    onsite_percent: float = 0.05,
    offsite_percent: float = 0.15,
    min_remaining_fraction: float = MIN_REMAINING_HP_FRACTION,
) -> int:
    total_removed = 0
    for ally in onsite_allies:
        total_removed += reduce_hp_percent_of_max(
            ally,
            percent=onsite_percent,
            min_remaining_fraction=min_remaining_fraction,
        )
    for ally in offsite_allies:
        total_removed += reduce_hp_percent_of_max(
            ally,
            percent=offsite_percent,
            min_remaining_fraction=min_remaining_fraction,
        )
    return total_removed


def dark_damage_multiplier_from_removed_hp(removed_hp: int) -> float:
    return 1.0 + 0.0001 * max(0, int(removed_hp))


def apply_fire_self_bleed(
    *,
    combatant: Combatant,
    turns_taken: int,
    per_turn_fraction: float = 0.0005,
    cap_fraction: float = 0.50,
    min_remaining_fraction: float = MIN_REMAINING_HP_FRACTION,
) -> int:
    turns_taken = max(0, int(turns_taken))
    if turns_taken <= 0:
        return 0

    bleed_fraction = min(max(0.0, float(cap_fraction)), max(0.0, float(per_turn_fraction)) * turns_taken)
    return reduce_hp_percent_of_max(
        combatant,
        percent=bleed_fraction,
        min_remaining_fraction=min_remaining_fraction,
    )


def fire_damage_multiplier_from_removed_hp(removed_hp: int) -> float:
    return 1.0 + 0.05 * max(0, int(removed_hp))


def resolve_light_heal(
    *,
    attacker: Combatant,
    onsite_allies: list[Combatant],
    offsite_allies: list[Combatant],
) -> list[tuple[Combatant, int]]:
    base_power = max(1, int(round(float(attacker.stats.atk) * 0.05)))
    wounded_onsite = [ally for ally in onsite_allies if int(ally.stats.hp) < int(ally.max_hp)]
    wounded_offsite = [ally for ally in offsite_allies if int(ally.stats.hp) < int(ally.max_hp)]
    wounded = wounded_onsite + wounded_offsite
    if not wounded:
        return []

    if len(wounded) == 1:
        target = wounded[0]
        multiplier = 2 if target in wounded_offsite else 1
        healed = heal_amount(target, amount=base_power * multiplier)
        return [(target, healed)] if healed else []

    per_target = max(1, int(round(base_power / float(len(wounded)))))
    results: list[tuple[Combatant, int]] = []
    for target in wounded:
        multiplier = 2 if target in wounded_offsite else 1
        healed = heal_amount(target, amount=per_target * multiplier)
        if healed:
            results.append((target, healed))
    return results

