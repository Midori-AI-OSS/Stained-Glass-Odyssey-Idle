# Task: Implement Lady Light Radiant Aegis Passive

**ID**: 04f7b1f9  
**Parent**: 7437c51e-passive-system-overview  
**Priority**: High  
**Complexity**: Medium  
**Assigned Mode**: Coder  
**Dependencies**: 1e4e2d6b (base infrastructure), b243ccf7 (metadata extraction)

## Objective

Implement the `lady_light_radiant_aegis` passive ability that heals all party members (onsite + offsite) when Lady Light is offsite.

## Passive Specification

**Name**: Radiant Aegis  
**ID**: `lady_light_radiant_aegis`  
**Owner**: Lady Light  
**Trigger**: `TURN_START` (every turn)  
**Condition**: Lady Light must be offsite (not in active combat)  
**Effect**: Heal all characters (onsite + offsite) for a percentage of Lady Light's regain stat

### Healing Calculation

```
heal_amount = lady_light_regain * heal_multiplier
heal_multiplier = 0.50  # 50% of regain per turn
```

Each character healed:
- Cannot exceed their max_hp
- Receives the same heal amount
- Offsite and onsite characters are treated equally

## Implementation

### File: `endless_idler/passives/implementations/lady_light_radiant_aegis.py`

```python
"""Lady Light's Radiant Aegis passive ability"""

from endless_idler.passives.base import Passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext
from endless_idler.passives.registry import register_passive


@register_passive
class LadyLightRadiantAegis(Passive):
    """When Lady Light is offsite, heal all party members each turn.
    
    Passive Effect:
    - Triggers at the start of each turn
    - Requires Lady Light to be offsite (not in active combat)
    - Heals all allies (onsite + offsite) for 50% of Lady Light's regain stat
    - Healing respects max HP limits
    """
    
    def __init__(self):
        super().__init__()
        self.id = "lady_light_radiant_aegis"
        self.display_name = "Radiant Aegis"
        self.description = (
            "When Lady Light is offsite, heal all party members (onsite + offsite) "
            "for 50% of her regain stat at the start of each turn."
        )
        self.triggers = [PassiveTrigger.TURN_START]
        self.heal_multiplier = 0.50
    
    def can_trigger(self, context: TriggerContext) -> bool:
        """Check if Lady Light is offsite.
        
        Args:
            context: Trigger context with party composition
            
        Returns:
            True if Lady Light is offsite, False otherwise
        """
        # Check if owner (Lady Light) is in offsite list
        if context.owner_stats in context.offsite_allies:
            return True
        
        return False
    
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Execute healing for all party members.
        
        Args:
            context: Trigger context with party and stats
            
        Returns:
            Dictionary containing:
                - healed: list of (character_id, heal_amount) tuples
                - total_healing: sum of all healing done
        """
        from typing import Any
        
        # Calculate heal amount based on Lady Light's regain
        base_heal = int(context.owner_stats.regain * self.heal_multiplier)
        
        healed_targets = []
        total_healing = 0
        
        # Heal all allies (onsite + offsite)
        for ally_stats in context.all_allies:
            # Calculate actual healing (cannot exceed max HP)
            current_hp = ally_stats.hp
            max_hp = ally_stats.max_hp
            missing_hp = max(0, max_hp - current_hp)
            actual_heal = min(base_heal, missing_hp)
            
            if actual_heal > 0:
                ally_stats.hp += actual_heal
                # Ensure we don't exceed max HP due to floating point errors
                ally_stats.hp = min(ally_stats.hp, max_hp)
                
                # Track healing done
                char_id = getattr(ally_stats, 'character_id', 'unknown')
                healed_targets.append((char_id, actual_heal))
                total_healing += actual_heal
        
        return {
            "healed": healed_targets,
            "total_healing": total_healing,
            "base_heal_amount": base_heal,
        }
```

### Update `passives/implementations/__init__.py`

```python
"""Passive ability implementations"""

from endless_idler.passives.implementations.lady_light_radiant_aegis import LadyLightRadiantAegis

__all__ = [
    "LadyLightRadiantAegis",
]
```

## Technical Considerations

1. **Character Identification**: The Stats object may not have a character_id field. Consider:
   - Adding character_id to Stats class, OR
   - Passing character_id through TriggerContext, OR
   - Using a fallback like 'unknown' for logging

2. **Heal Amount Type**: Use `int` for heal amounts to match HP type

3. **Overheal Prevention**: Ensure heals never push HP above max_hp

4. **Performance**: Iterating all allies once per turn should be acceptable

5. **Edge Cases**:
   - Lady Light is dead but offsite → should still trigger? (decision needed)
   - Empty party → no-op
   - Lady Light heals herself while offsite → allowed

## Testing Strategy

### Unit Test Scenarios

```python
# Test 1: Lady Light offsite, allies damaged
lady_light = create_stats(hp=1000, max_hp=1000, regain=200)
ally1 = create_stats(hp=500, max_hp=1000)
ally2 = create_stats(hp=800, max_hp=1000)

context = TriggerContext(
    trigger=PassiveTrigger.TURN_START,
    owner_stats=lady_light,
    all_allies=[lady_light, ally1, ally2],
    onsite_allies=[ally1, ally2],
    offsite_allies=[lady_light],
    enemies=[],
    extra={},
)

passive = LadyLightRadiantAegis()
assert passive.can_trigger(context) == True

result = passive.execute(context)
# Expected heal: 200 * 0.50 = 100
assert ally1.hp == 600  # 500 + 100
assert ally2.hp == 900  # 800 + 100

# Test 2: Lady Light onsite, should not trigger
context.onsite_allies = [lady_light, ally1, ally2]
context.offsite_allies = []
assert passive.can_trigger(context) == False

# Test 3: Overheal prevention
ally3 = create_stats(hp=980, max_hp=1000)
context = TriggerContext(
    trigger=PassiveTrigger.TURN_START,
    owner_stats=lady_light,
    all_allies=[ally3],
    onsite_allies=[],
    offsite_allies=[lady_light],
    enemies=[],
    extra={},
)
result = passive.execute(context)
assert ally3.hp == 1000  # Capped at max
assert result["healed"][0][1] == 20  # Only 20 HP was actually healed
```

## Acceptance Criteria

- [ ] File created at correct path
- [ ] Passive registered with decorator
- [ ] `can_trigger()` correctly checks if Lady Light is offsite
- [ ] `execute()` heals all allies (onsite + offsite)
- [ ] Healing based on Lady Light's regain stat
- [ ] Healing capped at max HP
- [ ] Returns result dictionary with healing details
- [ ] Code passes linting
- [ ] All methods have docstrings
- [ ] Imports work correctly

## Integration Notes

This passive will be automatically loaded when:
1. Character metadata extracts `"lady_light_radiant_aegis"` from Lady Light's passive list
2. The passive registry is queried with this ID
3. Combat system calls passive triggers at turn start

## Future Enhancements

Consider adding:
- Visual feedback for healing (combat log entry)
- Scaling with Lady Light's level or stars
- Option to increase/decrease heal_multiplier
- Trigger on additional events (e.g., Lady Light taking damage)

## Related Files

- `endless_idler/passives/base.py` - Base class
- `endless_idler/passives/registry.py` - Registration system
- `endless_idler/characters/lady_light.py` - Character definition
- Future: Combat integration file (task 1f19c441)
