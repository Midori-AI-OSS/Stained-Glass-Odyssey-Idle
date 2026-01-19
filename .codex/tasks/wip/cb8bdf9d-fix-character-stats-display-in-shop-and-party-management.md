# Fix Character Stats Display in Shop and Party Management

## Issue Reference
Part of: Fix tooltip styling, correct character stats display outside combat, and normalize off-site character experience and tooltips

## Problem
Characters in the Shop and Party Management screens always show as level 1, regardless of their actual progression. This creates confusion and makes it impossible to see character growth when managing the party.

## Current State
- File: `endless_idler/ui/party_builder_slot.py`
- The `get_tooltip_stats` callback is used to fetch stats for tooltips
- Stats are likely being generated with default values instead of loading saved progression data

## Requirements
1. Shop screen must display real character stats (level, experience, multipliers)
2. Party Management screen must display real character stats
3. Use the same source of truth for character data across all modes
4. Do not display placeholder values like always showing level 1

## ⚠️ AUDITOR BLOCK: Investigation Required Before Implementation

**Finding:** The code ALREADY loads character progression correctly!

**Evidence from `party_builder.py` lines 846-866:**
1. Line 864: `progress=self._save.character_progress.get(char_id)` - loads saved progress
2. Line 865: `saved_base_stats=self._save.character_stats.get(char_id)` - loads saved stats

**Evidence from `combat/party_stats.py`:**
1. Lines 107-119 in `apply_progress_meta()`: Correctly applies level, exp, and exp_multiplier from progress dict
2. This function is called at line 164 of `build_scaled_character_stats()`

**Possible Issues:**
1. The save data might not be populated correctly (check if `character_progress` is being saved)
2. There might be a display/rendering issue, not a data loading issue
3. The problem might only occur in specific scenarios (new game, after certain actions)
4. The tooltip might be caching old data and not refreshing

**⚠️ MANDATORY Investigation Steps - DO THESE FIRST:**
1. **Run the game** and manually verify the issue still exists:
   - Level up a character in combat/idle
   - Go to Shop screen → hover over character → check level shown
   - Go to Party Management → hover over character → check level shown
   - **If levels show correctly, CLOSE THIS TASK - it's already fixed**
   
2. **If issue confirmed**, add debug logging:
   ```python
   # In party_builder.py, _tooltip_stats_for_character method
   print(f"DEBUG: Loading stats for {char_id}")
   print(f"  Progress: {self._save.character_progress.get(char_id)}")
   print(f"  Stats: {self._save.character_stats.get(char_id)}")
   print(f"  Built level: {final_stats.level}")
   ```

3. Test in both shop and party management screens separately

4. Check if tooltip is cached and not refreshing on stat changes

### Implementation Phase
1. In `endless_idler/ui/party_builder.py` and related files:
   - Locate where character stats are built for tooltips
   - Ensure saved progression data from `RunSave.character_stats` and `RunSave.character_progress` is loaded
   - Pass the real level, exp, exp_multiplier values when building stats

2. Verify these files use saved data:
   - `endless_idler/ui/party_builder_common.py` - the `build_character_stats_tooltip()` function
   - `endless_idler/ui/party_builder_slot.py` - tooltip generation
   - `endless_idler/ui/party_builder_bar.py` - shop items

3. Look at `endless_idler/combat/party_stats.py` for reference on how combat loads character stats correctly

## Testing
1. Level up a character in combat or idle mode
2. Return to Shop screen - verify character shows correct level
3. Open Party Management - verify character shows correct level and exp
4. Verify exp_multiplier displays correctly if it's shown
5. Test with multiple characters at different levels

## Success Criteria
- [ ] Shop screen shows actual character levels, not always level 1
- [ ] Party Management screen shows actual character levels
- [ ] Experience values are displayed correctly
- [ ] Experience multipliers are displayed correctly (if shown)
- [ ] Stats match what's shown in combat/idle modes
- [ ] All character progression data persists correctly

## Files to Investigate/Modify
- `endless_idler/ui/party_builder_slot.py` (tooltip stats generation)
- `endless_idler/ui/party_builder.py` (main party builder logic)
- `endless_idler/ui/party_builder_bar.py` (shop bar)
- `endless_idler/ui/party_builder_common.py` (shared tooltip building)
- `endless_idler/save.py` (saved stats reference)
- `endless_idler/combat/party_stats.py` (reference implementation)

## Notes
- This is part B of the main issue requirements
- The combat system already loads character stats correctly - use that as a reference
- Character progression data is in `save.character_stats` and `save.character_progress`
