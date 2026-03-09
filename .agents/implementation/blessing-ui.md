# Blessing UI System

## Overview

The blessing UI system displays the player's accumulated Odyssey's Blessing multiplier. The blessing grows over time, granting a stacking percentage increase every 5 minutes.

## IdleBlessingMeterWidget

**Location:** `endless_idler/ui/idle/blessing_meter.py:46`

**Inheritance:** Extends `QWidget` with custom `paintEvent()` rendering (line 131).

The widget renders a horizontal progress bar with dynamic visual effects. No child widgets; all rendering is custom painter-based.

### Key Features

**Aurora Gradient Background:**
- Background fill uses a three-stop gradient blending between base blue and aurora colors
- Gradient transitions based on progress: base blue at low progress, full aurora above 65%
- Colors defined in theme module as RGBA tuples

**Shimmer Effect Animation:**
- Horizontal shimmer band sweeps across the filled portion of the bar
- Alpha-blended white gradient creates the glow effect
- Shimmer intensity controlled by external logic (0.0 to 1.0)
- Shimmer speed increases with intensity (0.20 to 0.68 phase speed)

**Smooth Progress Animation:**
- Internal `QTimer` fires every 16ms (~60 FPS) (line 60)
- Progress and shimmer values use exponential approach blending
- Blend rates: 22.0 for progress, 16.0 for shimmer (lines 106, 114)
- Animation auto-stops when targets are reached (lines 124-127)

**Visual States:**

| State | Trigger | Visual Effect |
|-------|---------|---------------|
| progress | Normal cycle | Fills left-to-right with aurora gradient |
| shimmer | Countdown < 30s | Sweeping highlight band, speed increases |
| reset | New step gained | 3-second reset animation, shimmer pulses |

**Reset Animation:**
- Triggered when blessing step count increases (screen.py:442-444)
- Visual progress sweeps from full to empty over 3 seconds
- Shimmer intensity tied to remaining reset time
- Reset flag passed to `set_visual_state()` method

## Theme Integration

**Module Location:** `endless_idler/ui/theme/idle_blessing_meter_widget.py`

**Purpose:** Defines color constants and base styling for the IdleBlessingMeterWidget.

### Color Constants

| Constant | RGBA | Description |
|----------|------|-------------|
| `TRACK_FILL_RGBA` | `(0, 0, 0, 42)` | Dark track background |
| `TRACK_BORDER_RGBA` | `(255, 255, 255, 24)` | Subtle track border |
| `BLUE_BASE_RGBA` | `(52, 152, 219, 174)` | Base blue fill color |
| `AURORA_START_RGBA` | `(78, 170, 230, 170)` | Aurora gradient left |
| `AURORA_MID_RGBA` | `(62, 178, 130, 170)` | Aurora gradient center |
| `AURORA_END_RGBA` | `(215, 188, 120, 176)` | Aurora gradient right (gold) |
| `SHIMMER_RGBA` | `(245, 250, 255, 128)` | Shimmer highlight base alpha |

**Theme Selectors:**
```css
QWidget#idleBlessingMeter {
    background-color: transparent;
    min-height: 14px;
}
```

### Registry Wiring

**Theme Import:** `endless_idler/ui/theme/registry.py:12-14`

```python
from endless_idler.ui.theme.idle_blessing_meter_widget import (
    STYLESHEET as IDLE_BLESSING_METER_WIDGET_STYLESHEET,
)
```

**Included in build:** `endless_idler/ui/theme/registry.py:49`

The stylesheet is concatenated into the global theme in `build_stained_glass_stylesheet()` (line 58).

## Screen Integration

**Location:** `endless_idler/ui/idle/screen.py:381-412`

The blessing panel is created as a `QFrame` within the right column of the idle screen layout.

### Panel Layout

```
+----------------------------------+
|  Odyssey's Blessing              |  <- Title label
+----------------------------------+
|  [==========>          ] x1.0000 |  <- Meter + Value
+----------------------------------+
```

**Components:**
- Title label: "Odyssey's Blessing" (objectName: `idleBlessingTitle`)
- Meter widget: `IdleBlessingMeterWidget` (objectName: `idleBlessingMeter`)
- Value label: Shows current multiplier (objectName: `idleBlessingValueLabel`)

**Panel Construction:**
- `QFrame` with `idleBlessingPanel` objectName (line 382)
- Fixed width of 220px (line 384)
- Horizontal layout row containing meter and value (lines 396-410)

### Tooltip Display

**Method:** `_build_blessing_tooltip()` (line 420)

All panel components share the same tooltip showing:
- Current multiplier (e.g., "x1.0500")
- Stacks gained count
- Countdown to next blessing
- Base increment rate

**Tooltip Assignment:** Lines 471-473

### Update Cycle

**Method:** `_update_blessing_ui()` (line 436)

Called on every tick to refresh the blessing display:
1. Queries `IdleGameState` for blessing data
2. Detects step increases to trigger reset animation
3. Computes shimmer intensity based on countdown
4. Calls `set_visual_state()` with progress/shimmer/reset flags
5. Updates value label text

## Animation System Details

**Timer Configuration:**
- `QTimer` interval: 16ms (60 FPS) (blessing_meter.py:60)
- Connected to `_on_animation_frame()` slot (line 61)

**Blend Approach Function:**
```python
def _approach(self, current: float, target: float, rate: float, dt: float) -> float:
    blend = 1.0 - math.exp(-rate * dt)
    return current + ((target - current) * blend)
```

**Animation Variables:**
- `_display_progress`: Currently rendered progress (0.0 to 1.0)
- `_display_shimmer`: Currently rendered shimmer intensity (0.0 to 1.0)
- `_shimmer_phase`: Position of shimmer sweep (0.0 to 1.0, wraps)
- `_target_progress`: Desired progress from game state
- `_target_shimmer`: Desired shimmer from countdown logic

**Phase Speed Calculation:**
```
phase_speed = 0.20 + (0.48 * display_shimmer)
if reset_active:
    phase_speed *= 0.72
```

**Reset Animation Triggers:**
- Detected when `steps > _last_blessing_step_count` (screen.py:442)
- Sets `_blessing_reset_remaining_seconds = 3.0` (line 444)
- Each tick decrements remaining time by `IDLE_TICK_INTERVAL_SECONDS` (lines 452-455)
- Visual progress mapped from remaining time: `progress = remaining / 3.0`

**Auto-Stop Conditions:**
Animation timer stops when all conditions in `_should_animate()` return false:
- No active reset
- Shimmer values near zero
- Progress and shimmer at their targets
