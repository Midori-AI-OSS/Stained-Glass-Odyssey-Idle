# Task: Run Loss Clarity and Stale Run Menu Fix

## Category
UI/UX / Game Flow

## Priority
Medium

## Description
Improve the user experience when a run is lost by adding clear feedback and properly cleaning up the game state to prevent stale run data from persisting.

## Requirements

### Run Loss Feedback
- Show a popup or toast notification when a run is lost
- Clearly indicate that the run has ended
- Optionally show run statistics (time survived, level reached, etc.)

### Post-Loss Flow
- Automatically return to main menu after run loss
- Clear the stale run from the run menu/state
- Ensure no leftover state from the lost run persists
- Reset any combat/run-specific state appropriately

### Implementation Details
- Detect when a run loss occurs (character death, fail condition, etc.)
- Display clear feedback to the player
- Clean up run state completely
- Return to main menu or appropriate screen
- Ensure save data doesn't contain stale run information

### Acceptance Criteria
- [ ] Popup/toast is shown when run is lost
- [ ] Feedback clearly indicates the run has ended
- [ ] Player is returned to main menu after run loss
- [ ] Stale run data is cleared from game state
- [ ] Run menu doesn't show the lost run
- [ ] No leftover state causes issues for next run
- [ ] Save data is properly updated

## Related Tasks
None

## Technical Notes
This improves the player experience by providing clear feedback about what happened and ensuring a clean slate for the next run. Consider adding optional run statistics to the loss popup to give players feedback on their performance.

## Dependencies
None

## Estimated Complexity
Medium

## Completion Notes

**Status:** ✅ Complete  
**Commit:** a8c6251  
**Date:** 2025-01-11

### Implementation Summary
Improved user experience when a run is lost:
- Added defeat popup using QMessageBox to show clear feedback
- Displays run statistics: fight number reached, foes defeated in final battle
- Auto-returns to main menu after popup dismissal with smooth 100ms transition
- Stale run clearing already handled by existing reset logic (no changes needed)

### Post-Loss Flow
1. Battle detects defeat condition
2. Status label shows "Defeat"
3. Defeat popup displays with run statistics
4. User acknowledges by clicking OK
5. Automatic return to main menu after 100ms delay
6. Stale run data cleared (existing functionality in lines 735-760)

### Acceptance Criteria Met
- [x] Popup/toast is shown when run is lost
- [x] Feedback clearly indicates the run has ended
- [x] Player is returned to main menu after run loss
- [x] Stale run data is cleared from game state (existing)
- [x] Run menu doesn't show the lost run (existing)
- [x] No leftover state causes issues for next run (existing)
- [x] Save data is properly updated (existing)

### Files Modified
- `endless_idler/ui/battle/screen.py` (defeat popup and auto-return)

### Technical Details
- Used `QMessageBox` for cross-platform compatible popup
- Connected `finished` signal for auto-return flow
- Non-blocking popup with smooth transition
- Maintains existing state management and save logic
