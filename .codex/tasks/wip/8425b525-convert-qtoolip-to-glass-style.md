# Task: Convert Standard QToolTip to Stained Glass Style

**Status**: Work In Progress  
**Priority**: High  
**Category**: UI/Tooltips  
**Task ID**: 8425b525

## Objective

Update the standard Qt tooltip stylesheet in `theme.py` to use a stained glass visual style instead of the current opaque background that matches the main menu panel.

## Background

The application uses standard Qt tooltips (via `.setToolTip()`) in several locations. These are styled in `endless_idler/ui/theme.py` at lines 383-389:

```python
QToolTip {
    background-color: rgba(10, 14, 26, 238);
    color: rgba(255, 255, 255, 235);
    border: 1px solid rgba(255, 255, 255, 52);
    padding: 8px 10px;
    font-size: 12px;
}
```

The current style uses:
- Very opaque background: `rgba(10, 14, 26, 238)` (alpha 238/255)
- Dark blue-gray color similar to main menu panels
- This creates a solid, opaque tooltip that doesn't match the stained glass aesthetic

## Requirements

### A) Replace Opaque Background
1. Change background to a transparent/translucent base
2. Reduce alpha to create glass effect (e.g., alpha 25-45)
3. Add subtle color tint for glass appearance

### B) Enhance Visual Style
1. Add rounded corners: `border-radius: 4px` or `6px`
2. Update border to be softer/more glass-like:
   - Consider `rgba(255, 255, 255, 80-100)` for brightness
   - May add subtle glow effect if possible with Qt stylesheets
3. Maintain adequate padding for readability

### C) Maintain Text Readability
1. Keep white text color: `rgba(255, 255, 255, 235)`
2. May need to add text shadow for contrast:
   - `color: rgba(255, 255, 255, 245);`
   - Add backdrop or increase alpha slightly if text is unreadable

### D) Match StainedGlassTooltip Style
1. Visual appearance should be consistent with the refactored `StainedGlassTooltip`
2. Both tooltip types should look like stained glass
3. Color tint and transparency should be similar
4. Standard QToolTips won't have element-based tinting (that's specific to StainedGlassTooltip)

## Proposed Stylesheet

```css
QToolTip {
    background-color: rgba(80, 100, 140, 35);
    color: rgba(255, 255, 255, 245);
    border: 1px solid rgba(255, 255, 255, 85);
    border-radius: 5px;
    padding: 8px 10px;
    font-size: 12px;
}
```

**Rationale:**
- `rgba(80, 100, 140, 35)` - Blue-tinted glass with low opacity
- `rgba(255, 255, 255, 245)` - Bright white text for contrast
- `rgba(255, 255, 255, 85)` - Brighter border for glass outline
- `border-radius: 5px` - Soft rounded corners
- Same padding and font size as before

## Implementation Steps

1. Locate the `QToolTip` block in `endless_idler/ui/theme.py` (lines 383-389)
2. Replace with the new glass-style stylesheet
3. Test standard tooltips in all locations where they appear
4. Adjust alpha values if text readability is insufficient
5. Ensure visual consistency with `StainedGlassTooltip`

## Acceptance Criteria

- [ ] QToolTip background is transparent/translucent (not opaque)
- [ ] Tooltip has a subtle color tint (glass appearance)
- [ ] Rounded corners are applied
- [ ] Border is soft and glass-like
- [ ] Text is readable over varied backgrounds
- [ ] Visual style matches the refactored StainedGlassTooltip
- [ ] No regression in tooltip positioning or behavior
- [ ] Tooltips appear correctly in all screens where they're used

## Testing Checklist

- [ ] Test `.setToolTip()` tooltips in Party Builder components
- [ ] Test tooltips in Battle Screen
- [ ] Test tooltips in Idle Screen
- [ ] Test tooltips in any other screens (main menu, settings, etc.)
- [ ] Verify tooltip appears over light backgrounds
- [ ] Verify tooltip appears over dark backgrounds
- [ ] Verify tooltip appears over busy/textured backgrounds
- [ ] Check that tooltip text is legible in all contexts

## Notes

- Standard Qt tooltips have limited styling options compared to custom widgets
- Cannot apply blur effects or complex graphics to QToolTip via stylesheet
- If text readability is poor, increase alpha slightly (e.g., 45 instead of 35)
- The goal is visual consistency with StainedGlassTooltip, not pixel-perfect match

## Alternative Approach (If Needed)

If the standard QToolTip stylesheet doesn't provide sufficient glass effect:
1. Consider replacing all `.setToolTip()` calls with `show_stained_tooltip()`
2. This would unify all tooltips under the custom implementation
3. Would require more code changes but provides better control
4. Defer this approach unless standard styling is insufficient

## Related Files

- `endless_idler/ui/theme.py` - Contains QToolTip stylesheet (lines 383-389)
- `endless_idler/ui/tooltip.py` - StainedGlassTooltip for visual reference
- Audit document: `.codex/implementation/tooltip-audit.md` (from task 9be68a50)

## Estimated Effort

30-45 minutes

## Dependencies

- Should be done after task `a3f64b79-refactor-stainedglasstooltip-background.md`
- Requires visual reference from refactored StainedGlassTooltip
- Should reference findings from task `9be68a50-audit-tooltip-implementations.md`
