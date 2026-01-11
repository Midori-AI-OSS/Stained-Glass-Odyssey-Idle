# Remove Arrow Head Calls from paintEvent

## Description
Remove all calls to `self._draw_arrow_head()` from the `paintEvent` method in the `LineOverlay` class in `endless_idler/ui/battle/widgets.py`. This will eliminate the rendering of arrow heads on targeting animations.

## Requirements
- Locate all calls to `self._draw_arrow_head()` in the `paintEvent` method of the `LineOverlay` class
- The `paintEvent` method starts at line 319 (class starts at line 264)
- Remove each call to `_draw_arrow_head` while preserving the surrounding animation logic
- There are exactly 7 calls to remove:
  - Line 392: Arrow head for wrong-way healing segment 1
  - Line 411: Arrow head for wrong-way healing segment 2
  - Line 440: Arrow head for wrong-way healing segment 3
  - Line 459: Arrow head for wrong-way healing segment 4
  - Line 507: Arrow head for same-team healing
  - Line 552: Arrow head for curved enemy attacks
  - Line 555: Arrow head for straight-line attacks

## Acceptance Criteria
- [x] All calls to `self._draw_arrow_head()` are removed from the `paintEvent` method
- [x] The animation paths (lines and curves) continue to render correctly
- [x] No syntax errors are introduced
- [x] The file still has valid Python syntax

## Notes
**⚠️ IMPORTANT**: Complete this task BEFORE task 83418a6c (removing the method definition). This ensures we remove the calls first, then clean up the unused method.

Only remove the method CALLS, not the surrounding logic that draws the paths and curves. The lines should still animate, just without the triangular arrow heads at the end.

Example of what to remove:
```python
self._draw_arrow_head(painter, start, current_pos, color, width=pulse.width)
```

## Status Updates
- 2025-01-11: Task created
- 2025-01-11: Task completed - All 7 arrow head calls removed, plus unused calculation blocks. Syntax verified. Committed in b1c4de2.
