# Task: Refactor battle layout to horizontal rows

## Priority
High - Visual foundation for new battle system

## Category
UI Refactor

## Description
Change the battle layout to display characters in two horizontal rows at the bottom: onsite (bottom row) and offsite (row below onsite). Reuse existing character containers.

## Requirements
1. Locate the current character layout code in `endless_idler/ui/battle/` or `endless_idler/ui/onsite/`

2. Change layout structure:
   - **Onsite row**: Bottom of battle view, horizontal left-to-right
   - **Offsite row**: Directly below onsite row, horizontal left-to-right
   - Do NOT stack vertically as currently done

3. Reuse existing character containers/widgets:
   - Do not redesign character cards
   - Only change the layout manager and positioning
   - Ensure existing character rendering logic still works

4. Offsite characters must remain:
   - Visible in both Idle and Fight battle screens
   - Selectable for interaction (tooltips, etc.)
   - Clearly distinguishable from onsite

## Acceptance Criteria
- [ ] Onsite characters displayed in horizontal row at bottom
- [ ] Offsite characters displayed in horizontal row below onsite
- [ ] Same character containers/widgets are used (no redesign)
- [ ] Offsite characters visible and selectable in Idle mode
- [ ] Offsite characters visible and selectable in Fight mode
- [ ] Layout is clean and characters do not overlap

## Dependencies
- None (independent task)

## Testing
- Open battle screen with 3+ onsite and 2+ offsite characters
- Verify horizontal layout for both rows
- Verify offsite characters are interactive
- Test both Idle and Fight modes

## Notes
- This is purely a layout change
- Character rendering and behavior should remain the same
