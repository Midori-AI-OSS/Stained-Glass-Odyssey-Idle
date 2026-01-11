# Implement Wrong-Way Healing Arrow Animations

**Priority:** High  
**Status:** Blocked (depends on 43ada00a)  
**Category:** Feature / Combat UI / Animation  
**Task ID:** f3d695c0  
**Date Created:** 2026-01-11

## Problem Statement

When healing goes to the "wrong" target (player healing enemy or enemy healing player), the arrow must follow a special animation sequence: travel to midpoint, curve to wrong-way target, then return from wrong-way target back through midpoint to the intended target.

## Prerequisites

- Task 9ca82b45 completed (combat midpoint defined)
- Task a55c3682 completed (Bezier curved paths implemented)
- Task 43ada00a completed (normal midpoint healing arrows)

## Requirements

### Wrong-Way Healing Cases

1. **Player healing enemy:** Player casts heal, but it targets an enemy (unusual case/bug/mechanic)
2. **Enemy healing player:** Enemy casts heal, but it targets a player (unusual case/bug/mechanic)

### Animation Sequence

```
Caster → Midpoint → Wrong Target → Midpoint → Intended Target
```

**Four-segment animation:**
1. **Segment 1:** Caster to midpoint (curved)
2. **Segment 2:** Midpoint to wrong-way target (curved)
3. **Segment 3:** Wrong-way target back to midpoint (curved)
4. **Segment 4:** Midpoint to intended target (curved)

## Visual Behavior

The arrow should:
- Visibly travel to the wrong target first
- "Bounce" or "realize the mistake" at wrong target
- Return through midpoint
- Finally reach the intended target
- Heal value applies only when reaching intended target

## Implementation Design

### Four-Segment Sequential Animation

```python
def animate_healing_arrow_wrongway(caster_pos, wrong_target_pos, 
                                   intended_target_pos, midpoint):
    """
    Animate healing arrow with wrong-way redirect behavior.
    """
    arrow = create_arrow_sprite()
    arrow.set_position(caster_pos)
    
    # Segment 1: Caster to midpoint
    def segment_1():
        control1 = calculate_control_point(caster_pos, midpoint)
        animate_bezier(arrow, caster_pos, control1, midpoint, 
                       duration=300, on_complete=segment_2)
    
    # Segment 2: Midpoint to wrong target
    def segment_2():
        control2 = calculate_control_point(midpoint, wrong_target_pos)
        animate_bezier(arrow, midpoint, control2, wrong_target_pos,
                       duration=300, on_complete=segment_3)
    
    # Segment 3: Wrong target back to midpoint
    def segment_3():
        # Optional: Brief pause at wrong target
        schedule_after(100, lambda: do_segment_3_animation())
        
    def do_segment_3_animation():
        control3 = calculate_control_point(wrong_target_pos, midpoint)
        animate_bezier(arrow, wrong_target_pos, control3, midpoint,
                       duration=300, on_complete=segment_4)
    
    # Segment 4: Midpoint to intended target
    def segment_4():
        control4 = calculate_control_point(midpoint, intended_target_pos)
        animate_bezier(arrow, midpoint, control4, intended_target_pos,
                       duration=300, on_complete=on_animation_complete)
    
    segment_1()  # Start the sequence
```

## Visual Enhancements

Consider adding visual indicators:
- **Color change:** Arrow changes color when at wrong target
- **Particle effect:** Small "confusion" particles at wrong target
- **Bounce animation:** Arrow briefly bounces or wobbles at wrong target
- **Speed change:** Faster return speed to show "correction"

## Timing Considerations

- **Total duration:** ~1200-1600ms (longer than normal healing)
- **Segment durations:** Each segment ~300-400ms
- **Pause at wrong target:** 50-150ms for clarity
- **Balance:** Animation should be clear but not too slow

## Edge Cases

1. **Wrong target dies during animation:** Continue to intended target
2. **Intended target dies during animation:** Arrow dissipates or completes anyway
3. **Caster dies during animation:** Animation continues
4. **Wrong target = intended target:** Fall back to normal animation
5. **Multiple wrong-way arrows:** Each follows its own path independently

## When to Trigger Wrong-Way Animation

Determine logic for when healing is "wrong-way":
- Is this a bug to fix, or intentional mechanic?
- Should it only trigger in specific circumstances?
- How does game logic determine "wrong-way" vs normal healing?

**Important:** Coordinate with game design to understand when this should occur.

## Healing Application Timing

Critical decision: When does the heal actually apply?
- **Option A:** Only when reaching intended target (recommended)
- **Option B:** At wrong target, then again at intended target (double heal?)
- **Option C:** Split between wrong and intended targets

Recommend **Option A** for clarity and balance.

## Files to Modify

- Healing arrow animation code
- Combat action resolution for healing
- Light damage type healing (`resolve_light_heal()`)
- Healing targeting/validation logic

## Testing Requirements

1. **Player heals enemy (wrong-way):**
   - Trigger scenario where player heal targets enemy
   - Verify four-segment animation
   - Verify heal applies to intended target only

2. **Enemy heals player (wrong-way):**
   - Trigger scenario where enemy heal targets player
   - Verify animation sequence
   - Verify correct final target

3. **Visual verification:**
   - Arrow clearly visits wrong target
   - Return path is visible and smooth
   - Final healing applies correctly

4. **Edge cases:**
   - Test all edge cases listed above
   - Multiple wrong-way arrows simultaneously
   - Wrong-way during other animations

## Success Criteria

- [ ] Wrong-way arrows follow four-segment path
- [ ] All segments use smooth curved paths
- [ ] Wrong target visit is clear and visible
- [ ] Return journey is smooth and obvious
- [ ] Healing applies only to intended target
- [ ] Timing feels appropriate
- [ ] Visual enhancements (if added) enhance clarity
- [ ] Edge cases handled gracefully
- [ ] Performance acceptable with multiple arrows

## Configuration

Consider making this configurable:
```python
WRONGWAY_HEALING_CONFIG = {
    'enabled': True,  # Can disable for simpler behavior
    'pause_at_wrong_target_ms': 100,
    'segment_duration_ms': 300,
    'show_visual_effects': True
}
```

## Alternative Approach

If wrong-way healing is a bug rather than a feature, consider:
- Fixing the targeting logic instead of adding animation
- Preventing wrong-way healing entirely
- This task may be unnecessary if targeting is corrected

**Confirm with game design before implementing.**

## Notes

- Coordinate with design team on whether wrong-way healing should exist
- This is the most complex healing arrow animation
- Consider performance with many simultaneous wrong-way arrows
- May want to add sound effects at wrong target "bounce"
- Animation clarity is critical for player understanding
