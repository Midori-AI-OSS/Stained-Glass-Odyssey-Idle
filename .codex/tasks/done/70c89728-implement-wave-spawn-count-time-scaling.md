# Task: Implement wave spawn count time scaling

## Priority
Medium - Difficulty ramp mechanic

## Category
Feature

## Description
Scale wave spawn count based on survival time using the specified formula. More foes spawn as the party survives longer.

## Requirements
1. Track survival time:
   - `t = seconds survived in current battle`
   - Reset `t` to 0 when battle starts
   - Increment continuously during battle

2. Calculate time multiplier:
   ```
   time_mult = 1 + 0.15 * floor(t / 25) + 0.05 * floor(t / 30)
   ```

3. Calculate spawn count:
   ```
   wave_spawn_count = ceil(base_spawn_count * time_mult)
   ```

4. Apply to wave spawns:
   - Use `wave_spawn_count` for each new wave
   - Baseline `base_spawn_count` is the existing default spawn count
   - Do not modify foe stats in this task

5. Examples for verification:
   - t = 0s: time_mult = 1.0
   - t = 25s: time_mult = 1.15
   - t = 50s: time_mult = 1 + 0.30 + 0.05 = 1.35
   - t = 75s: time_mult = 1 + 0.45 + 0.10 = 1.55
   - t = 120s: time_mult = 1 + 0.60 + 0.20 = 1.80

## Acceptance Criteria
- [ ] Survival time `t` is tracked per battle
- [ ] `time_mult` formula is implemented correctly
- [ ] Spawn count increases over time as formula specifies
- [ ] At t=50s, time_mult equals 1.35 (verification test)
- [ ] Spawn count uses ceiling function (rounds up)
- [ ] Baseline spawn count is preserved from existing game

## Dependencies
- Requires: 0dcdf834-implement-wave-spawning-system.md

## Testing
- Start battle, track spawn counts at t=0, 25, 50, 75 seconds
- Verify spawn counts match expected time_mult scaling
- Verify formula: 1 + 0.15 * floor(t/25) + 0.05 * floor(t/30)

## Notes
- This creates gradually increasing difficulty
- Foe cap and overflow handling are in separate task
- Keep formula exactly as specified
