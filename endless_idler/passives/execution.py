"""Passive ability execution utilities.

This module provides helper functions for triggering and executing
passive abilities during combat.
"""

from typing import Any

from endless_idler.combat.stats import Stats
from endless_idler.passives.triggers import PassiveTrigger
from endless_idler.passives.triggers import TriggerContext


def trigger_passives_for_characters(
    *,
    characters: list[Stats],
    trigger: PassiveTrigger,
    all_allies: list[Stats],
    onsite_allies: list[Stats],
    offsite_allies: list[Stats],
    enemies: list[Stats],
    extra: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Trigger passives for multiple characters.

    Args:
        characters: Characters whose passives to check
        trigger: The trigger point (TURN_START, PRE_DAMAGE, etc.)
        all_allies: All ally Stats objects
        onsite_allies: Allies on the battlefield
        offsite_allies: Allies off the battlefield
        enemies: Enemy Stats objects
        extra: Additional context data specific to trigger

    Returns:
        List of results from executed passives
    """
    results: list[dict[str, Any]] = []
    extra = extra or {}

    for character in characters:
        if not hasattr(character, "_passive_instances"):
            continue

        for passive in character._passive_instances:
            if not hasattr(passive, "triggers") or trigger not in passive.triggers:
                continue

            context = TriggerContext(
                trigger=trigger,
                owner_stats=character,
                all_allies=all_allies,
                onsite_allies=onsite_allies,
                offsite_allies=offsite_allies,
                enemies=enemies,
                extra=dict(extra),
            )

            try:
                if passive.can_trigger(context):
                    result = passive.execute(context)
                    if result:
                        result["passive_id"] = getattr(passive, "id", "unknown")
                        result["passive_name"] = getattr(
                            passive, "display_name", "Unknown"
                        )
                        result["owner_id"] = character.character_id
                        results.append(result)
            except Exception:
                # Silently skip failed passives to avoid crashing combat
                pass

    return results


def trigger_turn_start_passives(
    *,
    all_allies: list[Stats],
    onsite_allies: list[Stats],
    offsite_allies: list[Stats],
    enemies: list[Stats],
) -> list[dict[str, Any]]:
    """Trigger TURN_START passives for all allies.

    Args:
        all_allies: All ally Stats objects
        onsite_allies: Allies on the battlefield
        offsite_allies: Allies off the battlefield
        enemies: Enemy Stats objects

    Returns:
        List of results from executed passives
    """
    return trigger_passives_for_characters(
        characters=all_allies,
        trigger=PassiveTrigger.TURN_START,
        all_allies=all_allies,
        onsite_allies=onsite_allies,
        offsite_allies=offsite_allies,
        enemies=enemies,
    )


def apply_pre_damage_passives(
    *,
    attacker: Stats,
    target: Stats,
    all_allies: list[Stats],
    onsite_allies: list[Stats],
    offsite_allies: list[Stats],
    enemies: list[Stats],
) -> tuple[float, float]:
    """Apply PRE_DAMAGE passives to modify damage calculation.

    Args:
        attacker: The attacking character
        target: The target character
        all_allies: All ally Stats objects
        onsite_allies: Allies on the battlefield
        offsite_allies: Allies off the battlefield
        enemies: Enemy Stats objects

    Returns:
        Tuple of (damage_multiplier, defense_ignore_percent)
    """
    damage_multiplier = 1.0
    defense_ignore = 0.0

    results = trigger_passives_for_characters(
        characters=[attacker],
        trigger=PassiveTrigger.PRE_DAMAGE,
        all_allies=all_allies,
        onsite_allies=onsite_allies,
        offsite_allies=offsite_allies,
        enemies=enemies,
        extra={"attacker": attacker, "target": target},
    )

    for result in results:
        if "damage_multiplier" in result:
            damage_multiplier *= float(result["damage_multiplier"])
        if "defense_ignore" in result:
            defense_ignore += float(result["defense_ignore"])

    # Cap defense ignore at 100%
    defense_ignore = min(1.0, defense_ignore)

    return damage_multiplier, defense_ignore


def apply_target_selection_passives(
    *,
    attacker: Stats,
    original_target: Stats,
    available_targets: list[Stats],
    all_allies: list[Stats],
    onsite_allies: list[Stats],
    offsite_allies: list[Stats],
    enemies: list[Stats],
) -> Stats:
    """Apply TARGET_SELECTION passives to potentially redirect attacks.

    Args:
        attacker: The attacking character
        original_target: The initially selected target
        available_targets: All available targets
        all_allies: All ally Stats objects
        onsite_allies: Allies on the battlefield
        offsite_allies: Allies off the battlefield
        enemies: Enemy Stats objects

    Returns:
        The final target (may be redirected)
    """
    # Check all allies for target redirection passives
    results = trigger_passives_for_characters(
        characters=all_allies,
        trigger=PassiveTrigger.TARGET_SELECTION,
        all_allies=all_allies,
        onsite_allies=onsite_allies,
        offsite_allies=offsite_allies,
        enemies=enemies,
        extra={
            "attacker": attacker,
            "original_target": original_target,
            "available_targets": available_targets,
        },
    )

    # Check if any passive redirected the target
    for result in results:
        if "new_target" in result and isinstance(result["new_target"], Stats):
            # Verify the new target is in the available targets
            if result["new_target"] in available_targets:
                return result["new_target"]

    return original_target
