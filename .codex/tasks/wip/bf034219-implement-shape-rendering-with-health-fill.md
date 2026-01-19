# Task: Implement shape rendering with health fill

## Priority
High - Visual representation of foes

## Category
Feature

## Description
Implement rendering of foe shapes with color (damage type) and health-based fill. Replace old foe visual system.

## Requirements
1. Create a new widget for shape-based foe rendering (e.g., `ShapeFoeWidget`)

2. Shape rendering features:
   - Draw shape geometry from selected template
   - Apply color based on damage type
   - Show foe name label (generated character name)
   - Implement health-based fill visualization

3. Health fill visualization:
   - Fill ratio = current_hp / max_hp
   - Visual "unfill" as health decreases
   - Use fill_direction from shape template
   - Smooth visual updates as health changes
   - Examples:
     - 100% health: fully filled
     - 50% health: half filled
     - 0% health: empty/outline only

4. Color encoding:
   - Use existing `color_for_damage_type_id` function
   - Apply color to shape fill
   - Consider outline/border for readability

5. Remove old foe visual system:
   - Identify and remove old foe card/portrait rendering
   - Keep the underlying `build_foes` logic (stats generation)

## Acceptance Criteria
- [ ] Foes render as shapes, not portraits
- [ ] Shape displays foe name (generated character name)
- [ ] Shape color matches foe damage type
- [ ] Shape fill reflects health ratio (full at 100%, empty at 0%)
- [ ] Fill updates smoothly as health changes
- [ ] Old foe visual system is removed
- [ ] Foe stats generation (build_foes) remains unchanged

## Dependencies
- Requires: ea22d177-create-shape-palette-system.md
- Requires: 3d3ed165-implement-foe-shape-selection-logic.md

## Testing
- Spawn foe at full health, verify full fill
- Damage foe to 50%, verify half fill
- Damage foe to near 0%, verify nearly empty
- Verify different damage types show different colors
- Verify foe name displays correctly

## Notes
- Performance is important; shapes will be drawn frequently
- Consider using QPainter clipping for fill effect
- Smooth interpolation may require animation/update loop
