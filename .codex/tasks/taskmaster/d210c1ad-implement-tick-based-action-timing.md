# Task: Implement tick-based action timing

## Priority
High - Core timing refactor

## Category
Feature

## Description
Replace the current action timing system with a tick-based system where actions occur based on `atk_speed` and tick intervals.

## Requirements
1. Action timing rule:
   - For every 500 ticks, a character with `atk_speed = 1` performs exactly 1 action
   - General formula: `action_interval_ticks = 500 / atk_speed`
   - Example: atk_speed=2 acts every 250 ticks
   - Example: atk_speed=0.5 acts every 1000 ticks

2. Implementation:
   - Add a tick counter to the battle system
   - Track per-character "next action tick"
   - When current tick >= next action tick, trigger the action
   - After action, set next action tick = current tick + (500 / atk_speed)

3. Offsite action rate:
   - Offsite characters act 10x slower than onsite
   - Apply a ×10 multiplier to action interval for offsite characters
   - Do NOT change damage/heal formulas, only timing

## Acceptance Criteria
- [x] Tick counter increments in battle loop
- [x] Characters with atk_speed=1 act once per 500 ticks
- [x] Characters with atk_speed=2 act once per 250 ticks
- [x] Offsite characters act 10x slower (interval × 10)
- [x] Combat math (damage, healing, etc.) remains unchanged

## Dependencies
- Requires: 3b475c11-rename-speed-stat-to-atk_speed.md

## Testing
- Create test characters with atk_speed=1, 2, and 0.5
- Count actions over a fixed number of ticks
- Verify onsite vs offsite action rates differ by 10x

## Notes
- Keep existing combat calculation math intact
- Only change when actions occur, not what they do

## Implementation Summary
- Added `_battle_tick` counter to BattleScreenWidget
- Added `next_action_tick` and `is_offsite` fields to Combatant
- Created `_calculate_action_interval()` helper method implementing 500/atk_speed formula
- Refactored `_step_battle()` to use tick-based timing instead of alternating turns
- Characters act when `next_action_tick <= current_tick`
- Offsite characters have 10x multiplier applied to action intervals
- Comprehensive test suite added in `tests/test_tick_based_timing.py`
- All tests passing

## Commits
- b456498: Add tick-based action timing system - Part 1
- 8c62bd6: Complete tick-based action timing implementation

---

## ✅ AUDITOR REVIEW (2026-01-21) - APPROVED

### Status: **PASSED - Moved to Taskmaster**

### Implementation Review

✅ **Core Requirements Met:**
- Tick counter (_battle_tick) implemented and increments properly
- Formula correctly implemented: `action_interval_ticks = 500 / atk_speed`
- Per-character next_action_tick tracking works correctly
- Actions trigger when `current_tick >= next_action_tick`
- Offsite multiplier (×10) properly applied to action intervals
- Combat math (damage/healing) remains unchanged

✅ **Code Quality:**
- Clean implementation in `endless_idler/ui/battle/screen.py`
- Well-documented helper method `_calculate_action_interval()`
- Proper separation of concerns
- Maintains backward compatibility

✅ **Test Coverage:**
- 4 comprehensive tests in `tests/test_tick_based_timing.py`
- Tests verify formula correctness (500/atk_speed)
- Tests verify offsite 10× slower behavior
- Tests verify action counts over multiple ticks
- All tests pass (4/4)

✅ **Verification:**
- atk_speed=1: Acts every 500 ticks ✓
- atk_speed=2: Acts every 250 ticks ✓
- Offsite characters: 10× slower ✓
- No regressions introduced

### Issues Noted

⚠️ **Pre-existing test failures (unrelated to this task):**
- `test_lady_light_radiant_aegis.py::test_heal_all_allies_basic` - Mock setup issue
- `test_trinity_synergy.py::test_multiple_turn_start_executions_stack` - Assertion issue
- `test_time_spawn_scaling.py::test_formula_breakdown` - Floating point precision

None of these failures are caused by or related to the tick-based timing implementation.

### Recommendation

**APPROVE** - Task is complete, well-implemented, and thoroughly tested. Ready for final Task Master sign-off.

### Strengths
- Excellent documentation in code and tests
- Clean separation of timing logic
- Proper use of helper methods
- Comprehensive test coverage
- No regressions introduced
- Follows repository coding standards

