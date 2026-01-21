# Replace Rebirth Bonus Hard Cap with Soft Cap

## Context
In `endless_idler/combat/party_stats.py`, the `calculate_atk_speed_bonus()` function currently uses a hard cap for the rebirth bonus calculation:

```python
rebirth_bonus = min(0.2, rebirths * 0.002)
```

This hard cap at 0.2 (reached at rebirth 100) prevents any further benefit from additional rebirths.

## PR Feedback
From PR #69 review comment: "Caps are never okay... we can do a soft cap but hard caps are never okay..."

## Task
Replace the hard cap with a soft cap that slows gain by 2x per 5% gain past the 0.2 threshold.

### Implementation Details

**Current behavior:**
- Linear gain: +0.002 per rebirth up to rebirth 100
- Hard stop at 0.2 (any rebirth >= 100 gives exactly 0.2)

**Desired behavior:**
- Linear gain: +0.002 per rebirth up to rebirth 100 (reaches 0.2)
- Soft cap beyond rebirth 100: Gain continues but slows by 2x per 5% additional gain
- Formula: For each additional 0.01 (5% of 0.2) gained past 0.2, the rate slows by 2x

### Soft Cap Formula

**Implementation approach:**
```python
import math

def apply_soft_cap_to_rebirth_bonus(rebirths: int) -> float:
    """
    Apply soft cap to rebirth bonus calculation.
    
    Linear up to 0.2 (rebirth 100), then logarithmic diminishing returns.
    Rate slows by 2x for each 5% gain past threshold.
    """
    THRESHOLD = 0.2
    STEP_SIZE = 0.01  # 5% of threshold
    
    # Calculate raw linear value
    raw_value = rebirths * 0.002
    
    # If below threshold, no soft cap needed
    if raw_value <= THRESHOLD:
        return raw_value
    
    # Calculate excess over threshold
    excess = raw_value - THRESHOLD
    
    # Apply logarithmic diminishing returns
    soft_excess = STEP_SIZE * math.log2(1 + (excess / STEP_SIZE))
    
    return THRESHOLD + soft_excess
```

**Example values:**
- Rebirth 100: 0.2000 (at threshold, no soft cap)
- Rebirth 150: 0.2346 (instead of 0.30 linear)
- Rebirth 200: 0.2439 (instead of 0.40 linear)
- Rebirth 300: 0.2536 (instead of 0.60 linear)
- Rebirth 500: 0.2634 (instead of 1.00 linear)

### Testing Requirements
- Verify rebirth 100 gives exactly 0.2000 bonus
- Verify rebirth 150 gives ~0.2346 (diminishing returns working)
- Verify rebirth 200 gives ~0.2439 (continued slowing of gains)
- Verify rebirth 300 gives ~0.2536
- Verify rebirth 500 gives ~0.2634
- Add unit tests covering edge cases (rebirth 0, rebirth 100, rebirth 500+)

### Files to Modify
- `endless_idler/combat/party_stats.py` - Update `calculate_atk_speed_bonus()` function
  - Replace `min(0.2, rebirths * 0.002)` with `apply_soft_cap_to_rebirth_bonus(rebirths)`
  - Add the soft cap helper function above
  - Update docstring to reflect soft cap behavior
- `tests/combat/test_party_stats.py` - Add/update tests for soft cap behavior
  - Test rebirth 100 returns exactly 0.2000
  - Test rebirth 150 returns ~0.2346
  - Test rebirth 200 returns ~0.2439
  - Test rebirth 300 returns ~0.2536
  - Test rebirth 500 returns ~0.2634
  - Verify continuous growth (no plateau)

## Success Criteria
- Rebirth bonus continues to increase beyond rebirth 100
- Gain rate demonstrably slows according to 2x per 5% formula
- All existing tests pass
- New tests cover soft cap behavior
- Docstring accurately describes new behavior

---

## TASK MASTER SPECIFICATION UPDATE (2025-01-21)

**SPECIFICATION CORRECTED**

The example values in the original task specification were mathematically inconsistent with the formula that correctly implements "slows by 2x per 5% gain past the hard cap point".

**Correct Formula Derivation:**

The phrase "slows by 2x per 5% gain" means:
- To gain the 1st 5% (0.01) past threshold requires 1x the normal rate
- To gain the 2nd 5% requires 2x the normal rate (cumulative: 3x)
- To gain the 3rd 5% requires 4x the normal rate (cumulative: 7x)
- To gain the nth 5% requires 2^(n-1) the normal rate

This relationship inverts to the logarithmic formula:
```
soft_excess = step_size * log₂(1 + excess / step_size)
```

**Updated Example Values (Correct):**

These values are calculated from the mathematically correct formula and must be used for testing:

- Rebirth 100: 0.2000 (at threshold, no soft cap)
- Rebirth 150: 0.2346 (instead of 0.30 linear)
- Rebirth 200: 0.2439 (instead of 0.40 linear)
- Rebirth 300: 0.2536 (instead of 0.60 linear)
- Rebirth 500: 0.2634 (instead of 1.00 linear)

**Previous Specification Error:**

The original task specified values (0.2485, 0.2830, 0.3398, 0.4150) that cannot be produced by any logarithmic formula. These were based on a misunderstanding of the soft cap behavior and have been replaced with the mathematically correct values above.

**For Coders:**

The implementation using `STEP_SIZE * math.log2(1 + excess / STEP_SIZE)` is CORRECT. Update test expectations to match the corrected values above.
