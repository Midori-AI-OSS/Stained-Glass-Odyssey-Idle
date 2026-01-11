# Verify All Experience Events Use Updated Formula

**Priority:** High  
**Status:** Blocked (depends on e7e40e77)  
**Category:** Verification / Experience System  
**Task ID:** a4516cc1  
**Date Created:** 2026-01-11

## Problem Statement

After implementing the passive modifier in the experience calculation (task e7e40e77), verify that ALL experience gain events throughout the game use the updated formula. This ensures no experience source bypasses the passive modifier.

## Prerequisites

- Task 94715ad3 completed (source of truth identified)
- Task e7e40e77 completed (passive modifier implemented)

## Requirements

1. Verify all experience gain events use the updated calculation:
   - Kill/defeat rewards
   - Timed tick rewards (idle/incremental gains)
   - End-of-fight bonuses
   - Quest/mission completion rewards
   - Achievement rewards
   - Any other experience sources

2. Check for any direct experience assignments that bypass the calculation function

3. Test each experience source with passive modifier active

4. Document any experience sources that were missed or need special handling

## Verification Steps

1. **Code Review:**
   - Search codebase for all exp/experience assignment operations
   - Verify each goes through the centralized calculation function
   - Check for any direct stat modifications that bypass the formula
   - Look for patterns like `player.exp +=`, `stats.experience =`, etc.

2. **Runtime Testing:**
   - Enable passive modifier
   - Trigger each experience gain event type
   - Verify multiplier is applied in each case
   - Check logs/debug output for calculation details

3. **Edge Case Testing:**
   - Multiple experience sources in quick succession
   - Experience gain while passive modifier changes
   - Experience gain with multiple passives active
   - Experience gain from background/idle processes

## Expected Behavior

For every experience gain event:
```
✓ Experience calculated using: base_exp * experience_multiplier * passive_modifier
✓ Passive modifier applied exactly once
✓ Final experience amount is correct
✓ No direct bypasses of the calculation function
```

## Testing Checklist

- [ ] **Kill rewards:** Defeat enemy, verify exp uses passive modifier
- [ ] **Timed ticks:** Wait for idle/incremental tick, verify exp uses modifier
- [ ] **End-of-fight:** Complete combat, verify end-of-fight exp uses modifier
- [ ] **Quest completion:** Complete quest (if applicable), verify exp uses modifier
- [ ] **Achievement unlock:** Unlock achievement (if applicable), verify exp uses modifier
- [ ] **Other sources:** Test any other identified experience sources
- [ ] **No bypasses:** Confirm no direct experience assignments found in code
- [ ] **Edge cases:** Multiple sources, timing issues, concurrent gains all work

## Files to Review

- All files identified in task 94715ad3 as granting experience
- Combat/battle system files
- Idle/incremental tick handlers
- Quest/mission system files
- Achievement system files
- Any reward distribution code

## Deliverables

- [ ] List of all verified experience sources with test results
- [ ] Documentation of any sources that needed fixes
- [ ] Confirmation that no bypasses exist
- [ ] Test report showing passive modifier working for all sources

## Success Criteria

- All experience gain events use the updated formula
- No direct experience assignments bypass the calculation
- Passive modifier applies correctly in all scenarios
- No double-application or missing applications found
- Edge cases handled properly
- Documentation updated with verification results

## Rollback Plan

If issues are found:
1. Document which sources are problematic
2. Create new tasks for fixing bypasses
3. Consider reverting e7e40e77 if fundamental architecture issue found
4. Update task 94715ad3 if source of truth was incorrectly identified

## Notes

- This is a critical verification step to ensure feature completeness
- Even one bypass could lead to player confusion or balance issues
- Thorough testing is essential before marking this complete
- Consider adding automated tests for each experience source
