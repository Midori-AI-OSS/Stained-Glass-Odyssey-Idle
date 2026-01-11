# Locate Experience Calculation Source of Truth

**Priority:** High  
**Status:** New  
**Category:** Investigation / Experience System  
**Task ID:** 94715ad3  
**Date Created:** 2026-01-11

## Problem Statement

The passive modifier for experience must be applied exactly once to all experience gained. To implement this correctly, we need to identify the single best source of truth location where experience is computed or awarded.

## Requirements

1. Search the codebase for all locations where experience is awarded to players or characters
2. Identify the common entry point or calculation function
3. Document all experience gain events:
   - Kill/defeat rewards
   - Timed tick rewards
   - End-of-fight rewards
   - Any other experience-granting events
4. Determine the single best location to apply the multiplier formula

## Expected Formula

```
final_experience_gained = base_experience_gained * experience_multiplier * passive_modifier
```

- `base_experience_gained`: Raw experience value before any modifiers
- `experience_multiplier`: Existing multiplier(s) in the system
- `passive_modifier`: New passive modifier to be applied

## Investigation Steps

1. Search for experience-related functions (grep for "exp", "experience", "xp", "award", etc.)
2. Trace the flow from experience source to player stats update
3. Identify if there's a centralized function or if experience is awarded in multiple places
4. Check for existing multipliers and how they're applied
5. Document findings in this task file

## Deliverables

- [ ] List of all files/functions that award experience
- [ ] Diagram or description of experience flow
- [ ] Recommendation for where to implement the passive modifier
- [ ] Notes on existing multiplier implementations
- [ ] Confirmation that chosen location will catch ALL experience events

## Success Criteria

- Single source of truth identified
- All experience gain paths documented
- Clear recommendation provided for implementation location
- No risk of duplicate multiplier application

## Notes

- This is a prerequisite task for implementing the passive modifier
- Must ensure the multiplier is applied exactly once, not in multiple layers
- The goal is to avoid fragmentation and maintain a single calculation point
