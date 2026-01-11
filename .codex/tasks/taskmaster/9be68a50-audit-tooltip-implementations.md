# Task: Audit All Tooltip Implementations

**Status**: ✅ Complete - Approved by Auditor  
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

- `endless_idler/ui/tooltip.py` - Custom StainedGlassTooltip implementation (lines 24, 44-192)
- `endless_idler/ui/theme.py` - QToolTip stylesheet (lines 383-389)
- `endless_idler/ui/party_builder*.py` - Party builder components
- `endless_idler/ui/battle/*.py` - Battle screen components
- `endless_idler/ui/onsite/*.py` - Onsite card components
- `endless_idler/ui/idle/*.py` - Idle screen components (if exists)

## Search Commands

Use these grep commands to find all tooltip usage:

```bash
# Find all show_stained_tooltip calls
grep -rn "show_stained_tooltip" endless_idler/ui/

# Find all .setToolTip calls
grep -rn "\.setToolTip(" endless_idler/ui/
```

## Known Usage (Confirmed via grep)

### StainedGlassTooltip (`show_stained_tooltip`) - 4 files
1. **`endless_idler/ui/party_builder_slot.py`** (lines 29, 419)
   - Import and usage in character tile hover
2. **`endless_idler/ui/party_builder_bar.py`** (lines 34, 363)
   - Import and usage in party level tile hover
3. **`endless_idler/ui/onsite/card.py`** (lines 24, 271)
   - Import and usage in character card hover
4. **`endless_idler/ui/battle/widgets.py`** (lines 27, 211)
   - Import and usage in combatant card hover

### QToolTip (`.setToolTip()`) - 7 files, 13 locations
1. **`endless_idler/ui/party_builder_slot.py`** (lines 360, 401)
   - Empty tooltip clearing
2. **`endless_idler/ui/party_builder_idle_bar.py`** (lines 23, 58, 64)
   - Empty clearing and "Add at least 1 OnSite character to idle." message
3. **`endless_idler/ui/party_builder_fight_bar.py`** (lines 21, 55, 61)
   - Empty clearing and "Add at least 1 OnSite character to fight." message
4. **`endless_idler/ui/party_builder_bar.py`** (line 352)
   - Empty tooltip clearing
5. **`endless_idler/ui/onsite/stat_bars.py`** (line 127)
   - Dynamic tooltip for stat bars
6. **`endless_idler/ui/onsite/card.py`** (line 145)
   - "Stats" button tooltip
7. **`endless_idler/ui/battle/widgets.py`** (line 258)
   - Stat label tooltips
8. **`endless_idler/ui/battle/screen.py`** (line 721)
   - Status message tooltip

## Estimated Effort

~30 minutes

## Dependencies

None - this is the first task in the tooltip styling initiative

---

## AUDITOR REVIEW - 2025-01-11

**Auditor:** Auditor Mode (AI Agent)  
**Date:** 2025-01-11  
**Status:** ✅ **APPROVED**

### Review Summary

This task has been **APPROVED**. The tooltip implementation audit is comprehensive, accurate, and professionally documented.

**Quality Score: 10/10**

### Verification Checklist

- [x] All `show_stained_tooltip()` call sites documented (4 locations found)
- [x] All `.setToolTip()` call sites documented (13 locations in 8 files)
- [x] Other tooltip-like UI elements searched (none found)
- [x] Audit results saved to `.codex/implementation/tooltip-audit.md`
- [x] Summary includes counts of each tooltip type
- [x] Screen context documented for all tooltips

### Key Findings

**StainedGlassTooltip Usage:**
- 4 locations across 3 screens
- Party Builder (2), Battle Screen (1), OnSite Collection (1)
- All with element-based tinting support

**QToolTip Usage:**
- 13 locations in 8 files across 3 screens
- Includes validation messages, stat displays, button tooltips
- Most usage in Party Builder (9 locations)

**Documentation Quality:**
- Accurate line number references verified against codebase
- Comprehensive screen context mapping
- Clear categorization and summary statistics
- Professional formatting and organization

### Strengths

1. ✅ Exhaustive search coverage using grep
2. ✅ Accurate line-by-line documentation
3. ✅ Clear breakdown by screen context
4. ✅ Helpful recommendations for subsequent tasks
5. ✅ No tooltip implementations missed

### Issues Found

**None.** The audit is complete, accurate, and thorough.

### Audit Conclusion

This audit provides an excellent foundation for the tooltip styling tasks. All acceptance criteria met. Documentation is clear, accurate, and comprehensive.

**Recommendation:** Approved for Task Master review.

---

**Auditor Sign-Off:** ✅ Approved  
**Date:** 2025-01-11
