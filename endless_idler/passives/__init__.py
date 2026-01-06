"""Passive ability system for characters.

This package provides the infrastructure for implementing and managing
passive abilities that trigger during combat based on specific events.

Key Components:
    - PassiveTrigger: Enum defining when passives can activate
    - TriggerContext: Data passed to passives during activation
    - PassiveBase: Protocol defining the passive interface
    - Passive: Abstract base class for implementations
    - Registry functions: For registering and loading passives

Example Usage:
    from endless_idler.passives import (
        Passive, PassiveTrigger, TriggerContext, register_passive
    )
    
    @register_passive
    class MyPassive(Passive):
        def __init__(self):
            super().__init__()
            self.id = "my_passive"
            self.display_name = "My Passive"
            self.description = "Triggers at turn start"
            self.triggers = [PassiveTrigger.TURN_START]
        
        def can_trigger(self, context: TriggerContext) -> bool:
            return True
        
        def execute(self, context: TriggerContext) -> dict:
            return {"message": "Activated!"}
"""

from endless_idler.passives.base import Passive, PassiveBase
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext

from endless_idler.passives.registry import (
    get_passive,
    load_passive,
    list_passives,
    register_passive,
)

from endless_idler.passives.execution import (
    apply_pre_damage_passives,
    apply_target_selection_passives,
    trigger_passives_for_characters,
    trigger_turn_start_passives,
)

# Import implementations to ensure they are registered
from endless_idler.passives import implementations  # noqa: F401

__all__ = [
    "PassiveBase",
    "Passive",
    "PassiveTrigger",
    "TriggerContext",
    "register_passive",
    "get_passive",
    "load_passive",
    "list_passives",
    "apply_pre_damage_passives",
    "apply_target_selection_passives",
    "trigger_passives_for_characters",
    "trigger_turn_start_passives",
]
