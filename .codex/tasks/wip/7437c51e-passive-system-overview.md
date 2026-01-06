# Passive System Implementation - Master Overview

**Created**: 2024-01-06  
**Priority**: High  
**Estimated Complexity**: Large (Multi-phase implementation)

## Context

Characters already declare passives in their class definitions (e.g., `passives: list[str] = field(default_factory=lambda: ["lady_light_radiant_aegis"])`), and the `Stats` class has a `passives: list[str]` field. However:
- No passive implementation or execution system exists
- The metadata extraction in `characters/metadata.py` doesn't parse passive IDs
- No passive module structure exists

## Objective

Implement a complete passive system that:
1. Extracts passive IDs from character files during metadata parsing
2. Provides a modular folder structure for passive implementations
3. Implements three specific passives with complex behaviors
4. Integrates with the combat/turn system to trigger passive effects

## Architecture Overview

### File Structure
```
endless_idler/
├── passives/
│   ├── __init__.py              # Module initialization, passive registry
│   ├── base.py                  # Base passive class/protocol
│   ├── registry.py              # Passive registration and loading
│   ├── triggers.py              # Event trigger definitions (turn_start, turn_end, etc.)
│   └── implementations/
│       ├── __init__.py
│       ├── lady_light_radiant_aegis.py
│       ├── lady_darkness_eclipsing_veil.py
│       └── trinity_synergy.py
└── characters/
    └── metadata.py              # Extended to extract passives
```

### Passive System Components

1. **Base Passive Protocol** (`passives/base.py`)
   - Defines the interface all passives must implement
   - Includes hooks for different trigger points
   - Provides access to character stats, party composition, and combat state

2. **Passive Registry** (`passives/registry.py`)
   - Dynamic loading of passive implementations
   - Maps passive IDs to implementation classes
   - Handles passive instantiation with character context

3. **Trigger System** (`passives/triggers.py`)
   - Defines when passives can activate (turn_start, turn_end, pre_damage, post_damage, etc.)
   - Provides event data structures for passing context to passives

4. **Metadata Extension** (`characters/metadata.py`)
   - Add AST parsing to extract `passives: list[str]` from character classes
   - Return passive IDs alongside other character metadata

## Passive Specifications

### 1. Lady Light Radiant Aegis
**ID**: `lady_light_radiant_aegis`  
**Trigger**: Every turn (turn_start)  
**Condition**: Lady Light is offsite (not in active combat party)  
**Effect**: Heal all characters (onsite + offsite) for a percentage of Lady Light's regain stat

### 2. Lady Darkness Eclipsing Veil
**ID**: `lady_darkness_eclipsing_veil`  
**Trigger**: Pre-damage calculation  
**Condition**: Always active when Lady Darkness attacks  
**Effect**:
- Deal 2x base damage
- Ignore 50% of target's defense

### 3. Trinity Synergy
**ID**: `trinity_synergy`  
**Trigger**: Multiple (turn_start for stat boosts, target_selection for redirection)  
**Condition**: All three characters in party (any placement):
  - Lady Darkness
  - Lady Light
  - Persona Light and Dark
**Effects**:
- **Lady Light**: 15x regain multiplier, 4x healing output
- **Lady Darkness**: 2x damage output, allies take 1/2 damage from darkness bleed
- **Persona Light and Dark**: Redirect all attacks targeting Lady Darkness to Persona instead

## Task Breakdown

This overview links to individual implementation tasks:

1. **[Task 1e4e2d6b]** - Create passive base infrastructure (base.py, triggers.py, registry.py)
2. **[Task b243ccf7]** - Extend metadata.py to extract passive IDs
3. **[Task 04f7b1f9]** - Implement lady_light_radiant_aegis passive
4. **[Task 91a0af9d]** - Implement lady_darkness_eclipsing_veil passive
5. **[Task cea883a7]** - Implement trinity_synergy passive
6. **[Task 1f19c441]** - Integrate passive system with combat/turn execution

## Dependencies

```
Task 1e4e2d6b (Base Infrastructure)
     ↓
Task b243ccf7 (Metadata Extraction) ← Can run in parallel with base
     ↓
Task 04f7b1f9 (Lady Light Passive) ← Depends on base + metadata
Task 91a0af9d (Lady Darkness Passive) ← Depends on base + metadata  
Task cea883a7 (Trinity Synergy) ← Depends on base + metadata
     ↓
Task 1f19c441 (Combat Integration) ← Depends on all passive implementations
```

## Agent Assignment Strategy

- **Tasks 1e4e2d6b, b243ccf7**: **Coder** - Foundation work, straightforward implementation
- **Tasks 04f7b1f9, 91a0af9d, cea883a7**: **Coder** - Passive implementations following base protocol
- **Task 1f19c441**: **Coder** - Integration work with existing combat system
- **All tasks**: **Auditor** - Review after completion, verify correctness

## Success Criteria

- [ ] All passive IDs are extracted from character metadata
- [ ] Passives can be loaded dynamically from the registry
- [ ] All three specified passives are implemented and functional
- [ ] Passive effects trigger at appropriate points in combat
- [ ] No breaking changes to existing character or combat code
- [ ] Code follows repository standards (linting, documentation, etc.)

## Notes

- The passive system should be extensible for future passive additions
- Consider how passives interact with save/load system
- Performance: Passives should not significantly slow combat simulation
- The trinity_synergy passive is the most complex, requiring party composition checks and multiple effect types

## References

- `endless_idler/characters/metadata.py` - Current metadata extraction
- `endless_idler/combat/stats.py` - Stats class with passives field
- `endless_idler/characters/lady_light.py` - Example passive declaration
- `endless_idler/combat/party_stats.py` - Party and placement handling
