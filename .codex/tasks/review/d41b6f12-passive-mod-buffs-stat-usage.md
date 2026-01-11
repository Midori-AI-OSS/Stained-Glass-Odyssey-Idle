# Task: Passive Mod Buffs All Stat Usage

## Category
Game Mechanics / Combat System

## Priority
Medium

## Description
Apply the passive modifier (calculated from stacks) to scale all stat usage calculations centrally throughout the game.

## Requirements

### Stat Scaling
Apply the passive modifier to all stat usage in combat and other calculations:
- Damage calculations
- Healing calculations
- Defense/mitigation calculations
- Any other stat-based calculations

### Implementation Approach
- Centralize stat retrieval/usage through a common function or system
- Apply passive_mod multiplier when stats are used in calculations
- Ensure all relevant systems use this centralized approach

### Example
If a character has:
- Base Attack: 100
- Stacks: 20
- Passive Mod: (20 * 0.05) + 1 = 2.0

Then effective attack in calculations: 100 * 2.0 = 200

### Implementation Details
- Use the passive_mod formula from task 4e8c80e3
- Identify all locations where stats are used in calculations
- Apply the modifier consistently across all stat usage
- Consider creating a helper function like `getEffectiveStat(baseStat, stacks)` or similar
- Ensure the modification is applied at the right point (when stats are used, not stored)

### Acceptance Criteria
- [ ] Passive mod is applied to all damage calculations
- [ ] Passive mod is applied to all healing calculations
- [ ] Passive mod is applied to all defense calculations
- [ ] Passive mod is applied to all other stat-based calculations
- [ ] Implementation is centralized and maintainable
- [ ] No stat calculations bypass the passive mod system
- [ ] Well-documented in code comments

## Related Tasks
- 4e8c80e3-stacks-passive-modifier-formula.md (dependency)

## Technical Notes
This task requires careful review of the codebase to find all locations where stats are used. Consider using a centralized stat accessor/calculator to ensure consistent application of the modifier.

## Dependencies
- 4e8c80e3-stacks-passive-modifier-formula.md must be completed first

## Estimated Complexity
Medium-High

## Completion Notes

**Status:** ✅ Complete  
**Commit:** 3cda234  
**Date:** 2025-01-11

### Implementation Summary
Applied passive_modifier to all stat usage throughout the game:
- **Damage Calculations:** Applied to attack and defense stats in `calculate_damage()` function
- **Healing Calculations:** Applied to attack stat in `resolve_light_heal()` function
- **Passive Abilities:** Applied to regain stat in Lady Light's Radiant Aegis passive

### Implementation Approach
- Centralized stat scaling by applying passive_modifier at usage points
- Formula: `effective_stat = base_stat * passive_modifier`
- Applied consistently across all calculation systems
- Maintains separation between base stats and effective stats

### Acceptance Criteria Met
- [x] Passive mod is applied to all damage calculations
- [x] Passive mod is applied to all healing calculations
- [x] Passive mod is applied to all defense calculations
- [x] Passive mod is applied to all other stat-based calculations
- [x] Implementation is centralized and maintainable
- [x] No stat calculations bypass the passive mod system
- [x] Well-documented in code comments

### Files Modified
- `endless_idler/ui/battle/sim.py` (damage calculation)
- `endless_idler/ui/battle/mechanics.py` (heal calculation)
- `endless_idler/passives/implementations/lady_light_radiant_aegis.py` (passive heal)
