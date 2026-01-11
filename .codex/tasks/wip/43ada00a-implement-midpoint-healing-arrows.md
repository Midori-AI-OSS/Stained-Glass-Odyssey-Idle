# Implement Healing Arrow Midpoint Behavior for Normal Cases

**Priority:** High  
**Status:** Blocked (depends on 9ca82b45, a55c3682)  
**Category:** Feature / Combat UI / Animation  
**Task ID:** 43ada00a  
**Date Created:** 2026-01-11

## Problem Statement

Implement the core midpoint-curve behavior for healing arrows in normal cases (non-wrong-way). Each healing arrow must travel toward the combat midpoint and then curve back to its intended destination.

## Prerequisites

- Task 9ca82b45 completed (combat midpoint defined)
- Task a55c3682 completed (Bezier curved paths implemented)

## Requirements

### Normal Healing Cases

1. **Player healing player:** Arrow goes from caster to midpoint, then curves to target player
2. **Enemy healing enemy:** Arrow goes from caster to midpoint, then curves to target enemy

### Animation Path

```
Caster → (curved path) → Combat Midpoint → (curved path) → Target
```

The path is a single continuous animation with two segments:
- **Segment 1:** Curved path from caster to midpoint
- **Segment 2:** Curved path from midpoint to target

## Implementation Design

### Two-Segment Animation Approach

```python
def animate_healing_arrow_normal(caster_pos, target_pos, midpoint):
    """
    Animate healing arrow through midpoint to target.
    """
    arrow = create_arrow_sprite()
    arrow.set_position(caster_pos)
    
    # Segment 1: Caster to midpoint
    control1 = calculate_control_point(caster_pos, midpoint, arc_height=40)
    animate_bezier(arrow, caster_pos, control1, midpoint, duration=400,
                   on_complete=lambda: animate_segment_2())
    
    # Segment 2: Midpoint to target
    def animate_segment_2():
        control2 = calculate_control_point(midpoint, target_pos, arc_height=40)
        animate_bezier(arrow, midpoint, control2, target_pos, duration=400,
                       on_complete=on_arrow_complete)
```

### Alternative: Single Cubic Bezier

```python
def animate_healing_arrow_normal(caster_pos, target_pos, midpoint):
    """
    Animate using single cubic Bezier passing through midpoint.
    """
    # Calculate control points to ensure path goes through midpoint
    control1 = calculate_control_toward_midpoint(caster_pos, midpoint)
    control2 = calculate_control_from_midpoint(midpoint, target_pos)
    
    animate_cubic_bezier(arrow, caster_pos, control1, control2, target_pos,
                         duration=800)
```

## Visual Requirements

1. **Smooth curve:** No sharp angles or discontinuities
2. **Visible midpoint pass:** Arrow must visibly approach/pass through midpoint area
3. **Consistent speed:** Animation should feel smooth, not jerky
4. **Proper arc:** Curves should arc naturally, not loop excessively

## Timing Considerations

- **Total duration:** ~800-1000ms for full animation
- **Segment balance:** Each segment should be roughly equal time
- **Pause at midpoint:** Optional brief pause (50-100ms) for emphasis
- **Speed ramping:** Consider ease-in/ease-out for more natural motion

## Edge Cases to Handle

1. **Caster at midpoint:** Arrow should still have visible arc
2. **Target at midpoint:** Similar handling
3. **Caster and target aligned with midpoint:** Ensure curve is still visible
4. **Very close caster/target:** Midpoint visit should still be visible

## Files to Modify

- Healing arrow animation code (likely `endless_idler/ui/battle/`)
- Combat action resolution code
- Light damage type healing code (`mechanics.py` - `resolve_light_heal()`)
- Healing passive animation code

## Testing Requirements

1. **Player heals player:**
   - Lady Light heals ally with light damage
   - Radiant Aegis passive healing
   - Any other player-to-player healing

2. **Enemy heals enemy:**
   - Enemy with healing ability targets ally
   - Enemy passive healing effects

3. **Visual verification:**
   - Arrow visibly travels to midpoint
   - Smooth curve from midpoint to target
   - No visual glitches or teleporting
   - Timing feels natural

4. **Edge cases:**
   - Test all edge case scenarios listed above
   - Multiple simultaneous healing arrows
   - Healing during other animations

## Success Criteria

- [ ] Healing arrows travel to midpoint then to target
- [ ] Both segments use smooth curved paths
- [ ] Animation is visually pleasing and clear
- [ ] Timing is appropriate (not too fast or slow)
- [ ] Works for both player and enemy healing
- [ ] Edge cases handled gracefully
- [ ] No performance issues with multiple arrows
- [ ] Code is clean and maintainable

## Integration with Existing Code

This will replace or modify existing healing arrow animations. Ensure:
- Backward compatibility with healing mechanics
- Proper triggering from all healing sources
- Correct target resolution
- Health changes still apply at correct time

## Next Steps

After this task:
- Task (next): Implement wrong-way healing arrow animations
- Task (next): Test and handle all edge cases comprehensively

## Notes

- Focus on normal healing cases only; wrong-way handled separately
- Midpoint visit is mandatory for all healing arrows
- Consider adding config options for animation speed/style
- May want to add particle effects or visual flourishes at midpoint

---

## AUDITOR REVIEW (2026-01-11)

### Status Assessment

This task is marked as **BLOCKED** awaiting:
- Task 9ca82b45 (combat midpoint defined)
- Task a55c3682 (Bezier curved paths)

**Current State**: 0/8 acceptance criteria checked - no work started

### Recommendation

**Move to WIP** - This is a design/feature task that hasn't been started, not completed work awaiting final approval. The taskmaster folder should contain tasks that are complete and awaiting final sign-off, not blocked or unstarted tasks.

---

**Review Date**: 2026-01-11
**Auditor**: AI Assistant (Auditor Mode)
