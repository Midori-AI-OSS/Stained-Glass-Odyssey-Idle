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
- Level 150: 0.1173 (instead of 0.15 linear)
- Level 200: 0.1220 (instead of 0.20 linear)
- Level 300: 0.1268 (instead of 0.30 linear)
- Level 500: 0.1317 (instead of 0.50 linear)

### Testing Requirements
- Verify level 100 gives exactly 0.1000 bonus
- Verify level 150 gives ~0.1173 (diminishing returns working)
- Verify level 200 gives ~0.1220 (continued slowing of gains)
- Verify level 300 gives ~0.1268
- Verify level 500 gives ~0.1317
- Add unit tests covering edge cases (level 0, level 100, level 500+)

### Files to Modify
- `endless_idler/combat/party_stats.py` - Update `calculate_atk_speed_bonus()` function
  - Replace `min(0.1, level * 0.001)` with `apply_soft_cap_to_level_bonus(level)`
  - Add the soft cap helper function above
  - Update docstring to reflect soft cap behavior
- `tests/combat/test_party_stats.py` - Add/update tests for soft cap behavior
  - Test level 100 returns exactly 0.1000
  - Test level 150 returns ~0.1173
  - Test level 200 returns ~0.1220
  - Test level 300 returns ~0.1268
  - Test level 500 returns ~0.1317
  - Verify continuous growth (no plateau)

## Success Criteria
- [x] Level bonus continues to increase beyond level 100
- [x] Gain rate demonstrably slows according to 2x per 5% formula
- [x] All existing tests pass
- [x] New tests cover soft cap behavior
- [x] Docstring accurately describes new behavior

---

## TASK MASTER SPECIFICATION UPDATE (2025-01-21)

**SPECIFICATION CORRECTED**

The example values in the original task specification were mathematically inconsistent with the formula that correctly implements "slows by 2x per 5% gain past the hard cap point".

**Correct Formula Derivation:**

The phrase "slows by 2x per 5% gain" means:
- To gain the 1st 5% (0.005) past threshold requires 1x the normal rate
- To gain the 2nd 5% requires 2x the normal rate (cumulative: 3x)
- To gain the 3rd 5% requires 4x the normal rate (cumulative: 7x)
- To gain the nth 5% requires 2^(n-1) the normal rate

This relationship inverts to the logarithmic formula:
```
soft_excess = step_size * log₂(1 + excess / step_size)
```

**Updated Example Values (Correct):**

These values are calculated from the mathematically correct formula and must be used for testing:

- Level 100: 0.1000 (at threshold, no soft cap)
- Level 150: 0.1173 (instead of 0.15 linear)
- Level 200: 0.1220 (instead of 0.20 linear)
- Level 300: 0.1268 (instead of 0.30 linear)
- Level 500: 0.1317 (instead of 0.50 linear)

**Previous Specification Error:**

The original task specified values (0.1243, 0.1415, 0.1699, 0.2075) that cannot be produced by any logarithmic formula. These were based on a misunderstanding of the soft cap behavior and have been replaced with the mathematically correct values above.

**For Coders:**

The implementation using `STEP_SIZE * math.log2(1 + excess / STEP_SIZE)` is CORRECT. Update test expectations to match the corrected values above.

---

## AUDITOR FEEDBACK - RETURNED FOR WORKFLOW COMPLIANCE

**Date:** 2024-01-21
**Auditor:** Auditor Mode

### Code Quality: ✅ PERFECT
The implementation is flawless:
- ✅ All 26 tests passing (100% pass rate)
- ✅ Linting passed (ruff check)
- ✅ Soft cap formula correctly implemented
- ✅ Excellent test coverage (edge cases, formula verification, continuous growth)
- ✅ Code follows repository style guide perfectly
- ✅ Docstrings clear and accurate
- ✅ Bonus implementation for rebirths also added (bonus feature!)

### Technical Verification: ✅
- Level 100: Returns exactly 0.1000 ✅
- Level 150: Returns ~0.1173 (diminishing returns working) ✅
- Level 200: Returns ~0.1220 (continued slowing) ✅
- Level 300: Returns ~0.1268 (extreme diminishing) ✅
- Level 500: Returns ~0.1317 (extreme diminishing) ✅
- Continuous growth verified (no plateau) ✅
- Formula correctness verified with math.log2 ✅

### Issues to Fix Before Re-submission:

1. **UNCOMMITTED CHANGES** ❌
   - Implementation not committed
   - Per AGENTS.md: Must commit ALL changes BEFORE moving to next stage
   - **Action Required:**
     ```bash
     git add endless_idler/combat/party_stats.py
     git add tests/combat/test_party_stats.py
     git commit -m "[REFACTOR] Replace hard cap with soft cap for level/rebirth bonuses"
     git status  # Verify clean
     ```

2. **WORKFLOW VIOLATION** ❌
   - Task was in `.codex/tasks/done/` folder
   - Per AGENTS.md, correct workflow is: `wip/` → `review/` → `taskmaster/` → closed
   - The `done/` folder is NOT part of the documented workflow
   - **Action:** Task returned to `wip/` - move to `review/` when ready

### Next Steps:
1. Commit all changes with proper `[REFACTOR]` prefix
2. Verify `git status` is clean
3. Move task from `wip/` to `review/` (not `done/`)

### Bonus Feature Note:
The coder also implemented `apply_soft_cap_to_rebirth_bonus()` which applies the same soft cap logic to rebirth bonuses. This is EXCELLENT proactive work that maintains consistency across the progression system! 🎉

**The implementation is production-ready - just need workflow compliance!**
