"""Lady Darkness's Eclipsing Veil passive ability.

This passive amplifies Lady Darkness's offensive capabilities by
increasing her base damage and ignoring enemy defenses.
"""

from typing import Any

from endless_idler.passives.base import Passive
from endless_idler.passives.registry import register_passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext


@register_passive
class LadyDarknessEclipsingVeil(Passive):
    """Lady Darkness deals increased damage and ignores enemy defense.
    
    Passive Effect:
    - Triggers before damage calculation (PRE_DAMAGE)
    - Always active when Lady Darkness attacks
    - Deals 2x base damage
    - Ignores 50% of target's defense
    
    This is a powerful offensive passive that makes Lady Darkness
    extremely effective against high-defense enemies. The defense
    ignore is applied first, reducing the effective defense value,
    then the damage multiplier is applied to the result.
    
    Attributes:
        id: Passive identifier "lady_darkness_eclipsing_veil"
        display_name: "Eclipsing Veil"
        description: Human-readable description of the effect
        triggers: [PassiveTrigger.PRE_DAMAGE]
        damage_multiplier: 2.0x damage amplification
        defense_ignore: 0.50 (50% defense penetration)
    """
    
    def __init__(self) -> None:
        """Initialize the Eclipsing Veil passive with default values."""
        super().__init__()
        self.id = "lady_darkness_eclipsing_veil"
        self.display_name = "Eclipsing Veil"
        self.description = (
            "Lady Darkness always deals 2x base damage and ignores 50% of "
            "the target's defense when attacking."
        )
        self.triggers = [PassiveTrigger.PRE_DAMAGE]
        self.damage_multiplier = 2.0
        self.defense_ignore = 0.50
    
    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if Lady Darkness is the attacker in this damage event.
        
        This passive triggers whenever Lady Darkness is attacking an enemy.
        It always returns True when the owner is the attacker.
        
        Args:
            context: Trigger context with attack information
            
        Returns:
            True if this is a damage event with Lady Darkness as attacker,
            False otherwise
        """
        # Check if attacker exists in the context
        attacker = context.extra.get("attacker")
        if attacker is None:
            return False
        
        # Verify the attacker is the owner of this passive
        return attacker == context.owner_stats
    
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Apply damage amplification and defense ignore effects.
        
        Modifies the damage calculation by:
        1. Reducing effective defense by 50%
        2. Multiplying final damage by 2.0x
        
        Args:
            context: Trigger context with damage calculation data
            
        Returns:
            Dictionary containing damage modifiers:
                - damage_multiplier: float (2.0)
                - defense_ignore: float (0.50)
                - original_defense: int (for logging)
                - effective_defense: int (for logging)
        """
        target = context.extra.get("target")
        if target is None:
            # No target, return neutral modifiers
            return {
                "damage_multiplier": 1.0,
                "defense_ignore": 0.0,
            }
        
        # Calculate effective defense after ignore
        original_defense = target.defense
        effective_defense = int(original_defense * (1.0 - self.defense_ignore))
        
        return {
            "damage_multiplier": self.damage_multiplier,
            "defense_ignore": self.defense_ignore,
            "original_defense": original_defense,
            "effective_defense": effective_defense,
        }
