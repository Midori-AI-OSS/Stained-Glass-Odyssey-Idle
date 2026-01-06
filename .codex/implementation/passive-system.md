# Passive System Architecture

## Overview

The passive system allows characters to have special abilities that trigger automatically during combat based on specific events. Passives are loaded when characters are created and execute when their trigger conditions are met.

## Architecture

### Core Components

#### 1. Passive Base (`endless_idler/passives/base.py`)

Defines the interface that all passives must implement:

```python
class PassiveBase(Protocol):
    id: str                      # Unique identifier
    display_name: str            # Human-readable name
    description: str             # Full description
    triggers: list[PassiveTrigger]  # When this passive activates
    
    def can_trigger(context: TriggerContext) -> bool
    def execute(context: TriggerContext) -> dict[str, Any]
```

Passives inherit from the `Passive` abstract base class which implements this protocol.

#### 2. Trigger Points (`endless_idler/passives/triggers.py`)

Defines when passives can activate:

- **TURN_START**: Beginning of each combat turn
- **TURN_END**: End of each combat turn (not yet implemented)
- **PRE_DAMAGE**: Before damage is calculated
- **POST_DAMAGE**: After damage is dealt (not yet implemented)
- **PRE_HEAL**: Before healing is applied (not yet implemented)
- **POST_HEAL**: After healing is applied (not yet implemented)
- **TARGET_SELECTION**: During target selection for attacks
- **DEATH**: When a character dies (not yet implemented)

#### 3. Trigger Context (`endless_idler/passives/triggers.py`)

Contains all combat state information passed to passives:

```python
@dataclass
class TriggerContext:
    trigger: PassiveTrigger       # The trigger that activated
    owner_stats: Stats            # Character who owns this passive
    all_allies: list[Stats]       # All allies (onsite + offsite)
    onsite_allies: list[Stats]    # Allies on battlefield
    offsite_allies: list[Stats]   # Allies off battlefield
    enemies: list[Stats]          # Enemy combatants
    extra: dict[str, Any]         # Trigger-specific data
```

#### 4. Registry (`endless_idler/passives/registry.py`)

Central registry for all passive implementations:

- `register_passive(cls)`: Register a passive class (used as decorator)
- `load_passive(passive_id)`: Create an instance of a passive by ID
- `get_passive(passive_id)`: Get the class for a passive
- `list_passives()`: List all registered passive IDs

#### 5. Execution Utilities (`endless_idler/passives/execution.py`)

Helper functions for triggering passives:

- `trigger_passives_for_characters()`: Generic passive triggering
- `trigger_turn_start_passives()`: Trigger TURN_START for all allies
- `apply_pre_damage_passives()`: Apply damage modifiers from PRE_DAMAGE
- `apply_target_selection_passives()`: Handle target redirection

### Integration Points

#### Character Loading (`endless_idler/ui/battle/sim.py`)

When characters are created for combat:

1. Extract passive IDs from character metadata
2. Set `character_id` on Stats object
3. Load passive instances using registry
4. Store instances in `stats._passive_instances`

```python
def load_passives_for_character(stats: Stats, plugin: CharacterPlugin, char_id: str):
    stats.character_id = char_id
    if plugin and plugin.passives:
        loaded_passives = []
        for passive_id in plugin.passives:
            passive = load_passive(passive_id)
            if passive:
                loaded_passives.append(passive)
        stats._passive_instances = loaded_passives
```

#### Combat Flow (`endless_idler/ui/battle/screen.py`)

Passives integrate into the combat loop at specific points:

**TURN_START** (beginning of `_step_battle`):
```python
turn_start_results = trigger_turn_start_passives(
    all_allies=all_party_stats,
    onsite_allies=party_stats,
    offsite_allies=reserve_stats,
    enemies=foe_stats,
)
# Process results (e.g., healing, stat buffs)
```

**PRE_DAMAGE** (in `calculate_damage`):
```python
if all_allies is not None:  # Context provided
    passive_damage_mult, defense_ignore = apply_pre_damage_passives(
        attacker=attacker,
        target=target,
        all_allies=all_allies,
        onsite_allies=onsite_allies,
        offsite_allies=offsite_allies,
        enemies=enemies,
    )
    # Apply modifiers to damage calculation
```

**TARGET_SELECTION** (when choosing attack target):
```python
new_target = apply_target_selection_passives(
    attacker=attacker,
    original_target=original_target,
    available_targets=enemies,
    all_allies=all_allies,
    onsite_allies=onsite_allies,
    offsite_allies=offsite_allies,
    enemies=enemies,
)
```

#### Stats Extension (`endless_idler/combat/stats.py`)

Stats class has two new fields:

```python
@dataclass(slots=True)
class Stats:
    character_id: str = ""  # Identifies which character owns these stats
    # ... other fields ...
    _passive_instances: list[Any] = field(default_factory=list, init=False)
```

## Implemented Passives

### Lady Light: Radiant Aegis

**ID**: `lady_light_radiant_aegis`

**Trigger**: TURN_START

**Effect**: When Lady Light is offsite, heal all party members (onsite + offsite) for 50% of her regain stat.

**Implementation Details**:
- Only triggers when owner is in offsite_allies
- Calculates heal amount as `int(owner.regain * 0.50)`
- Heals all allies up to their max HP
- Returns `healing_done` dict mapping Stats to heal amounts

### Lady Darkness: Eclipsing Veil

**ID**: `lady_darkness_eclipsing_veil`

**Trigger**: PRE_DAMAGE

**Effect**: When Lady Darkness attacks, deal 2x damage and ignore 50% of target's defense.

**Implementation Details**:
- Only triggers when attacker is Lady Darkness
- Returns `damage_multiplier: 2.0`
- Returns `defense_ignore: 0.50`
- Applied before damage calculation

### Trinity Synergy

**ID**: `trinity_synergy`

**Triggers**: TURN_START, TARGET_SELECTION

**Effect**: When Lady Light, Lady Darkness, and Persona: Light and Dark are all in party:
- Lady Light gains +50% regain
- Lady Darkness gains +30% damage
- Attacks targeting Lady Light or Lady Darkness redirect to Persona

**Implementation Details**:
- Checks for all three characters by ID
- Sets temporary multipliers on TURN_START
- Redirects targets on TARGET_SELECTION
- Each character should have this passive

## Creating New Passives

### Step 1: Create Passive Class

Create a new file in `endless_idler/passives/implementations/`:

```python
from endless_idler.passives.base import Passive
from endless_idler.passives.registry import register_passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext


@register_passive
class MyPassive(Passive):
    """Description of what this passive does."""
    
    def __init__(self) -> None:
        super().__init__()
        self.id = "my_passive_unique_id"
        self.display_name = "My Passive Name"
        self.description = "Full description of passive effect"
        self.triggers = [PassiveTrigger.TURN_START]  # When to trigger
    
    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if conditions are met for activation."""
        # Example: only trigger if owner has > 50% HP
        max_hp = context.owner_stats.max_hp
        current_hp = context.owner_stats.hp
        return current_hp > (max_hp * 0.5)
    
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Execute the passive's effect."""
        # Example: boost all allies' attack by 10%
        from endless_idler.combat.stat_effect import StatEffect
        
        for ally in context.all_allies:
            effect = StatEffect(
                name="my_passive_buff",
                source="my_passive",
                duration=1,  # Lasts 1 turn
                stat_modifiers={"atk": ally.atk * 0.1},
            )
            ally.add_effect(effect)
        
        return {
            "message": f"Boosted {len(context.all_allies)} allies!",
            "allies_affected": len(context.all_allies),
        }
```

### Step 2: Import Implementation

Add to `endless_idler/passives/implementations/__init__.py`:

```python
from endless_idler.passives.implementations.my_passive import MyPassive

__all__ = [
    # ... existing passives ...
    "MyPassive",
]
```

### Step 3: Add to Character

Add passive ID to character metadata in character file:

```python
from dataclasses import dataclass, field

@dataclass
class MyCharacter:
    id: str = "my_character"
    name: str = "My Character"
    passives: list[str] = field(default_factory=lambda: ["my_passive_unique_id"])
```

### Step 4: Write Tests

Create `tests/passives/test_my_passive.py`:

```python
import pytest
from endless_idler.combat.stats import Stats
from endless_idler.passives.registry import load_passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext


def test_my_passive_registration():
    """Test that passive is registered."""
    passive = load_passive("my_passive_unique_id")
    assert passive is not None
    assert passive.id == "my_passive_unique_id"


def test_my_passive_can_trigger():
    """Test trigger conditions."""
    passive = load_passive("my_passive_unique_id")
    owner = Stats()
    owner.hp = 600
    owner._base_max_hp = 1000
    
    context = TriggerContext(
        trigger=PassiveTrigger.TURN_START,
        owner_stats=owner,
        all_allies=[owner],
        onsite_allies=[owner],
        offsite_allies=[],
        enemies=[],
        extra={},
    )
    
    assert passive.can_trigger(context) is True


def test_my_passive_execute():
    """Test passive execution."""
    passive = load_passive("my_passive_unique_id")
    # ... test execution ...
```

## Adding New Trigger Points

To add a new trigger point (e.g., ON_KILL):

### 1. Add to PassiveTrigger enum

```python
class PassiveTrigger(Enum):
    # ... existing triggers ...
    ON_KILL = "on_kill"
```

### 2. Create execution utility

In `endless_idler/passives/execution.py`:

```python
def trigger_on_kill_passives(
    *,
    killer: Stats,
    victim: Stats,
    all_allies: list[Stats],
    onsite_allies: list[Stats],
    offsite_allies: list[Stats],
    enemies: list[Stats],
) -> list[dict[str, Any]]:
    """Trigger ON_KILL passives when a character kills an enemy."""
    return trigger_passives_for_characters(
        characters=[killer],
        trigger=PassiveTrigger.ON_KILL,
        all_allies=all_allies,
        onsite_allies=onsite_allies,
        offsite_allies=offsite_allies,
        enemies=enemies,
        extra={"killer": killer, "victim": victim},
    )
```

### 3. Integrate into combat

In `endless_idler/ui/battle/screen.py`, add trigger when kill happens:

```python
if previous_hp > 0 and target.stats.hp <= 0:
    # Character died
    self._handle_combatant_fell(target)
    
    # Trigger ON_KILL passives
    from endless_idler.passives.execution import trigger_on_kill_passives
    results = trigger_on_kill_passives(
        killer=attacker.stats,
        victim=target.stats,
        all_allies=all_allies_stats,
        onsite_allies=onsite_stats,
        offsite_allies=offsite_stats,
        enemies=enemy_stats,
    )
    # Process results...
```

## Debugging Passives

### Enable Logging

Passives fail silently by design to prevent combat crashes. To debug:

1. Add logging to execution utility:
```python
import logging
logger = logging.getLogger(__name__)

# In trigger_passives_for_characters:
except Exception as e:
    logger.error(f"Passive {passive.id} failed: {e}", exc_info=True)
```

2. Check passive is registered:
```python
from endless_idler.passives.registry import list_passives
print("Registered:", list_passives())
```

3. Verify passive loads:
```python
from endless_idler.passives.registry import load_passive
passive = load_passive("my_passive_id")
print("Loaded:", passive)
```

4. Test can_trigger:
```python
context = TriggerContext(...)  # Create context
result = passive.can_trigger(context)
print("Can trigger:", result)
```

### Common Issues

**Passive not triggering**:
- Check passive is registered (`list_passives()`)
- Check character has passive ID in metadata
- Check `can_trigger()` returns True
- Check trigger point is correctly integrated in combat

**Wrong effects applied**:
- Check `execute()` return values
- Check execution utility processes results correctly
- Verify passive context has correct data

**Combat crashes**:
- Passives should never crash combat (silently fail)
- If crashes occur, check integration points
- Ensure all context data is valid before passing to passives

## Performance Considerations

### Passive Lookup Overhead

- Passives are loaded once at character creation
- No runtime lookups needed during combat
- Stored as instances in `_passive_instances`

### Trigger Overhead

- Each trigger point iterates all characters
- Each character iterates its passives
- O(characters × passives per character)
- Typically ~10-20 checks per turn

### Optimization Tips

1. **Minimal conditions in can_trigger()**:
   - Quick checks first (owner HP, simple conditions)
   - Expensive checks last (count allies, complex logic)

2. **Cache computed values**:
   - Store results on Stats if needed across triggers
   - Use extra dict in context to pass data between triggers

3. **Profile if needed**:
```python
import cProfile
cProfile.run('trigger_turn_start_passives(...)')
```

## Future Enhancements

### Planned Trigger Points

- **TURN_END**: Effects at end of turn
- **POST_DAMAGE**: Reactions after taking/dealing damage
- **PRE_HEAL/POST_HEAL**: Modify healing calculations
- **DEATH**: Effects when character dies
- **ABILITY_USED**: Trigger on special abilities

### Planned Features

- **Passive UI**: Visual indicators for active passives
- **Passive management**: Enable/disable specific passives
- **Passive stacks**: Count how many times passive triggered
- **Passive cooldowns**: Limit activation frequency
- **Conditional passives**: Based on game state, progression, etc.
- **Passive visual effects**: Animations when passives trigger

### Extension Points

The system is designed for extension:

- Add new triggers without modifying existing code
- Create new passive types with different behaviors
- Implement conditional activation based on game state
- Add passive-to-passive interactions
- Create passive sets/synergies

## Testing

### Test Coverage

- Unit tests for each passive implementation
- Integration tests for passive loading
- Integration tests for combat execution
- Edge case tests (invalid IDs, missing data, etc.)

### Running Tests

```bash
# All passive tests
pytest tests/passives/ -v

# Integration tests
pytest tests/test_passive_integration.py -v

# All tests
pytest tests/ -v
```

### Test Guidelines

1. Test passive registration
2. Test trigger conditions (can_trigger)
3. Test passive effects (execute)
4. Test edge cases (zero values, missing data)
5. Test integration with combat
6. Test multiple passives per character
7. Test passive interactions

## Summary

The passive system is fully integrated with combat and provides a flexible framework for character abilities. Key strengths:

- **Extensible**: Easy to add new passives and trigger points
- **Safe**: Failures don't crash combat
- **Testable**: Comprehensive test coverage
- **Performant**: Minimal overhead per trigger
- **Well-documented**: Clear architecture and examples

All three implemented passives (Lady Light, Lady Darkness, Trinity Synergy) are working and tested.
