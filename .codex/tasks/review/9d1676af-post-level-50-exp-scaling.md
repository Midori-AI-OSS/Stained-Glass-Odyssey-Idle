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
- [x] Scaling is applied every 5 levels after level 50
- [x] Correct multiplier formula is used: (1.25 + (0.05 * power))
- [x] Scaling compounds correctly across multiple 5-level steps
- [x] Power value from current rebirth is used for calculations
- [x] EXP requirements update correctly when crossing threshold levels
- [x] Formula is well-documented in code comments

## Implementation Notes
Completed in commit 3addbf1. Implementation details:
- Replaced old scaling formula: `tax = 1.5 ** ((level - 50) // 5)` with power-based formula
- Implemented in `_level_up` method at lines 618-629 in `endless_idler/ui/idle/idle_state.py`:
  - Gets power from character data: `power = float(data.get("rebirth_power", 1.0))`
  - Calculates step multiplier: `step_multiplier = 1.25 + (0.05 * power)`
  - Determines number of 5-level steps: `steps = (level - 50) // 5`
  - Compounds the multiplier: `tax = step_multiplier ** steps`
- Applied at levels 55, 60, 65, 70, etc.
- Power value from rebirth persists throughout the rebirth cycle
- Scaling affects the base EXP calculation at line 629: `level * 30 * req_mult * tax`

## Related Tasks
- 6945eec8-define-power-formula.md (dependency)
- 5db638b7-rebirth-exp-multiplier-bonus.md

## Technical Notes
This creates an exponential growth curve that makes higher levels significantly more difficult. The power value should be stored/tracked with the current rebirth state so it remains consistent throughout the rebirth cycle.

## Dependencies
- 6945eec8-define-power-formula.md must be completed first

## Estimated Complexity
Medium-High
