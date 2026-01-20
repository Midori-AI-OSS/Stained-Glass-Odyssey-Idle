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
- [x] wave_index tracked per battle
- [x] wave_index increments on each wave spawn
- [x] spawn_wave_mult formula is correct
- [x] Multiplier applies to newly spawned foes
- [x] Earlier wave foes are not affected
- [x] wave_index resets on new battle
- [x] Multiplier persists and grows within same battle

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

---

## Audit Results (Auditor Mode)

**Status: APPROVED ✓**

**Audited by:** Auditor Mode  
**Date:** 2025-01-20

### Implementation Review

1. **wave_index Tracking** ✓
   - Implemented in `endless_idler/ui/battle/screen.py:136`
   - Initialized to 0 in `__init__`
   - Correctly resets on new battle (BattleScreenWidget instantiation)

2. **wave_index Increment** ✓
   - Increments after each wave spawn at line 401
   - Properly incremented after applying multiplier to current wave

3. **spawn_wave_mult Formula** ✓
   - Correctly implemented at line 385: `pow(1.0005, self._wave_index)`
   - Formula verified with test cases:
     - wave_index=0: 1.0000 (expected 1.0)
     - wave_index=100: 1.0513 (expected ≈1.0512)
     - wave_index=500: 1.2839 (expected ≈1.2840)
     - wave_index=1000: 1.6485 (expected ≈1.6487)

4. **Multiplier Application** ✓
   - Applied in `build_foes()` function (`endless_idler/ui/battle/sim.py:169-172`)
   - Multiplies max_hp, atk, and defense at spawn time
   - Only affects newly spawned foes, not existing ones

5. **Battle Reset** ✓
   - wave_index initialized to 0 in BattleScreenWidget.__init__
   - Each new battle creates a new BattleScreenWidget instance
   - Verified reset behavior through code inspection

6. **Persistence Within Battle** ✓
   - wave_index persists as instance variable
   - Grows incrementally with each wave spawn
   - Maintained throughout battle lifetime

### Code Quality
- Clean implementation with clear comments
- Proper integration with existing wave spawning system
- No code smells or anti-patterns detected
- Formula documented inline at line 384

### Testing
- Game launches successfully (verified with timeout test)
- No remaining issues or edge cases identified
- All acceptance criteria met

**Recommendation:** Move to `.codex/tasks/taskmaster/` for final Task Master approval.
