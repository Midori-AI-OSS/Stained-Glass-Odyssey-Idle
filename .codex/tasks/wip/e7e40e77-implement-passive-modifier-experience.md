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

- [ ] Formula implemented at single source of truth location
- [ ] Passive modifier retrieved correctly from passive system
- [ ] Defaults to 1.0 if modifier not present
- [ ] No double multiplication or duplicate layers
- [ ] All edge cases handled gracefully
- [ ] Existing experience calculations still work
- [ ] Code is clear and well-commented

## Notes

- This task is blocked until 94715ad3 identifies the source of truth
- The passive modifier value itself should already exist in the passive system
- This task only implements the multiplication logic
- Next task (verification) will ensure all experience events use this formula
