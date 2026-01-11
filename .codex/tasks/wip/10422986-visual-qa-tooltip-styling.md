# Task: Visual QA - Test Tooltip Styling Across All Screens

**Status**: Work In Progress  
**Priority**: High  
**Category**: UI/Tooltips/QA  
**Task ID**: 10422986

## Objective

Perform comprehensive visual quality assurance on both tooltip types (StainedGlassTooltip and QToolTip) across all application screens to ensure the stained glass styling is consistent, readable, and visually appealing.

## Background

After refactoring both tooltip types to use stained glass styling:
- `StainedGlassTooltip` (custom widget) should have transparent glass with tint and blur
- `QToolTip` (standard Qt) should have transparent glass with tint via stylesheet

This task ensures the visual changes work correctly in all contexts and don't introduce layout issues, readability problems, or visual artifacts.

## Testing Scope

### A) Test StainedGlassTooltip
Test in all locations identified in audit (task 9be68a50):

1. **Party Builder**
   - Character tiles (drag/drop tiles)
   - Standby shop tiles
   - Party level tiles
   - Any other hoverable elements

2. **Battle Screen**
   - Combatant cards
   - Stat bars
   - Action buttons
   - Any hoverable elements

3. **Onsite Cards**
   - Character portraits
   - Stats display
   - Any hoverable elements

4. **Any Other Screens**
   - Per audit findings

### B) Test QToolTip
Test in all locations identified in audit (task 9be68a50):

1. **Party Builder Components**
   - Slot placeholders
   - Bars (fight/idle)
   - Any buttons with tooltips

2. **Battle Screen**
   - Stat labels
   - Status messages
   - Any buttons with tooltips

3. **Onsite Components**
   - Stats bars
   - Buttons
   - Any elements with `.setToolTip()`

4. **Any Other Screens**
   - Per audit findings

## Testing Checklist

### Visual Appearance
- [ ] Tooltips have transparent/translucent background (not opaque)
- [ ] Visible color tint is present (glass effect)
- [ ] Blur effect is visible (if implemented)
- [ ] Rounded corners appear correctly
- [ ] Soft borders with subtle glow/highlight
- [ ] No solid rectangle artifacts
- [ ] Drop shadow enhances depth (StainedGlassTooltip)
- [ ] Element-based tinting works (StainedGlassTooltip: fire, ice, etc.)
- [ ] Default (no element) tinting works (StainedGlassTooltip)

### Readability
- [ ] Text is legible over light backgrounds
- [ ] Text is legible over dark backgrounds
- [ ] Text is legible over busy/textured backgrounds
- [ ] Text color provides sufficient contrast
- [ ] Font size is appropriate
- [ ] Padding provides adequate spacing

### Layout & Positioning
- [ ] Tooltips position correctly near cursor (StainedGlassTooltip)
- [ ] Tooltips don't clip off-screen more than before
- [ ] Tooltips resize properly to fit content
- [ ] No flicker or jitter on hover
- [ ] No rapid resize or redraw issues
- [ ] Tooltips hide correctly when hover ends

### Consistency
- [ ] StainedGlassTooltip style is consistent across all screens
- [ ] QToolTip style is consistent across all screens
- [ ] Visual similarity between both tooltip types
- [ ] Color tints match the stained glass theme
- [ ] Border and shadow styles are harmonious

### Background Contexts
Test tooltip appearance over:
- [ ] Party Builder background
- [ ] Battle Screen background
- [ ] Idle Screen background (if applicable)
- [ ] Character portraits (various colors)
- [ ] Light-colored UI elements
- [ ] Dark-colored UI elements
- [ ] Main menu background (if tooltips appear there)

## Bug/Issue Reporting

For each issue found, document:
1. **Tooltip Type**: StainedGlassTooltip or QToolTip
2. **Location**: Screen and UI component
3. **Issue**: Description and screenshot if possible
4. **Severity**: Critical, High, Medium, Low
5. **Suggested Fix**: Proposed solution

Create a report file: `.codex/tasks/wip/10422986-tooltip-qa-findings.md`

## Acceptance Criteria

- [ ] All tooltip locations from audit are tested
- [ ] Both tooltip types tested in all applicable screens
- [ ] Tooltips appear with stained glass style (not opaque)
- [ ] Text readability is confirmed across contexts
- [ ] No layout/positioning regressions
- [ ] No flicker, jitter, or rendering artifacts
- [ ] Visual consistency confirmed across application
- [ ] QA findings documented if issues are found
- [ ] All critical and high-priority issues are reported

## Pass/Fail Criteria

**Pass if:**
- Tooltips look like stained glass (transparent, tinted, not solid)
- Text is readable in all tested contexts
- No critical layout or visual bugs
- Minor issues are documented for follow-up

**Fail if:**
- Tooltips still look opaque/solid
- Text is unreadable in common contexts
- Critical visual artifacts present
- Tooltips clip or position incorrectly
- Flicker or jitter issues occur

## Notes

- Take screenshots of good and bad examples for documentation
- If issues are found, create follow-up tasks for fixes
- Prioritize readability and usability over pure aesthetics
- Small adjustments to alpha values are acceptable during QA
- Document any edge cases or unusual behaviors

## Output

Create `.codex/tasks/wip/10422986-tooltip-qa-findings.md` with:
1. Summary (Pass/Fail/Pass with Issues)
2. Screenshots or descriptions of tooltip appearance
3. List of issues found (if any) with severity
4. Recommendations for adjustments
5. Sign-off or request for fixes

## Related Files

- `endless_idler/ui/tooltip.py` - StainedGlassTooltip implementation (class at lines 44-192)
- `endless_idler/ui/theme.py` - QToolTip stylesheet (lines 383-389)
- `.codex/implementation/tooltip-audit.md` - Audit findings (created by task 9be68a50)

## Test Locations (Confirmed via Code Audit)

### A) StainedGlassTooltip Locations (4 files)
1. **Party Builder** (`endless_idler/ui/party_builder_slot.py`, line 419)
   - Character drag/drop tiles
2. **Party Builder** (`endless_idler/ui/party_builder_bar.py`, line 363)
   - Party level tiles
3. **Onsite Cards** (`endless_idler/ui/onsite/card.py`, line 271)
   - Character portraits
4. **Battle Screen** (`endless_idler/ui/battle/widgets.py`, line 211)
   - Combatant cards

### B) QToolTip Locations (8 files, 13 uses)
1. **Party Builder Slots** (`party_builder_slot.py`, lines 360, 401)
2. **Party Builder Idle Bar** (`party_builder_idle_bar.py`, lines 23, 58, 64)
   - Tooltip text: "Add at least 1 OnSite character to idle."
3. **Party Builder Fight Bar** (`party_builder_fight_bar.py`, lines 21, 55, 61)
   - Tooltip text: "Add at least 1 OnSite character to fight."
4. **Party Builder Bar** (`party_builder_bar.py`, line 352)
5. **Onsite Stat Bars** (`onsite/stat_bars.py`, line 127)
   - Dynamic tooltips on stat bars
6. **Onsite Card Stats Button** (`onsite/card.py`, line 145)
   - Tooltip text: "Stats"
7. **Battle Widgets Stat Labels** (`battle/widgets.py`, line 258)
   - Dynamic stat tooltips
8. **Battle Screen Status** (`battle/screen.py`, line 721)
   - Status message tooltips

## Estimated Effort

1-2 hours (depending on number of issues found)

## Dependencies

- Must be done after task `a3f64b79-refactor-stainedglasstooltip-background.md`
- Must be done after task `8425b525-convert-qtoolip-to-glass-style.md`
- Requires audit findings from task `9be68a50-audit-tooltip-implementations.md`
