# Task: Prestige System - Unlock and Core Mechanics

## Category
Game Mechanics / Prestige System (New Feature)

## Priority
High

## Description
Implement a new prestige system that unlocks when the player's EXP multiplier reaches 10 or higher. This system provides a new layer of progression with trade-offs.

## Requirements

### Unlock Condition
- Prestige becomes available when EXP multiplier >= 10

### Prestige Effects
When prestige is activated:

1. **EXP Multiplier Reset**:
   ```
   new_exp_mult = max(0.01, 0.5 * (0.5 ** (prestige_count - 1)))
   ```
   - First prestige (prestige_count = 0 → 1): sets multiplier to 0.5 * (0.5^0) = 0.5
   - Second prestige (prestige_count = 1 → 2): sets multiplier to 0.5 * (0.5^1) = 0.25
   - Third prestige (prestige_count = 2 → 3): sets multiplier to 0.5 * (0.5^2) = 0.125
   - Fourth prestige (prestige_count = 3 → 4): sets multiplier to 0.5 * (0.5^3) = 0.0625
   - Fifth prestige (prestige_count = 4 → 5): sets multiplier to 0.01 (floor hit)
   - All subsequent prestiges: remain at 0.01

2. **Stat Gain Multiplier**:
   ```
   stat_gain_per_level = base_stat_gain * (2 ** prestige_count)
   ```
   - Each prestige doubles the stat gains per level-up

3. **Post-Floor EXP Penalty**:
   - After EXP multiplier hits the floor (0.01)
   - Add 2x EXP required per level-up for each additional prestige

### Implementation Details
- Track `prestige_count` starting at 0
- Persist `prestige_count` per character in save data
- Prestige button should be disabled until EXP multiplier >= 10
- Apply all three effects when prestige is activated
- Increment prestige_count by 1 each time prestige is used

### Acceptance Criteria
- [ ] Prestige unlock check (EXP mult >= 10) is implemented
- [ ] EXP multiplier reset formula is correct
- [ ] Stat gain multiplier (2^prestige_count) is applied to level-ups
- [ ] Post-floor EXP penalty (2x per prestige) is implemented
- [ ] prestige_count is persisted in character save data
- [ ] prestige_count increments correctly on each prestige
- [ ] All formulas are well-documented in code comments

## Related Tasks
- abfd16a2-prestige-system-ui.md

## Technical Notes
The prestige system creates a permanent power increase (stat gains) at the cost of making EXP harder to gain. The floor at 0.01 ensures the penalty doesn't become infinite, but the 2x EXP requirement per prestige after the floor keeps the difficulty scaling.

## Dependencies
None - this is a new feature

## Estimated Complexity
High
