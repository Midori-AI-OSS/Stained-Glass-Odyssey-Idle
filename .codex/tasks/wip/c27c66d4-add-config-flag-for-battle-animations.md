# Add Configuration Flag for Battle Animations

## Description
Add a configuration flag or constant to control whether battle screen lines and arrows are displayed. This provides a clean way to disable the animations without removing the code.

## Requirements
- Add a boolean flag/constant (e.g., `SHOW_BATTLE_ANIMATIONS = False`) in an appropriate location
- Choose a suitable location: either at the top of the battle widgets module, in a config file, or as a class constant
- Make it easy to toggle for testing purposes
- Document the purpose of the flag

## Acceptance Criteria
- [ ] Configuration flag added with clear name
- [ ] Flag is easily accessible from battle animation code
- [ ] Flag defaults to `False` (animations disabled)
- [ ] Flag location is logical and well-documented
- [ ] Code compiles without errors

## Notes
This flag will be used in subsequent tasks to conditionally disable line/arrow rendering. Keep it simple - just add the flag, don't implement the conditional logic yet.

Consider adding the flag near the `LinePulse` and `LineOverlay` classes in `/endless_idler/ui/battle/widgets.py`.

## Status Updates
- 2025-01-11: Task created by Task Master
