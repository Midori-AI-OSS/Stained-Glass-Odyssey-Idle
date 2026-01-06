"""Base classes and protocols for passive abilities.

This module provides the foundational interfaces and implementations that
all passive abilities must follow.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Protocol

if TYPE_CHECKING:
    from typing import Any
    
    from endless_idler.passives.triggers import PassiveTrigger
    from endless_idler.passives.triggers import TriggerContext


class PassiveBase(Protocol):
    """Base interface for all passive abilities.
    
    This protocol defines the minimum contract that all passive implementations
    must satisfy. Use this for type hints when you need to accept any passive.
    
    Attributes:
        id: Unique passive identifier (e.g., "radiant_aegis")
        display_name: Human-readable name shown in UI
        description: Description of what the passive does
        triggers: List of trigger events this passive responds to
    """
    
    id: str
    display_name: str
    description: str
    triggers: list[PassiveTrigger]
    
    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if conditions are met for this passive to activate.
        
        Args:
            context: The trigger context containing all relevant battle state
            
        Returns:
            True if the passive should execute, False otherwise
        """
        ...
    
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Execute the passive effect.
        
        Args:
            context: The trigger context containing all relevant battle state
            
        Returns:
            Dictionary containing results of the passive execution.
            Common keys include:
            - "applied": bool, whether the effect was applied
            - "targets": list of affected Stats objects
            - "description": str, human-readable description of what happened
        """
        ...


class Passive(ABC):
    """Abstract base class for passive implementations.
    
    Extend this class when creating new passive abilities. It provides
    default attribute initialization and enforces the implementation of
    required methods through abstract methods.
    
    Example:
        ```python
        class RadiantAegis(Passive):
            def __init__(self):
                super().__init__()
                self.id = "radiant_aegis"
                self.display_name = "Radiant Aegis"
                self.description = "Reduces damage taken by allies"
                self.triggers = [PassiveTrigger.PRE_DAMAGE]
            
            def can_trigger(self, context: TriggerContext) -> bool:
                return True  # Always active
            
            def execute(self, context: TriggerContext) -> dict[str, Any]:
                # Implement damage reduction logic
                return {"applied": True}
        ```
    """
    
    def __init__(self) -> None:
        """Initialize passive with default values.
        
        Subclasses should call super().__init__() and then set their
        specific attribute values.
        """
        self.id: str = ""
        self.display_name: str = ""
        self.description: str = ""
        self.triggers: list[PassiveTrigger] = []
    
    @abstractmethod
    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if conditions are met for this passive to activate.
        
        Args:
            context: The trigger context containing all relevant battle state
            
        Returns:
            True if the passive should execute, False otherwise
        """
        return False
    
    @abstractmethod
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Execute the passive effect.
        
        Args:
            context: The trigger context containing all relevant battle state
            
        Returns:
            Dictionary containing results of the passive execution.
            Common keys include:
            - "applied": bool, whether the effect was applied
            - "targets": list of affected Stats objects
            - "description": str, human-readable description of what happened
        """
        return {}
