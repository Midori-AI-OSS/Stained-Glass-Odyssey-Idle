# Task: Implement foe cap and wave-only overflow scaling

## Priority
Medium - Balance mechanic

## Category
Feature

## Description
Cap total foes at 100. When a wave would exceed the cap, block extra spawns and apply a wave-only buff to that wave's foes.

## Requirements
1. Foe count cap:
   - Maximum 100 foes alive at any time
   - Track current foe count continuously

2. Overflow handling during wave spawn:
   - Calculate: `available_slots = 100 - current_foe_count`
   - If `wave_spawn_count > available_slots`:
     - Spawn only `available_slots` foes
     - `blocked_spawns = wave_spawn_count - available_slots`
   - Track blocked spawns for this wave

3. Wave-only multiplier:
   - For each blocked spawn in this wave:
     - `wave_only_mult *= 1.01`
   - Apply to all foes spawned in this wave only
   - Example: 5 blocked spawns → wave_only_mult = 1.01^5 ≈ 1.051

4. Multiplier scope:
   - Apply only to foes spawned in the current wave
   - Do NOT carry over to future waves
   - Do NOT affect foes from previous waves
   - Reset multiplier for next wave

5. Stat application:
   - Apply wave_only_mult to foe base stats at spawn time
   - Multiply: max_hp, atk, defense (or all combat stats)
   - Apply before any other scaling

## Acceptance Criteria
- [ ] Total foes alive never exceeds 100
- [ ] Blocked spawns are tracked per wave
- [ ] Each blocked spawn increases wave_only_mult by 1.01
- [ ] Multiplier applies only to same-wave foes
- [ ] Multiplier resets for next wave
- [ ] Foes spawned with multiplier are stronger

## Dependencies
- Requires: 70c89728-implement-wave-spawn-count-time-scaling.md

## Testing
- Force spawn 100 foes, verify cap
- Trigger wave with 95 foes alive, spawn count 10
  - Verify only 5 spawn
  - Verify 5 blocked spawns
  - Verify wave_only_mult = 1.01^5 ≈ 1.051
- Verify next wave resets multiplier

## Notes
- This prevents spawn spam while keeping difficulty ramping
- Wave-only scope is critical for balance
- Multiplier compounds per wave but resets between waves
