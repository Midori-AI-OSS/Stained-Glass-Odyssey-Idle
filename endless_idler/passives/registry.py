"""Passive ability registration and loading system.

This module provides a centralized registry for passive ability classes,
allowing them to be registered, retrieved, and instantiated by ID.
"""

from typing import Type

from endless_idler.passives.base import PassiveBase


# Global registry mapping passive IDs to their class implementations
_PASSIVE_REGISTRY: dict[str, Type[PassiveBase]] = {}


def register_passive(passive_class: Type[PassiveBase]) -> Type[PassiveBase]:
    """Register a passive ability class in the global registry.
    
    Can be used as a decorator or called directly.
    The passive class must have an 'id' attribute.
    
    Args:
        passive_class: The passive class to register
        
    Returns:
        The same class (for decorator chaining)
        
    Example:
        @register_passive
        class MyPassive(Passive):
            def __init__(self):
                super().__init__()
                self.id = "my_passive"
                ...
    """
    # For classes that set id as a class attribute
    if hasattr(passive_class, 'id') and isinstance(passive_class.id, str):
        _PASSIVE_REGISTRY[passive_class.id] = passive_class
    else:
        # For classes that set id in __init__, we need to instantiate temporarily
        temp_instance = passive_class()
        if hasattr(temp_instance, 'id') and temp_instance.id:
            _PASSIVE_REGISTRY[temp_instance.id] = passive_class
    
    return passive_class


def get_passive(passive_id: str) -> Type[PassiveBase] | None:
    """Retrieve a passive class by its ID.
    
    Args:
        passive_id: The unique identifier of the passive
        
    Returns:
        The passive class if found, None otherwise
        
    Example:
        passive_cls = get_passive("radiant_aegis")
        if passive_cls:
            instance = passive_cls()
    """
    return _PASSIVE_REGISTRY.get(passive_id)


def load_passive(passive_id: str) -> PassiveBase | None:
    """Instantiate a passive ability by its ID.
    
    Convenience function that retrieves and instantiates in one call.
    
    Args:
        passive_id: The unique identifier of the passive
        
    Returns:
        An instance of the passive if found, None otherwise
        
    Example:
        passive = load_passive("radiant_aegis")
        if passive:
            can_activate = passive.can_trigger(context)
    """
    passive_class = get_passive(passive_id)
    if passive_class:
        return passive_class()
    return None


def list_passives() -> list[str]:
    """Get a list of all registered passive IDs.
    
    Returns:
        Sorted list of passive IDs currently in the registry
        
    Example:
        available = list_passives()
        print(f"Available passives: {', '.join(available)}")
    """
    return sorted(_PASSIVE_REGISTRY.keys())


def clear_registry() -> None:
    """Clear all registered passives from the registry.
    
    Primarily useful for testing purposes.
    """
    _PASSIVE_REGISTRY.clear()
