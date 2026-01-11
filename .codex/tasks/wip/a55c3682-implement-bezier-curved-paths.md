# Implement Bezier Curved Paths for Healing Arrows

**Priority:** High  
**Status:** Blocked (depends on 9ca82b45)  
**Category:** Feature / Combat UI / Animation  
**Task ID:** a55c3682  
**Date Created:** 2026-01-11

## Problem Statement

Healing arrows must travel along curved paths (Bezier or equivalent) rather than straight lines. This creates a more visually appealing animation and is required for the midpoint-curve behavior.

## Prerequisites

- Task 9ca82b45 completed (combat midpoint defined)

## Requirements

1. Implement Bezier curve or equivalent curved path animation for arrows
2. Support quadratic or cubic Bezier curves
3. Make curve control points configurable
4. Smooth animation along the curve
5. Maintain consistent animation speed regardless of curve length

## Bezier Curve Primer

### Quadratic Bezier (3 points)
```
P(t) = (1-t)² * P0 + 2(1-t)t * P1 + t² * P2
```
- P0: Start point
- P1: Control point (defines curve)
- P2: End point
- t: Parameter from 0 to 1

### Cubic Bezier (4 points)
```
P(t) = (1-t)³ * P0 + 3(1-t)²t * P1 + 3(1-t)t² * P2 + t³ * P3
```
- P0: Start point
- P1, P2: Control points
- P3: End point

## Implementation Approach

### Option A: Use Existing Animation Library

If the project uses an animation library (like GSAP, anime.js, or similar), use its Bezier curve support:

```javascript
// Example with animation library
animateAlongBezier(arrow, {
  start: {x: startX, y: startY},
  control: {x: midX, y: midY - 50},  // Arc upward
  end: {x: endX, y: endY},
  duration: 800,  // ms
  easing: 'linear'
});
```

### Option B: Custom Implementation

Implement Bezier curve calculation manually:

```python
def bezier_quadratic(t: float, p0: tuple, p1: tuple, p2: tuple) -> tuple:
    """Calculate point on quadratic Bezier curve at parameter t."""
    x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
    y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
    return (x, y)

def animate_along_bezier(arrow, start, control, end, duration_ms):
    """Animate arrow along Bezier curve."""
    start_time = time.now()
    
    def update():
        elapsed = time.now() - start_time
        t = min(1.0, elapsed / duration_ms)
        
        position = bezier_quadratic(t, start, control, end)
        arrow.set_position(position)
        
        if t < 1.0:
            schedule_next_frame(update)
        else:
            on_animation_complete()
    
    update()
```

## Control Point Calculation

For healing arrows going to midpoint then to target:

```python
def calculate_control_point(start, end, arc_height=50):
    """Calculate control point for smooth arc."""
    mid_x = (start['x'] + end['x']) / 2
    mid_y = (start['y'] + end['y']) / 2
    
    # Offset perpendicular to path for arc effect
    dx = end['x'] - start['x']
    dy = end['y'] - start['y']
    length = math.sqrt(dx**2 + dy**2)
    
    # Perpendicular offset (normalized)
    perp_x = -dy / length * arc_height
    perp_y = dx / length * arc_height
    
    return {
        'x': mid_x + perp_x,
        'y': mid_y + perp_y
    }
```

## Animation Considerations

1. **Speed Consistency:** Arc length varies, so adjust animation duration or use arc-length parameterization
2. **Frame Rate:** Use requestAnimationFrame or equivalent for smooth animation
3. **Performance:** Pre-calculate curve points if animation is repeated
4. **Orientation:** Optionally rotate arrow sprite to face direction of travel

## Files to Modify

- Healing arrow animation code (location TBD, likely in `endless_idler/ui/battle/`)
- Animation utilities or helpers
- Combat UI rendering code

## Testing Requirements

1. **Visual Test:** Arrows follow smooth curves
2. **Speed Test:** Animation speed is consistent
3. **Performance Test:** No frame drops during multiple simultaneous animations
4. **Edge Cases:**
   - Very short distances (start near end)
   - Very long distances
   - Vertical or horizontal paths
   - Overlapping start and end points

## Integration Points

This curved path system will be used by:
- Next task: Implement midpoint-curve behavior
- Future task: Wrong-way healing animations
- Any other projectile or effect animations

## Success Criteria

- [ ] Bezier curve path calculation implemented
- [ ] Arrows animate smoothly along curves
- [ ] Animation speed is consistent
- [ ] Control points calculated correctly
- [ ] No performance issues with multiple arrows
- [ ] Code is reusable for other animations
- [ ] Well-documented with examples

## Recommendation

Use **quadratic Bezier** (3 points) for simplicity. Only use cubic if more complex curve shapes are needed.

## Notes

- This task focuses on the curve implementation only
- Next task will combine this with midpoint travel
- Consider making curve parameters configurable (arc height, curve type, etc.)
- May want to add debug visualization to show curve paths

---

## AUDITOR REVIEW (2026-01-11)

### Status Assessment

**Current State**: 0/7 acceptance criteria checked - no work started

This is an implementation task for arrow animation curves.

### Recommendation

**Move to WIP** - Unstarted implementation tasks belong in WIP folder for coders to pick up, not in taskmaster awaiting final approval.

---

**Review Date**: 2026-01-11
**Auditor**: AI Assistant (Auditor Mode)
