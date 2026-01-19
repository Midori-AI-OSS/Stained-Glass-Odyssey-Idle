# Verify Tooltip Styling Consistency Across All Screens

## Issue Reference
Part of: Fix tooltip styling, correct character stats display outside combat, and normalize off-site character experience and tooltips

## Problem
After fixing the tooltip styling (square corners and blur), we must verify that the changes apply everywhere tooltips appear in the application. The requirement states "Apply the same tooltip style everywhere tooltips exist in the application: Do not fix only one screen."

## ⚠️ BLOCKED - Dependencies Must Complete First

**This task is BLOCKED until:**
- Task `87abfe35-fix-tooltip-styling-square-corners-and-blur.md` is completed
- **Check `.codex/tasks/wip/` and `.codex/tasks/review/` for the dependent task**
- **DO NOT START** this verification task until the base styling is implemented

## Current State
All tooltips use the centralized `StainedGlassTooltip` class from `endless_idler/ui/tooltip.py`, so changes should automatically propagate everywhere. However, we need to verify this is actually the case.

## Requirements
1. Verify all tooltips use the centralized `StainedGlassTooltip` system
2. Confirm square corners appear on all screens
3. Confirm background blur appears on all screens
4. Check for any custom tooltip implementations that bypass the central system
5. Document any screens that don't use the centralized tooltip

## Screens to Verify

### Main Screens
1. **Main Menu** (`endless_idler/ui/main_menu.py`)
   - Check if any tooltips appear here

2. **Shop Screen / Party Builder** (`endless_idler/ui/party_builder.py`, `party_builder_bar.py`, `party_builder_slot.py`)
   - Character cards in shop
   - Drop slots in party composition
   - Verify character stat tooltips

3. **Battle / Fight Mode** (`endless_idler/ui/battle/screen.py`, `battle/widgets.py`)
   - On-site character cards
   - Off-site/reserve character cards (after task `e283d8ff` is complete)
   - Enemy cards

4. **Idle Mode** (`endless_idler/ui/idle/screen.py`, `idle/widgets.py`)
   - Off-site character cards (after task `d7fb182a` is complete)
   - Any other UI elements with tooltips

5. **Party Management Screens**
   - Party builder idle bar (`party_builder_idle_bar.py`)
   - Party builder fight bar (`party_builder_fight_bar.py`)
   - On-site stat bars (`onsite/stat_bars.py`, `onsite/card.py`)

## Technical Approach

### Phase 1: Verify Centralized Usage
```bash
# Find all tooltip imports
grep -r "show_stained_tooltip\|StainedGlassTooltip" endless_idler/ui/

# Find any custom tooltip implementations
grep -r "setToolTip\|QToolTip" endless_idler/ui/
```

### Phase 2: Manual Testing Checklist
For each screen listed above:
1. Load the screen
2. Hover over elements that should have tooltips
3. Verify tooltip appears with:
   - Square corners (no rounding)
   - Blurred background
   - Readable text
   - Correct positioning
   - Proper element tinting (if applicable)

### Phase 3: Edge Case Testing
1. Test tooltips near screen edges (verify positioning still works)
2. Test on different screen resolutions
3. Test with multiple tooltips in quick succession
4. Test tooltip appearance/disappearance transitions

### Phase 4: Documentation
Create a checklist of all verified screens and document results:
```markdown
## Verification Results

### Screens Using Centralized Tooltip System
- [ ] Shop Screen - VERIFIED / ISSUES FOUND
- [ ] Party Builder - VERIFIED / ISSUES FOUND
- [ ] Battle Mode (onsite) - VERIFIED / ISSUES FOUND
- [ ] Battle Mode (offsite) - VERIFIED / ISSUES FOUND
- [ ] Idle Mode - VERIFIED / ISSUES FOUND
- [ ] Party Management - VERIFIED / ISSUES FOUND

### Custom Tooltip Implementations Found
(List any screens that don't use StainedGlassTooltip)

### Issues Found
(Document any styling inconsistencies)
```

## Expected Outcome
Since all screens import from `endless_idler/ui/tooltip.py` and use `show_stained_tooltip()`, the styling changes should automatically apply everywhere. This task is primarily verification and catching any edge cases.

## Success Criteria
- [ ] All tooltips verified to use `StainedGlassTooltip` from `tooltip.py`
- [ ] Square corners confirmed on all screens with tooltips
- [ ] Background blur confirmed on all screens with tooltips
- [ ] No custom tooltip implementations found that bypass the central system
- [ ] All tooltips remain readable and properly positioned
- [ ] Element tinting still works correctly where applicable
- [ ] Documentation of verification results completed

## Files to Review
- `endless_idler/ui/*.py` (all UI files)
- `endless_idler/ui/battle/*.py`
- `endless_idler/ui/idle/*.py`
- `endless_idler/ui/onsite/*.py`
- Any file that imports `show_stained_tooltip` or `StainedGlassTooltip`

## Testing Commands
```bash
# Find all tooltip usage
cd /home/midori-ai/workspace
grep -rn "show_stained_tooltip" endless_idler/ui/ | wc -l

# Find non-standard tooltip usage
grep -rn "setToolTip\|QToolTip" endless_idler/ui/

# Run the application and test each screen
uv run python -m endless_idler
```

## Notes
- This is part A requirement #4 from the main issue
- **This is a VERIFICATION/QA task, not an implementation task**
- **Task type: Manual Testing** - requires running the application
- If custom tooltips are found, they should be migrated to use `StainedGlassTooltip`
- Document any legitimate reasons why a screen might need custom tooltips
- **BLOCKED** - cannot complete until dependent task 87abfe35 is done
- **Estimated time**: 30-60 minutes of manual testing across all screens
