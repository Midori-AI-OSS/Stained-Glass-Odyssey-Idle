# Tooltip Implementation Audit

**Date**: 2024-01-11  
**Task ID**: 9be68a50  
**Status**: Complete

## Executive Summary

This audit identifies all tooltip implementations in the Stained Glass Odyssey Idle game. Two distinct tooltip systems were found:

1. **StainedGlassTooltip** - Custom tooltip widget (4 usage locations)
2. **QToolTip** - Standard Qt tooltips (8 files, 13 usage locations)

No other tooltip-like UI elements (help text popups, info icons, custom hover overlays) were discovered.

---

## 1. StainedGlassTooltip (Custom Widget)

### Implementation Details

**File**: `endless_idler/ui/tooltip.py`
- **Lines 24-42**: Global functions `show_stained_tooltip()` and `hide_stained_tooltip()`
- **Lines 44-192**: `StainedGlassTooltip` class implementation

**Styling Mechanism**:
- Custom QFrame widget with translucent background attribute
- Background layer with cityscape image (`backgrounds/main_menu_cityscape.png`)
- Blur effect on background (radius 14)
- Stained glass overlay with colored grid cells (32px cells, alpha 38)
- Element-based color tinting (alpha 35) or default tint (alpha 30)
- Drop shadow effect (radius 26, offset 0,8)
- Border: `1px solid rgba(255, 255, 255, 60)`

### Usage Locations

#### 1. Party Builder - Character Slot
- **File**: `endless_idler/ui/party_builder_slot.py`
- **Import**: Line 29
- **Usage**: Line 419 (in `enterEvent` method)
- **Context**: Character tile hover in party builder grid
- **Element Tinting**: Yes (character's element ID)

#### 2. Party Builder - Party Level Bar
- **File**: `endless_idler/ui/party_builder_bar.py`
- **Import**: Line 34
- **Usage**: Line 363 (in `enterEvent` method)
- **Context**: Party level tile hover in top bar
- **Element Tinting**: Yes (element ID passed)

#### 3. OnSite Card
- **File**: `endless_idler/ui/onsite/card.py`
- **Import**: Line 24
- **Usage**: Line 271 (in `enterEvent` method)
- **Context**: Character card hover in OnSite collection
- **Element Tinting**: Yes (character's element ID)

#### 4. Battle - Combatant Widget
- **File**: `endless_idler/ui/battle/widgets.py`
- **Import**: Line 27
- **Usage**: Line 211 (in `enterEvent` method)
- **Context**: Combatant card hover during battle
- **Element Tinting**: Yes (damage type element ID)

### Screen Context Summary

- **Party Builder Screen**: 2 locations (character slots + party level bar)
- **Battle Screen**: 1 location (combatant cards)
- **OnSite Collection**: 1 location (character cards)

**Total**: 4 usage locations across 3 screens

---

## 2. QToolTip (Standard Qt Tooltips)

### Implementation Details

**File**: `endless_idler/ui/theme.py`
- **Lines 383-389**: Global QToolTip stylesheet

**Current Styling**:
```css
QToolTip {
    background-color: rgba(10, 14, 26, 238);
    color: rgba(255, 255, 255, 235);
    border: 1px solid rgba(255, 255, 255, 52);
    padding: 8px 10px;
    font-size: 12px;
}
```

**Styling Mechanism**:
- Very opaque background (alpha 238/255 = 93% opacity)
- Dark blue-gray color matching main menu panels
- Standard Qt tooltip behavior (appears on hover after delay)
- No custom widget or blur effects

### Usage Locations

#### 1. Party Builder - Character Slot
- **File**: `endless_idler/ui/party_builder_slot.py`
- **Lines**: 360, 401
- **Purpose**: Empty tooltip clearing (`.setToolTip("")`)
- **Context**: Clearing tooltip on drag operations

#### 2. Party Builder - Idle Bar
- **File**: `endless_idler/ui/party_builder_idle_bar.py`
- **Lines**: 23, 58, 64
- **Purpose**: 
  - Line 23: Initialize with empty tooltip
  - Line 58: Clear tooltip when characters added
  - Line 64: Show "Add at least 1 OnSite character to idle."
- **Context**: Idle button validation message

#### 3. Party Builder - Fight Bar
- **File**: `endless_idler/ui/party_builder_fight_bar.py`
- **Lines**: 21, 55, 61
- **Purpose**:
  - Line 21: Initialize with empty tooltip
  - Line 55: Clear tooltip when characters added
  - Line 61: Show "Add at least 1 OnSite character to fight."
- **Context**: Fight button validation message

#### 4. Party Builder - Party Level Bar
- **File**: `endless_idler/ui/party_builder_bar.py`
- **Line**: 352
- **Purpose**: Empty tooltip clearing (`.setToolTip("")`)
- **Context**: Clearing tooltip before showing StainedGlassTooltip

#### 5. OnSite - Stat Bars
- **File**: `endless_idler/ui/onsite/stat_bars.py`
- **Line**: 127
- **Purpose**: Dynamic tooltip with stat information (`.setToolTip(tooltip)`)
- **Context**: Stat bar hover in character card

#### 6. OnSite - Card Stats Button
- **File**: `endless_idler/ui/onsite/card.py`
- **Line**: 145
- **Purpose**: Static "Stats" button tooltip
- **Context**: Stats button in character card

#### 7. Battle - Combatant Stat Labels
- **File**: `endless_idler/ui/battle/widgets.py`
- **Line**: 258
- **Purpose**: Dynamic stat value tooltips (`.setToolTip(display)`)
- **Context**: Stat labels in combatant widget

#### 8. Battle - Status Message
- **File**: `endless_idler/ui/battle/screen.py`
- **Line**: 721
- **Purpose**: Dynamic status message tooltip (`.setToolTip(message)`)
- **Context**: Battle status display

### Screen Context Summary

- **Party Builder Screen**: 4 files, 7 locations
  - Character slot: 2 (clearing)
  - Idle bar: 3 (clearing + validation message)
  - Fight bar: 3 (clearing + validation message)
  - Party level bar: 1 (clearing)
- **OnSite Collection**: 2 files, 2 locations
  - Stat bars: 1 (dynamic stat info)
  - Stats button: 1 (static label)
- **Battle Screen**: 2 files, 2 locations
  - Combatant stats: 1 (dynamic stat values)
  - Status message: 1 (dynamic battle status)

**Total**: 8 files, 13 usage locations across 3 screens

---

## 3. Other Tooltip-Like Elements

### Search Results

The following searches were conducted to identify tooltip-like UI elements:

1. **Hover popups/overlays**: `grep -rni "hover" endless_idler/ui/ | grep -i "popup\|overlay\|help\|info"`
   - **Result**: No matches found

2. **enterEvent/leaveEvent handlers**: `grep -rn "enterEvent\|leaveEvent" endless_idler/ui/`
   - **Result**: Only found handlers associated with `show_stained_tooltip()` calls (4 locations documented above)
   - No custom hover overlays or popup widgets detected

3. **Other tooltip references**: `grep -rn "QToolTip\|ToolTip" endless_idler/ui/ | grep -v "\.setToolTip\|show_stained_tooltip"`
   - **Result**: Only found the QToolTip stylesheet and window flag in StainedGlassTooltip implementation

### Conclusion

No tooltip-like UI elements exist beyond the two documented systems. All hover interactions are handled by either `StainedGlassTooltip` or standard `QToolTip`.

---

## Summary Statistics

| Tooltip Type | Files | Locations | Screens |
|-------------|-------|-----------|---------|
| **StainedGlassTooltip** | 4 | 4 | 3 (Party Builder, Battle, OnSite) |
| **QToolTip** | 8 | 13 | 3 (Party Builder, Battle, OnSite) |
| **Other** | 0 | 0 | 0 |
| **TOTAL** | 12 | 17 | 3 |

### Tooltip Type Breakdown

- **StainedGlassTooltip**: 23.5% of locations (4/17)
- **QToolTip**: 76.5% of locations (13/17)

### Screen Coverage

All three main interactive screens use tooltips:
1. **Party Builder**: Most tooltip usage (11 total)
   - 2 StainedGlassTooltip (character slot, party level bar)
   - 9 QToolTip (validation messages, clearing operations)

2. **Battle Screen**: Moderate tooltip usage (3 total)
   - 1 StainedGlassTooltip (combatant cards)
   - 2 QToolTip (stat labels, status message)

3. **OnSite Collection**: Moderate tooltip usage (3 total)
   - 1 StainedGlassTooltip (character cards)
   - 2 QToolTip (stat bars, stats button)

4. **Idle Screen**: No tooltip usage detected
   - No `.setToolTip()` or `show_stained_tooltip()` calls found

---

## Recommendations for Styling Updates

1. **Priority 1**: Update `StainedGlassTooltip` background to true glass style (Task a3f64b79)
   - Remove opaque cityscape background
   - Implement transparent base with tint and blur

2. **Priority 2**: Update `QToolTip` stylesheet to match glass aesthetic (Task 8425b525)
   - Reduce opacity from alpha 238 to ~35-45
   - Add border-radius for rounded corners
   - Brighten border for glass appearance

3. **Consistency**: Ensure both tooltip types have similar visual appearance
   - Matching transparency levels
   - Similar color tinting approach
   - Consistent border styles

4. **Testing**: Focus on Party Builder for comprehensive testing
   - Highest tooltip density (11 of 17 locations)
   - Uses both tooltip types
   - Various background contexts

---

## Related Files Reference

### Implementation Files
- `endless_idler/ui/tooltip.py` - StainedGlassTooltip widget (lines 24-192)
- `endless_idler/ui/theme.py` - QToolTip stylesheet (lines 383-389)
- `endless_idler/ui/battle/colors.py` - Element color mapping for tinting

### UI Component Files (StainedGlassTooltip Users)
- `endless_idler/ui/party_builder_slot.py` (lines 29, 419)
- `endless_idler/ui/party_builder_bar.py` (lines 34, 363)
- `endless_idler/ui/onsite/card.py` (lines 24, 271)
- `endless_idler/ui/battle/widgets.py` (lines 27, 211)

### UI Component Files (QToolTip Users)
- `endless_idler/ui/party_builder_slot.py` (lines 360, 401)
- `endless_idler/ui/party_builder_idle_bar.py` (lines 23, 58, 64)
- `endless_idler/ui/party_builder_fight_bar.py` (lines 21, 55, 61)
- `endless_idler/ui/party_builder_bar.py` (line 352)
- `endless_idler/ui/onsite/stat_bars.py` (line 127)
- `endless_idler/ui/onsite/card.py` (line 145)
- `endless_idler/ui/battle/widgets.py` (line 258)
- `endless_idler/ui/battle/screen.py` (line 721)

---

## Audit Methodology

1. **Code Search**: Used `grep` to find all occurrences of:
   - `show_stained_tooltip` - Found 5 results (1 definition + 4 usages)
   - `.setToolTip(` - Found 13 results across 8 files

2. **File Inspection**: Examined implementation files to understand:
   - Tooltip styling mechanisms
   - Current visual properties
   - Element tinting behavior

3. **Context Analysis**: Identified screen context for each tooltip usage:
   - Party Builder screens
   - Battle screen
   - OnSite collection screen
   - Idle screen (no tooltips found)

4. **Additional Searches**: Searched for tooltip-like elements:
   - Hover-based popups
   - Custom overlay widgets
   - Help text implementations
   - Result: None found

**Audit Completion**: All tooltip implementations have been identified and documented.
