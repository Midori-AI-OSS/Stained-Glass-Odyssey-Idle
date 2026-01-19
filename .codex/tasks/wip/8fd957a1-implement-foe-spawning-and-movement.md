# Task: Implement foe spawning and movement

## Priority
High - Core battle flow mechanic

## Category
Feature

## Description
Implement foe spawning at top of battle area, downward movement, and engagement when reaching onsite characters.

## Requirements
1. Spawning:
   - New foes spawn at top of battle area
   - Use existing `build_foes` logic for stat generation
   - Position shape widgets at top position

2. Movement - **CONCRETE PARAMETERS**:
   - After spawning, foes move downward toward onsite row
   - **Movement duration**: 2.0 seconds (2000ms) from spawn to engagement line
   - **Animation type**: QPropertyAnimation with linear easing curve
   - **Property to animate**: Widget's `y()` position or geometry
   - Movement speed is consistent across all foes (same duration)
   - **Implementation**: `animation.setDuration(2000)`, `animation.setEasingCurve(QEasingCurve.Type.Linear)`

3. Engagement line - **CONCRETE POSITION**:
   - **Position**: 80% down the battle area height (20% above bottom)
   - Calculate as: `engagement_y = battle_area_height * 0.8`
   - When a foe reaches this line (y position >= engagement_y), it "engages" and can attack
   - Foes stop moving once they reach engagement line
   - **Visual indicator** (optional): Draw a subtle horizontal line at engagement_y for debugging/clarity

4. Combat trigger:
   - Before reaching engagement: foe cannot attack
   - After reaching engagement: foe participates in combat (existing combat math)
   - Onsite characters can attack foes at any position
   - Offsite characters can attack foes at any position (with slower action rate)

5. Visual feedback:
   - Foes should be visually distinct when engaged vs approaching
   - Consider subtle visual indicator at engagement line

## Acceptance Criteria
- [ ] Foes spawn at top of battle area
- [ ] Foes visibly move downward after spawning
- [ ] Movement is smooth and continuous
- [ ] Foes stop at engagement line near onsite row
- [ ] Foes only attack after reaching engagement line
- [ ] Players can attack foes before they engage
- [ ] Existing combat math is unchanged

## Dependencies
- Requires: bf034219-implement-shape-rendering-with-health-fill.md

## Testing
- Spawn a foe, watch it move from top to engagement line
- Verify foe does not attack while moving
- Verify foe attacks after reaching engagement line
- Spawn multiple foes, verify they all move correctly

## Notes
- Movement animation should not block battle updates
- Consider using QPropertyAnimation for smooth movement
- Engagement line position may need tuning for visual balance
