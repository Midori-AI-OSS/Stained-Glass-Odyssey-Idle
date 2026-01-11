# Define Stable Combat Midpoint for Healing Arrow Animations

**Priority:** High  
**Status:** New  
**Category:** Feature / Combat UI / Animation  
**Task ID:** 9ca82b45  
**Date Created:** 2026-01-11

## Problem Statement

Healing arrows must travel to the combat midpoint and then curve back to their destination. To implement this, we need to define a stable combat midpoint that remains consistent throughout the entire animation sequence.

## Requirements

1. Define a combat midpoint that represents the center of the combat area
2. Ensure the midpoint is stable (doesn't change during animations)
3. Make the midpoint easily accessible to animation code
4. Consider both player and enemy positioning when calculating midpoint

## Implementation Guidelines

### Option A: Static Configuration

Define the midpoint as a fixed coordinate in the combat UI configuration:

```python
# In combat UI config or constants
COMBAT_MIDPOINT = {
    'x': 400,  # Center of combat area
    'y': 300   # Vertical center
}
```

### Option B: Dynamic Calculation at Combat Start

Calculate midpoint based on combatant positions when combat begins:

```python
def calculate_combat_midpoint(player_positions, enemy_positions):
    """Calculate the center point of the combat area."""
    all_positions = player_positions + enemy_positions
    avg_x = sum(pos['x'] for pos in all_positions) / len(all_positions)
    avg_y = sum(pos['y'] for pos in all_positions) / len(all_positions)
    return {'x': avg_x, 'y': avg_y}
```

### Option C: UI Viewport Based

Calculate midpoint based on the combat viewport dimensions:

```python
def get_combat_midpoint(viewport):
    """Get the center of the combat viewport."""
    return {
        'x': viewport.width / 2,
        'y': viewport.height / 2
    }
```

## Design Considerations

1. **Stability:** Midpoint must not change when combatants die or move
2. **Visibility:** Midpoint should be in a visually clear area
3. **Performance:** Calculation should be fast (ideally cached)
4. **Accessibility:** Easy to retrieve from animation code
5. **Edge Cases:** Handle empty combat, single combatant, etc.

## Deliverables

- [ ] Define combat midpoint calculation method (choose option)
- [ ] Implement midpoint calculation/storage
- [ ] Make midpoint accessible to animation system
- [ ] Cache midpoint at combat start (if dynamic)
- [ ] Handle edge cases (no combatants, single combatant, etc.)
- [ ] Add comments explaining midpoint usage

## Files to Consider

- `endless_idler/ui/battle/mechanics.py` - Combat mechanics
- `endless_idler/ui/battle/` - UI/animation files
- Combat state or manager files
- Animation system files

## Testing Requirements

1. **Visual Test:** Display midpoint marker in combat for debugging
2. **Stability Test:** Verify midpoint doesn't change during combat
3. **Edge Cases:**
   - Empty combat area
   - Single combatant
   - Very asymmetric positioning
4. **Performance:** Ensure calculation doesn't impact frame rate

## Integration Points

This task provides the foundation for:
- Task (next): Implement curved healing arrow paths
- Future animations that need combat center reference

## Success Criteria

- [ ] Combat midpoint is clearly defined
- [ ] Midpoint is stable throughout combat/animations
- [ ] Midpoint is easily accessible from animation code
- [ ] Edge cases handled gracefully
- [ ] Performance is acceptable
- [ ] Code is well-documented

## Recommendation

**Option A (Static Configuration)** is recommended for simplicity and stability, unless the combat area is highly dynamic. The midpoint can be configured per combat screen layout.

## Notes

- This is a prerequisite for all healing arrow animation tasks
- Midpoint should be calculated/stored once per combat, not per animation
- Consider adding debug visualization to help with testing
- May need adjustment based on actual combat UI layout

---

## AUDITOR REVIEW (2026-01-11)

### Status Assessment

**Current State**: 0/12 acceptance criteria checked - no work started

This is a design/specification task for defining animation behavior.

### Recommendation

**Move to WIP** - Unstarted design tasks belong in WIP, not taskmaster. Taskmaster is for completed work awaiting final approval.

---

**Review Date**: 2026-01-11
**Auditor**: AI Assistant (Auditor Mode)
