# Task: Integrate Passive System with Combat

**ID**: 1f19c441  
**Parent**: 7437c51e-passive-system-overview  
**Priority**: Critical  
**Complexity**: High  
**Assigned Mode**: Coder  
**Dependencies**: All previous tasks (1e4e2d6b, b243ccf7, 04f7b1f9, 91a0af9d, cea883a7)

## Objective

Integrate the passive system with the combat/turn execution system so that passives are loaded, triggered at appropriate times, and their effects are applied to combat calculations.

## Integration Points

### 1. Load Passives from Character Metadata

When characters are initialized, their passives need to be loaded and stored.

**Location**: Wherever character Stats are created from character plugins  
**Action**: Load passive instances and attach to Stats

```python
# In character initialization code
from endless_idler.passives.registry import load_passive

# After extracting metadata
char_id, display_name, stars, placement, damage_type_id, damage_type_random, base_stats, base_aggro, damage_reduction_passes, passive_ids = extract_character_metadata(path)

# Create Stats object
stats = Stats()
stats.passives = passive_ids  # Store passive IDs

# Load passive instances
loaded_passives = []
for passive_id in passive_ids:
    passive = load_passive(passive_id)
    if passive:
        loaded_passives.append(passive)

# Store loaded passives on Stats (may need to add field)
stats._passive_instances = loaded_passives
```

**Consideration**: Stats class may need a new field to store passive instances:
```python
# In endless_idler/combat/stats.py
_passive_instances: list[Any] = field(default_factory=list, init=False)
```

### 2. Add Character ID to Stats

Passives need to identify which character they belong to. Add character_id field:

```python
# In endless_idler/combat/stats.py
character_id: str = ""  # Add near top of Stats class
```

Update character creation code to set this:
```python
stats.character_id = char_id
```

### 3. Trigger Passives in Combat Turn Loop

**Location**: Find the main combat/turn execution code  
**Action**: Add passive trigger calls at appropriate points

```python
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext

# At turn start
def execute_turn_start(party: list[Stats], reserves: list[Stats], enemies: list[Stats]):
    """Execute turn start phase"""
    
    all_allies = party + reserves
    
    # Trigger TURN_START passives for all allies
    for ally in all_allies:
        for passive in ally._passive_instances:
            if PassiveTrigger.TURN_START in passive.triggers:
                context = TriggerContext(
                    trigger=PassiveTrigger.TURN_START,
                    owner_stats=ally,
                    all_allies=all_allies,
                    onsite_allies=party,
                    offsite_allies=reserves,
                    enemies=enemies,
                    extra={},
                )
                
                if passive.can_trigger(context):
                    result = passive.execute(context)
                    # Log or handle result
                    log_passive_effect(passive, result)
```

### 4. Integrate with Damage Calculation

**Location**: Damage calculation function  
**Action**: Trigger PRE_DAMAGE passives and apply modifiers

```python
def calculate_damage(attacker: Stats, target: Stats, all_allies: list[Stats], onsite: list[Stats], offsite: list[Stats], enemies: list[Stats]) -> int:
    """Calculate damage with passive effects"""
    
    # Trigger PRE_DAMAGE passives
    damage_multiplier = 1.0
    defense_ignore = 0.0
    
    for passive in attacker._passive_instances:
        if PassiveTrigger.PRE_DAMAGE in passive.triggers:
            context = TriggerContext(
                trigger=PassiveTrigger.PRE_DAMAGE,
                owner_stats=attacker,
                all_allies=all_allies,
                onsite_allies=onsite,
                offsite_allies=offsite,
                enemies=enemies,
                extra={
                    "attacker": attacker,
                    "target": target,
                },
            )
            
            if passive.can_trigger(context):
                result = passive.execute(context)
                
                # Apply damage modifiers
                if "damage_multiplier" in result:
                    damage_multiplier *= result["damage_multiplier"]
                
                if "defense_ignore" in result:
                    defense_ignore += result["defense_ignore"]
    
    # Calculate effective defense
    effective_defense = int(target.defense * (1.0 - min(1.0, defense_ignore)))
    
    # Calculate base damage
    base_damage = max(0, attacker.atk - effective_defense)
    
    # Apply damage multiplier
    final_damage = int(base_damage * damage_multiplier)
    
    return final_damage
```

### 5. Integrate with Target Selection

**Location**: Enemy targeting/selection logic  
**Action**: Trigger TARGET_SELECTION passives to allow redirection

```python
def select_target(attacker: Stats, available_targets: list[Stats], all_allies: list[Stats], onsite: list[Stats], offsite: list[Stats], enemies: list[Stats]) -> Stats:
    """Select a target, allowing passive redirection"""
    
    # Initial target selection (e.g., highest aggro, random, etc.)
    original_target = _select_initial_target(available_targets)
    
    # Trigger TARGET_SELECTION passives for all allies
    new_target = original_target
    
    for ally in all_allies:
        for passive in ally._passive_instances:
            if PassiveTrigger.TARGET_SELECTION in passive.triggers:
                context = TriggerContext(
                    trigger=PassiveTrigger.TARGET_SELECTION,
                    owner_stats=ally,
                    all_allies=all_allies,
                    onsite_allies=onsite,
                    offsite_allies=offsite,
                    enemies=enemies,
                    extra={
                        "attacker": attacker,
                        "original_target": original_target,
                    },
                )
                
                if passive.can_trigger(context):
                    result = passive.execute(context)
                    
                    # Check for target redirection
                    if "new_target" in context.extra:
                        new_target = context.extra["new_target"]
                        # Log redirection
                        log_target_redirection(original_target, new_target, passive)
    
    return new_target
```

### 6. Integrate with Healing Calculations

**Location**: Healing/regen logic  
**Action**: Check for healing multipliers from passives

```python
def apply_healing(healer: Stats, target: Stats, base_heal: int, all_allies: list[Stats]) -> int:
    """Apply healing with passive bonuses"""
    
    healing_multiplier = 1.0
    
    # Check healer's passives for healing bonuses
    # (e.g., from Trinity Synergy)
    for passive in healer._passive_instances:
        # Check if passive has set a healing multiplier in turn_start
        # This would be stored somewhere accessible, maybe on the Stats object
        pass
    
    # Apply multiplier
    final_heal = int(base_heal * healing_multiplier)
    
    # Apply heal to target
    target.hp = min(target.max_hp, target.hp + final_heal)
    
    return final_heal
```

**Note**: Healing multipliers from Trinity Synergy are set during TURN_START. Consider storing them on the Stats object or in a combat state manager.

## Required Changes by File

### `endless_idler/combat/stats.py`

```python
# Add these fields to Stats class:

character_id: str = ""  # Near top with other basic fields

_passive_instances: list[Any] = field(default_factory=list, init=False)  # Near bottom
```

### Character Loading Code

Find where characters are instantiated and Stats objects created. Update to:
1. Extract passive IDs from metadata
2. Set character_id on Stats
3. Load passive instances
4. Store instances on Stats

### Combat/Turn Execution Code

Find the main combat loop. Add passive triggers at:
- **Turn start**: TURN_START passives
- **Before damage**: PRE_DAMAGE passives
- **After damage**: POST_DAMAGE passives (if implemented)
- **Target selection**: TARGET_SELECTION passives
- **Before healing**: PRE_HEAL passives (if implemented)

### Logging/UI

Consider adding combat log entries for passive effects:
```python
def log_passive_effect(passive: PassiveBase, result: dict[str, Any]):
    """Log passive activation to combat log"""
    print(f"[PASSIVE] {passive.display_name}: {result}")
```

## Testing Strategy

### Integration Tests

1. **Lady Light Radiant Aegis**:
   - Put Lady Light offsite
   - Run combat turn
   - Verify all allies are healed

2. **Lady Darkness Eclipsing Veil**:
   - Lady Darkness attacks high-defense enemy
   - Verify damage is 2x and defense is reduced

3. **Trinity Synergy**:
   - Add all three characters to party
   - Verify Lady Light regain boost
   - Verify Lady Darkness damage boost
   - Verify attacks redirect to Persona

4. **Multiple Passives**:
   - Test character with multiple passives
   - Verify all trigger correctly

5. **Edge Cases**:
   - Character with invalid passive ID → gracefully skip
   - Passive returns None or malformed data → handle safely
   - Character dies mid-combat → passive stops triggering

### Manual Testing Checklist

- [ ] Passives load correctly at character initialization
- [ ] Turn start passives trigger each turn
- [ ] Pre-damage passives modify damage calculations
- [ ] Target selection passives redirect attacks
- [ ] Multiple characters with same passive work correctly
- [ ] Combat log shows passive activations
- [ ] No crashes or errors with passives active
- [ ] Performance is acceptable with multiple passives

## Technical Considerations

1. **Performance**: 
   - Triggering passives adds overhead to combat loop
   - Consider caching passive instances
   - Profile performance with many characters

2. **Order of Operations**:
   - Multiple passives of same type: apply in order added
   - Multiplicative effects stack multiplicatively
   - Additive effects stack additively

3. **State Management**:
   - Some passive effects (like Trinity Synergy multipliers) need to persist across triggers
   - Consider a combat state manager or store on Stats

4. **Error Handling**:
   - Passive execution failures should not crash combat
   - Log errors but continue combat loop

5. **Extensibility**:
   - Make it easy to add new trigger points
   - Document how to add new passives

## Acceptance Criteria

- [ ] Stats class has character_id and _passive_instances fields
- [ ] Passive instances loaded when characters created
- [ ] TURN_START passives trigger at turn start
- [ ] PRE_DAMAGE passives modify damage calculation
- [ ] TARGET_SELECTION passives can redirect attacks
- [ ] All three implemented passives work correctly
- [ ] Combat log shows passive activations
- [ ] No regressions in existing combat behavior
- [ ] Code passes linting
- [ ] Integration tests pass

## Documentation

Create or update `.codex/implementation/passive-system.md` with:
- Overview of passive system architecture
- How to add new passives
- How to add new trigger points
- Examples of each passive type
- Troubleshooting guide

## Related Files

- `endless_idler/combat/stats.py` - Add fields
- `endless_idler/characters/plugins.py` - Likely handles character loading
- Combat/turn execution files - Add triggers
- Damage calculation files - Add PRE_DAMAGE integration
- Target selection files - Add TARGET_SELECTION integration

## Notes

This is the most complex integration task. Start by:
1. Adding fields to Stats
2. Loading passives at character creation
3. Adding one trigger point (TURN_START) as proof of concept
4. Then add remaining trigger points
5. Test each passive individually
6. Test all passives together

Take time to understand the existing combat flow before making changes. Consider running existing tests (if any) before and after to catch regressions.

## Future Enhancements

- Add POST_DAMAGE, PRE_HEAL, POST_HEAL triggers
- Add DEATH trigger for passive effects on death
- Add ABILITY_USED trigger for skill-based passives
- Create visual effects for passive activations
- Add passive management UI
- Allow enabling/disabling specific passives
