# Change Shared EXP Minimum from 0% to 1%

## Overview
Update the shared experience slider minimum value from 0% to 1% across all relevant files.

## Context
Currently, the shared EXP slider allows users to set the minimum to 0%. The user has requested this be changed to 1% as the minimum value.

## Files to Modify
1. `./endless_idler/ui/idle/screen.py` - Lines 246, 253, 255
2. `./endless_idler/ui/idle/idle_state.py` - Lines 65, 685
3. `./endless_idler/save.py` - Line 302

## Tasks

### Task 1: Update UI Screen Slider Minimum
**File:** `./endless_idler/ui/idle/screen.py`

**Changes needed:**
- Line 246: Update initial label text from `"Shared EXP: 0%"` to `"Shared EXP: 1%"`
- Line 253: Update `self._shared_exp_slider.setMinimum(0)` to `self._shared_exp_slider.setMinimum(1)`
- Line 255: Update `self._shared_exp_slider.setValue(0)` to `self._shared_exp_slider.setValue(1)`

### Task 2: Update Idle State Validation (Constructor)
**File:** `./endless_idler/ui/idle/idle_state.py`

**Changes needed:**
- Line 65: Update validation from `max(0, min(95, int(shared_exp_percentage)))` to `max(1, min(95, int(shared_exp_percentage)))`

### Task 3: Update Idle State Validation (Setter Method)
**File:** `./endless_idler/ui/idle/idle_state.py`

**Changes needed:**
- Line 685: Update validation from `max(0, min(95, int(percentage)))` to `max(1, min(95, int(percentage)))`

### Task 4: Update Save File Normalization
**File:** `./endless_idler/save.py`

**Changes needed:**
- Line 302: Update validation from `max(0, min(95, int(getattr(save, "idle_shared_exp_percentage", 0))))` to `max(1, min(95, int(getattr(save, "idle_shared_exp_percentage", 1))))`
  - Note: This changes both the minimum from 0 to 1 AND the default value from 0 to 1

## Acceptance Criteria
- [ ] Slider minimum value is set to 1 in the UI
- [ ] Initial slider value is set to 1
- [ ] Initial label displays "Shared EXP: 1%"
- [ ] All validation logic enforces minimum of 1% instead of 0%
- [ ] Save file loading sets default to 1% if not present
- [ ] Existing save files with 0% are upgraded to 1% on load

## Priority
Medium

## Estimated Effort
Small (15 minutes) - Simple value changes across 4 locations

## Notes
This is a straightforward change updating constant values. No complex logic or testing beyond basic verification that the slider works correctly with the new minimum value.

---

## AUDIT REPORT

**Auditor:** Auditor Mode  
**Date:** 2026-01-11  
**Status:** ⚠️ BLOCKED - CRITICAL ISSUES FOUND

### Summary
The implementation successfully changed the shared EXP slider minimum from 0% to 1% in all the specified locations. However, the audit revealed **critical missing changes** in several additional locations that were not identified in the original task specification.

### Issues Found

#### 🔴 CRITICAL ISSUE 1: Dataclass Default Value Not Updated
**File:** `endless_idler/save.py` (Line 61)  
**Current:** `idle_shared_exp_percentage: int = 0`  
**Required:** `idle_shared_exp_percentage: int = 1`

**Impact:** When creating new RunSave instances without explicitly setting this field, it will default to 0 instead of 1, bypassing the validation logic.

#### 🔴 CRITICAL ISSUE 2: from_json Default Value Not Updated  
**File:** `endless_idler/save.py` (Line 92)  
**Current:** `shared_exp_percentage = as_int(data.get("idle_shared_exp_percentage", 0), default=0)`  
**Required:** `shared_exp_percentage = as_int(data.get("idle_shared_exp_percentage", 1), default=1)`

**Impact:** When loading save files that don't contain the `idle_shared_exp_percentage` key, it will default to 0. While the normalization at line 302 will correct this to 1, it's inconsistent and could cause issues if the normalization is ever skipped.

#### 🔴 CRITICAL ISSUE 3: Screen Initialization Default Value Not Updated
**File:** `endless_idler/ui/idle/screen.py` (Line 96)  
**Current:** `shared_exp_percentage=int(getattr(self._save, "idle_shared_exp_percentage", 0))`  
**Required:** `shared_exp_percentage=int(getattr(self._save, "idle_shared_exp_percentage", 1))`

**Impact:** If the save object doesn't have this attribute, it will pass 0 to the IdleGameState constructor, which will then be clamped to 1. While this works due to validation, it's inconsistent and could mask issues.

#### 🔴 CRITICAL ISSUE 4: IdleGameState Constructor Default Parameter Not Updated
**File:** `endless_idler/ui/idle/idle_state.py` (Line 44)  
**Current:** `shared_exp_percentage: int = 0,`  
**Required:** `shared_exp_percentage: int = 1,`

**Impact:** When creating IdleGameState instances without explicitly providing this parameter, it will default to 0 and then be clamped to 1 by validation. This is inconsistent and could lead to confusion.

#### ⚠️ WARNING: Game Balance Logic Change
**File:** `endless_idler/ui/idle/idle_state.py` (Line 364)  
**Current:** `regain = 0.1 if self._shared_exp_percentage == 0 else 0.5`

**Impact:** This logic gives 0.1 HP regain when shared_exp is 0%, but 0.5 HP regain otherwise. Since 0% is no longer possible, ALL players will now get 0.5 HP regain. This is a **game balance change** that may not be intentional.

**Recommendation:** This needs clarification:
- Option A: Keep as-is (all players get 0.5 regain, removing the penalty for 0% sharing)
- Option B: Change to `regain = 0.1 if self._shared_exp_percentage == 1 else 0.5` (penalty now applies to 1% instead)
- Option C: Remove the condition entirely and always use one value

### Acceptance Criteria Review

- [x] Slider minimum value is set to 1 in the UI ✅
- [x] Initial slider value is set to 1 ✅
- [x] Initial label displays "Shared EXP: 1%" ✅
- [x] All validation logic enforces minimum of 1% instead of 0% ✅
- [x] Save file loading sets default to 1% if not present ✅ (via normalization)
- [x] Existing save files with 0% are upgraded to 1% on load ✅
- [ ] ❌ All default values updated to 1 (4 locations missed)
- [ ] ❌ Game balance logic reviewed and adjusted for 0% removal

### Commit Review

**Commit:** 16d2500 `[FEAT] Change shared EXP slider minimum from 0% to 1%`  
**Files Changed:** 3 files, 6 insertions(+), 6 deletions(-)

The commit message is well-written and describes the changes accurately. However, the implementation is incomplete.

### Required Actions

1. **Update dataclass default:** Change line 61 in `save.py` from `= 0` to `= 1`
2. **Update from_json default:** Change line 92 in `save.py` - both occurrences of `0` to `1`
3. **Update screen initialization:** Change line 96 in `screen.py` from `, 0))` to `, 1))`
4. **Update constructor parameter:** Change line 44 in `idle_state.py` from `= 0,` to `= 1,`
5. **Address game balance:** Make a decision about line 364 in `idle_state.py` and document it

### Testing Recommendations

1. Create a new save file and verify default is 1%
2. Load an old save file with 0% and verify it upgrades to 1%
3. Load a save file without the field and verify it defaults to 1%
4. Test HP regeneration at 1% and higher percentages
5. Verify the slider cannot be moved below 1%

### Verdict

**BLOCKED** - Task must return to WIP for completion. The core changes are correct, but critical default values were missed. Additionally, the game balance implications of removing 0% need to be addressed.

**Estimated Time to Fix:** 10 minutes (update 4 default values + decision on HP regain logic)
