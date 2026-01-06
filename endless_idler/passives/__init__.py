"""Passive ability system for characters.

This package provides the infrastructure for defining, registering, and
executing passive abilities in combat. Passive abilities are effects that
trigger automatically based on specific combat events.

Key Components:
    - PassiveBase/Passive: Base classes for implementing passive abilities
    - PassiveTrigger: Enum of trigger events
    - TriggerContext: Data provided to passives when they trigger
    - Registry functions: For registering and loading passive implementations

Example Usage:
    ```python
    from endless_idler.passives import Passive, PassiveTrigger, register_passive
    
    @register_passive
    class MyPassive(Passive):
        def __init__(self):
            super().__init__()
            self.id = "my_passive"
            self.display_name = "My Passive"
            self.description = "Does something cool"
            self.triggers = [PassiveTrigger.TURN_START]
        
        def can_trigger(self, context):
            return True
        
        def execute(self, context):
            return {"applied": True}
    ```
"""

from endless_idler.passives.base import Passive
from endless_idler.passives.base import PassiveBase
from endless_idler.passives.triggers import PassiveTrigger
from endless_idler.passives.triggers import TriggerContext

from endless_idler.passives.registry import get_passive
from endless_idler.passives.registry import list_passives
from endless_idler.passives.registry import load_passive
from endless_idler.passives.registry import register_passive

__all__ = [
    "PassiveBase",
    "Passive",
    "PassiveTrigger",
    "TriggerContext",
    "register_passive",
    "get_passive",
    "load_passive",
    "list_passives",
]
