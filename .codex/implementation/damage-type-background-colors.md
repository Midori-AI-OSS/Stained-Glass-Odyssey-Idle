# Damage Type Background Colors Implementation

## Overview

This document describes the implementation of damage type background colors for character cards and tooltips in Stained Glass Odyssey Idle.

## Problem Statement

Previous implementations attempted to apply damage type colors to character card backgrounds and tooltips, but the colors were not being displayed due to Qt CSS specificity issues.

## Root Cause

The Qt CSS model gives precedence to application-level stylesheets (defined in `theme.py` and applied to QApplication) over widget-level stylesheets (set via `widget.setStyleSheet()`). 

The theme had hardcoded background colors for:
- `QFrame#onsiteCharacterCard` 
- `QFrame#idleOffsiteCard`
- `QFrame#stainedTooltipPanel`

These hardcoded values were blocking the dynamic element-based colors being set via `setStyleSheet()` calls in the widget code.

## Solution

### Phase 1: Remove Hardcoded Background Colors from Theme

**File**: `endless_idler/ui/theme.py`

Removed the `background-color` properties from three selectors:

```css
/* Before */
QFrame#onsiteCharacterCard {
    background-color: rgba(255, 255, 255, 10);  /* REMOVED */
    border: 1px solid rgba(255, 255, 255, 18);
}

/* After */
QFrame#onsiteCharacterCard {
    border: 1px solid rgba(255, 255, 255, 18);
}
```

Same changes applied to:
- `QFrame#idleOffsiteCard` (line 712-715)
- `QFrame#stainedTooltipPanel` (line 373-376)

### Phase 2: Update Widget-Level Stylesheets

Updated the `_apply_element_tint()` methods in three files to use proper CSS selectors with `!important` flags:

#### Onsite Character Cards

**File**: `endless_idler/ui/onsite/card.py` (lines 250-256)

```python
def _apply_element_tint(self, stats: Stats) -> None:
    from endless_idler.ui.battle.colors import color_for_damage_type_id
    element_id = getattr(stats, "element_id", "generic")
    color = color_for_damage_type_id(element_id)
    
    tint_color = f"rgba({color.red()}, {color.green()}, {color.blue()}, 60)"
    self.setStyleSheet(f"QFrame#onsiteCharacterCard {{ background-color: {tint_color} !important; }}")
```

Key changes:
1. Full selector: `QFrame#onsiteCharacterCard` (was `#onsiteCharacterCard`)
2. Alpha value: 60 (was 20) - 23.5% opacity for better visibility
3. Added `!important` flag to override any remaining base styles

#### Offsite Character Cards

**File**: `endless_idler/ui/idle/widgets.py` (lines 159-207)

```python
def _apply_element_tint(self, data: dict) -> None:
    # ... stats building code ...
    
    from endless_idler.ui.battle.colors import color_for_damage_type_id
    element_id = getattr(stats, "element_id", "generic")
    color = color_for_damage_type_id(element_id)
    
    tint_color = f"rgba({color.red()}, {color.green()}, {color.blue()}, 60)"
    self.setStyleSheet(f"QFrame#idleOffsiteCard {{ background-color: {tint_color} !important; }}")
```

Same key changes as onsite cards.

#### Tooltips

**File**: `endless_idler/ui/tooltip.py` (lines 168-176)

```python
def _apply_element_tint(self) -> None:
    if not self._element_id:
        return
    
    from endless_idler.ui.battle.colors import color_for_damage_type_id
    color = color_for_damage_type_id(self._element_id)
    
    tint_color = f"rgba({color.red()}, {color.green()}, {color.blue()}, 60)"
    self._panel.setStyleSheet(f"QFrame#stainedTooltipPanel {{ background-color: {tint_color} !important; }}")
```

Key changes:
1. Full selector: `QFrame#stainedTooltipPanel` (was `#stainedTooltipPanel`)
2. Alpha value: 60 (was 30) - 23.5% opacity
3. Added `!important` flag

## Damage Type Colors

Damage type colors are defined in `endless_idler/ui/battle/colors.py`:

| Damage Type | RGB Color | Hex |
|-------------|-----------|-----|
| fire | (255, 90, 40) | #FF5A28 |
| ice | (80, 200, 255) | #50C8FF |
| lightning | (185, 90, 255) | #B95AFF |
| wind | (80, 230, 170) | #50E6AA |
| water | (60, 130, 255) | #3C82FF |
| nature | (80, 200, 120) | #50C878 |
| arcane | (255, 80, 200) | #FF50C8 |
| dark | (150, 80, 220) | #9650DC |
| light | (255, 220, 120) | #FFDC78 |
| physical | (180, 180, 190) | #B4B4BE |
| generic | (235, 235, 240) | #EBEBF0 |

## Expected Behavior

### Onsite Character Cards

When displayed in battle or onsite mode:
1. Each character card background should show a tinted color matching their damage type
2. The tint has 23.5% opacity (alpha=60) over a transparent background
3. Fire characters show reddish-orange tint
4. Ice characters show light blue tint
5. Lightning characters show purple tint
6. And so on for other damage types

### Offsite Character Cards

When displayed in the idle screen:
1. Each character card background should show a tinted color matching their damage type
2. Same opacity and color rules as onsite cards
3. The tint is applied on every `update_display()` call

### Tooltips

When hovering over character elements:
1. The tooltip panel background should show a tinted color matching the character's damage type
2. Same opacity (23.5%) as character cards
3. Applied when `show_stained_tooltip()` is called with an `element_id` parameter

## Testing Checklist

To verify this implementation works correctly:

### Visual Tests

- [ ] Launch the game and navigate to battle/onsite view
- [ ] Verify onsite character cards have colored backgrounds matching their element
- [ ] Navigate to idle view with offsite characters
- [ ] Verify offsite character cards have colored backgrounds matching their element
- [ ] Hover over character cards to view tooltips
- [ ] Verify tooltips have colored backgrounds matching the character's element
- [ ] Test with multiple element types:
  - [ ] Fire (reddish-orange)
  - [ ] Ice (light blue)
  - [ ] Lightning (purple)
  - [ ] Wind (greenish-blue)
  - [ ] Light (yellowish)
  - [ ] Dark (purple-ish)
  - [ ] Generic (light gray)

### Edge Cases

- [ ] Characters without element data should show generic/transparent background
- [ ] Dual-element characters should show the resolved element color
- [ ] Colors should update correctly when character data changes
- [ ] No visual glitches or color bleeding into other elements

## Technical Details

### Qt CSS Specificity Rules

Qt's CSS implementation follows these precedence rules (highest to lowest):

1. Widget-level stylesheet with `!important` flag
2. Application-level stylesheet with `!important` flag
3. Widget-level stylesheet without `!important`
4. Application-level stylesheet without `!important`

Our solution uses #1 to override the application-level theme (#4).

### Why Full Selectors?

Using `QFrame#onsiteCharacterCard` instead of `#onsiteCharacterCard` ensures:
1. Higher CSS specificity
2. More explicit targeting of the exact widget
3. Better compatibility with Qt's stylesheet parser
4. Reduced chance of conflicts with other selectors

### Why !important?

The `!important` flag guarantees that our dynamic colors override any base styles, even if Qt's CSS precedence rules would normally give priority to the application-level theme.

### Opacity Choice

Alpha value of 60 (23.5% opacity) was chosen to:
1. Make the element color visible but not overwhelming
2. Allow the underlying UI elements to remain readable
3. Maintain visual consistency across all three widget types
4. Balance between subtlety and visibility

Previous values (20 and 30) were too subtle and barely visible.

## Related Files

- `endless_idler/ui/theme.py` - Application-level stylesheet
- `endless_idler/ui/onsite/card.py` - Onsite character card widgets
- `endless_idler/ui/idle/widgets.py` - Offsite character card widgets
- `endless_idler/ui/tooltip.py` - Tooltip widget
- `endless_idler/ui/battle/colors.py` - Damage type color definitions
- `endless_idler/combat/damage_types.py` - Damage type system

## Audit Trail

This implementation was developed through an iterative process:

1. **Initial Audit** (a5edb163): Identified root cause as Qt CSS specificity conflict
2. **Implementation** (5063103): Coder implemented Option A solution
3. **Second Audit** (fe3f02cb): Found missing tooltip background removal
4. **Fix** (504d62d): Removed tooltip background from theme.py
5. **Final Audit** (ec7aecfd): Confirmed 100% implementation complete

All audits passed with final verdict: ✅ READY FOR MERGE

## Maintenance Notes

### Adding New Damage Types

To add a new damage type color:

1. Add the color to `_TYPE_COLORS` in `endless_idler/ui/battle/colors.py`
2. No changes needed to card or tooltip code - it will automatically use the new color

### Changing Opacity

To adjust the opacity of element tints:

1. Change the alpha value in all three `_apply_element_tint()` methods
2. Keep values consistent across onsite cards, offsite cards, and tooltips
3. Recommended range: 40-80 (15-31% opacity)

### Changing Colors

Colors are centralized in `endless_idler/ui/battle/colors.py`. Update the RGB tuples in `_TYPE_COLORS` to change any damage type color globally.

## Known Limitations

1. **No border tinting**: Currently only backgrounds are tinted. Border colors could be added as an enhancement.
2. **Performance**: Offsite cards rebuild stats on every update. This is noted for potential optimization in a future task.
3. **No visual tests**: Manual testing required. Consider adding automated visual regression tests.

## Future Enhancements

Potential improvements for future consideration:

1. Add border color tinting to match element colors
2. Optimize offsite card stats rebuilding
3. Add animated transitions when element colors change
4. Create automated visual regression tests
5. Add theme variants with different base opacities
6. Document Qt CSS patterns in contributor guides
