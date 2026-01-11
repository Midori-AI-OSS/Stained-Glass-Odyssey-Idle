# Task: Refactor StainedGlassTooltip Background to True Glass Style

**Status**: Work In Progress  
**Priority**: High  
**Category**: UI/Tooltips  
**Task ID**: a3f64b79

## Objective

Replace the opaque main-menu-style background in `StainedGlassTooltip` with a true stained glass appearance: transparent base with tint, blur, and soft borders.

## Background

The current `StainedGlassTooltip` in `endless_idler/ui/tooltip.py` uses:
- The main menu cityscape background image (`main_menu_cityscape.png`)
- A blur effect applied to the background
- A stained glass overlay pattern that creates colored cells

While this creates a textured look, it still appears as an opaque panel similar to the main menu background. The tooltip needs to look like **transparent glass** with a subtle tint and blur effect.

## Current Implementation Analysis

From `endless_idler/ui/tooltip.py`:
- Lines 52-65: Background layer with pixmap and blur
- Lines 67-74: Panel layer with drop shadow
- Lines 123-136: `_refresh_background()` scales the cityscape pixmap
- Lines 137-140: `_load_background()` loads cityscape image
- Lines 142-166: `_apply_stained_glass_overlay()` adds colored grid pattern
- Lines 168-191: `_apply_element_tint()` applies element-based color tint to panel

## Requirements

### A) Remove Opaque Background
1. Stop using the main menu cityscape background image
2. Remove or refactor `_load_background()` and `_refresh_background()`
3. The background layer (`self._bg`) should either:
   - Be removed entirely, OR
   - Show a very subtle gradient or texture (not a photo)

### B) Implement True Glass Effect
1. Make the panel background (`self._panel`) nearly transparent:
   - Base opacity should be very low (e.g., alpha 20-40 instead of current 130-238)
   - Apply a subtle color tint (not a solid panel color)
2. Add a backdrop blur effect if Qt supports it
   - Research `QWidget.setAttribute(Qt.WA_TranslucentBackground)` usage
   - Check if `QGraphicsBlurEffect` can blur the content behind the widget
   - If Qt doesn't support backdrop blur, use a very subtle semi-transparent tint

### C) Maintain Element Tinting
1. Keep the element-based tinting system in `_apply_element_tint()`
2. Ensure element colors remain visible with the new glass style
3. Adjust alpha values to maintain readability over varied backgrounds

### D) Enhance Visual Style
1. Add a soft border with subtle glow/highlight
   - Current border: `1px solid rgba(255, 255, 255, 60)`
   - Consider adding a subtle outer glow or brighter edge
2. Add small border-radius for rounded corners (e.g., 4-6px)
3. Ensure drop shadow remains visible and enhances the glass effect

### E) Preserve Readability
1. Text must remain legible over varied backgrounds
2. Test tooltip appearance over:
   - Light backgrounds
   - Dark backgrounds  
   - Busy/textured backgrounds
3. Increase text shadow or backdrop opacity if needed for contrast

## Implementation Approach

### Option 1: Remove Background Layer (Recommended)
```python
# Remove self._bg entirely
# Use only self._panel with:
# - Very low opacity background (alpha 20-40)
# - Subtle tint color
# - Border with glow
# - Small border radius
```

### Option 2: Subtle Background Layer
```python
# Keep self._bg but:
# - Use a simple gradient (no cityscape image)
# - Very low opacity (alpha 15-25)
# - Blur effect to simulate frosted glass
```

## Acceptance Criteria

- [ ] Tooltip background is no longer opaque
- [ ] Tooltip has a transparent/translucent base
- [ ] Visible color tint is applied (element-based or default)
- [ ] Blur effect is present (either backdrop or layer blur)
- [ ] Soft border with subtle highlight/glow
- [ ] Small border radius (rounded corners)
- [ ] Text remains readable over varied backgrounds
- [ ] Element tinting still works correctly
- [ ] No visual artifacts or rectangle outlines
- [ ] Drop shadow enhances the glass appearance

## Testing Checklist

- [ ] Test tooltips in Party Builder over different areas
- [ ] Test tooltips in Battle Screen
- [ ] Test tooltips over character portraits
- [ ] Test tooltips over light backgrounds
- [ ] Test tooltips over dark backgrounds
- [ ] Verify element-tinted tooltips (fire, ice, etc.) are visible
- [ ] Verify default (no element) tooltips are visible
- [ ] Check tooltip positioning still works correctly

## Notes

- If Qt doesn't support backdrop blur, focus on:
  - Very low opacity background
  - Subtle gradient or solid color with low alpha
  - Strong text contrast (white text with shadow)
- Consider looking at how modern glass/frosted UI is implemented in Qt
- May need to experiment with different alpha values to find the right balance

## Related Files

- `endless_idler/ui/tooltip.py` - StainedGlassTooltip implementation
- `endless_idler/ui/theme.py` - Tooltip panel stylesheet (lines 373-381)
- `endless_idler/ui/assets.py` - Asset path helper
- `endless_idler/ui/battle/colors.py` - Element color mapping

## Estimated Effort

1-2 hours

## Dependencies

- Should be done after task `9be68a50-audit-tooltip-implementations.md`
- Must be tested before moving to review
