# Task: Audit All Tooltip Implementations

**Status**: Work In Progress  
**Priority**: High  
**Category**: UI/Tooltips  
**Task ID**: 9be68a50

## Objective

Identify and document all tooltip implementations used throughout the application to ensure complete coverage when converting tooltips to the stained glass visual style.

## Background

The application currently uses at least two tooltip systems:
1. **StainedGlassTooltip** - Custom tooltip widget in `endless_idler/ui/tooltip.py`
2. **QToolTip** - Standard Qt tooltips styled in `endless_idler/ui/theme.py` (lines 383-389)

Before making styling changes, we need a complete audit to ensure we don't miss any tooltip type.

## Requirements

### A) Document StainedGlassTooltip Usage
1. Identify all locations where `show_stained_tooltip()` is called
2. List all UI components that use the custom stained glass tooltip
3. Document the screens/contexts where these tooltips appear:
   - Party Builder
   - Battle Screen
   - Idle Screen
   - Any other screens

### B) Document QToolTip Usage
1. Identify all locations where `.setToolTip()` is called with non-empty strings
2. List all UI components that use standard Qt tooltips
3. Document the screens/contexts where these tooltips appear

### C) Identify Any Other Tooltip-Like Elements
1. Search for "help text" hover popups
2. Search for info icon hover behaviors
3. Search for any custom hover overlays that function like tooltips
4. Look for any popup widgets that appear on hover

### D) Create Comprehensive Documentation
1. Create a file `.codex/implementation/tooltip-audit.md` with findings
2. List all tooltip types with:
   - Implementation file path
   - Styling mechanism (custom widget, stylesheet, etc.)
   - Usage locations (file:line references)
   - Screen context
3. Provide a summary count of each tooltip type

## Acceptance Criteria

- [ ] All `show_stained_tooltip()` call sites are documented
- [ ] All `.setToolTip()` call sites are documented
- [ ] Any other tooltip-like UI elements are identified
- [ ] Audit results are saved to `.codex/implementation/tooltip-audit.md`
- [ ] Summary includes counts of each tooltip type found
- [ ] Documented which screens each tooltip type appears on

## Notes

- Use `grep` to find all tooltip-related function calls
- Check all UI modules in `endless_idler/ui/` directory
- Pay special attention to party builder, battle, and idle screens
- Document even empty tooltip calls (`.setToolTip("")`) as they may be placeholders

## Related Files

- `endless_idler/ui/tooltip.py` - Custom StainedGlassTooltip implementation
- `endless_idler/ui/theme.py` - QToolTip stylesheet (lines 383-389)
- `endless_idler/ui/party_builder*.py` - Party builder components
- `endless_idler/ui/battle/*.py` - Battle screen components
- `endless_idler/ui/onsite/*.py` - Onsite card components
- `endless_idler/ui/idle/*.py` - Idle screen components (if exists)

## Estimated Effort

~30 minutes

## Dependencies

None - this is the first task in the tooltip styling initiative
