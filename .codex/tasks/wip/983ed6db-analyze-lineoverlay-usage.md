# Analyze LineOverlay Usage in Battle Screen

## Description
Examine how `LineOverlay` is used in the battle screen to understand what lines and arrows are being rendered, where they're triggered, and what their visual effects are.

## Requirements
- Review the `LineOverlay` class in `/endless_idler/ui/battle/widgets.py`
- Review the `Arena` class in `/endless_idler/ui/battle/widgets.py` 
- Identify all locations in `/endless_idler/ui/battle/screen.py` where `add_pulse()` is called
- Document the types of animations (attack lines, healing arrows, etc.)
- Note the visual parameters (colors, widths, curves, effects)

## Acceptance Criteria
- [ ] Full understanding of `LineOverlay` rendering logic documented
- [ ] All `add_pulse()` call sites identified and categorized
- [ ] Animation types and their visual characteristics documented
- [ ] Prepare findings for next tasks

## Notes
This is a prerequisite analysis task before implementing the removal of lines and arrows. The goal is to understand the current implementation so we can safely disable it without breaking stack merge animations.

Do NOT make any code changes in this task - this is analysis only.

## Status Updates
- 2025-01-11: Task created by Task Master
