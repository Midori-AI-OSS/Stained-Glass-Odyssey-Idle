# Visual Testing Guide: Damage Type Background Colors

## Purpose

This guide helps testers verify that damage type background colors are correctly applied to character cards and tooltips.

## What Was Fixed

Previously, character cards (both Onsite and Offsite) and tooltips had hardcoded white/gray backgrounds that prevented damage type colors from showing. This fix ensures that:

1. **Onsite character cards** show their damage type color as a background tint
2. **Offsite character cards** show their damage type color as a background tint
3. **Character tooltips** show the damage type color as a background tint

## Expected Visual Results

### Test 1: Onsite Character Cards
- Each character card should have a subtle colored background matching their damage type
- Fire characters: Reddish-orange tint
- Ice characters: Light blue tint
- Lightning characters: Purple tint
- Wind characters: Greenish-blue tint
- Light/Dark characters: Yellow/Purple tints

### Test 2: Offsite Character Cards
- Same color behavior as onsite cards
- Smaller cards but same visual effect

### Test 3: Character Tooltips
- Tooltip backgrounds should show the character's damage type color
- Stained glass pattern should still be visible

## Success Criteria

✅ All onsite/offsite character cards show element-colored backgrounds
✅ All tooltips show element-colored backgrounds  
✅ Colors are visually distinct between different elements
✅ Text and UI elements remain readable
✅ No crashes or visual glitches

## Color Reference

- Fire: #FF5A28 (orange-red)
- Ice: #50C8FF (sky blue)
- Lightning: #B95AFF (bright purple)
- Wind: #50E6AA (mint green)
- Light: #FFDC78 (pale yellow)
- Dark: #9650DC (deep purple)
- Generic: #EBEBF0 (off-white)

At 23.5% opacity, these appear as subtle tints.
