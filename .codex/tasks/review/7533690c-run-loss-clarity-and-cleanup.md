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
