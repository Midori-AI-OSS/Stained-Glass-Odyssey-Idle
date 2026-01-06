"""Passive registration and loading system.

This module provides a centralized registry for all passive ability
implementations, allowing them to be looked up by ID and instantiated
dynamically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type
    
    from endless_idler.passives.base import PassiveBase


# Global registry mapping passive IDs to their class implementations
_PASSIVE_REGISTRY: dict[str, Type[PassiveBase]] = {}


def register_passive(passive_class: Type[PassiveBase]) -> Type[PassiveBase]:
    """Decorator to register a passive implementation.
    
    This decorator adds a passive class to the global registry, making it
    available for lookup and instantiation via get_passive() and load_passive().
    
    Args:
        passive_class: The passive class to register. Must have an 'id' attribute.
        
    Returns:
        The same passive class (allows use as a decorator)
        
    Example:
        ```python
        @register_passive
        class RadiantAegis(Passive):
            id = "radiant_aegis"
            ...
        ```
        
    Note:
        The passive class's 'id' attribute must be set before registration.
        Duplicate IDs will overwrite previous registrations.
    """
    # Access the id from a dummy instance to support both class and instance attributes
    instance = passive_class()
    _PASSIVE_REGISTRY[instance.id] = passive_class
    return passive_class


def get_passive(passive_id: str) -> Type[PassiveBase] | None:
    """Retrieve a passive class by ID.
    
    Args:
        passive_id: The unique identifier of the passive to retrieve
        
    Returns:
        The passive class if found, None otherwise
        
    Example:
        ```python
        passive_class = get_passive("radiant_aegis")
        if passive_class:
            passive = passive_class()
        ```
    """
    return _PASSIVE_REGISTRY.get(passive_id)


def load_passive(passive_id: str) -> PassiveBase | None:
    """Instantiate a passive by ID.
    
    This is a convenience function that combines get_passive() with
    instantiation. It retrieves the passive class and creates a new
    instance in one step.
    
    Args:
        passive_id: The unique identifier of the passive to instantiate
        
    Returns:
        A new instance of the passive if found, None otherwise
        
    Example:
        ```python
        passive = load_passive("radiant_aegis")
        if passive:
            result = passive.execute(context)
        ```
    """
    passive_class = get_passive(passive_id)
    if passive_class:
        return passive_class()
    return None


def list_passives() -> list[str]:
    """List all registered passive IDs.
    
    Returns:
        A list of all passive IDs currently in the registry
        
    Example:
        ```python
        available = list_passives()
        print(f"Available passives: {', '.join(available)}")
        ```
        
    Note:
        The order of IDs is not guaranteed to be consistent between calls.
    """
    return list(_PASSIVE_REGISTRY.keys())
