# Task: Implement survival idle exp multiplier

## Priority
Low - Enhancement mechanic

## Category
Feature

## Description
Increase idle experience gain multiplier as the party survives in battle. Longer survival means faster idle progression.

## Requirements
1. Multiplier tracking:
   - Track `idle_exp_mult` per battle (starts at 1.0)
   - Every 1 second the party is alive:
     ```
     idle_exp_mult *= 1.00001
     ```

2. Reset condition:
   - Reset `idle_exp_mult` to 1.0 when a new battle starts
   - Multiplier does NOT persist between battles

3. Application:
   - Apply multiplier to idle-mode experience gain
   - Identify existing idle exp calculation
   - Multiply idle exp by `idle_exp_mult`

4. Examples:
   - 0 seconds: idle_exp_mult = 1.0
   - 60 seconds: idle_exp_mult ≈ 1.0006
   - 600 seconds (10 min): idle_exp_mult ≈ 1.006
   - 3600 seconds (1 hour): idle_exp_mult ≈ 1.0366

5. No UI formula display:
   - Do not show raw multiplier formula to player
   - May show current multiplier value (e.g., "Idle XP: 1.05x")

## Acceptance Criteria
- [x] idle_exp_mult starts at 1.0 on new battle
- [x] Multiplier increases by 1.00001 every second
- [x] Multiplier resets to 1.0 on new battle
- [x] Idle exp gain uses this multiplier
- [x] At 60 seconds, multiplier is approximately 1.0006
- [x] No raw formula shown to player

## Dependencies
- None (can be implemented independently)

## Testing
- Start battle, wait 60 seconds, check idle_exp_mult ≈ 1.0006
- Verify idle exp gain increases over time
- Start new battle, verify multiplier resets to 1.0
- Let battle run for 10 minutes, verify continued growth

## Notes
- Very slow growth per second (0.01%)
- Encourages longer survival runs
- Compounds over time but resets per battle

---

## Audit Report (Auditor Mode)
**Date:** 2026-01-20  
**Auditor:** Midori AI Agent (Auditor Mode)  
**Status:** ✅ APPROVED - Ready for Task Master Review

### Implementation Review

#### Files Modified (6 files, 43 insertions):
1. `endless_idler/save.py` - Added `idle_exp_mult` and `battle_start_time` fields to RunSave
2. `endless_idler/ui/battle/screen.py` - Reset multiplier and start time on battle init
3. `endless_idler/ui/idle/idle_state.py` - Calculation and application of multiplier
4. `endless_idler/ui/idle/screen.py` - Pass battle_start_time to IdleGameState
5. `endless_idler/ui/party_builder.py` - Pass battle_start_time to shop exp state
6. `.codex/tasks/` - Task moved from wip to done

#### Commits Reviewed:
- `6d6daad` - Add fields to RunSave
- `f1608a5` - Initialize fields at battle start
- `d90a633` - Apply multiplier in idle mode
- `f4d18bd` - Pass battle_start_time to IdleGameState
- `1288bc9` - Task completion commit

### Acceptance Criteria Verification

✅ **Multiplier starts at 1.0 on new battle**
- Verified in `endless_idler/ui/battle/screen.py:91`
- `self._save.idle_exp_mult = 1.0` on BattleScreen init

✅ **Multiplier increases by 1.00001 every second**
- Verified in `endless_idler/ui/idle/idle_state.py:635`
- Implementation: `return 1.00001 ** seconds_survived`
- Mathematical verification passed for 60s, 600s, and 3600s test cases

✅ **Multiplier resets to 1.0 on new battle**
- Confirmed reset happens in BattleScreen.__init__
- Saved immediately after reset

✅ **Idle exp gain uses this multiplier**
- Applied in 3 locations in idle_state.py:
  - Line 471: onsite character base_gain
  - Line 551: onsite character display gain
  - Line 572: offsite character shared gain

✅ **At 60 seconds, multiplier ≈ 1.0006**
- Mathematical verification: `1.00001 ** 60 = 1.000600`
- Matches expected value within tolerance

✅ **No raw formula shown to player**
- Formula only appears in code comments (line 633)
- Internal calculation method is private (_calculate_idle_exp_mult)
- No UI text displays "1.00001" or the raw formula

### Code Quality Assessment

**Strengths:**
1. Clean implementation with clear separation of concerns
2. Proper field initialization and persistence in save system
3. Mathematical calculation is correct and efficient
4. Multiplier applied consistently across all exp gain paths
5. Good code documentation in docstrings
6. Follows repository style guidelines
7. All syntax checks pass

**Architecture:**
- Fields added to RunSave dataclass (save.py)
- Reset logic in BattleScreen (battle/screen.py)
- Calculation in IdleGameState private method (idle/idle_state.py)
- Applied in 3 locations for consistency

**Edge Cases Handled:**
- `battle_start_time <= 0.0` returns multiplier of 1.0
- `seconds_survived` clamped to minimum 0.0
- Fields normalized in `_normalized_save` with proper bounds

**Testing:**
- Syntax validation completed (py_compile)
- Mathematical calculations verified against requirements
- No automated tests exist, but manual testing documented in commit

### Findings

**No Issues Found** - Implementation is complete, correct, and follows all repository standards.

### Recommendation

**APPROVE** - Move to `.codex/tasks/taskmaster/` for final Task Master review.

This implementation:
- Meets all acceptance criteria
- Follows repository conventions
- Has clean, maintainable code
- Properly handles edge cases
- Correctly implements the mathematical formula
- Does not expose formula to players

**Ready for production deployment after Task Master sign-off.**
