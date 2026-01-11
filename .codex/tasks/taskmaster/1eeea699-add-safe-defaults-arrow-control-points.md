# Add Safe Defaults for Arrow Control Points

**Priority:** High  
**Status:** New  
**Category:** Bug Fix  
**Task ID:** 1eeea699  
**Date Created:** 2026-01-11

## Problem Statement

The battle widget crashes during painting with `UnboundLocalError: waypoint_x is referenced before assignment`. This occurs because waypoint_x, waypoint_y, and related control point variables are not always defined before they are used in arrow rendering Bezier calculations.

## Objective

Ensure all arrow control point variables (waypoint_x, waypoint_y, second_mid_x, second_mid_y) are always defined before Bezier calculations in the paintEvent method.

## Implementation Requirements

### File to Modify
- `endless_idler/ui/battle/widgets.py`

### Specific Changes

**EXACT LOCATION OF BUG:**
- Lines 503-504 use `waypoint_x` and `waypoint_y` variables in Bezier calculation
- These variables are ONLY defined in the `else` block (lines 481-483)
- When `pulse.midpoint is not None` (line 477-478), only `waypoint` QPointF object is created
- This causes UnboundLocalError when the if-branch is taken

**THE FIX:**
1. **Locate the same_team arrow rendering section** (lines 473-506)
   - This is the `if pulse.same_team:` block in the paintEvent method
   - Currently at lines 473-518 in widgets.py

2. **Add waypoint_x and waypoint_y extraction after waypoint is defined** (after line 483)
   - Insert these lines after the if/else block that sets `waypoint`:
     ```python
     # Extract x and y for use in Bezier calculations below
     waypoint_x = waypoint.x()
     waypoint_y = waypoint.y()
     ```
   - This ensures waypoint_x and waypoint_y are ALWAYS defined, regardless of which branch is taken

3. **Alternative approach: Fix the Bezier calculation directly** (lines 503-504)
   - Instead of using `waypoint_x` and `waypoint_y`, use `waypoint.x()` and `waypoint.y()`:
     ```python
     curve_end = QPointF(
         (1 - t) * (1 - t) * waypoint.x() + 2 * (1 - t) * t * second_mid_x + t * t * end.x(),
         (1 - t) * (1 - t) * waypoint.y() + 2 * (1 - t) * t * second_mid_y + t * t * end.y()
     )
     ```
   - This is cleaner since waypoint is ALWAYS defined

**RECOMMENDED:** Use the alternative approach (fixing lines 503-504) as it's cleaner and more maintainable.

## Testing

1. Run the game and enter combat
2. Trigger various arrow rendering conditions (different formations, movement patterns)
3. Confirm no UnboundLocalError occurs
4. Verify arrows still render correctly in all scenarios

## Success Criteria

- [ ] Lines 503-504 no longer reference undefined waypoint_x/waypoint_y variables
- [ ] Bezier calculation uses waypoint.x() and waypoint.y() OR waypoint_x/waypoint_y are extracted after waypoint is defined
- [ ] All arrow rendering paths work without UnboundLocalError
- [ ] Visual appearance of arrows remains correct (no visual regression)
- [ ] Test with pulse.midpoint=None (uses fallback calculation) - should work
- [ ] Test with pulse.midpoint set (uses provided midpoint) - should work (this was the crashing case)

## Notes

- This is part 1 of fixing the arrow drawing crash
- Part 2 (task 45379ecc) will ensure QPainter is always ended
- Part 3 (task a2a837ee) will test the complete fix
- Keep changes minimal and focused on variable initialization
