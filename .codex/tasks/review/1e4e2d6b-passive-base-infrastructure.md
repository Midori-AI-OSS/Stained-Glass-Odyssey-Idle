# Task: Create Passive Base Infrastructure

**ID**: 1e4e2d6b  
**Parent**: 7437c51e-passive-system-overview  
**Priority**: Critical  
**Complexity**: Medium  
**Assigned Mode**: Coder  
**Dependencies**: None (Foundation task)

## Objective

Create the foundational infrastructure for the passive system, including base classes, trigger definitions, and the passive registry.

## Requirements

### 1. Create `endless_idler/passives/` folder structure

```
endless_idler/passives/
├── __init__.py
├── base.py
├── triggers.py
├── registry.py
└── implementations/
    └── __init__.py
```

### 2. Implement `passives/triggers.py`

Define trigger points and event data structures:

```python
from enum import Enum
from dataclasses import dataclass
from typing import Any

class PassiveTrigger(Enum):
    """When a passive can activate"""
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
    """Context data passed to passive triggers"""
    trigger: PassiveTrigger
    owner_stats: Any  # Stats object of character owning the passive
    all_allies: list[Any]  # All ally Stats objects (onsite + offsite)
    onsite_allies: list[Any]  # Only onsite allies
    offsite_allies: list[Any]  # Only offsite allies
    enemies: list[Any]  # Enemy Stats objects
    # Additional context based on trigger type
    extra: dict[str, Any]
```

### 3. Implement `passives/base.py`

Create the base protocol/class for all passives:

```python
from typing import Protocol
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext

class PassiveBase(Protocol):
    """Base interface for all passive abilities"""
    
    id: str  # Unique passive identifier
    display_name: str
    description: str
    triggers: list[PassiveTrigger]  # Which events this passive responds to
    
    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if conditions are met for this passive to activate"""
        ...
    
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Execute the passive effect, return results"""
        ...
```

Consider also providing an abstract base class implementation:

```python
from abc import ABC, abstractmethod

class Passive(ABC):
    """Abstract base class for passive implementations"""
    
    def __init__(self):
        self.id = ""
        self.display_name = ""
        self.description = ""
        self.triggers = []
    
    @abstractmethod
    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if conditions are met"""
        return False
    
    @abstractmethod
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Execute the passive effect"""
        return {}
```

### 4. Implement `passives/registry.py`

Create the passive registration and loading system:

```python
from typing import Type
from endless_idler.passives.base import PassiveBase

_PASSIVE_REGISTRY: dict[str, Type[PassiveBase]] = {}

def register_passive(passive_class: Type[PassiveBase]) -> Type[PassiveBase]:
    """Decorator to register a passive implementation"""
    _PASSIVE_REGISTRY[passive_class.id] = passive_class
    return passive_class

def get_passive(passive_id: str) -> Type[PassiveBase] | None:
    """Retrieve a passive class by ID"""
    return _PASSIVE_REGISTRY.get(passive_id)

def load_passive(passive_id: str) -> PassiveBase | None:
    """Instantiate a passive by ID"""
    passive_class = get_passive(passive_id)
    if passive_class:
        return passive_class()
    return None

def list_passives() -> list[str]:
    """List all registered passive IDs"""
    return list(_PASSIVE_REGISTRY.keys())
```

### 5. Implement `passives/__init__.py`

Export key components:

```python
"""Passive ability system for characters"""

from endless_idler.passives.base import PassiveBase, Passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext
from endless_idler.passives.registry import (
    register_passive,
    get_passive,
    load_passive,
    list_passives,
)

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
```

### 6. Implement `passives/implementations/__init__.py`

Placeholder for passive implementations:

```python
"""Passive ability implementations"""

# Future passive implementations will be imported here
# from endless_idler.passives.implementations.lady_light_radiant_aegis import LadyLightRadiantAegis
```

## Technical Considerations

1. **Type Hints**: Use proper type hints for all functions and classes
2. **Documentation**: Add docstrings to all classes and methods
3. **Protocol vs ABC**: Consider using Protocol for the interface, ABC for the base implementation
4. **Extensibility**: Design should make adding new passives straightforward
5. **Performance**: Registry lookups should be O(1) dictionary access

## Testing Strategy

- Manual verification that modules import correctly
- Check that the registry can store and retrieve dummy passive classes
- Verify that TriggerContext dataclass can be instantiated with required fields

## Acceptance Criteria

- [ ] All files created with proper structure
- [ ] Imports work correctly (`from endless_idler.passives import ...`)
- [ ] Registry can register and retrieve passive classes
- [ ] TriggerContext includes all necessary fields
- [ ] Code passes linting (`ruff check endless_idler/passives`)
- [ ] All classes and functions have docstrings

## Notes

- This task establishes the foundation; other tasks will depend on these interfaces
- Consider forward compatibility when designing the TriggerContext
- The registry uses module-level storage; consider if this needs to be more sophisticated later

## Related Files

- Will be used by: `endless_idler/passives/implementations/*.py`
- Will integrate with: `endless_idler/combat/` (in later task)
- Pattern reference: `endless_idler/combat/damage_types.py` (similar registry pattern)
