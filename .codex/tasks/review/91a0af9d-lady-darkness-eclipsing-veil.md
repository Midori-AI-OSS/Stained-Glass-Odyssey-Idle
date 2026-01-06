# Task: Implement Lady Darkness Eclipsing Veil Passive

**ID**: 91a0af9d  
**Parent**: 7437c51e-passive-system-overview  
**Priority**: High  
**Complexity**: Medium  
**Assigned Mode**: Coder  
**Dependencies**: 1e4e2d6b (base infrastructure), b243ccf7 (metadata extraction)

## Objective

Implement the `lady_darkness_eclipsing_veil` passive ability that amplifies Lady Darkness's damage and ignores enemy defense.

## Passive Specification

**Name**: Eclipsing Veil  
**ID**: `lady_darkness_eclipsing_veil`  
**Owner**: Lady Darkness  
**Trigger**: `PRE_DAMAGE` (before damage calculation)  
**Condition**: Always active when Lady Darkness attacks  
**Effect**:
- Deal 2x base damage
- Ignore 50% of target's defense

### Damage Modification

This passive modifies the damage calculation formula:

**Normal damage**:
```
damage = (atk - target_defense) * [other multipliers]
```

**With Eclipsing Veil**:
```
effective_defense = target_defense * 0.50  # Ignore 50% of defense
damage = (atk - effective_defense) * 2.0 * [other multipliers]
```

The 2x multiplier applies to base damage (after defense reduction) but before other multipliers like crit.

## Implementation

### File: `endless_idler/passives/implementations/lady_darkness_eclipsing_veil.py`

```python
"""Lady Darkness's Eclipsing Veil passive ability"""

from endless_idler.passives.base import Passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext
from endless_idler.passives.registry import register_passive


@register_passive
class LadyDarknessEclipsingVeil(Passive):
    """Lady Darkness deals increased damage and ignores enemy defense.
    
    Passive Effect:
    - Triggers before damage calculation
    - Always active when Lady Darkness attacks
    - Deals 2x base damage
    - Ignores 50% of target's defense
    
    This is a powerful offensive passive that makes Lady Darkness
    extremely effective against high-defense enemies.
    """
    
    def __init__(self):
        super().__init__()
        self.id = "lady_darkness_eclipsing_veil"
        self.display_name = "Eclipsing Veil"
        self.description = (
            "Lady Darkness always deals 2x base damage and ignores 50% of "
            "the target's defense when attacking."
        )
        self.triggers = [PassiveTrigger.PRE_DAMAGE]
        self.damage_multiplier = 2.0
        self.defense_ignore = 0.50
    
    def can_trigger(self, context: TriggerContext) -> bool:
        """Always returns True when Lady Darkness attacks.
        
        Args:
            context: Trigger context with attack information
            
        Returns:
            True if this is a damage event with Lady Darkness as attacker
        """
        # Check if owner is the attacker
        attacker = context.extra.get("attacker")
        if attacker is None:
            return False
        
        # Verify the attacker is the owner of this passive
        return attacker == context.owner_stats
    
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        """Modify damage calculation to apply passive effects.
        
        Args:
            context: Trigger context with damage calculation data
            
        Returns:
            Dictionary containing damage modifiers:
                - damage_multiplier: float (2.0)
                - defense_ignore: float (0.50)
                - original_defense: int (for logging)
                - effective_defense: int (for logging)
        """
        from typing import Any
        
        target = context.extra.get("target")
        if target is None:
            return {
                "damage_multiplier": 1.0,
                "defense_ignore": 0.0,
            }
        
        original_defense = target.defense
        effective_defense = int(original_defense * (1.0 - self.defense_ignore))
        
        return {
            "damage_multiplier": self.damage_multiplier,
            "defense_ignore": self.defense_ignore,
            "original_defense": original_defense,
            "effective_defense": effective_defense,
        }
```

### Update `passives/implementations/__init__.py`

```python
"""Passive ability implementations"""

from endless_idler.passives.implementations.lady_light_radiant_aegis import LadyLightRadiantAegis
from endless_idler.passives.implementations.lady_darkness_eclipsing_veil import LadyDarknessEclipsingVeil

__all__ = [
    "LadyLightRadiantAegis",
    "LadyDarknessEclipsingVeil",
]
```

## Technical Considerations

1. **Integration with Damage Calculation**: The combat system will need to:
   - Call passive PRE_DAMAGE triggers before calculating damage
   - Apply defense_ignore to reduce target defense
   - Apply damage_multiplier to the result
   - Order of operations matters!

2. **Defense Calculation**:
   ```python
   # In combat damage calculation:
   effective_defense = target.defense
   
   # Apply defense ignore from passives
   for passive_result in pre_damage_passives:
       if "defense_ignore" in passive_result:
           effective_defense *= (1.0 - passive_result["defense_ignore"])
   
   # Calculate base damage
   base_damage = max(0, attacker.atk - effective_defense)
   
   # Apply damage multiplier from passives
   for passive_result in pre_damage_passives:
       if "damage_multiplier" in passive_result:
           base_damage *= passive_result["damage_multiplier"]
   ```

3. **Stacking Behavior**: If multiple defense-ignore or damage-multiplier effects exist:
   - Defense ignore: Multiplicative (50% + 50% = 75% total ignore)
   - Damage multiplier: Multiplicative (2x * 1.5x = 3x total)

4. **Edge Cases**:
   - Target with 0 defense → still gets 2x damage
   - Target with very high defense → significant benefit from defense ignore
   - Lady Darkness attacking herself (somehow?) → passive still applies

## Testing Strategy

### Unit Test Scenarios

```python
# Test 1: Basic damage amplification
lady_darkness = create_stats(atk=1000)
enemy = create_stats(defense=200, hp=1000)

context = TriggerContext(
    trigger=PassiveTrigger.PRE_DAMAGE,
    owner_stats=lady_darkness,
    all_allies=[lady_darkness],
    onsite_allies=[lady_darkness],
    offsite_allies=[],
    enemies=[enemy],
    extra={
        "attacker": lady_darkness,
        "target": enemy,
    },
)

passive = LadyDarknessEclipsingVeil()
assert passive.can_trigger(context) == True

result = passive.execute(context)
assert result["damage_multiplier"] == 2.0
assert result["defense_ignore"] == 0.50
assert result["effective_defense"] == 100  # 200 * 0.50

# Expected damage calculation:
# base = 1000 - 100 = 900
# final = 900 * 2.0 = 1800

# Test 2: High defense enemy
enemy_tank = create_stats(defense=800, hp=3000)
context.extra["target"] = enemy_tank
result = passive.execute(context)
assert result["effective_defense"] == 400  # 800 * 0.50

# Expected:
# base = 1000 - 400 = 600
# final = 600 * 2.0 = 1200

# Test 3: Not Lady Darkness attacking
other_character = create_stats(atk=500)
context.extra["attacker"] = other_character
assert passive.can_trigger(context) == False
```

### Integration Test

Once integrated with combat:
```python
# Lady Darkness vs high-defense enemy
# Should bypass defense and deal significant damage
# Compare to same attack without passive
```

## Acceptance Criteria

- [ ] File created at correct path
- [ ] Passive registered with decorator
- [ ] `can_trigger()` checks if owner is attacker
- [ ] `execute()` returns damage_multiplier and defense_ignore
- [ ] Defense ignore calculates effective_defense correctly
- [ ] Damage multiplier is 2.0
- [ ] Returns result dictionary with all required fields
- [ ] Code passes linting
- [ ] All methods have docstrings
- [ ] Imports work correctly

## Integration Notes

The combat damage calculation system will need updates (task 1f19c441) to:
1. Call PRE_DAMAGE passive triggers before calculating damage
2. Extract damage_multiplier and defense_ignore from results
3. Apply these modifiers in the correct order
4. Log the effects for debugging/UI

## Future Enhancements

Consider adding:
- Visual effect for eclipsing veil activation
- Scaling with Lady Darkness level or stats
- Different defense ignore % based on enemy type
- Additional effects (e.g., apply debuff on hit)

## Related Files

- `endless_idler/passives/base.py` - Base class
- `endless_idler/passives/registry.py` - Registration system
- `endless_idler/characters/lady_darkness.py` - Character definition
- Future: Combat damage calculation (task 1f19c441)

## Notes

This passive is straightforward but requires careful integration with damage calculation. The 2x multiplier and defense ignore make Lady Darkness a powerful damage dealer, especially against tanky enemies.
