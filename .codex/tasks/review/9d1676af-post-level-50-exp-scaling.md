# Task: Post-Level-50 EXP Requirement Scaling

## Category
Game Mechanics / Progression System

## Priority
High

## Description
Implement stepped EXP requirement scaling after level 50 that makes leveling progressively more difficult based on the power value.

## Requirements

### Scaling Rule
After level 50, EXP needed increases in steps:
- Every **5 levels**, multiply EXP required by: `(1.25 + (0.05 * power))`

Where `power` is calculated using the formula from task 6945eec8-define-power-formula.md

### Implementation Details
- Apply scaling at levels 55, 60, 65, 70, etc. (every 5 levels after 50)
- The multiplier should compound on previous EXP requirements
- Power value should be the one that was in effect when the current rebirth occurred
- Scaling should affect the base EXP requirement calculation

### Examples
- At level 55 with power = 1.75 (from rebirthing at level 55):
  - Multiplier: 1.25 + (0.05 * 1.75) = 1.3375
- At level 60 with same power:
  - Previous EXP × 1.3375 again

### Acceptance Criteria
- [ ] Scaling is applied every 5 levels after level 50
- [ ] Correct multiplier formula is used: (1.25 + (0.05 * power))
- [ ] Scaling compounds correctly across multiple 5-level steps
- [ ] Power value from current rebirth is used for calculations
- [ ] EXP requirements update correctly when crossing threshold levels
- [ ] Formula is well-documented in code comments

## Related Tasks
- 6945eec8-define-power-formula.md (dependency)
- 5db638b7-rebirth-exp-multiplier-bonus.md

## Technical Notes
This creates an exponential growth curve that makes higher levels significantly more difficult. The power value should be stored/tracked with the current rebirth state so it remains consistent throughout the rebirth cycle.

## Dependencies
- 6945eec8-define-power-formula.md must be completed first

## Estimated Complexity
Medium-High
