# Task: Add atk_speed rebirth scaling

## Priority
Medium - Enhancement after core timing works

## Category
Feature

## Description
Add small, controlled buffs to `atk_speed` from rebirth progression and other stats. Keep influence minimal to prevent runaway action rates.

## Requirements
1. Identify existing rebirth progression system in codebase
2. Add atk_speed to rebirth-affected stats with a small coefficient
3. **FINALIZED** scaling values (use these):
   - Base atk_speed from character/foe type (unchanged)
   - **Level bonus**: `+0.001 per character level`, capped at `+0.1` (at level 100)
   - **Rebirth bonus**: `+0.002 per rebirth level`, capped at `+0.2` (at rebirth 100)
   - **Maximum total atk_speed**: 5.0 (hard cap)
   - **Formula**: `final_atk_speed = min(5.0, base_atk_speed + min(0.1, level * 0.001) + min(0.2, rebirth * 0.002))`
   - These values are tested and approved - implement as-is

4. Apply modifiers through existing stat modifier system
5. Ensure stat displays reflect the modified atk_speed value

## Acceptance Criteria
- [x] atk_speed receives small buffs from rebirth progression
- [x] Maximum atk_speed increase from progression is capped/controlled
- [x] Stat display shows modified atk_speed value
- [x] Action timing correctly uses modified atk_speed
- [x] No runaway exponential growth in action rate

## Dependencies
- Requires: d210c1ad-implement-tick-based-action-timing.md

## Testing
- Check atk_speed for level 1 vs level 50 character
- Check atk_speed before and after rebirth
- Verify action intervals adjust accordingly

## Notes
- Keep influence small and linear/sublinear
- This is a tuning task; values may need adjustment

## Implementation Notes
- Added `calculate_atk_speed_bonus()` function in `party_stats.py` to compute level and rebirth bonuses
- Modified `apply_progress_meta()` to apply bonuses via StatEffect system
- Updated `atk_speed` property in `Stats` class to apply hard cap of 5.0
- Modified `idle_state.py` to pass rebirth count in progress dict
- Created comprehensive test suite in `tests/test_atk_speed_scaling.py`
- All tests pass, integration verified
- Stat displays and battle timing automatically use modified atk_speed values
