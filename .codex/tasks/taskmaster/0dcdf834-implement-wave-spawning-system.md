# Task: Implement wave spawning system

## Priority
High - Core battle flow

## Category
Feature

## Description
Implement wave-based foe spawning with two trigger conditions: 30-second timer or zero foes alive.

## Requirements
1. Wave trigger conditions (either triggers spawn):
   - **Timer**: 30 seconds since last wave spawn
   - **Clear**: Zero foes alive

2. Wave tracking:
   - Track time since last wave spawn
   - Track current foe count
   - Spawn new wave when either condition is met
   - Reset timer after spawning

3. Implementation:
   - Add wave spawn timer to battle state
   - Check conditions in battle update loop
   - When triggered, spawn new wave of foes
   - Do NOT delay spawning if both conditions are met

4. Spawn count:
   - Use existing baseline spawn count from game
   - Do NOT implement scaling yet (that's a separate task)
   - Log wave spawn events for debugging

## Acceptance Criteria
- [x] New wave spawns after 30 seconds
- [x] New wave spawns when foes reach zero
- [x] Timer resets after wave spawn
- [x] Both conditions work independently
- [x] Existing spawn logic is reused
- [x] Wave spawns are logged or visible

## Dependencies
- Requires: 8fd957a1-implement-foe-spawning-and-movement.md

## Testing
- Start battle, wait 30 seconds, verify new wave spawns
- Kill all foes before 30 seconds, verify immediate new wave
- Verify timer resets after each wave
- Verify waves spawn continuously

## Notes
- This task establishes the wave system foundation
- Scaling and overflow handling come in separate tasks
- Keep spawn count simple for now (baseline only)

---

## Auditor Review (Auditor Mode)

**Date**: 2025-01-19  
**Auditor**: AI Agent (Auditor Mode)  
**Status**: ✓ APPROVED

### Implementation Verified
- ✓ Wave spawning system fully implemented in `endless_idler/ui/battle/screen.py`
- ✓ Timer-based spawning (30 seconds): Lines 135-136, 365, 371
- ✓ Zero foes spawning: Lines 368, 371
- ✓ OR logic for independent conditions: Line 371
- ✓ Timer reset after spawn: Line 375
- ✓ Wave tracking and logging: Lines 134, 379, 422-423
- ✓ Baseline spawn count (5): Line 388
- ✓ Integration with main battle loop: Line 437 in `_step_battle()`

### Code Quality
- ✓ Type hints on all methods (`-> None`)
- ✓ Docstrings present and descriptive
- ✓ Clear variable names and comments
- ✓ Proper UI resource cleanup (`deleteLater()`)
- ✓ Follows repository Python conventions
- ✓ Async-friendly (no blocking operations)
- ✓ Minimal logging (single debug log per wave)

### All Acceptance Criteria Met
All 6 acceptance criteria verified in code and marked complete.

### Testing Status
⚠ No automated tests found. Testing section in task specifies manual testing scenarios, which should be verified before deployment. Automated tests not listed in acceptance criteria, so not blocking approval.

### Repository Standards Compliance
- ✓ Follows minimal documentation/logging guidelines
- ✓ No broad fallbacks
- ✓ Reuses existing systems (`build_foes()`)
- ✓ Async-friendly implementation

### Issues Found
None

### Recommendation
**APPROVED** for Task Master review. Implementation is complete, correct, and meets all requirements.
