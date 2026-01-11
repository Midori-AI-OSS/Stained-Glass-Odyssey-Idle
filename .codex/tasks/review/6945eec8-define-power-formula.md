# Task: Define Power Formula for Rebirth System

## Category
Game Mechanics / Rebirth System

## Priority
High

## Description
Implement the power formula that will be used as the foundation for rebirth calculations. This power value is calculated when the player clicks rebirth at level L (where L >= 50).

## Requirements

### Power Formula
When rebirth is clicked at level `L` (L >= 50):
```
power = 1 + 0.15 * (L - 50)
```

### Implementation Details
- Calculate power based on the current level when rebirth button is clicked
- Only calculate power for levels 50 and above
- Store or pass this power value for use in subsequent rebirth calculations
- Ensure the formula is centralized and reusable for other rebirth mechanics

### Acceptance Criteria
- [ ] Power formula is implemented correctly
- [ ] Power is calculated at rebirth time based on current level
- [ ] Power calculation only applies when level >= 50
- [ ] Power value is accessible for use in EXP multiplier and scaling calculations
- [ ] Formula is well-documented in code comments

## Related Tasks
- 5db638b7-rebirth-exp-multiplier-bonus.md
- 9d1676af-post-level-50-exp-scaling.md

## Technical Notes
This is a foundational task that other rebirth mechanics depend on. The power value should be calculated fresh each time rebirth is triggered, based on the current level at that moment.

## Dependencies
None - this is a foundational task

## Estimated Complexity
Low
