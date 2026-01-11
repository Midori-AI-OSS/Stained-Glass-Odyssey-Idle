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

**CURRENT STATE:**
- paintEvent method: lines 319-602
- QPainter is created at line 323: `painter = QPainter(self)`
- painter.end() is called at line 602 (last line before method ends)
- **PROBLEM:** If an exception occurs anywhere in lines 323-601, painter.end() is never called
- The UnboundLocalError from task 1eeea699 happens at line 503, which is BEFORE painter.end()

**THE FIX:**
1. **Wrap the painting code in try-finally** (recommended for PySide6)
   - Pattern to implement:
     ```python
     def paintEvent(self, event):
         if not self._pulses:
             return
         
         painter = QPainter(self)
         painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
         
         try:
             # All existing painting code (lines 326-601)
             for pulse in list(self._pulses):
                 # ... all the arrow drawing logic ...
         finally:
             painter.end()
     ```

2. **Important notes:**
   - Move the early return check (line 320-321) BEFORE creating QPainter
   - This is already correct in current code
   - The try block should start after painter setup and before the for loop
   - Finally ensures painter.end() is called even if UnboundLocalError or any other exception occurs

## Testing

1. Verify normal paint operations work correctly
2. Simulate an exception in paintEvent (can use task 1eeea699's test scenario)
3. Confirm QPainter.end() is called before exception propagates
4. Verify no Qt painter warnings appear in console during normal play
5. Check that subsequent paint events still work correctly

## Success Criteria

- [ ] Try-finally pattern wraps all painting code (lines 326-601)
- [ ] QPainter.end() is in the finally block
- [ ] QPainter.end() is called even when exceptions occur in paintEvent
- [ ] No Qt painter warnings during normal gameplay
- [ ] Exceptions still propagate properly for debugging (not suppressed)
- [ ] Normal rendering continues to work as expected
- [ ] When UnboundLocalError occurs (before task 1eeea699 is fixed), painter still ends properly

## Notes

- This is part 2 of fixing the arrow drawing crash
- Part 1 (task 1eeea699) fixes the UnboundLocalError
- Part 3 (task a2a837ee) tests the complete fix
- This pattern should be applied to all paintEvent methods if multiple exist
- Consider if other Qt cleanup patterns need similar protection

---

## AUDITOR REVIEW (2026-01-11)

### Verification

Checked current implementation in `endless_idler/ui/battle/widgets.py`:
- ✅ paintEvent method has try-finally wrapper (lines 336, 560-561)
- ✅ QPainter.end() is in the finally block
- ✅ Painter cleanup is guaranteed even on exceptions

### Current Implementation

```python
def paintEvent(self, event: object) -> None:
    # ... early returns ...
    painter = QPainter(self)
    
    try:
        # All painting logic
        for pulse in list(self._pulses):
            # ... drawing code ...
    finally:
        painter.end()
```

### Status: COMPLETE ✅

**Recommendation**: Delete this task - already implemented correctly.

---

**Review Date**: 2026-01-11
**Auditor**: AI Assistant (Auditor Mode)
