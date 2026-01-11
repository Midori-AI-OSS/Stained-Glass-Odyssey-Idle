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

1. **Locate the arrow drawing section in paintEvent**
   - Find where arrows are rendered (around lines 362-503 based on grep results)
   - Identify all code paths that lead to Bezier calculations

2. **Add safe defaults at the start of each arrow render**
   - Before any conditional branches that might skip variable assignment
   - Default waypoint should be the combat midpoint if it exists in layout data
   - If combat midpoint is not available, default waypoint must be the midpoint between start and end
   - Example pattern:
     ```python
     # Safe defaults for arrow control points
     waypoint_x = start.x() + (end.x() - start.x()) * 0.5
     waypoint_y = start.y() + (end.y() - start.y()) * 0.5
     second_mid_x = waypoint_x
     second_mid_y = waypoint_y
     
     # If combat midpoint exists in layout, use it
     if hasattr(layout_data, 'combat_midpoint'):
         waypoint_x = layout_data.combat_midpoint.x()
         waypoint_y = layout_data.combat_midpoint.y()
     ```

3. **Only override in branches that need special behavior**
   - Conditional branches can override these defaults as needed
   - Every path to Bezier calculations must have valid values

4. **Verify all Bezier calculations have access to these variables**
   - Check lines around 503 where waypoint_x and second_mid_x are used in Bezier formula
   - Ensure no path can reach Bezier calculations with undefined variables

## Testing

1. Run the game and enter combat
2. Trigger various arrow rendering conditions (different formations, movement patterns)
3. Confirm no UnboundLocalError occurs
4. Verify arrows still render correctly in all scenarios

## Success Criteria

- [ ] waypoint_x is defined before all Bezier calculations
- [ ] waypoint_y is defined before all Bezier calculations
- [ ] second_mid_x is defined before all Bezier calculations (if used)
- [ ] second_mid_y is defined before all Bezier calculations (if used)
- [ ] Default values use combat midpoint when available, else midpoint between start/end
- [ ] All arrow rendering paths work without UnboundLocalError
- [ ] Visual appearance of arrows remains correct

## Notes

- This is part 1 of fixing the arrow drawing crash
- Part 2 (task 45379ecc) will ensure QPainter is always ended
- Part 3 (task a2a837ee) will test the complete fix
- Keep changes minimal and focused on variable initialization
