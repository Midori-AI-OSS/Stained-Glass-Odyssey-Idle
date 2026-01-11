# Ensure QPainter Always Ends in paintEvent

**Priority:** High  
**Status:** New  
**Category:** Bug Fix  
**Task ID:** 45379ecc  
**Date Created:** 2026-01-11

## Problem Statement

When an exception occurs during paintEvent (such as the UnboundLocalError from undefined control points), the QPainter is left active. This causes Qt painter warnings and can lead to rendering issues.

## Objective

Ensure the QPainter.end() is always called in paintEvent, even when exceptions occur, to prevent Qt painter warnings and maintain proper rendering state.

## Implementation Requirements

### File to Modify
- `endless_idler/ui/battle/widgets.py`

### Specific Changes

1. **Locate the paintEvent method**
   - Find where QPainter is created
   - Identify where QPainter.end() is currently called (if at all)

2. **Wrap painting code in try-finally block**
   - Pattern to follow:
     ```python
     def paintEvent(self, event):
         painter = QPainter(self)
         try:
             # All existing painting code here
             # Arrow drawing
             # Other widget rendering
         finally:
             painter.end()
     ```

3. **Alternative: Use context manager pattern (if preferred)**
   - If the codebase uses context managers:
     ```python
     def paintEvent(self, event):
         with QPainter(self) as painter:
             # All painting code here
     ```
   - Note: Check if QPainter supports context manager protocol first

4. **Preserve exception propagation**
   - The finally block should not suppress exceptions
   - Exceptions should still propagate after painter.end() is called
   - This allows proper error logging while ensuring cleanup

## Testing

1. Verify normal paint operations work correctly
2. Simulate an exception in paintEvent (can use task 1eeea699's test scenario)
3. Confirm QPainter.end() is called before exception propagates
4. Verify no Qt painter warnings appear in console during normal play
5. Check that subsequent paint events still work correctly

## Success Criteria

- [ ] QPainter.end() is called even when exceptions occur in paintEvent
- [ ] Try-finally pattern (or equivalent) is properly implemented
- [ ] No Qt painter warnings during normal gameplay
- [ ] Exceptions still propagate properly for debugging
- [ ] Normal rendering continues to work as expected

## Notes

- This is part 2 of fixing the arrow drawing crash
- Part 1 (task 1eeea699) fixes the UnboundLocalError
- Part 3 (task a2a837ee) tests the complete fix
- This pattern should be applied to all paintEvent methods if multiple exist
- Consider if other Qt cleanup patterns need similar protection
