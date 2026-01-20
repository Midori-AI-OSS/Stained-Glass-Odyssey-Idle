# Task: Rename speed stat to atk_speed

## Priority
High - Foundation for timing refactor

## Category
Refactor

## Description
Rename the `spd` stat to `atk_speed` throughout the codebase. This is a foundational change for the new tick-based action timing system.

## Requirements
1. In `endless_idler/combat/stats.py`:
   - Rename `_base_spd` to `_base_atk_speed`
   - Rename the `spd` property to `atk_speed`
   - Update property getter and setter accordingly
   
2. Update all references to `spd` or `speed` stat in:
   - Character plugins
   - Combat calculations
   - UI displays
   - Any stat modifiers or effects

3. Update baselines:
   - Player characters: `_base_atk_speed = 1` (changed from 2)
   - Foes: `_base_atk_speed = 2` (keep as is)

## Acceptance Criteria
- [ ] `_base_spd` is renamed to `_base_atk_speed` in Stats class
- [ ] `spd` property is renamed to `atk_speed` 
- [ ] All references throughout codebase are updated
- [ ] Player character baseline is 1
- [ ] Foe baseline is 2
- [ ] No references to old `spd` remain (verify with grep)

## Testing
- Run the game and verify stat displays show "atk_speed" or appropriate label
- Check that character stats are accessible and functional

## Notes
- This is a pure rename; do not change any calculation logic yet
- The tick-based timing implementation comes in a separate task
