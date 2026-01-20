# Task: Rename speed stat to atk_speed

## Priority
High - Foundation for timing refactor

## Category
Refactor

## Description
Rename the `spd` stat to `atk_speed` throughout the codebase. This is a foundational change for the new tick-based action timing system.

## Requirements
1. In `endless_idler/combat/stats.py`:
   - Rename `_base_spd` to `_base_atk_speed`
   - Rename the `spd` property to `atk_speed`
   - Update property getter and setter accordingly
   
2. Update all references to `spd` or `speed` stat in:
   - Character plugins
   - Combat calculations
   - UI displays
   - Any stat modifiers or effects

3. Update baselines:
   - Player characters: `_base_atk_speed = 1` (changed from 2)
   - Foes: `_base_atk_speed = 2` (keep as is)

## Acceptance Criteria
- [x] `_base_spd` is renamed to `_base_atk_speed` in Stats class
- [x] `spd` property is renamed to `atk_speed` 
- [x] All references throughout codebase are updated
- [x] Player character baseline is 1
- [x] Foe baseline is 2
- [x] No references to old `spd` remain (verify with grep)

## Testing
- Run the game and verify stat displays show "atk_speed" or appropriate label
- Check that character stats are accessible and functional

## Notes
- This is a pure rename; do not change any calculation logic yet
- The tick-based timing implementation comes in a separate task

---

## Audit Results (Auditor Mode)

**Status: APPROVED ✓**

**Audited by:** Auditor Mode  
**Date:** 2025-01-20

### Implementation Review

1. **Stats Class Rename** ✓
   - `_base_spd` → `_base_atk_speed` in `endless_idler/combat/stats.py:45`
   - `spd` property → `atk_speed` property at lines 197-202
   - Property getter and setter correctly updated

2. **Codebase-Wide References** ✓
   - All references updated across multiple files:
     - `endless_idler/ui/theme.py` (CSS selectors)
     - `endless_idler/ui/onsite/stat_bars.py` (UI displays)
     - `endless_idler/combat/party_stats.py` (stat calculations)
     - `endless_idler/characters/metadata.py` (base stats)
     - `endless_idler/ui/battle/sim.py` (combat calculations)
   - Verified with grep: 0 remaining `\bspd\b` references (excluding comments)

3. **Player Baseline** ✓
   - Implemented in `endless_idler/combat/party_stats.py:134`
   - Default value: `atk_speed_value = int(atk_speed if atk_speed is not None else 1)`
   - Players get atk_speed=1 when no explicit value provided
   - Verified through code inspection and commit history (ec91568)

4. **Foe Baseline** ✓
   - Explicitly set in `endless_idler/ui/battle/sim.py:160`
   - Foes created with `atk_speed=2` parameter
   - Applied via `apply_scaled_bases()` function

5. **Grep Verification** ✓
   - No old `spd` or `_base_spd` references remain
   - All stat references now use `atk_speed` naming
   - Theme CSS updated to use `atk_speed` selectors

### Code Quality
- Clean, systematic rename with no logic changes
- Proper commit sequence in git history:
  1. Rename stat in Stats class (2689c7e)
  2. Update player/foe baselines (ec91568)
  3. Update theme CSS (032ad53)
  4. Task completion (9dbdbe6)
- No breaking changes introduced
- All UI elements properly updated

### Testing
- Game launches successfully (verified)
- No runtime errors detected
- Stat displays show correct labels
- Character stats accessible and functional

### Related Commits
- `2689c7e`: [REFACTOR] Rename spd stat to atk_speed in Stats class
- `ec91568`: [REFACTOR] Update player baseline atk_speed to 1, foe to 2
- `032ad53`: [REFACTOR] Update theme CSS selectors for atk_speed stat
- `9dbdbe6`: [TASK] Complete rename of spd stat to atk_speed

**Recommendation:** Move to `.codex/tasks/taskmaster/` for final Task Master approval.
