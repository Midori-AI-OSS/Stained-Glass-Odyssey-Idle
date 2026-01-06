"""Trinity Synergy passive ability - shared by Lady Darkness, Lady Light, and Persona Light and Dark.

This passive provides powerful bonuses when all three trinity members are present in the party.
"""

from typing import Any

from endless_idler.passives.base import Passive
from endless_idler.passives.registry import register_passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext


# Character IDs for the trinity
LADY_LIGHT_ID = "lady_light"
LADY_DARKNESS_ID = "lady_darkness"
PERSONA_LIGHT_AND_DARK_ID = "persona_light_and_dark"


def is_trinity_active(context: TriggerContext) -> tuple[bool, dict[str, Any]]:
    """Check if all three trinity members are present in the party.
    
    Args:
        context: Trigger context with party information
        
    Returns:
        Tuple of (is_active, member_map)
        - is_active: True if all three members present
        - member_map: Dict mapping character IDs to their Stats objects
    """
    all_chars = context.all_allies
    
    trinity_members = {
        LADY_LIGHT_ID: None,
        LADY_DARKNESS_ID: None,
        PERSONA_LIGHT_AND_DARK_ID: None,
    }
    
    # Find each trinity member
    for stats in all_chars:
        char_id = getattr(stats, 'character_id', '')
        if char_id in trinity_members:
            trinity_members[char_id] = stats
    
    # All must be present
    is_active = all(stats is not None for stats in trinity_members.values())
    
    return is_active, trinity_members


@register_passive
class TrinitySynergy(Passive):
    """Trinity Synergy passive shared by Lady Darkness, Lady Light, and Persona Light and Dark.
    
    When all three characters are in the party (onsite or offsite), they gain powerful bonuses:
    
    - Lady Light: 15x regain, 4x healing output
    - Lady Darkness: 2x damage, allies take 1/2 damage from darkness bleed
    - Persona Light and Dark: Redirects attacks targeting Lady Darkness to himself
    
    This passive encourages using all three family members together.
    """
    
    def __init__(self) -> None:
        """Initialize the Trinity Synergy passive."""
        super().__init__()
        self.id = "trinity_synergy"
        self.display_name = "Trinity Synergy"
        self.description = (
            "When Lady Darkness, Lady Light, and Persona Light and Dark are all in the party, "
            "each gains unique powerful bonuses based on their role."
        )
        self.triggers = [PassiveTrigger.TURN_START, PassiveTrigger.TARGET_SELECTION]
        
        # Effect multipliers
        self.lady_light_regain_mult = 15.0
        self.lady_light_healing_mult = 4.0
        self.lady_darkness_damage_mult = 2.0
        self.lady_darkness_bleed_reduction = 0.5
    
    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if trinity is active.
        
        Args:
            context: Trigger context with party information
            
        Returns:
            True if all three trinity members are in the party
        """
        is_active, _ = is_trinity_active(context)
        return is_active
    
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Apply trinity synergy effects based on trigger type.
        
        Args:
            context: Trigger context
            
        Returns:
            Dictionary with effects applied:
                - trigger_type: str
                - effects_applied: list of effect descriptions
                - character_id: str (owner of this passive instance)
        """
        is_active, trinity_members = is_trinity_active(context)
        
        if not is_active:
            return {"trigger_type": context.trigger.value, "effects_applied": []}
        
        effects_applied = []
        owner_id = getattr(context.owner_stats, 'character_id', '')
        
        # TURN_START: Apply stat modifications
        if context.trigger == PassiveTrigger.TURN_START:
            effects_applied.extend(self._apply_turn_start_effects(
                trinity_members, owner_id, context
            ))
        
        # TARGET_SELECTION: Handle attack redirection
        elif context.trigger == PassiveTrigger.TARGET_SELECTION:
            redirection = self._apply_target_redirection(
                trinity_members, context
            )
            if redirection:
                effects_applied.append(redirection)
        
        result = {
            "trigger_type": context.trigger.value,
            "effects_applied": effects_applied,
            "character_id": owner_id,
        }
        
        # For TARGET_SELECTION, include the new target if redirected
        if context.trigger == PassiveTrigger.TARGET_SELECTION and "new_target" in context.extra:
            result["new_target"] = context.extra["new_target"]
        
        return result
    
    def _apply_turn_start_effects(
        self,
        trinity_members: dict[str, Any],
        owner_id: str,
        context: TriggerContext,
    ) -> list[str]:
        """Apply stat modifications at turn start.
        
        Args:
            trinity_members: Map of character IDs to Stats
            owner_id: ID of character owning this passive instance
            context: Trigger context
            
        Returns:
            List of effect descriptions
        """
        effects = []
        
        # Lady Light: Regain and healing bonuses
        lady_light = trinity_members.get(LADY_LIGHT_ID)
        if lady_light and owner_id == LADY_LIGHT_ID:
            # Apply regain multiplier
            base_regain = getattr(lady_light, 'regain', 0)
            bonus_regain = int(base_regain * (self.lady_light_regain_mult - 1.0))
            if hasattr(lady_light, 'regain'):
                lady_light.regain += bonus_regain
            effects.append(f"Lady Light regain boosted by {self.lady_light_regain_mult}x")
            
            # Store healing multiplier for use in healing calculations
            # (Combat system will need to check for this)
            context.extra["lady_light_healing_mult"] = self.lady_light_healing_mult
            effects.append(f"Lady Light healing output x{self.lady_light_healing_mult}")
        
        # Lady Darkness: Damage boost and bleed reduction
        lady_darkness = trinity_members.get(LADY_DARKNESS_ID)
        if lady_darkness and owner_id == LADY_DARKNESS_ID:
            # Store damage multiplier for damage calculations
            context.extra["lady_darkness_damage_mult"] = self.lady_darkness_damage_mult
            effects.append(f"Lady Darkness damage x{self.lady_darkness_damage_mult}")
            
            # Store bleed reduction for ally damage calculations
            context.extra["lady_darkness_bleed_reduction"] = self.lady_darkness_bleed_reduction
            effects.append("Allies take 1/2 damage from Lady Darkness bleed")
        
        return effects
    
    def _apply_target_redirection(
        self,
        trinity_members: dict[str, Any],
        context: TriggerContext,
    ) -> str | None:
        """Redirect attacks targeting Lady Darkness to Persona.
        
        Args:
            trinity_members: Map of character IDs to Stats
            context: Trigger context with targeting information
            
        Returns:
            Description of redirection if applied, None otherwise
        """
        original_target = context.extra.get("original_target")
        persona = trinity_members.get(PERSONA_LIGHT_AND_DARK_ID)
        lady_darkness = trinity_members.get(LADY_DARKNESS_ID)
        
        # Check if target is Lady Darkness and Persona is available
        if original_target == lady_darkness and persona:
            # Check if Persona is alive (has HP > 0)
            persona_hp = getattr(persona, 'hp', 0)
            if persona_hp > 0:
                # Modify the target
                context.extra["new_target"] = persona
                return "Attack redirected from Lady Darkness to Persona Light and Dark"
        
        return None
