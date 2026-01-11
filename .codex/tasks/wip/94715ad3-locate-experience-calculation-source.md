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

- [x] List of all files/functions that award experience
- [x] Diagram or description of experience flow
- [x] Recommendation for where to implement the passive modifier
- [x] Notes on existing multiplier implementations
- [x] Confirmation that chosen location will catch ALL experience events

## Success Criteria

- [x] Single source of truth identified
- [x] All experience gain paths documented
- [x] Clear recommendation provided for implementation location
- [x] No risk of duplicate multiplier application

## Investigation Results

### Files That Award Experience

**Primary Source:** `endless_idler/ui/idle/idle_state.py`
- `_process_tick()` (lines 447-500): Awards experience to onsite and offsite characters during idle ticks
- `get_exp_gain_per_tick()` (lines 514-561): Calculates experience per tick for display/preview

**No other locations found** that directly modify character experience values.

### Experience Flow Diagram

```
Idle Game Loop (every 0.1s)
  └─> IdleGameState._process_tick()
      ├─> For each ONSITE character:
      │   ├─> base_gain = data["exp_multiplier"]
      │   ├─> base_gain *= (risk_reward_level + 1)  [if risk_reward > 0]
      │   ├─> base_gain *= exp_multiplier  [win/loss bonus]
      │   ├─> base_gain *= death_exp_debuff_multiplier
      │   ├─> base_gain *= self._exp_gain_scale
      │   ├─> onsite_gain = base_gain * onsite_mult  [shared exp reduction]
      │   └─> data["exp"] += onsite_gain
      │
      └─> For each OFFSITE character:
          ├─> Calculate total shared from onsite
          ├─> Add normal offsite share
          ├─> total_gain *= death_exp_debuff_multiplier
          └─> data["exp"] += total_gain
```

### Existing Multiplier System

Current multipliers applied in order:
1. **Character exp_multiplier** - Base per-character multiplier from stats
2. **Risk/Reward multiplier** - (risk_reward_level + 1) if enabled
3. **Win/Loss multiplier** - 4.0x for wins, 0.5x for losses
4. **Death debuff multiplier** - Reduction based on death stacks (5% per stack)
5. **Global exp_gain_scale** - Overall scaling factor
6. **Shared exp multiplier** - Reduction for onsite based on sharing percentage

### Passive Modifier Status

The `passive_modifier` field exists in `Stats` class and is populated:
- `combat/party_stats.py:139` - Formula: `(stacks * 0.05) + 1.0`
- `ui/party_builder_common.py:155` - Formula: `1.5 ** max(0, int(stacks) - 1)`
- `ui/battle/sim.py:152` - Default: `1.0`

However, **passive_modifier is NOT currently applied to experience calculations**.

It IS used in:
- `passives/implementations/lady_light_radiant_aegis.py:64` - Applied to regain for healing

## Recommendation: Implementation Location

**RECOMMENDED: Modify `_process_tick()` in `idle_state.py`**

Add `passive_modifier` multiplication at **lines 458-460** (onsite) and **line 497** (offsite).

### Rationale:
1. ✅ **Single source of truth** - All experience flows through this function
2. ✅ **Catches all events** - Both onsite and offsite experience
3. ✅ **Clear insertion point** - After base calculations, before assignment
4. ✅ **No double application** - Applied exactly once per gain event
5. ✅ **Consistent with existing multipliers** - Follows established pattern

### Specific Changes Needed:

**Location 1:** Lines 458-460 (onsite characters)
```python
base_gain *= exp_multiplier
base_gain *= self._death_exp_debuff_multiplier(data)
base_gain *= self._exp_gain_scale
# ADD HERE: base_gain *= data.get("passive_modifier", 1.0)
```

**Location 2:** Line 497 (offsite characters)
```python
data["exp"] += total_gain * self._death_exp_debuff_multiplier(data)
# CHANGE TO: 
# passive_mod = data.get("passive_modifier", 1.0)
# data["exp"] += total_gain * self._death_exp_debuff_multiplier(data) * passive_mod
```

## Notes

- This is a prerequisite task for implementing the passive modifier
- Must ensure the multiplier is applied exactly once, not in multiple layers
- The goal is to avoid fragmentation and maintain a single calculation point
- **STATUS:** Investigation complete, ready for implementation phase
