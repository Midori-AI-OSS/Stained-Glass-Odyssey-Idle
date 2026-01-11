# Implement Conditional Rendering in LineOverlay

## Description
Modify the `LineOverlay` class to check the configuration flag before rendering battle animations. When the flag is `False`, skip all line and arrow rendering.

## Requirements
- Modify the `paintEvent` method in `LineOverlay` class (`endless_idler/ui/battle/widgets.py`)
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

## Implementation Context

### File to Modify
**Primary file**: `endless_idler/ui/battle/widgets.py`

### LineOverlay Class Structure
- **Class definition**: Line 263
- **Constructor `__init__`**: Lines 264-270
  - Initializes `self._pulses` list (line 270)
  - Sets widget attributes for transparency
- **Method `add_pulse()`**: Lines 272-304
  - Adds new animation pulses to `self._pulses` list
  - Called from Arena.add_pulse() which is called from battle/screen.py
- **Method `tick()`**: Lines 306-316
  - Decrements `pulse.remaining_ms` for each pulse
  - Removes expired pulses (line 315)
  - Called by timer - MUST continue working even when rendering disabled
- **Method `paintEvent()`**: Lines 318-450+ ⚠️ **THIS IS WHERE CHANGES ARE NEEDED**
  - Currently renders all pulses unconditionally
  - Handles complex multi-segment animations for wrong-way healing

### Configuration Flag
The configuration flag will be created in task `c27c66d4-add-config-flag-for-battle-animations`. 

**Expected implementation pattern:**
```python
# Location TBD - could be in save.py, a new config module, or as a class variable
# Example access patterns to consider:
# - Global variable: `from endless_idler.config import BATTLE_ANIMATIONS_ENABLED`
# - Save data: `self._save.battle_animations_enabled`
# - Class variable: `LineOverlay.animations_enabled`
```

**Coordinate with task c27c66d4** to determine exact flag location and access pattern.

### Implementation Approach

**Step 1**: Add configuration check at start of `paintEvent()` (after line 318):
```python
def paintEvent(self, event: object) -> None:
    if not self._pulses:
        return
    
    # TODO: Check configuration flag here
    # if not BATTLE_ANIMATIONS_ENABLED:
    #     return
    
    painter = QPainter(self)
    # ... rest of rendering code
```

**Step 2**: Ensure `tick()` method continues to work:
- The `tick()` method (lines 306-316) MUST continue running
- It removes expired pulses to prevent memory leaks
- DO NOT add flag check to tick() - let it always run

**Step 3**: Test cleanup behavior:
- Verify pulses are added but not rendered when flag is False
- Confirm pulses expire and are removed by tick()
- Ensure no memory leak from accumulating pulses

### Helper Method Reference
- `_anchor_point()`: Method that calculates widget center point for line drawing
  - Used in paintEvent to get source/target positions
  - Not needed if not rendering, but safe to leave

### Related Classes
- **Arena** (`endless_idler/ui/battle/widgets.py`, lines 565-610)
  - Contains the LineOverlay as `self._overlay` (line 575)
  - Has its own `add_pulse()` that forwards to overlay
- **Battle Screen** (`endless_idler/ui/battle/screen.py`)
  - Calls `arena.add_pulse()` at lines: 479, 557, 590, 648, 694, 702

## Notes
Dependencies: This task requires completion of task `c27c66d4-add-config-flag-for-battle-animations`.

The key is to skip the painting logic while still maintaining the underlying animation state management. This prevents memory leaks and ensures the system remains stable.

Focus on modifying the `paintEvent` method around line 318 in `endless_idler/ui/battle/widgets.py`.

**Important**: The `tick()` mechanism must continue running even when rendering is disabled to properly expire and remove pulses from memory.

## Status Updates
- 2025-01-11: Task created by Task Master
- 2025-01-11: Enhanced with detailed implementation context and line numbers (Auditor)
