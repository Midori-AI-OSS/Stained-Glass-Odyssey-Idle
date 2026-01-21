# Replace Level Bonus Hard Cap with Soft Cap

## Context
In `endless_idler/combat/party_stats.py`, the `calculate_atk_speed_bonus()` function currently uses a hard cap for the level bonus calculation:

```python
level_bonus = min(0.1, level * 0.001)
```

This hard cap at 0.1 (reached at level 100) prevents any further benefit from gaining additional levels.

## PR Feedback
From PR #69 review comment: "Caps are never okay... we can do a soft cap but hard caps are never okay..."

## Task
Replace the hard cap with a soft cap that slows gain by 2x per 5% gain past the 0.1 threshold.

### Implementation Details

**Current behavior:**
- Linear gain: +0.001 per level up to level 100
- Hard stop at 0.1 (any level >= 100 gives exactly 0.1)

**Desired behavior:**
- Linear gain: +0.001 per level up to level 100 (reaches 0.1)
- Soft cap beyond level 100: Gain continues but slows by 2x per 5% additional gain
- Formula: For each additional 0.005 (5% of 0.1) gained past 0.1, the rate slows by 2x

### Soft Cap Formula

**Implementation approach:**
```python
import math

def apply_soft_cap_to_level_bonus(level: int) -> float:
    """
    Apply soft cap to level bonus calculation.
    
    Linear up to 0.1 (level 100), then logarithmic diminishing returns.
    Rate slows by 2x for each 5% gain past threshold.
    """
    THRESHOLD = 0.1
    STEP_SIZE = 0.005  # 5% of threshold
    
    # Calculate raw linear value
    raw_value = level * 0.001
    
    # If below threshold, no soft cap needed
    if raw_value <= THRESHOLD:
        return raw_value
    
    # Calculate excess over threshold
    excess = raw_value - THRESHOLD
    
    # Apply logarithmic diminishing returns
    # log2(1 + x) gives us the "doubling steps"
    soft_excess = STEP_SIZE * math.log2(1 + (excess / STEP_SIZE))
    
    return THRESHOLD + soft_excess
```

**Example values:**
- Level 100: 0.1000 (at threshold, no soft cap)
- Level 150: 0.1243 (instead of 0.15 linear)
- Level 200: 0.1415 (instead of 0.20 linear)
- Level 300: 0.1699 (instead of 0.30 linear)
- Level 500: 0.2075 (instead of 0.50 linear)

### Testing Requirements
- Verify level 100 still gives 0.1 bonus
- Verify level 150 gives > 0.1 but < 0.15 (diminishing returns working)
- Verify level 200 shows continued slowing of gains
- Add unit tests covering edge cases (level 0, level 100, level 500+)

### Files to Modify
- `endless_idler/combat/party_stats.py` - Update `calculate_atk_speed_bonus()` function
  - Replace `min(0.1, level * 0.001)` with `apply_soft_cap_to_level_bonus(level)`
  - Add the soft cap helper function above
  - Update docstring to reflect soft cap behavior
- `tests/combat/test_party_stats.py` - Add/update tests for soft cap behavior
  - Test level 100 returns 0.1
  - Test level 150 returns ~0.124
  - Test level 500 returns ~0.208
  - Verify continuous growth (no plateau)

## Success Criteria
- Level bonus continues to increase beyond level 100
- Gain rate demonstrably slows according to 2x per 5% formula
- All existing tests pass
- New tests cover soft cap behavior
- Docstring accurately describes new behavior
