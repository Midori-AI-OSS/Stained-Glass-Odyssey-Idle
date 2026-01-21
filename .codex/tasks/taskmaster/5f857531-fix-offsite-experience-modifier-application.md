# Fix Off-Site Character Experience Modifier Application

## Issue Reference
Part of: Fix tooltip styling, correct character stats display outside combat, and normalize off-site character experience and tooltips

## Problem
Off-site characters are not correctly applying experience multiplier and passive modifier to their experience gains. All off-site characters gain the same experience regardless of their individual modifiers.

## Current State
- File: `endless_idler/ui/idle/idle_state.py`
- Lines 500-508: Off-site experience calculation
- Line 505: `passive_mod` is applied, but `exp_multiplier` is NOT applied to off-site characters
- This differs from on-site characters (lines 456-469) which correctly apply `exp_multiplier`

## Requirements
1. Off-site experience gain must use the same modifier logic as on-site experience
2. Both `exp_multiplier` and `passive_modifier` must apply to off-site characters
3. Apply modifiers exactly once per experience award
4. Off-site characters with different modifiers must gain different final experience

## Current Code Analysis

### On-site experience (CORRECT - lines 456-469):
```python
exp_mult = data["exp_multiplier"]  # ✓ Uses character's exp_multiplier
base_gain = exp_mult
# ... additional multipliers ...
base_gain *= exp_multiplier  # ✓ Applies global multiplier
# ... more processing ...
passive_mod = data.get("passive_modifier", 1.0)
data["exp"] += base_gain * self._death_exp_debuff_multiplier(data) * passive_mod  # ✓ Complete
```

### Off-site experience (BROKEN - lines 500-508):
```python
normal_offsite_gain = total_onsite_base_gain * self._offsite_exp_share
total_gain = offsite_gain_per_char + normal_offsite_gain

# Apply passive modifier and death debuff to offsite experience
passive_mod = data.get("passive_modifier", 1.0)
data["exp"] += total_gain * self._death_exp_debuff_multiplier(data) * passive_mod  # ✗ Missing exp_multiplier!
```

## Technical Approach

### Fix in `endless_idler/ui/idle/idle_state.py`

Around line 500-508, modify the off-site experience calculation:

```python
for char_id in self._offsite_ids:
    data = self._char_data.get(char_id)
    if not data:
        continue
    
    normal_offsite_gain = total_onsite_base_gain * self._offsite_exp_share
    total_gain = offsite_gain_per_char + normal_offsite_gain
    
    # Apply ALL modifiers: exp_multiplier, passive_modifier, and death debuff
    exp_mult = float(data.get("exp_multiplier", 1.0))  # ADD THIS
    passive_mod = float(data.get("passive_modifier", 1.0))
    final_gain = total_gain * exp_mult * passive_mod * self._death_exp_debuff_multiplier(data)  # MODIFY THIS
    
    data["exp"] += final_gain
    data["hp"] = min(data["max_hp"], data["hp"] + 0.5)
    if data["exp"] >= data["next_exp"]:
        self._level_up(char_id)
```

### Also check `get_exp_gain_per_tick()` method
Lines 545-574 calculate expected gain per tick for display. This method ALSO needs to be updated to include `exp_multiplier` for offsite characters.

**Current code at line 572-573:**
```python
passive_mod = data.get("passive_modifier", 1.0)
return total_gain * self._death_exp_debuff_multiplier(data) * passive_mod
```

**Should be changed to:**
```python
exp_mult = float(data.get("exp_multiplier", 1.0))
passive_mod = float(data.get("passive_modifier", 1.0))
return total_gain * exp_mult * passive_mod * self._death_exp_debuff_multiplier(data)
```

This ensures the displayed "+X.XX/s" rate matches the actual experience gain.

## Testing
1. Set up two off-site characters with different `exp_multiplier` values (e.g., 1.0 and 2.0)
2. Run idle mode and observe experience gain over time
3. Verify the character with 2.0x multiplier gains approximately 2x more experience
4. Test with passive modifiers from stacking
5. Verify death debuff still applies correctly

## Success Criteria
- [x] Off-site characters with higher `exp_multiplier` gain proportionally more experience
- [x] Off-site characters with different `passive_modifier` values gain different amounts
- [x] Death debuff still applies correctly to off-site characters
- [x] Experience gain matches the displayed "+X.XX/s" rate in the UI
- [x] No duplicate modifier application (modifiers applied exactly once)

## Files to Modify
- `endless_idler/ui/idle/idle_state.py` (primary changes around lines 500-508)

## Notes
- This is part C of the main issue requirements
- The on-site calculation is correct - use it as reference
- Be careful not to apply modifiers twice
- The `get_exp_gain_per_tick()` method already handles this correctly for display purposes (line 572)

---

## ✅ AUDITOR REVIEW - 2025-01-21

**Status**: APPROVED FOR TASK MASTER REVIEW

### Verification Performed:
- ✅ Implementation verified in `endless_idler/ui/idle/idle_state.py`
  - Lines 508-511: Main off-site experience calculation
  - Lines 583-585: `get_exp_gain_per_tick()` display method
- ✅ Both `exp_multiplier` and `passive_modifier` now applied to off-site characters
- ✅ Matches on-site calculation logic correctly
- ✅ All acceptance criteria verified and checked

### Implementation Details:
```python
# Line 509-511 (actual experience gain)
exp_mult = float(data.get("exp_multiplier", 1.0))
passive_mod = data.get("passive_modifier", 1.0)
data["exp"] += total_gain * exp_mult * self._death_exp_debuff_multiplier(data) * passive_mod

# Line 583-585 (display calculation)
exp_mult = float(data.get("exp_multiplier", 1.0))
passive_mod = data.get("passive_modifier", 1.0)
return total_gain * exp_mult * self._death_exp_debuff_multiplier(data) * passive_mod
```

### Commits Verified:
- 503a985: Remove task from wip folder after completion
- 2ff954f: task: complete offsite experience modifier application fix

**Auditor**: AI Assistant | **No Issues Found**
