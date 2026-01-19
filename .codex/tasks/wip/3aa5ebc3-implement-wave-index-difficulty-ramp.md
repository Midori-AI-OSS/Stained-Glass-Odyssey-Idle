# Task: Implement wave index difficulty ramp

## Priority
Medium - Long-term difficulty scaling

## Category
Feature

## Description
Apply a per-wave difficulty multiplier based on wave index. Later waves spawn stronger foes.

## Requirements
1. Wave index tracking:
   - `wave_index` starts at 0 for new battle
   - Increment `wave_index` each time a wave spawns
   - Trigger counts: both 30-second timer and zero-foes-cleared
   - Reset `wave_index` to 0 when battle starts

2. Spawn wave multiplier:
   ```
   spawn_wave_mult = 1.0005 ^ wave_index
   ```

3. Application:
   - Apply to all foes spawned in the current wave
   - Multiply foe base stats at spawn time
   - Multiply: max_hp, atk, defense (or all combat stats)
   - Apply after wave-only overflow mult (if any)

4. Scope:
   - Applies to newly spawned foes only
   - Previous wave foes are unaffected
   - Resets when new battle starts
   - Persistent across waves in same battle

5. Examples:
   - wave_index = 0: spawn_wave_mult = 1.0
   - wave_index = 100: spawn_wave_mult ≈ 1.0512
   - wave_index = 500: spawn_wave_mult ≈ 1.2840
   - wave_index = 1000: spawn_wave_mult ≈ 1.6487

## Acceptance Criteria
- [ ] wave_index tracked per battle
- [ ] wave_index increments on each wave spawn
- [ ] spawn_wave_mult formula is correct
- [ ] Multiplier applies to newly spawned foes
- [ ] Earlier wave foes are not affected
- [ ] wave_index resets on new battle
- [ ] Multiplier persists and grows within same battle

## Dependencies
- Requires: 44ea3aa4-implement-foe-cap-and-wave-overflow-scaling.md

## Testing
- Track spawn_wave_mult for wave_index = 0, 10, 50, 100
- Verify formula: 1.0005^wave_index
- Spawn foes in wave 10, verify they're stronger than wave 0
- Start new battle, verify wave_index resets to 0

## Notes
- This creates long-term difficulty growth
- Multiplier is small per wave but compounds over time
- Combine with wave-only overflow mult for total spawn mult
