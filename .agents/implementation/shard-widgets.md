# Shard UI Widget System

## Overview

The shard UI widget system displays character shard progression toward 100-tick cycles. Each character tracks accumulation of elemental shards that award rewards upon reaching the 100-tick threshold.

## ShardProgressBar Widget

**Location:** `endless_idler/ui/widgets/shard_progress_bar.py:35`

**Inheritance:** `ShardProgressBar` extends `QWidget` (line 35) and contains an `AnimatedProgressBar` via composition (line 62).

The widget uses composition rather than inheritance:
- `ShardProgressBar` is the container QWidget
- `AnimatedProgressBar` (`self._progress_bar`) handles the actual bar rendering
- This design allows ShardProgressBar to manage element-themed coloring while delegating animation to the reusable progress bar component

### Key Features

**Text Display:**
- Shows "SHARD X/100" format (line 97)
- Updates dynamically with tick count changes

**Element-Themed Colors:**
Widget colors adapt to character element type:

| Element | RGBA Values | Description |
|---------|-------------|-------------|
| Fire | `(255, 90, 40, 170)` | Orange-red flame color |
| Ice | `(80, 200, 255, 170)` | Cyan frost color |
| Lightning | `(255, 220, 0, 170)` | Electric yellow |
| Wind | `(80, 230, 170, 170)` | Teal/turquoise air color |
| Dark | `(75, 45, 100, 170)` | Deep purple shadow color |
| Light | `(255, 220, 120, 170)` | Golden radiant color |

Color definitions located in `endless_idler/ui/theme/shard_progress_bar_widget.py:5-10`.

**Generic Damage Type Cycling:**
- Characters with all 6 element types trigger generic mode (lines 111-117)
- Progress bar cycles through all 6 element colors smoothly
- Full cycle duration: 3000ms (`GENERIC_CYCLE_DURATION_MS`, line 32)
- Timer updates every 100ms for smooth transitions (line 70)
- Colors blend between adjacent elements using `_blend_rgba()` (lines 179-192)

## Theme Module

**Location:** `endless_idler/ui/theme/shard_progress_bar_widget.py`

**Purpose:** Defines visual styling and color constants for the ShardProgressBar widget.

**Contents:**
- RGBA color constants for each element (lines 5-10)
- `GENERIC_CYCLE_COLORS` list for cycling mode (lines 13-20)
- Hex color values for reference (lines 23-28)
- Stylesheet with selectors for each element type (lines 30-68)

**Theme Selectors:**
```css
QWidget#shardProgressBarWidget[elementId="fire"]
QWidget#shardProgressBarWidget[elementId="ice"]
QWidget#shardProgressBarWidget[elementId="lightning"]
QWidget#shardProgressBarWidget[elementId="wind"]
QWidget#shardProgressBarWidget[elementId="dark"]
QWidget#shardProgressBarWidget[elementId="light"]
QWidget#shardProgressBarWidget[elementId="generic"]
```

## Integration Points

**Onsite Character Cards:**
- **File:** `endless_idler/ui/onsite/card.py:477`
- **Usage:** `IdleOnsiteCharacterCard` creates ShardProgressBar instance
- **Visibility:** Only visible when character has shard reward types
- **Placement:** Inserted after EXP bar (lines 480-481)

**Idle Offsite Character Cards:**
- **File:** `endless_idler/ui/idle/widgets.py:155`
- **Usage:** `IdleOffsiteCard` creates ShardProgressBar instance
- **Visibility:** Starts hidden, shown when character has shard types (line 156)

## Visual Specifications

**Widget Heights:**
- ShardProgressBar container: `min-height: 18px` (theme, line 33)
- AnimatedProgressBar inside: `FixedHeight(14)` (widget, line 63)

**Color Application:**
- Specific elements: Solid color from `ELEMENT_COLORS` dict (line 140)
- Generic types: Dynamic color blending during cycle (lines 149-177)
- All colors use alpha 170 for consistency with glass aesthetic

**Element Property:**
- Widget sets `elementId` property for CSS selector targeting (line 123)
- Repolish triggered on element change (lines 124-128)

## Registry Wiring

**Theme Registration:** `endless_idler/ui/theme/registry.py:37-39`

```python
from endless_idler.ui.theme.shard_progress_bar_widget import (
    STYLESHEET as SHARD_PROGRESS_BAR_WIDGET_STYLESHEET,
)
```

**Included in build:** `endless_idler/ui/theme/registry.py:56`

The stylesheet is concatenated into the global theme in `build_stained_glass_stylesheet()` (line 58).

## Related Components

**AnimatedProgressBar:** `endless_idler/ui/components/progress_bar.py:89`
- Reusable animated progress bar used by ShardProgressBar
- Supports color thresholds, gradients, shimmer effects
- Handles smooth value transitions at 60 FPS

**Element ID Mapping:** `endless_idler/ui/widgets/shard_progress_bar.py:22-29`
- Maps element strings to RGBA tuples
- Used for both specific elements and generic cycling
