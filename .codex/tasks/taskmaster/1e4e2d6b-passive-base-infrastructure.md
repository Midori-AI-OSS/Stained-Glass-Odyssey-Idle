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

- [x] All files created with proper structure
- [x] Imports work correctly (`from endless_idler.passives import ...`)
- [x] Registry can register and retrieve passive classes
- [x] TriggerContext includes all necessary fields
- [x] Code passes linting (`ruff check endless_idler/passives`)
- [x] All classes and functions have docstrings

## Notes

- This task establishes the foundation; other tasks will depend on these interfaces
- Consider forward compatibility when designing the TriggerContext
- The registry uses module-level storage; consider if this needs to be more sophisticated later

## Related Files

- Will be used by: `endless_idler/passives/implementations/*.py`
- Will integrate with: `endless_idler/combat/` (in later task)
- Pattern reference: `endless_idler/combat/damage_types.py` (similar registry pattern)

---

## Audit Report

**Auditor**: Auditor Agent  
**Date**: 2026-01-06  
**Status**: ✅ **APPROVED**  
**Commit**: b03c2fcad95bfc955dbd569259c2e4302836fcad

### Summary

This task has been completed to an **exemplary standard**. All acceptance criteria are met, code quality is excellent, and the implementation demonstrates thoughtful design decisions that will facilitate future development.

### Detailed Review

#### 1. File Structure ✅
All required files are present and correctly organized:
```
endless_idler/passives/
├── __init__.py (53 lines)
├── base.py (114 lines)
├── triggers.py (55 lines)
├── registry.py (105 lines)
└── implementations/
    └── __init__.py (9 lines)
```

#### 2. Code Quality ✅

**Documentation**: All modules, classes, and functions have comprehensive docstrings with clear descriptions, parameter documentation, return types, and usage examples.

**Type Hints**: Complete and accurate type annotations throughout. Notable highlights:
- Proper use of `Protocol` for interface definition
- Correct use of `ABC` and `abstractmethod` for base implementation
- Appropriate use of `Type[PassiveBase]` for class references
- Union types (`Type[PassiveBase] | None`) for nullable returns

**Import Style**: Follows repository standards perfectly:
- Grouped imports (standard library, then project modules)
- Sorted within groups
- Blank lines between groups
- No inline imports

#### 3. Implementation Excellence ✅

**triggers.py**: Clean enum and dataclass implementation. The `TriggerContext` is well-designed for extensibility with the `extra` field for trigger-specific data.

**base.py**: Excellent dual implementation:
- `PassiveBase` protocol for interface definition
- `Passive` ABC for convenient implementation
- Both approaches supported, giving future developers flexibility

**registry.py**: Robust registry implementation with several strengths:
- Handles both class-attribute and instance-attribute ID patterns
- Returns `None` for missing passives (fail-safe)
- Includes `clear_registry()` for testing
- `list_passives()` returns sorted list for deterministic output
- O(1) dictionary lookups as required

**__init__.py**: Clean public API with proper `__all__` exports and helpful docstring with usage example.

**implementations/__init__.py**: Appropriate placeholder with clear comment about future usage.

#### 4. Testing Results ✅

**Linting**: `ruff check endless_idler/passives/` passes with no issues.

**Import Testing**: All imports work correctly:
```python
from endless_idler.passives import (
    PassiveBase, Passive, PassiveTrigger, TriggerContext,
    register_passive, get_passive, load_passive, list_passives
)
```

**Functional Testing**:
- ✅ Registry registration works with decorator pattern
- ✅ Both class-attribute and instance-attribute ID patterns supported
- ✅ `load_passive()` correctly instantiates registered passives
- ✅ `TriggerContext` dataclass instantiates correctly
- ✅ Passive methods (`can_trigger`, `execute`) work as expected
- ✅ Edge cases handled properly (returns `None` for missing passives)

#### 5. Edge Cases & Error Handling ✅

Verified the following edge cases:
- Non-existent passive lookup returns `None` (not exception)
- Empty registry returns empty list
- Both registration patterns work correctly
- Registry can be cleared for testing

#### 6. Breaking Changes ✅

**No breaking changes detected**:
- This is new infrastructure; no existing code depends on it
- Character files reference `autofighter.passives` (external plugin), not this module
- No naming conflicts exist

#### 7. Code Patterns ✅

Implementation follows established repository patterns:
- Similar to `endless_idler/combat/damage_types.py` registry pattern
- Consistent with dataclass usage throughout codebase
- Follows module organization standards

### Areas of Excellence

1. **Comprehensive documentation** with usage examples in docstrings
2. **Dual implementation strategy** (Protocol + ABC) provides maximum flexibility
3. **Robust registry** that handles multiple ID assignment patterns
4. **Extensive testing** coverage including edge cases
5. **Forward compatibility** designed into `TriggerContext.extra` field
6. **Clean public API** with well-thought-out exports
7. **Added utility function** (`clear_registry`) not in requirements but useful for testing

### Issues Found

**None**. Zero issues identified.

### Recommendations

None required. Implementation is ready for integration. Future tasks can confidently build on this foundation.

### Approval

This task is **approved without reservations** and ready for Task Master review.
