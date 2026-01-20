# Task: Implement run health loss on defeat

## Priority
Medium - Core defeat mechanic

## Category
Feature

## Description
On battle loss, reduce run health based on survival time. Longer survival means less health lost.

## Requirements
1. Identify run health:
   - **ACTION REQUIRED**: Before implementing, search the codebase for run health variable
   - Look in `endless_idler/save.py` for `RunSave` class definition
   - Search for "run.*health" or "health" in save-related files
   - Common patterns: `run_hp`, `health`, `current_health`, `hp`
   - **Do not proceed with implementation until variable is confirmed**

2. Loss formula:
   - Loss amount depends on survival time
   - Function must be:
     - Monotonic decreasing (longer survival → less loss)
     - Clamped: max 95% loss, min 5% loss (never below 0% total)
   - Example implementation:
     ```python
     survival_seconds = time_survived_in_battle
     # Linear scaling example:
     loss_percent = 95 - (survival_seconds / 10)  # -1% per 10 seconds
     loss_percent = max(5, min(95, loss_percent))  # clamp to [5, 95]
     
     new_run_health = run_health * (1 - loss_percent / 100)
     ```

3. Apply on loss:
   - Trigger when party is defeated (all onsite characters at 0 hp)
   - Calculate survival time from battle start to defeat
   - Apply loss formula
   - Update run health in save

4. Tuning:
   - **FINALIZE FORMULA**: The exact formula must be chosen before implementation
   - Formula MUST meet: monotonic decreasing, max 95%, min 5%
   - **Suggested concrete formula**: `loss_percent = max(5, min(95, 100 - (survival_seconds * 0.3)))`
     - At 10s: 97% loss (high penalty for quick defeat)
     - At 100s: 70% loss
     - At 300s: 10% loss
     - At 317s: 5% loss (minimum, floors here)
   - **Adjust coefficients if needed** but document the chosen formula in code comments

5. No formula display:
   - Do not show raw formula to player
   - May show "Run Health Lost: X%" message

## Acceptance Criteria
- [ ] Correct run health variable identified and used
- [ ] Loss formula is monotonic decreasing with survival time
- [ ] Maximum loss is 95% (when survival time is very short)
- [ ] Minimum loss is 5% (when survival time is very long)
- [ ] Loss never reduces run health below 0
- [ ] Loss applies on party defeat
- [ ] No raw formula shown to player

## Dependencies
- None (independent of wave/timing refactor)

## Testing
- Lose battle at 10 seconds, verify high loss (~90%+)
- Lose battle at 300 seconds, verify low loss (~5%)
- Verify run health cannot go below 0
- Verify loss is applied to persistent run health

## Notes
- Formula may need tuning based on typical survival times
- Consider logarithmic or exponential decay for smoother scaling
- Minimum 5% loss ensures defeat always has consequence

---

## AUDIT REPORT

**Auditor:** Midori AI Auditor  
**Date:** 2026-01-20  
**Status:** ❌ FAILED - Requires fixes

### Issues Found

#### CRITICAL Issue 1: Minimum Loss Requirement Violated
**Severity:** CRITICAL  
**Location:** `endless_idler/run_rules.py`, lines 61-62  

**Problem:**
The code applies a +2 HP heal (`PARTY_HP_LOSS_HEAL`) AFTER calculating and applying the health loss. This violates the acceptance criterion "Minimum loss is 5%".

**Evidence:**
- At 100 HP with 400s survival (5% loss):
  - Formula correctly calculates: 5% loss
  - Health lost: 5 HP (100 → 95)
  - Then +2 heal applied: 95 → 97
  - **Effective loss: 3 HP = 3%** (NOT 5%)

**Impact:**
- Defeats with long survival times result in only 2-3% effective loss instead of the required 5% minimum
- This makes defeats too forgiving at high survival times
- Breaks the game balance intention of "minimum 5% loss ensures defeat always has consequence"

**Required Fix:**
Option 1: Remove the `PARTY_HP_LOSS_HEAL` bonus on defeat (keep it only for victory if that exists)
Option 2: Adjust the formula to account for the +2 heal, ensuring net loss is still 5% minimum
Option 3: Apply the heal BEFORE the loss calculation, not after

**Recommended:** Option 1 is cleanest - the loss formula should be the final word on defeat penalty.

### Issues Found Summary

1. ❌ **CRITICAL:** Minimum 5% loss requirement violated due to +2 heal applied after loss
2. ✅ Run health variable correctly identified (party_hp_current)
3. ✅ Loss formula is monotonically decreasing
4. ✅ Maximum loss capped at 95%
5. ⚠️  Minimum loss shows as 5% in formula but actually 2-3% after heal
6. ✅ Health never goes below 0
7. ✅ Applied on defeat and retreat
8. ✅ Battle start time properly initialized
9. ✅ Survival time calculation correct
10. ✅ No raw formula shown to player

### Test Results

Comprehensive audit test created and run (`test_health_loss_audit.py`):
- ✅ Health loss formula calculations correct (before heal)
- ✅ Monotonic decreasing property verified
- ❌ Bounds test revealed 3% effective loss at long survival (should be 5% minimum)
- ✅ Health never goes below 0
- ✅ Correct run health variable used
- ✅ Partial health scenarios work correctly

### Code Quality Assessment

**Strengths:**
- Clean implementation with good comments
- Formula well-documented in code
- Proper use of max/min for bounds
- Good integration with battle screen
- Proper handling of battle_start_time across defeat and retreat

**Concerns:**
- Logic flaw with heal applied after loss calculation
- No tests included with implementation
- Old constant properly deprecated with clear comments

### Acceptance Criteria Status

- [x] Correct run health variable identified and used
- [x] Loss formula is monotonic decreasing with survival time
- [x] Maximum loss is 95% (when survival time is very short)
- [ ] **Minimum loss is 5% (when survival time is very long)** - FAILED (actual: 2-3%)
- [x] Loss never reduces run health below 0
- [x] Loss applies on party defeat
- [x] No raw formula shown to player

**Overall:** 6/7 criteria met (85.7%)

### Recommendations

1. **MUST FIX:** Remove or relocate the `PARTY_HP_LOSS_HEAL` bonus to ensure minimum 5% loss
2. **SHOULD ADD:** Unit tests for this feature (test file created as reference: `test_health_loss_audit.py`)
3. **CONSIDER:** Document why defeats get a small heal if it's intentional, or remove it

### Next Steps

1. Fix the minimum loss issue in `run_rules.py`
2. Re-run audit test to verify fix
3. Move back to review once fixed
4. Consider adding the audit test to the permanent test suite

**Task Status:** Moving back to WIP for required fixes.
