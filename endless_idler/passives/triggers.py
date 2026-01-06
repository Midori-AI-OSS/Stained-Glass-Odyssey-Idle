"""Passive trigger definitions and event context.

This module defines when passive abilities can activate (trigger points)
and the context data passed to them during activation.
"""

from enum import Enum
from typing import Any
from dataclasses import dataclass


class PassiveTrigger(Enum):
    """Defines when a passive ability can activate.
    
    Each trigger represents a specific point in combat where
    passive abilities can check conditions and execute their effects.
    """
    
    TURN_START = "turn_start"
    TURN_END = "turn_end"
    PRE_DAMAGE = "pre_damage"
    POST_DAMAGE = "post_damage"
    PRE_HEAL = "pre_heal"
    POST_HEAL = "post_heal"
    TARGET_SELECTION = "target_selection"
    DEATH = "death"


@dataclass
class TriggerContext:
    """Context data passed to passive abilities during activation.
    
    Contains all information needed for a passive to check conditions
    and execute its effects, including character stats, combat state,
    and trigger-specific data.
    
    Attributes:
        trigger: The specific trigger point that activated
        owner_stats: Stats object of the character who owns this passive
        all_allies: All ally Stats objects (both onsite and offsite)
        onsite_allies: Only the allies currently on the battlefield
        offsite_allies: Only the allies currently off the battlefield
        enemies: All enemy Stats objects
        extra: Additional context data specific to the trigger type.
               For example, PRE_DAMAGE might include damage_amount,
               TARGET_SELECTION might include available_targets, etc.
    """
    
    trigger: PassiveTrigger
    owner_stats: Any  # Will be Stats type from combat module
    all_allies: list[Any]
    onsite_allies: list[Any]
    offsite_allies: list[Any]
    enemies: list[Any]
    extra: dict[str, Any]
