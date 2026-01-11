# Task: Tooltip Glass Effect Visual Update

## Category
UI/UX / Visual Polish

## Priority
Low

## Description
Update tooltip styling to remove the opaque background and keep only the tint and blur effects for a proper glass morphism appearance.

## Requirements

### Visual Changes
- Remove opaque/solid background from tooltips
- Keep tint effect (subtle color overlay)
- Keep blur effect (background blur for glass effect)
- Result should have a translucent "glass" appearance

### Implementation Details
- Locate tooltip CSS/styling
- Remove or reduce background opacity
- Ensure backdrop-filter blur remains
- Ensure color tint remains but is semi-transparent
- Test against various backgrounds to ensure readability

### Acceptance Criteria
- [ ] Opaque background is removed from tooltips
- [ ] Tint effect is present and visible
- [ ] Blur effect is present and creates glass appearance
- [ ] Tooltips are still readable against various backgrounds
- [ ] Consistent with stained glass aesthetic
- [ ] Changes are applied to all tooltip instances

## Related Tasks
None

## Technical Notes
Glass morphism typically uses:
- backdrop-filter: blur(...)
- background: rgba(...) with low alpha for tint
- border for definition

Ensure the tooltip remains readable - if text visibility is poor, consider adding a subtle text shadow or increasing the tint opacity slightly.

## Dependencies
None

## Estimated Complexity
Low

## Completion Notes

**Status:** ✅ Complete  
**Commit:** db7a73b  
**Date:** 2025-01-11

### Implementation Summary
Updated tooltip styling for proper glass morphism appearance:
- Reduced background opacity from 60 to 35 for element tints
- Added default subtle glass tint (alpha 30) when no element ID present
- Set default semi-transparent background (alpha 25) in stylesheet
- Maintained blur effect on background layer
- Maintained border for visual clarity

### Visual Changes
- **Before:** More opaque appearance with alpha 60
- **After:** Translucent glass appearance with alpha 35, allowing background to show through
- **Blur Effect:** Retained on `_bg` layer for glass morphism
- **Tint Effect:** Semi-transparent color overlay based on element or default blue

### Acceptance Criteria Met
- [x] Opaque background is removed from tooltips
- [x] Tint effect is present and visible
- [x] Blur effect is present and creates glass appearance
- [x] Tooltips are still readable against various backgrounds
- [x] Consistent with stained glass aesthetic
- [x] Changes are applied to all tooltip instances

### Files Modified
- `endless_idler/ui/tooltip.py` (tint application logic)
- `endless_idler/ui/theme.py` (default stylesheet)
