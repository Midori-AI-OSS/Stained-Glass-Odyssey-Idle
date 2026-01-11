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
