# Fix Tooltip Styling: Square Corners and Blur Background

## Issue Reference
Part of: Fix tooltip styling, correct character stats display outside combat, and normalize off-site character experience and tooltips

## Problem
Tooltips currently have rounded corners and lack background blur, making them inconsistent with the intended "stained glass" aesthetic and harder to read on busy backgrounds.

## Current State
- File: `endless_idler/ui/tooltip.py`
- Line 138: `border-radius: 6px;` causes rounded corners
- No backdrop blur is applied to the tooltip panel background

## Requirements
1. **Square Corners**: Change `border-radius` from `6px` to `0` in the `_apply_glass_style()` method
2. **Background Blur**: Add CSS backdrop-filter or implement QGraphicsBlurEffect on the background layer
3. **Maintain Readability**: Ensure text remains readable with the blur effect
4. **Preserve Existing Features**: Keep element-based tinting and all current tooltip functionality

## Technical Approach
In `endless_idler/ui/tooltip.py` in the `StainedGlassTooltip._apply_glass_style()` method:

1. Change line 138 from:
   ```python
   f"border-radius: 6px; "
   ```
   to:
   ```python
   f"border-radius: 0px; "
   ```

2. For background blur:
   - **Note:** There's already a drop shadow effect (line 55-59) but this blurs the SHADOW, not the background
   - Need to add a backdrop blur that blurs content BEHIND the tooltip for better readability
   - Consider these approaches:
     * Add a semi-transparent background layer with QGraphicsBlurEffect
     * Capture the screen area behind the tooltip, blur it, and use as background
     * Note: Qt doesn't support CSS `backdrop-filter`, so need Qt-native solution
   - **Alternative simpler approach:** Increase the opacity of the background color to make text more readable without implementing complex backdrop blur

## Testing
1. Test tooltips in all screens (Shop, Party Management, Battle, Idle)
2. Verify square corners appear correctly
3. Verify background blur makes text more readable
4. Test with both default and element-tinted tooltips
5. Test on different background colors/images

## Success Criteria
- [ ] Tooltip corners are perfectly square (no rounding)
- [ ] Tooltip backgrounds are blurred for better text readability
- [ ] All existing tooltip functionality works correctly
- [ ] Changes apply to all tooltips throughout the application

## Files to Modify
- `endless_idler/ui/tooltip.py` (primary changes in `_apply_glass_style()` method)

## Notes
- This is part A requirement #1 and #2 from the main issue
- Changes should be minimal and focused on the styling only
- Do not break existing element tinting or tooltip positioning logic
