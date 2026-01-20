# Task: Implement coin rewards per foe kill

## Priority
Medium - Reward system

## Category
Feature

## Description
Award coins when a foe is defeated. Coin amount is based on foe level.

## Requirements
1. Coin reward formula:
   ```
   coins_gained = 1 * foe_level
   ```

2. Implementation:
   - When a foe is defeated (hp reaches 0):
     - Calculate coins: `1 * foe_level`
     - Add coins to player's total
   - Track in battle state or run save

3. Display:
   - Show coin gain notification (optional, if UI supports it)
   - Update total coin display
   - Do not show raw formula to player (just "gained X coins")

4. Integration:
   - Identify existing coin/currency system
   - Use existing coin tracking variable
   - Ensure coins persist to save file

## Acceptance Criteria
- [ ] Killing a level 1 foe grants exactly 1 coin
- [ ] Killing a level 10 foe grants exactly 10 coins
- [ ] Coins are added immediately on foe defeat
- [ ] Coin total persists across battles
- [ ] No raw formula text shown to player
- [ ] Coin gain integrates with existing currency system

## Dependencies
- Requires: 8fd957a1-implement-foe-spawning-and-movement.md (need foes to exist)

## Testing
- Kill a level 1 foe, verify +1 coin
- Kill a level 5 foe, verify +5 coins
- Kill multiple foes, verify coin total accumulates
- Save and reload, verify coins persist

## Notes
- Simple linear scaling by level
- May be modified by multipliers in future tasks
- Use existing `RunSave` or similar for coin storage
