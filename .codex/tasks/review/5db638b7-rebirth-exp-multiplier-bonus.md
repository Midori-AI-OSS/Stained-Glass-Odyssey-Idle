# Task: Rebirth EXP Multiplier Bonus

## Category
Game Mechanics / Rebirth System

## Priority
High

## Description
Replace the current rebirth bonus formula with a new EXP multiplier system based on the power value calculated at rebirth time.

## Requirements

### New EXP Multiplier Formula
```
rebirth_exp_mult_gain = 0.01 + (power * 0.000005)
```

Where `power` is calculated using the formula from task 6945eec8-define-power-formula.md

### Implementation Details
- Remove any existing rebirth bonus formula
- Implement the new EXP multiplier formula
- Apply the multiplier gain to the character's EXP multiplier on rebirth
- Ensure the multiplier is cumulative across multiple rebirths
- Persist the multiplier value in character save data

### Acceptance Criteria
- [ ] Old rebirth bonus formula is removed
- [ ] New EXP multiplier formula is implemented
- [ ] Multiplier uses the correct power value from rebirth
- [ ] Multiplier is applied correctly when rebirth occurs
- [ ] Multiplier value persists in save data
- [ ] Formula is well-documented in code comments

## Related Tasks
- 6945eec8-define-power-formula.md (dependency)
- 9d1676af-post-level-50-exp-scaling.md

## Technical Notes
This task depends on the power formula being implemented first. The EXP multiplier should accumulate across multiple rebirths - each rebirth adds the calculated gain to the existing multiplier.

## Dependencies
- 6945eec8-define-power-formula.md must be completed first

## Estimated Complexity
Medium
