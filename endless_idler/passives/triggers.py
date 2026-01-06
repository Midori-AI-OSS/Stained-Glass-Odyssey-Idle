"""Trigger points and event data structures for passive abilities.

This module defines when passives can activate (PassiveTrigger) and what
context data is provided to them (TriggerContext).
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from dataclasses import field
from dataclasses import dataclass

if TYPE_CHECKING:
    from typing import Any


class PassiveTrigger(Enum):
    """When a passive can activate.
    
    These triggers represent key moments in combat when passive abilities
    can check their conditions and execute their effects.
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
    """Context data passed to passive triggers.
    
    Provides all the information a passive ability needs to check its
    conditions and execute its effects.
    
    Attributes:
        trigger: The specific trigger event that occurred
        owner_stats: Stats object of the character owning this passive
        all_allies: All ally Stats objects (both onsite and offsite)
        onsite_allies: Only allies currently on the battlefield
        offsite_allies: Only allies currently off the battlefield
        enemies: Enemy Stats objects
        extra: Additional context data specific to the trigger type
    """
    
    trigger: PassiveTrigger
    owner_stats: Any  # Stats object of character owning the passive
    all_allies: list[Any]  # All ally Stats objects (onsite + offsite)
    onsite_allies: list[Any]  # Only onsite allies
    offsite_allies: list[Any]  # Only offsite allies
    enemies: list[Any]  # Enemy Stats objects
    extra: dict[str, Any] = field(default_factory=dict)
