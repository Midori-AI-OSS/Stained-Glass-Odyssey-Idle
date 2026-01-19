# Task: Implement tick-based action timing

## Priority
High - Core timing refactor

## Category
Feature

## Description
Replace the current action timing system with a tick-based system where actions occur based on `atk_speed` and tick intervals.

## Requirements
1. Action timing rule:
   - For every 500 ticks, a character with `atk_speed = 1` performs exactly 1 action
   - General formula: `action_interval_ticks = 500 / atk_speed`
   - Example: atk_speed=2 acts every 250 ticks
   - Example: atk_speed=0.5 acts every 1000 ticks

2. Implementation:
   - Add a tick counter to the battle system
   - Track per-character "next action tick"
   - When current tick >= next action tick, trigger the action
   - After action, set next action tick = current tick + (500 / atk_speed)

3. Offsite action rate:
   - Offsite characters act 10x slower than onsite
   - Apply a ×10 multiplier to action interval for offsite characters
   - Do NOT change damage/heal formulas, only timing

## Acceptance Criteria
- [ ] Tick counter increments in battle loop
- [ ] Characters with atk_speed=1 act once per 500 ticks
- [ ] Characters with atk_speed=2 act once per 250 ticks
- [ ] Offsite characters act 10x slower (interval × 10)
- [ ] Combat math (damage, healing, etc.) remains unchanged

## Dependencies
- Requires: 3b475c11-rename-speed-stat-to-atk_speed.md

## Testing
- Create test characters with atk_speed=1, 2, and 0.5
- Count actions over a fixed number of ticks
- Verify onsite vs offsite action rates differ by 10x

## Notes
- Keep existing combat calculation math intact
- Only change when actions occur, not what they do
