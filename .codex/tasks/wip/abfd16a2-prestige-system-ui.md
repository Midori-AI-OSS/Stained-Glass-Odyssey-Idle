# Task: Prestige System - UI Controls

## Category
UI/UX / Prestige System

## Priority
Medium

## Description
Add UI controls for the prestige system, including a prestige button that becomes enabled when the unlock condition is met.

## Requirements

### Prestige Button
- Add a prestige button to the main progression UI
- Button should be disabled until EXP multiplier >= 10
- Button should be visually distinct (different from rebirth button)
- Show prestige count somewhere visible in the UI

### Visual Feedback
- Clearly indicate when prestige is available (button enabled state)
- Show current prestige count
- Optionally show what the next prestige will do:
  - New EXP multiplier value
  - Current stat gain multiplier
  - EXP penalty if applicable

### Confirmation Dialog (Optional but Recommended)
- Show a confirmation dialog before prestiging
- Explain the trade-offs:
  - EXP multiplier will be reduced
  - Stat gains will double
  - EXP penalty (if applicable)

### Implementation Details
- Integrate with the prestige system logic from task 98bb5c95
- Ensure button state updates when EXP multiplier changes
- Use consistent styling with existing UI elements
- Handle button click to trigger prestige action

### Acceptance Criteria
- [ ] Prestige button is visible in the UI
- [ ] Button is disabled when EXP multiplier < 10
- [ ] Button is enabled when EXP multiplier >= 10
- [ ] Prestige count is displayed
- [ ] Button triggers prestige action correctly
- [ ] UI updates correctly after prestige
- [ ] Styling is consistent with game theme

## Related Tasks
- 98bb5c95-prestige-system-unlock-mechanic.md (dependency)

## Technical Notes
Consider placing the prestige button near the rebirth button since they're related progression mechanics. Use the stained glass aesthetic for the button design.

## Dependencies
- 98bb5c95-prestige-system-unlock-mechanic.md must be completed first

## Estimated Complexity
Medium
