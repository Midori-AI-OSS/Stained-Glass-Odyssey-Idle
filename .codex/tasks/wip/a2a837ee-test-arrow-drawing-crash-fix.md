# Test Arrow Drawing Crash Fix

**Priority:** High  
**Status:** New  
**Category:** Testing  
**Task ID:** a2a837ee  
**Date Created:** 2026-01-11

## Problem Statement

After implementing fixes for the arrow drawing crash (tasks 1eeea699 and 45379ecc), comprehensive testing is needed to verify the fixes work correctly and arrows still render properly.

## Objective

Verify that the arrow drawing crash is fixed and that all arrow rendering scenarios work correctly without errors.

## Implementation Requirements

### Prerequisites
- Task 1eeea699 must be completed (safe defaults for control points)
- Task 45379ecc must be completed (QPainter always ends)

### Test Scenarios

1. **Normal Combat Entry**
   - Start the game with: `uv run python main.py`
   - Enter combat through normal gameplay
   - Verify arrows render without errors
   - Check console for any UnboundLocalError or Qt warnings
   - Look for: "QPainter::begin: Paint device returned engine == 0" or similar warnings

2. **Specific Bug Trigger - Same Team Healing with Provided Midpoint**
   - This is the exact scenario that was crashing
   - When pulse.same_team=True AND pulse.midpoint is not None
   - Previously caused: `UnboundLocalError: waypoint_x is referenced before assignment` at line 503
   - After fix: Arrow should render correctly using the provided midpoint

3. **Various Combat Formations**
   - Test different party formations
   - Test different enemy formations  
   - Test same-team abilities (healing, buffs) that use curved arrows
   - Test cross-team attacks that use straight/curved arrows
   - Verify arrows render correctly for all positions
   - Check that arrow paths look visually correct

3. **Edge Cases**
   - Single combatant scenarios
   - Maximum combatants on field
   - Rapid combat transitions (enter/exit combat quickly)
   - Different screen resolutions/window sizes
   - Minimize and restore window during combat
   - Pulse animations with wrong_target set (4-segment animation)
   - Pulse animations without wrong_target (normal 2-segment animation)

4. **Error Scenarios (Previously Crashing)**
   - Trigger same-team healing abilities with combat midpoint set
   - This was the exact crashing condition (pulse.same_team=True with pulse.midpoint set)
   - Verify no UnboundLocalError occurs
   - Verify no Qt painter warnings: "QPainter::begin: Paint device returned engine == 0"
   - Confirm game continues to function normally
   - Check that subsequent paint events still work (painter state not corrupted)

5. **Visual Validation**
   - Arrows should connect source to target
   - Arrow curves should be smooth and natural
   - Combat midpoints should be used when available
   - Fallback midpoints should work when combat midpoint unavailable

## Testing Checklist

Execute each test and document results:

- [ ] Enter combat - no errors
- [ ] Arrows visible and rendering
- [ ] No UnboundLocalError in console
- [ ] No Qt painter warnings in console
- [ ] Test formation A (describe formation)
- [ ] Test formation B (describe formation)
- [ ] Single combatant works
- [ ] Maximum combatants works
- [ ] Rapid combat entry/exit works
- [ ] Different window sizes work
- [ ] Previously crashing scenario now works
- [ ] Arrow visual appearance is correct
- [ ] Game performance is acceptable

## Success Criteria

- [ ] All acceptance checks from original issue pass:
  - Run the game and enter combat
  - Trigger the arrow rendering conditions that previously crashed
  - Confirm there is no UnboundLocalError
  - Confirm the Qt painter warnings no longer occur during normal play
  - Confirm arrows still render
- [ ] No regression in arrow rendering quality
- [ ] No new bugs introduced
- [ ] Game remains playable and stable

## Reporting

Document test results including:
- Environment (OS, Python version via `python --version`, Qt version)
- Python version used: Check with `uv run python --version`
- PySide6 version: Check with `uv run python -c "import PySide6; print(PySide6.__version__)"`
- Each test scenario result (pass/fail with details)
- Any unexpected behavior
- Screenshots of arrow rendering if applicable (especially for visual regressions)
- Console output from test runs (capture any warnings or errors)
- Specific reproduction steps for any failures found

**Test Results Template:**
```
Environment:
- OS: [Linux/Windows/Mac]
- Python: [version]
- PySide6: [version]

Test Results:
1. Normal Combat Entry: [PASS/FAIL] - [notes]
2. Same-team healing with midpoint: [PASS/FAIL] - [notes]
3. Various formations: [PASS/FAIL] - [notes]
...
```

## Notes

- This is part 3 of fixing the arrow drawing crash
- Depends on completion of tasks 1eeea699 and 45379ecc
- If any test fails, create follow-up tasks with specific fixes needed
- Update `.codex/implementation/` docs if arrow rendering behavior changed
