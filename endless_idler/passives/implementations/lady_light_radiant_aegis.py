"""Lady Light's Radiant Aegis passive ability.

This passive provides healing to all party members when Lady Light is offsite.
"""

from typing import Any

from endless_idler.passives.base import Passive
from endless_idler.passives.registry import register_passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext


@register_passive
class LadyLightRadiantAegis(Passive):
    """When Lady Light is offsite, heal all party members each turn.

    Passive Effect:
    - Triggers at the start of each turn
    - Requires Lady Light to be offsite (not in active combat)
    - Heals all allies (onsite + offsite) for 50% of Lady Light's regain stat
    - Healing respects max HP limits
    """

    def __init__(self) -> None:
        """Initialize the Radiant Aegis passive."""
        super().__init__()
        self.id = "lady_light_radiant_aegis"
        self.display_name = "Radiant Aegis"
        self.description = (
            "When Lady Light is offsite, heal all party members (onsite + offsite) "
            "for 50% of her regain stat at the start of each turn."
        )
        self.triggers = [PassiveTrigger.TURN_START]
        self.heal_multiplier = 0.50

    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if Lady Light is offsite.

        Args:
            context: Trigger context with party composition

        Returns:
            True if Lady Light is offsite, False otherwise
        """
        # Check if owner (Lady Light) is in offsite list
        if context.owner_stats in context.offsite_allies:
            return True

        return False

    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Execute healing for all party members.

        Args:
            context: Trigger context with party and stats

        Returns:
            Dictionary containing:
                - healed: list of (character_id, heal_amount) tuples
                - total_healing: sum of all healing done
                - base_heal_amount: the base heal calculated
        """
        # Calculate heal amount based on Lady Light's regain
        base_heal = int(context.owner_stats.regain * self.heal_multiplier)

        healed_targets = []
        total_healing = 0

        # Heal all allies (onsite + offsite)
        for ally_stats in context.all_allies:
            # Calculate actual healing (cannot exceed max HP)
            current_hp = ally_stats.hp
            max_hp = ally_stats.max_hp
            missing_hp = max(0, max_hp - current_hp)
            actual_heal = min(base_heal, missing_hp)

            if actual_heal > 0:
                ally_stats.hp += actual_heal
                # Ensure we don't exceed max HP due to floating point errors
                ally_stats.hp = min(ally_stats.hp, max_hp)

                # Track healing done
                # Using a fallback since character_id may not exist on Stats
                char_id = getattr(ally_stats, "character_id", "unknown")
                healed_targets.append((char_id, actual_heal))
                total_healing += actual_heal

        return {
            "healed": healed_targets,
            "total_healing": total_healing,
            "base_heal_amount": base_heal,
        }
