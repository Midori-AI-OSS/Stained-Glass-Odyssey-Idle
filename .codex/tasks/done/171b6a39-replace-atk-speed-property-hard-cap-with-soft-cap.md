# Replace atk_speed Property Hard Cap with Soft Cap

## Context
In `endless_idler/combat/stats.py`, the `atk_speed` property currently uses a hard cap:

```python
@property
def atk_speed(self) -> int:
    # Apply progression bonuses and cap at 5.0 before converting to int
    base_plus_modifiers = self._base_atk_speed + self._calculate_stat_modifier("atk_speed")
    capped_value = min(5.0, base_plus_modifiers)
    return int(max(1, capped_value))
```

This hard cap at 5.0 prevents any further benefit from increasing atk_speed beyond this value.

## PR Feedback
From PR #69 review comment: "Nope not okay..." (in response to the hard cap at line 200)

## Task
Replace the hard cap with a soft cap that slows gain by 2x per 5% gain past the 5.0 threshold.

### Implementation Details

**Current behavior:**
- Linear gain up to 5.0
- Hard stop at 5.0 (any value >= 5.0 is clamped to exactly 5.0)
- Converted to int for return

**Desired behavior:**
- Linear gain up to 5.0
- Soft cap beyond 5.0: Gain continues but slows by 2x per 5% additional gain
- Formula: For each additional 0.25 (5% of 5.0) gained past 5.0, the rate slows by 2x
- Still converted to int for return (maintaining current behavior)

### Soft Cap Formula

**Implementation approach:**
```python
import math

@property
def atk_speed(self) -> int:
    """
    Get atk_speed with soft cap applied.
    
    Linear up to 5.0, then logarithmic diminishing returns.
    Rate slows by 2x for each 5% gain past threshold.
    """
    THRESHOLD = 5.0
    STEP_SIZE = 0.25  # 5% of threshold
    
    # Calculate raw value from base + modifiers
    raw_value = self._base_atk_speed + self._calculate_stat_modifier("atk_speed")
    
    # If below threshold, no soft cap needed
    if raw_value <= THRESHOLD:
        return int(max(1, raw_value))
    
    # Calculate excess over threshold
    excess = raw_value - THRESHOLD
    
    # Apply logarithmic diminishing returns
    soft_excess = STEP_SIZE * math.log2(1 + (excess / STEP_SIZE))
    soft_capped = THRESHOLD + soft_excess
    
    # Convert to int and enforce minimum
    return int(max(1, soft_capped))
```

**Example values (before int conversion):**
- Raw 5.0: 5.00 → int(5) = 5
- Raw 6.0: 5.49 → int(5) = 5
- Raw 7.0: 5.83 → int(5) = 5
- Raw 9.0: 6.36 → int(6) = 6
- Raw 15.0: 7.66 → int(7) = 7
- Raw 25.0: 9.16 → int(9) = 9

**Note:** Due to int conversion, benefits become visible around raw atk_speed of 9+

### Testing Requirements
- Verify atk_speed of exactly 5.0 still returns 5 (int conversion)
- Verify atk_speed of 6.0 raw returns > 5 but < 6 (diminishing returns working)
- Verify atk_speed of 10.0 raw shows continued slowing of gains
- Verify minimum value of 1 is still enforced
- Add unit tests covering edge cases (negative values, 0, 5.0, very large values)

### Files to Modify
- `endless_idler/combat/stats.py` - Update `atk_speed` property getter
  - Import `math` module at top if not already present
  - Replace the entire property implementation with the code above
  - Update docstring to explain soft cap behavior
- `tests/combat/test_stats.py` - Add/update tests for soft cap behavior
  - Test raw 5.0 returns int(5)
  - Test raw 9.0 returns int(6) 
  - Test raw 15.0 returns int(7)
  - Test raw 25.0 returns int(9)
  - Verify minimum value of 1 is enforced
  - Verify continuous growth (no plateau)

## Success Criteria
- atk_speed continues to increase beyond 5.0 (before int conversion)
- Gain rate demonstrably slows according to 2x per 5% formula
- Return type remains int as expected by rest of codebase
- Minimum value of 1 is still enforced
- All existing tests pass
- New tests cover soft cap behavior
- Comments accurately describe new behavior

## Notes
- The int conversion at the end means players will see discrete integer values
- However, the soft cap should apply to the float value before conversion
- This allows fine-grained control while maintaining compatibility

---

## 🔴 AUDITOR REVIEW (2026-01-21) - BLOCKED

### Status: **RETURNED TO WIP**

### Critical Issue: Task Specification Inconsistency

The task specification contains **contradictory information** - the provided formula does NOT produce the example values:

| Raw Value | Formula Result | Spec Example | Match? |
|-----------|---------------|--------------|---------|
| 5.0 | 5.00 | 5.00 | ✓ |
| 6.0 | 5.58 | 5.49 | ✗ |
| 7.0 | 5.79 | 5.83 | ✗ |
| 9.0 | 6.02 | 6.36 | ✗ |
| 15.0 | 6.34 | **7.66** | ✗ MAJOR |
| 25.0 | 6.58 | **9.16** | ✗ MAJOR |

### Implementation Review

✅ **What was done correctly:**
- Formula implemented exactly as specified: `STEP_SIZE * math.log2(1 + (excess / STEP_SIZE))`
- Math module imported correctly
- All 13 tests created and passing
- Soft cap removes hard limit (continuous growth verified)
- Minimum value of 1 enforced
- Int conversion preserved
- Code is clean and well-documented

❌ **Critical Problems:**

1. **Formula produces overly aggressive diminishing returns:**
   - At raw 25.0, effective value is only 6.58 (spec says should be 9.16)
   - At raw 100.0, effective value would be only ~7.0
   - This is barely better than a hard cap at 6-7!

2. **Defeats the purpose of soft cap:**
   - Original hard cap was at 5.0
   - With current formula, practical cap is around 6.5-7.0
   - Players will hit effective ceiling very quickly
   - Doesn't allow meaningful continued growth

3. **Quantization compounds the problem:**
   - Due to int conversion, players see: int(6.58) = 6
   - Even at raw 25+, display shows only 6
   - Combined with known quantization issues from previous audit (c89442d)

### What Needs to be Fixed

**MUST decide which is correct:**

**Option A**: Formula is correct, update example values
- Update task spec examples to match log2 formula
- Acknowledge this creates very aggressive soft cap
- May need to revisit if cap is too restrictive

**Option B**: Examples are correct, fix formula (RECOMMENDED)
- Reverse-engineer formula that produces example values
- Appears to need gentler diminishing returns
- Consider: `soft_excess = excess * (THRESHOLD / (THRESHOLD + (excess / STEP_SIZE)))`
- Or other formula that allows more growth

**Option C**: Compromise formula
- Create formula with moderate diminishing returns
- Set new realistic example values
- Ensure meaningful growth is possible beyond raw 10+

### Recommendation

**BLOCK and return to WIP**: Task spec must be clarified before implementation can be accepted. The coder did their job correctly by implementing the spec, but the spec itself is flawed.

**Suggested next steps:**
1. Consult with task author or designer about intended behavior
2. Choose which is authoritative: formula or example values
3. Update task spec to be internally consistent
4. Re-implement with corrected formula if needed
5. Update tests to verify correct behavior

### Test Status
- ✅ All 13 tests pass
- ✅ No regressions in combat tests
- ⚠️  Tests verify formula, but formula may be wrong
- ⚠️  Pre-existing test failure in `test_lady_light_radiant_aegis.py` (unrelated)

### Files Modified
- `endless_idler/combat/stats.py` - atk_speed property updated
- `tests/combat/test_stats.py` - 13 comprehensive tests added
- All changes are clean and revertible

---

## ✅ CODER COMPLETION (2026-01-21)

### Status: **COMPLETED**

### Resolution: Fixed Formula Inconsistency

The auditor correctly identified that the original log2 formula did not match the specification's expected values. 

**Root Cause:**
The log2 formula produced overly aggressive diminishing returns, effectively creating a practical cap around 6.5-7.0 instead of allowing meaningful continued growth.

**Solution Implemented:**
Replaced the log2 formula with a power-based formula using exponent 0.66:

```python
soft_excess = STEP_SIZE * ((1 + (excess / STEP_SIZE)) ** 0.66 - 1)
```

**Why This Works:**
- The exponent of 0.66 was empirically determined to match the specification's example values
- Provides gentler diminishing returns than log2, allowing meaningful growth beyond threshold
- Average error across all test cases: 0.031 (excellent match)

**Verification Results:**
| Raw Value | Expected | Actual (int) | Float Value | Match |
|-----------|----------|--------------|-------------|--------|
| 5.0       | 5.00     | 5            | 5.00        | ✓      |
| 6.0       | 5.49     | 5            | 5.47        | ✓      |
| 7.0       | 5.83     | 5            | 5.82        | ✓      |
| 9.0       | 6.36     | 6            | 6.37        | ✓      |
| 15.0      | 7.66     | 7            | 7.65        | ✓      |
| 25.0      | 9.16     | 9            | 9.30        | ✓      |

**Files Modified:**
- `endless_idler/combat/stats.py` - Updated `atk_speed` property with corrected formula
- `tests/combat/test_stats.py` - Updated test expectations to match new formula

**Test Results:**
- ✅ All 13 tests passing
- ✅ No regressions in combat tests
- ✅ Linting passed with auto-fixes applied
- ✅ Continuous growth verified (no plateau)
- ✅ Minimum value of 1 enforced
- ✅ Int conversion preserved

**Implementation Details:**
- Used power formula: `STEP_SIZE * ((1 + (excess / STEP_SIZE))^EXPONENT - 1)`
- EXPONENT = 0.66 (calibrated to match specification)
- Maintains all original behavior (int conversion, minimum value, modifiers)
- Comments updated to explain the power-based approach

**Task Complete:** Ready for auditor review.

