# Test Battle Screen Without Animations

## Description
Thoroughly test the battle screen with animations disabled to ensure:
1. Stack merge animations still work correctly
2. Battle functionality remains intact
3. No visual glitches or errors occur
4. Performance is acceptable

## Requirements
- Run the game with the animation flag set to `False`
- Test multiple battles with different party compositions
- Verify stack merge functionality in party builder works normally
- Check for any console errors or warnings
- Observe battle flow and UI responsiveness
- Verify characters still attack, take damage, and die properly
- Test edge cases (criticals, healing, multi-target attacks)

## Acceptance Criteria
- [ ] Multiple battles completed successfully without visual artifacts
- [ ] Stack merge animations display correctly (arrows still appear)
- [ ] No console errors or exceptions during battle
- [ ] Battle mechanics function correctly (damage, healing, death)
- [ ] UI remains responsive and stable
- [ ] Visual appearance is acceptable without the lines/arrows
- [ ] Performance is good (no lag or stuttering)

## Implementation Context

### Files Involved
- **Configuration**: Location where animation flag is stored (to be created in task c27c66d4)
- **LineOverlay class**: `endless_idler/ui/battle/widgets.py` (lines 263-450+)
  - `paintEvent()` method (line 318+) - where conditional rendering will be added
- **Battle Screen**: `endless_idler/ui/battle/screen.py`
  - Calls to `add_pulse()` at lines: 479, 557, 590, 648, 694, 702
- **Party Builder Merge FX**: `endless_idler/ui/party_builder_merge_fx.py`
  - `MergeArrow` class (lines 20-65) - should NOT be affected by battle animation flag

### What Should Be Disabled
When animation flag is `False`, the following should NOT render:
- Attack line pulses (regular attacks from line 557, 590, 648, 702)
- Healing arrow animations (same-team effects from line 479)
- Critical hit visual effects (thick lines with `crit=True`)
- Wrong-way healing animations (4-segment paths with `wrong_target` parameter)

### What Should Still Work
- Stack merge arrows in Party Builder (`MergeArrow` class in `party_builder_merge_fx.py`)
- Battle mechanics (damage calculation, health updates, death)
- `LineOverlay.tick()` method for cleanup (line 306)
- Arena layout and combatant cards

### Testing Approach
1. Launch game: `DISPLAY=:1 uv run python main.py` (or `python main.py`)
2. Navigate to party builder and verify merge arrows appear when stacking characters
3. Start a battle and verify NO lines/arrows appear during combat
4. Test various battle scenarios (see test scenarios below)
5. Check terminal output for errors/warnings

## Notes
Dependencies: This task requires completion of tasks:
- `c27c66d4-add-config-flag-for-battle-animations`
- `95f5b1c9-implement-conditional-rendering-in-lineoverlay`

If any issues are found during testing, document them clearly and move this task back to WIP with detailed findings. Create follow-up tasks for any bugs discovered.

Test scenarios to cover:
- Basic combat (single target attacks)
- Healing abilities (light element characters)
- Multi-target attacks
- Critical hits
- Character deaths
- Boss battles
- Stack merges in party builder (verify NOT affected - arrows should still appear)
- Wrong-way healing scenarios (if applicable)

## Status Updates
- 2025-01-11: Task created by Task Master
- 2025-01-11: Enhanced with file paths and implementation context (Auditor)
