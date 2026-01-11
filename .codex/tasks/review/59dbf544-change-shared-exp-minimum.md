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

## Coder Notes

All audit issues have been addressed in commit 653c85e:

### Fixed Issues
1. ✅ Updated dataclass default in `save.py` (line 61): `idle_shared_exp_percentage: int = 1`
2. ✅ Updated `from_json` default in `save.py` (line 92): Both occurrences changed from 0 to 1
3. ✅ Updated screen initialization in `screen.py` (line 96): Default changed from 0 to 1
4. ✅ Updated constructor parameter in `idle_state.py` (line 44): Default changed from 0 to 1
5. ✅ Updated HP regain logic (line 364): Penalty now applies at 1% instead of 0% with documentation

### Game Balance Decision
Chose Option B: The HP regain penalty (0.1 instead of 0.5) now applies at 1% shared EXP (the new minimum) instead of 0% (which is no longer possible). This maintains the intended game balance where players who share the minimum amount get a reduced HP regeneration rate.

### Acceptance Criteria - All Met
- [x] Slider minimum value is set to 1 in the UI
- [x] Initial slider value is set to 1
- [x] Initial label displays "Shared EXP: 1%"
- [x] All validation logic enforces minimum of 1% instead of 0%
- [x] Save file loading sets default to 1% if not present
- [x] Existing save files with 0% are upgraded to 1% on load
- [x] All default values updated to 1
- [x] Game balance logic reviewed and adjusted

Ready for review.
