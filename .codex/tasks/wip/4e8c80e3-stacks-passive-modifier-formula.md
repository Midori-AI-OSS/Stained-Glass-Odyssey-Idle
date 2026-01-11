# Task: Stacks to Passive Modifier Formula

## Category
Game Mechanics / Combat System

## Priority
Medium

## Description
Implement a formula to convert stack count into a passive modifier value that will be used to scale stat usage in calculations.

## Requirements

### Passive Modifier Formula
```
passive_mod = (stacks * 0.05) + 1
```

Where `stacks` is the current number of stacks accumulated.

### Examples
- 0 stacks: passive_mod = (0 * 0.05) + 1 = 1.0 (no bonus)
- 10 stacks: passive_mod = (10 * 0.05) + 1 = 1.5 (50% bonus)
- 20 stacks: passive_mod = (20 * 0.05) + 1 = 2.0 (100% bonus)
- 100 stacks: passive_mod = (100 * 0.05) + 1 = 6.0 (500% bonus)

### Implementation Details
- Calculate passive_mod dynamically based on current stack count
- This formula should be centralized for reuse across stat calculations
- The passive modifier starts at 1.0 (neutral) with 0 stacks
- Each stack adds 5% to the multiplier

### Acceptance Criteria
- [ ] Passive modifier formula is implemented correctly
- [ ] Formula calculates dynamically based on current stacks
- [ ] Returns 1.0 when stacks = 0
- [ ] Returns correct values for various stack counts
- [ ] Formula is centralized and reusable
- [ ] Well-documented in code comments

## Related Tasks
- d41b6f12-passive-mod-buffs-stat-usage.md

## Technical Notes
This is a foundational calculation that will be used by task d41b6f12 to apply the modifier to all stat usage. The linear scaling (5% per stack) provides straightforward progression.

## Dependencies
None - this is a foundational task

## Estimated Complexity
Low
