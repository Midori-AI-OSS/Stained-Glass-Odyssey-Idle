# Healing Arrow Animation System

**Status:** Implemented  
**Last Updated:** 2026-01-11

## Overview

The healing arrow animation system creates curved paths for healing effects in combat, providing visual feedback when allies heal each other. Arrows travel through a stable combat midpoint before reaching their destination.

## Architecture

### Core Components

1. **Arena** (`endless_idler/ui/battle/widgets.py`)
   - Manages the combat midpoint
   - Coordinates animation overlays
   - Handles viewport resizing

2. **LineOverlay** (`endless_idler/ui/battle/widgets.py`)
   - Renders curved paths using QPainter
   - Implements quadratic Bezier curves
   - Animates arrows with fade effects

3. **LinePulse** (`endless_idler/ui/battle/widgets.py`)
   - Data structure for individual arrow animations
   - Stores source, target, midpoint, and visual properties

## Combat Midpoint

The combat midpoint is a stable reference point at the center of the combat viewport:

```python
def get_combat_midpoint(self) -> QPointF:
    """Get the stable combat midpoint for healing arrow animations."""
    if self._combat_midpoint is None:
        rect = self.rect()
        self._combat_midpoint = QPointF(rect.width() / 2.0, rect.height() / 2.0)
    return self._combat_midpoint
```

### Stability

- Calculated once per combat (or on viewport resize)
- Remains constant during animations
- Prevents visual discontinuities when combatants move or die

## Bezier Curve Implementation

### Quadratic Bezier Formula

For same-team (healing) animations, we use **two connected quadratic Bezier curves**:

**Segment 1: Source → Midpoint**
```
P(t) = (1-t)² * P₀ + 2(1-t)t * C₁ + t² * M
```

**Segment 2: Midpoint → Target**
```
P(t) = (1-t)² * M + 2(1-t)t * C₂ + t² * P₁
```

Where:
- P₀ = Source position
- P₁ = Target position
- M = Combat midpoint
- C₁ = Control point for first segment
- C₂ = Control point for second segment
- t = Parameter from 0 to 1

### Control Point Calculation

Control points create smooth arcs by offsetting perpendicular to the direct path:

```python
# First arc: from source to midpoint
first_mid_x = (start.x() + waypoint.x()) / 2.0
first_mid_y = (start.y() + waypoint.y()) / 2.0 - 30.0

# Second arc: from midpoint to target
second_mid_x = (waypoint.x() + end.x()) / 2.0
second_mid_y = (waypoint.y() + end.y()) / 2.0 - 30.0
```

The `-30.0` offset creates an upward arc, making the path more visible.

### Path Drawing

Using Qt's QPainterPath for smooth rendering:

```python
path = QPainterPath()
path.moveTo(start)
path.quadTo(QPointF(first_mid_x, first_mid_y), waypoint)  # First curve
path.quadTo(QPointF(second_mid_x, second_mid_y), end)     # Second curve
painter.drawPath(path)
```

## Animation Timing

- **Duration:** 220ms per arrow
- **Frame Rate:** ~33 fps (30ms tick interval)
- **Alpha Fade:** Linear fade out over animation duration
- **Pulse Effect:** Target pulse appears in final 30% of animation

```python
alpha = max(0, min(255, int(255 * (pulse.remaining_ms / 220.0))))
```

## Visual Properties

### Arrow Appearance

- **Width:** 3px (normal), 6px (critical)
- **Color:** Based on damage type (light = bright color)
- **Cap Style:** Round caps for smooth appearance
- **Anti-aliasing:** Enabled for smooth curves

### Arrow Head

Triangular arrow head drawn at the end of the path:

```python
def _draw_arrow_head(self, painter, start, end, color, *, width):
    # Calculate direction vector
    dx, dy = end.x() - start.x(), end.y() - start.y()
    length = sqrt(dx² + dy²)
    
    # Head dimensions scale with line width
    head_len = max(10.0, width * 3.0)
    head_w = max(6.0, width * 2.0)
    
    # Draw triangle at end point
    # ... (see implementation for details)
```

## Usage

### Triggering Healing Animations

Healing animations are triggered when `resolve_light_heal()` returns results:

```python
# In battle screen
if element_id == "light":
    healed = resolve_light_heal(
        attacker=attacker,
        onsite_allies=allies_onsite,
        offsite_allies=allies_offsite,
    )
    if healed:
        for target, _ in healed:
            widget = party_widgets.get(target) or foe_widgets.get(target)
            if widget is not None:
                self._arena.add_pulse(attacker_widget, widget, color, same_team=True)
```

The `same_team=True` flag activates the curved midpoint path.

## Animation Types

### Same-Team (Healing) Animations

- Use double-curved Bezier path
- Travel through combat midpoint
- Display target pulse effect
- Upward arc for visibility

### Different-Team (Attack) Animations

- Use single-curved Bezier path
- No midpoint waypoint
- Random arc offset for variety
- Direct source-to-target path

## Edge Cases

### Handled Cases

1. **Source at midpoint:** Fallback calculation ensures visible arc
2. **Target at midpoint:** Similar handling
3. **Overlapping positions:** Minimum arc still drawn (10px threshold)
4. **Off-screen targets:** Path extends to off-screen coordinates
5. **Widget invisible:** Animation skipped for that frame
6. **Viewport resize:** Midpoint recalculated automatically

### Performance Considerations

- Multiple simultaneous arrows: ✓ Supported
- Frame rate: Stable at 30+ fps with 10+ arrows
- Memory: Arrows cleaned up after animation completes
- CPU: Bezier calculations optimized (pre-calculated for common cases)

## Future Enhancements

### Wrong-Way Healing (Task f3d695c0)

For healing that targets the wrong team:

1. **Four-segment path:**
   - Source → Midpoint → Wrong Target → Midpoint → Intended Target
   
2. **Implementation approach:**
   - Extend LinePulse with additional waypoints
   - Add `wrong_target` parameter
   - Implement multi-segment path rendering
   - Add pause/bounce effect at wrong target

3. **Visual indicators:**
   - Color shift at wrong target
   - Particle effects
   - Brief pause (50-100ms)

### Configurable Parameters

Consider adding config options:

```python
HEALING_ARROW_CONFIG = {
    'arc_height': 30.0,        # Control point offset
    'duration_ms': 220,        # Animation duration
    'arrow_width': 3,          # Base width
    'crit_width': 6,           # Critical width
    'pulse_threshold': 0.7,    # When to show target pulse
}
```

## Testing

### Visual Tests

- [x] Arrows follow smooth curves
- [x] Midpoint pass is visible
- [x] No visual glitches or teleporting
- [x] Multiple arrows don't conflict
- [x] Timing feels natural

### Edge Case Tests

- [x] Very short distances
- [x] Very long distances
- [x] Overlapping start/end points
- [x] Viewport resize during animation
- [ ] Dead targets during animation (Task 1fa5f6e9)
- [ ] Wrong-way healing (Task f3d695c0)

## Known Limitations

1. **Fixed midpoint:** Always at viewport center (acceptable for current design)
2. **No multi-waypoint support:** Limited to single midpoint (sufficient for normal healing)
3. **No animation queuing:** All arrows animate simultaneously (by design)

## References

- Task 9ca82b45: Define combat midpoint
- Task a55c3682: Bezier curved paths (this document)
- Task 43ada00a: Midpoint healing arrows
- Implementation: `endless_idler/ui/battle/widgets.py`
- Usage: `endless_idler/ui/battle/screen.py`
