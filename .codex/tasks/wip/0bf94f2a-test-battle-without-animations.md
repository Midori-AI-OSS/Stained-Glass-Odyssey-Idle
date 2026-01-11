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

## Notes
Dependencies: This task requires completion of tasks:
- `c27c66d4-add-config-flag-for-battle-animations`
- `95f5b1c9-implement-conditional-rendering-in-lineoverlay`

If any issues are found during testing, document them clearly and move this task back to WIP with detailed findings. Create follow-up tasks for any bugs discovered.

Test scenarios to cover:
- Basic combat (single target attacks)
- Healing abilities
- Multi-target attacks
- Critical hits
- Character deaths
- Boss battles
- Stack merges in party builder (verify NOT affected)

## Status Updates
- 2025-01-11: Task created by Task Master
