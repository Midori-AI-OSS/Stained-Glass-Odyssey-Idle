# Implement Conditional Rendering in LineOverlay

## Description
Modify the `LineOverlay` class to check the configuration flag before rendering battle animations. When the flag is `False`, skip all line and arrow rendering.

## Requirements
- Modify the `paintEvent` method in `LineOverlay` class (`/endless_idler/ui/battle/widgets.py`)
- Add an early return when the configuration flag is `False`
- Ensure the method still handles cleanup (removing expired pulses) even when not rendering
- Keep the tick mechanism working (pulse expiration must continue)

## Acceptance Criteria
- [ ] `paintEvent` checks configuration flag at the start
- [ ] When flag is `False`, no lines or arrows are drawn
- [ ] Pulse list is still cleaned up properly (expired pulses removed)
- [ ] Timer and tick mechanism continues to function
- [ ] No visual artifacts or errors when animations are disabled
- [ ] Code is clean and well-commented

## Notes
Dependencies: This task requires completion of task `c27c66d4-add-config-flag-for-battle-animations`.

The key is to skip the painting logic while still maintaining the underlying animation state management. This prevents memory leaks and ensures the system remains stable.

Focus on modifying the `paintEvent` method around line 318 in `/endless_idler/ui/battle/widgets.py`.

## Status Updates
- 2025-01-11: Task created by Task Master
