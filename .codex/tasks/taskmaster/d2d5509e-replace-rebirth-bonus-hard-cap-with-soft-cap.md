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

---

## AUDITOR REVIEW (2025-01-21)

**APPROVED - READY FOR TASK MASTER CLOSURE**

### Implementation Review

✅ **Code Quality**
- Hard cap `min(0.2, rebirths * 0.002)` successfully removed from `calculate_atk_speed_bonus()`
- Soft cap function `apply_soft_cap_to_rebirth_bonus()` correctly implements logarithmic diminishing returns
- Formula matches specification: `STEP_SIZE * math.log2(1 + excess / STEP_SIZE)`
- Constants correctly set: `THRESHOLD = 0.2`, `STEP_SIZE = 0.01` (5% of threshold)
- Function properly handles edge cases (rebirth 0, negative inputs clamped)
- Docstrings accurately describe behavior

✅ **Mathematical Correctness**
- Rebirth 100: 0.2000 (at threshold) ✓
- Rebirth 150: 0.2346 (vs 0.30 linear) ✓
- Rebirth 200: 0.2439 (vs 0.40 linear) ✓
- Rebirth 300: 0.2536 (vs 0.60 linear) ✓
- Rebirth 500: 0.2634 (vs 1.00 linear) ✓
- All values verified with independent calculation
- Continuous growth confirmed (no plateau)

✅ **Test Coverage**
- 26 tests total: all passing
- Comprehensive edge case coverage (0, 1, 99, 100, 101 rebirths)
- Continuous growth validation (no plateau at any level)
- Formula correctness verification tests
- Combined bonus tests (level + rebirth)
- Negative input handling verified
- 47 related tests across codebase: all passing

✅ **Integration**
- Function integrated into `apply_progress_meta()` via `calculate_atk_speed_bonus()`
- Applied as permanent `StatEffect` with name "progression_atk_speed"
- Works correctly with existing level bonus soft cap
- All downstream systems functioning correctly

✅ **Repository Standards**
- Follows Python style guide (imports sorted, typed, documented)
- File size reasonable (~309 lines)
- Code is well-commented and readable
- Commit history shows proper iteration and correction cycle
- Task specification was corrected by Task Master to fix mathematical inconsistency

### Security & Performance
- No security concerns identified
- Mathematical operations are lightweight (single log2 call)
- No blocking operations or I/O
- Performance impact negligible

### Verification Steps Completed
1. ✅ Reviewed all code changes in `endless_idler/combat/party_stats.py`
2. ✅ Verified hard cap removed, soft cap correctly implemented
3. ✅ Ran all 26 party_stats tests - all passed
4. ✅ Ran all 47 related atk_speed tests - all passed
5. ✅ Independently verified mathematical correctness with Python script
6. ✅ Verified continuous growth (no plateau)
7. ✅ Checked edge cases (0, 1, 99, 100, 101, 500+ rebirths)
8. ✅ Verified integration with existing systems
9. ✅ Reviewed commit history for completeness
10. ✅ Confirmed no regressions in related tests

### Recommendation
**APPROVE** - Task is complete, implementation is correct, all tests pass, and the soft cap behaves exactly as specified. Ready for Task Master final closure.

**Audited by:** Auditor Mode  
**Date:** 2025-01-21  
**Confidence:** HIGH
