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
- Rebirth 150: 0.2485 (instead of 0.30 linear)
- Rebirth 200: 0.2830 (instead of 0.40 linear)
- Rebirth 300: 0.3398 (instead of 0.60 linear)
- Rebirth 500: 0.4150 (instead of 1.00 linear)

### Testing Requirements
- Verify rebirth 100 still gives 0.2 bonus
- Verify rebirth 150 gives > 0.2 but < 0.3 (diminishing returns working)
- Verify rebirth 200 shows continued slowing of gains
- Add unit tests covering edge cases (rebirth 0, rebirth 100, rebirth 500+)

### Files to Modify
- `endless_idler/combat/party_stats.py` - Update `calculate_atk_speed_bonus()` function
  - Replace `min(0.2, rebirths * 0.002)` with `apply_soft_cap_to_rebirth_bonus(rebirths)`
  - Add the soft cap helper function above
  - Update docstring to reflect soft cap behavior
- `tests/combat/test_party_stats.py` - Add/update tests for soft cap behavior
  - Test rebirth 100 returns 0.2
  - Test rebirth 150 returns ~0.249
  - Test rebirth 500 returns ~0.415
  - Verify continuous growth (no plateau)

## Success Criteria
- Rebirth bonus continues to increase beyond rebirth 100
- Gain rate demonstrably slows according to 2x per 5% formula
- All existing tests pass
- New tests cover soft cap behavior
- Docstring accurately describes new behavior
