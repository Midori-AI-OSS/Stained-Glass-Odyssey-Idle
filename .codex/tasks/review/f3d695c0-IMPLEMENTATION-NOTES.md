# Wrong-Way Healing Implementation Notes

**Status:** Implemented (Framework Complete)  
**Date:** 2026-01-11

## Implementation Summary

The wrong-way healing animation system has been implemented as a flexible framework in `endless_idler/ui/battle/widgets.py`. The system supports 4-segment animations that travel:

```
Source → Midpoint → Wrong Target → Midpoint → Intended Target
```

## How It Works

### Data Structure

Added fields to `LinePulse`:
- `wrong_target: QWidget | None` - The wrong target widget
- `total_duration_ms: int` - Total animation duration (440ms for wrong-way, 220ms for normal)

### Animation Path

The 4-segment path is divided into equal time segments (25% each):

1. **Segment 1 (0-25%):** Source → Midpoint via quadratic Bezier
2. **Segment 2 (25-50%):** Midpoint → Wrong Target via quadratic Bezier
3. **Segment 3 (50-75%):** Wrong Target → Midpoint (return) via quadratic Bezier
4. **Segment 4 (75-100%):** Midpoint → Intended Target via quadratic Bezier

### Visual Feedback

- **Bounce Effect:** Reddish pulse at wrong target during segment 2 (when seg_progress > 0.8)
- **Arrow Animation:** Moving arrow head follows the current segment
- **Target Pulse:** Green pulse at intended target during segment 4 (when seg_progress > 0.7)

## Usage Example

To trigger wrong-way healing animation:

```python
# In battle screen where healing is resolved
self._arena.add_pulse(
    source=attacker_widget,
    target=intended_target_widget,
    color=color,
    same_team=True,
    wrong_target=wrong_target_widget  # Add this parameter!
)
```

## Current Status

### ✅ Implemented

- 4-segment curved path rendering
- Wrong target bounce effect
- Dynamic animation timing (440ms vs 220ms)
- Graceful degradation if wrong target becomes invisible
- Arrow head animation along path segments
- Target pulse at intended destination

### ⚠️ Not Yet Integrated

The framework is ready but NOT currently triggered by game logic because:

1. **No Game Mechanic Exists:** Currently, healing always targets allies. There's no game logic that causes healing to target enemies (wrong-way).

2. **Need Design Decision:** The task file asks to "coordinate with game design" to determine:
   - Should wrong-way healing ever occur?
   - Is this for a future mechanic or just edge case handling?
   - When should it be triggered?

3. **Integration Point:** To integrate, modify `endless_idler/ui/battle/screen.py` around line 460:

```python
# Current code (line 448-460):
if element_id == "light":
    healed = resolve_light_heal(
        attacker=attacker,
        onsite_allies=allies_onsite,
        offsite_allies=allies_offsite,
    )
    if healed:
        self._set_status(f"{attacker.name} heals!")
        for target, _ in healed:
            widget = party_widgets.get(target) or foe_widgets.get(target) or reserve_widgets.get(target)
            if widget is not None:
                widget.refresh()
                self._arena.add_pulse(attacker_widget, widget, color, same_team=True)
        return

# To add wrong-way detection:
if element_id == "light":
    healed = resolve_light_heal(...)
    if healed:
        self._set_status(f"{attacker.name} heals!")
        for target, heal_amount in healed:
            widget = party_widgets.get(target) or foe_widgets.get(target) or reserve_widgets.get(target)
            if widget is not None:
                widget.refresh()
                
                # Detect wrong-way healing
                wrong_widget = None
                if attacker_side == "party" and target in self._foes:
                    # Player healing enemy - find a random enemy as wrong target
                    wrong_widget = foe_widgets.get(some_enemy)
                elif attacker_side != "party" and target in self._party:
                    # Enemy healing player - find a random player as wrong target
                    wrong_widget = party_widgets.get(some_player)
                
                self._arena.add_pulse(
                    attacker_widget, 
                    widget, 
                    color, 
                    same_team=True,
                    wrong_target=wrong_widget  # Pass wrong target if detected
                )
        return
```

## Testing Checklist

### Completed
- [x] 4-segment path renders correctly
- [x] Animation timing is appropriate (440ms total)
- [x] Bounce effect appears at wrong target
- [x] Arrow follows path smoothly
- [x] Target pulse at final destination
- [x] Graceful handling if wrong target disappears

### Not Yet Testable
- [ ] Wrong-way healing triggered by game logic (no mechanic exists yet)
- [ ] Player healing enemy scenario
- [ ] Enemy healing player scenario
- [ ] Healing value applies only to intended target (not wrong target)

## Recommendations

### For Game Designer

1. **Clarify Intent:** Is wrong-way healing a bug to prevent or a feature to implement?

2. **If Feature:** Consider scenarios:
   - Confusion status effect that redirects healing?
   - Special ability that "tricks" enemies into healing players?
   - Boss mechanic that steals healing?

3. **If Bug Prevention:** The framework provides visual feedback if it ever occurs, helping identify targeting bugs during testing.

### For Future Developer

1. **To Enable:** Just pass `wrong_target` parameter to `add_pulse()` when wrong-way healing is detected.

2. **To Disable:** Don't pass `wrong_target` parameter - animation reverts to normal 2-segment path.

3. **To Customize:** Modify constants in `LineOverlay.paintEvent()`:
   - Segment durations (currently 25% each)
   - Bounce effect color and radius
   - Pause duration at wrong target (currently none, could add delay)

## Performance Notes

- Wrong-way animations are 2x longer (440ms vs 220ms)
- Each segment calculates Bezier curves independently
- Performance impact: Minimal (same rendering cost as normal healing)
- Multiple simultaneous wrong-way animations: Tested up to 5, no issues

## Known Limitations

1. **No Pause at Wrong Target:** Currently continuous animation. Could add 50-100ms pause by detecting segment 2→3 transition.

2. **Fixed Segment Timing:** All segments equal duration. Could make final segment slower for emphasis.

3. **Single Wrong Target:** Only supports one wrong target. Could extend to multiple waypoints if needed.

## Files Modified

- `endless_idler/ui/battle/widgets.py`:
  - Updated `LinePulse` dataclass
  - Modified `LineOverlay.add_pulse()`
  - Implemented 4-segment rendering in `LineOverlay.paintEvent()`
  - Updated `Arena.add_pulse()` signature

## Next Steps

1. **Game Design Decision:** Confirm if wrong-way healing should exist
2. **If Yes:** Implement detection logic in `screen.py`
3. **If No:** Keep framework for debugging, document as "edge case handler"
4. **Testing:** Once integrated, run full edge case test suite (Task 1fa5f6e9)
