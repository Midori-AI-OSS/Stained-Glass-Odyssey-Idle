"""Base classes and protocols for passive abilities.

This module provides the foundational interfaces that all passive
ability implementations must follow.
"""

from typing import Any, Protocol
from abc import ABC, abstractmethod

from endless_idler.passives.triggers import PassiveTrigger, TriggerContext


class PassiveBase(Protocol):
    """Protocol defining the interface for all passive abilities.
    
    All passive implementations should conform to this interface,
    either directly or by inheriting from the Passive ABC.
    
    Attributes:
        id: Unique identifier for this passive (e.g., "radiant_aegis")
        display_name: Human-readable name shown in UI
        description: Full description of what the passive does
        triggers: List of trigger points this passive responds to
    """
    
    id: str
    display_name: str
    description: str
    triggers: list[PassiveTrigger]
    
    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if this passive's conditions are met for activation.
        
        Args:
            context: Current combat state and trigger information
            
        Returns:
            True if the passive should activate, False otherwise
        """
        ...
    
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Execute the passive's effect.
        
        Args:
            context: Current combat state and trigger information
            
        Returns:
            Dictionary containing results of the passive's execution.
            Can include keys like:
            - "damage_dealt": int
            - "healing_done": int
            - "shields_applied": dict[str, int]
            - "message": str (for combat log)
            etc.
        """
        ...


class Passive(ABC):
    """Abstract base class providing default passive implementation.
    
    Inherit from this class to create concrete passive abilities.
    Override can_trigger() and execute() to define behavior.
    
    Example:
        class MyPassive(Passive):
            def __init__(self):
                super().__init__()
                self.id = "my_passive"
                self.display_name = "My Passive"
                self.description = "Does something cool"
                self.triggers = [PassiveTrigger.TURN_START]
            
            def can_trigger(self, context: TriggerContext) -> bool:
                return context.owner_stats.hp > 0
            
            def execute(self, context: TriggerContext) -> dict[str, Any]:
                return {"message": "Passive activated!"}
    """
    
    def __init__(self) -> None:
        """Initialize passive with default values.
        
        Subclasses should override these in their __init__.
        """
        self.id: str = ""
        self.display_name: str = ""
        self.description: str = ""
        self.triggers: list[PassiveTrigger] = []
    
    @abstractmethod
    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if conditions are met for activation.
        
        Args:
            context: Current combat state and trigger information
            
        Returns:
            True if the passive should activate, False otherwise
        """
        return False
    
    @abstractmethod
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Execute the passive effect.
        
        Args:
            context: Current combat state and trigger information
            
        Returns:
            Dictionary with execution results
        """
        return {}
