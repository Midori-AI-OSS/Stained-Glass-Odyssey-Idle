# Remove Arrow Head Drawing Method

## Description
Remove the `_draw_arrow_head` method from the `LineOverlay` class in `endless_idler/ui/battle/widgets.py`. This method is responsible for drawing the triangular arrow heads on targeting animations in the fight screen.

## Requirements
- Locate the `_draw_arrow_head` method in `endless_idler/ui/battle/widgets.py` (lines 618-648, total file: 709 lines)
- The method is part of the `LineOverlay` class (class starts at line 264)
- Delete the entire method including its signature and implementation (31 lines total)
- The method draws a triangular polygon at the end of attack/heal animation lines

## Acceptance Criteria
- [ ] The `_draw_arrow_head` method is completely removed from the `LineOverlay` class
- [ ] The file still has valid Python syntax after removal
- [ ] No syntax errors are introduced

## Notes
**⚠️ IMPORTANT**: This task should be completed AFTER task 47bddb69 (removing the method calls). If you remove the method before removing the calls, you'll get Python errors.

This method is currently called from multiple locations in the `paintEvent` method. Those calls will be removed in a separate task. The method signature is:
```python
def _draw_arrow_head(
    self,
    painter: QPainter,
    start: QPointF,
    end: QPointF,
    color: QColor,
    *,
    width: int,
) -> None:
```

## Status Updates
- 2025-01-11: Task created
