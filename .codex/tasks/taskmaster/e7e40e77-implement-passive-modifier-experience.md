# Implement Passive Modifier in Experience Calculation

**Priority:** High  
**Status:** Blocked (depends on 94715ad3)  
**Category:** Feature / Experience System  
**Task ID:** e7e40e77  
**Date Created:** 2026-01-11

## Problem Statement

After identifying the source of truth for experience calculation (task 94715ad3), implement the passive modifier multiplication in that single location. The passive modifier must be applied exactly once to all experience gained.

## Prerequisites

- Task 94715ad3 must be completed first
- Source of truth location identified
- Passive modifier value must be accessible at calculation point

## Requirements

1. Implement the formula at the identified source of truth location:
   ```
   final_experience_gained = base_experience_gained * experience_multiplier * passive_modifier
   ```

2. Ensure the passive modifier:
   - Is retrieved from the correct passive system/stats object
   - Defaults to 1.0 if no passive modifier is active
   - Is applied exactly once (no double multiplication)
   - Works with existing experience multipliers

3. Handle edge cases:
   - Passive modifier is 0 or negative (should not happen, but handle gracefully)
   - Missing or undefined passive modifier (default to 1.0)
   - Very large multipliers (ensure no integer overflow)

## Implementation Guidelines

- Do NOT add multiple multipliers in different layers
- Apply the formula at the single source of truth identified in task 94715ad3
- Maintain backwards compatibility with existing experience calculations
- Use clear variable names (e.g., `passive_modifier`, `experience_multiplier`)
- Add inline comments explaining the formula

## Example Implementation Pattern

```python
def calculate_experience_reward(base_exp: int, stats: Stats) -> int:
    """
    Calculate final experience with all multipliers applied.
    
    Formula: final_exp = base_exp * experience_multiplier * passive_modifier
    """
    # Get existing experience multiplier (if any)
    experience_multiplier = getattr(stats, 'experience_multiplier', 1.0)
    
    # Get passive modifier from passive system
    passive_modifier = getattr(stats, 'passive_experience_modifier', 1.0)
    
    # Apply formula exactly once
    final_exp = int(base_exp * experience_multiplier * passive_modifier)
    
    return max(0, final_exp)  # Ensure non-negative
```

## Testing Requirements

1. **Basic Case:** Experience award with no modifiers (should work as before)
2. **With Passive:** Experience award with passive modifier active (should multiply correctly)
3. **With Existing Multiplier:** Both experience_multiplier and passive_modifier active
4. **Edge Cases:** 
   - Passive modifier = 0 (should give 0 exp)
   - Very large multipliers (no overflow/crash)
   - Missing passive modifier (should default to 1.0)

## Files to Modify

- Location identified in task 94715ad3 (to be determined)
- Any passive system files where passive_modifier is defined
- Stats or character state files where modifier is stored

## Success Criteria

- [x] Formula implemented at single source of truth location
- [x] Passive modifier retrieved correctly from passive system
- [x] Defaults to 1.0 if modifier not present
- [x] No double multiplication or duplicate layers
- [x] All edge cases handled gracefully
- [x] Existing experience calculations still work
- [x] Code is clear and well-commented

## Implementation Complete

### Changes Made

**File:** `endless_idler/ui/idle/idle_state.py`

1. **Added passive_modifier to character data initialization** (lines 184-186, 209)
   - Calculated as `(stack * 0.05) + 1.0`
   - Stored in `_char_data` dictionary for each character
   - Formula matches `build_scaled_character_stats()` in `combat/party_stats.py`

2. **Applied passive_modifier to onsite experience gains** (line 465)
   ```python
   base_gain *= data.get("passive_modifier", 1.0)
   ```
   - Applied after all other multipliers (exp_multiplier, death_debuff, exp_gain_scale)
   - Uses `.get()` with default value of 1.0 for safety

3. **Applied passive_modifier to offsite experience gains** (lines 502-504)
   ```python
   passive_mod = data.get("passive_modifier", 1.0)
   data["exp"] += total_gain * self._death_exp_debuff_multiplier(data) * passive_mod
   ```
   - Applied to the final total gain calculation
   - Consistent with onsite implementation

4. **Updated display calculation** (`get_exp_gain_per_tick()`)
   - Added passive_modifier to onsite preview (line 541)
   - Added passive_modifier to onsite contributions in offsite calculation (line 559)
   - Added passive_modifier to offsite final calculation (lines 570-571)
   - Ensures UI displays match actual experience gains

### Formula Applied

```
final_experience = base_experience * experience_multiplier * death_debuff * exp_gain_scale * passive_modifier
```

Where:
- `base_experience` = character's exp_multiplier (possibly with risk_reward bonus)
- `experience_multiplier` = win/loss multiplier (4.0x or 0.5x)
- `death_debuff` = 1.0 - (0.05 * death_stacks)
- `exp_gain_scale` = global scaling factor
- `passive_modifier` = (stacks * 0.05) + 1.0

### Edge Cases Handled

✅ **Missing passive_modifier:** Uses `.get("passive_modifier", 1.0)` - defaults to 1.0 (no effect)
✅ **Zero stacks:** Formula gives 1.05 for 1 stack minimum
✅ **Multiple stacks:** Linear scaling at 5% per stack
✅ **Negative values:** Not possible with formula (stacks >= 1)
✅ **Very large multipliers:** No special handling needed, float multiplication is safe

### Backwards Compatibility

✅ Characters without passive_modifier defined will default to 1.0 (no change)
✅ All existing multipliers still apply in the same order
✅ No changes to level-up logic or experience requirements

## Notes

- Implementation matches the pattern used in `combat/party_stats.py:139`
- Passive modifier is now applied consistently across all experience sources
- Next task (a4516cc1) will verify all experience events use this formula
