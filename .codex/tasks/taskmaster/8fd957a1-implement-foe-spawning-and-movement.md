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
- [x] Foes spawn at top of battle area
- [x] Foes visibly move downward after spawning
- [x] Movement is smooth and continuous
- [x] Foes stop at engagement line near onsite row
- [x] Foes only attack after reaching engagement line
- [x] Players can attack foes before they engage
- [x] Existing combat math is unchanged

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

---

## Audit Report (2026-01-21)

### Implementation Verified ✅

**Auditor:** Midori AI Auditor  
**Status:** APPROVED  
**Commits Reviewed:**
- 09f3a2f: [TASK] Complete foe spawning and movement implementation
- 0f8a494: [FEAT] Add optional engagement line visual indicator
- 3ec5ae3: [REFACTOR] Use absolute positioning for foe animation
- 2efbe84: [FEAT] Implement foe spawning animation and engagement system

### Audit Findings

All 7 acceptance criteria verified and passed:

1. ✅ **Foes spawn at top of battle area** - Confirmed at y=10 in screen.py
2. ✅ **Foes visibly move downward** - QPropertyAnimation in ShapeFoeWidget.animate_entry()
3. ✅ **Movement smooth and continuous** - 2000ms duration with Linear easing curve
4. ✅ **Foes stop at engagement line** - Calculated at 80% of battle_area_height
5. ✅ **Foes only attack after engagement** - Combat logic checks c.engaged flag
6. ✅ **Players attack foes at any position** - Players default engaged=True
7. ✅ **Combat math unchanged** - Existing calculate_damage still in use

### Technical Implementation Details

**Core Changes:**
- Added `engaged: bool = True` field to Combatant dataclass
- New foes spawn with `engaged=False` in build_foes()
- ShapeFoeWidget.animate_entry() implements 2.0s linear animation
- Combat loop filters by `c.engaged` before allowing attacks
- Engagement line position: `engagement_y = int(battle_height * 0.8)`
- Optional visual indicator in Arena.paintEvent() (disabled by default)

**Code Quality:**
- Clean separation of concerns (widget animation, battle logic, sim data)
- Non-blocking animations using QPropertyAnimation
- Absolute positioning for foe container supports animation
- Animation callback properly marks combatant as engaged
- All tests passing (15/15 foe-related tests)

**Files Modified:**
- endless_idler/ui/battle/shape_foe_widget.py (+41 lines)
- endless_idler/ui/battle/screen.py (+59 lines)
- endless_idler/ui/battle/sim.py (+4 lines)
- endless_idler/ui/battle/widgets.py (+24 lines)

### Security & Performance Review

- ✅ No security concerns identified
- ✅ Animation is async and non-blocking
- ✅ No memory leaks (animations cleaned up properly)
- ✅ Performance impact minimal (QPropertyAnimation is efficient)

### Recommendation

**APPROVED FOR PRODUCTION** - Move to Task Master for final sign-off.

All requirements met, code quality excellent, no issues found.
