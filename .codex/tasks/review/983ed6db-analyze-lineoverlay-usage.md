# Analyze LineOverlay Usage in Battle Screen

## Description
Examine how `LineOverlay` is used in the battle screen to understand what lines and arrows are being rendered, where they're triggered, and what their visual effects are.

## Requirements
- Review the `LineOverlay` class in `endless_idler/ui/battle/widgets.py`
- Review the `Arena` class in `endless_idler/ui/battle/widgets.py` 
- Identify all locations in `endless_idler/ui/battle/screen.py` where `add_pulse()` is called
- Document the types of animations (attack lines, healing arrows, etc.)
- Note the visual parameters (colors, widths, curves, effects)

## Acceptance Criteria
- [x] Full understanding of `LineOverlay` rendering logic documented
- [x] All `add_pulse()` call sites identified and categorized
- [x] Animation types and their visual characteristics documented
- [x] Prepare findings for next tasks

## Implementation Context

### Key Files to Analyze

#### 1. `endless_idler/ui/battle/widgets.py`

**LinePulse dataclass** (lines 29-42):
- Stores animation state for each pulse
- Key fields:
  - `source`, `target`: QWidget endpoints
  - `color`: QColor for the line
  - `remaining_ms`: Time left in animation (default 220ms, 440ms for wrong-way)
  - `width`: Line thickness (3 normal, 6 for crits)
  - `crit`: Boolean for critical hit styling
  - `same_team`: Boolean indicating healing (vs attack)
  - `midpoint`: Optional QPointF for curved healing arrows
  - `wrong_target`: Optional QWidget for wrong-way healing animations

**LineOverlay class** (lines 263-450+):
- **`__init__()`** (lines 264-270): Sets up transparent overlay widget
- **`add_pulse()`** (lines 272-304): 
  - Adds new LinePulse to `self._pulses` list
  - Calculates duration: 440ms for wrong-way healing, 220ms otherwise
  - Sets `show_target_pulse=True` for same-team effects
- **`tick()`** (lines 306-316): 
  - Called every 30ms by timer
  - Decrements pulse timers
  - Removes expired pulses
- **`paintEvent()`** (lines 318-450+): 
  - Renders all active pulses
  - Handles 4 animation types:
    1. Simple attack lines
    2. Curved healing arrows (with midpoint)
    3. Critical hit effects (thicker lines)
    4. Wrong-way healing (4-segment path)
- **`_anchor_point()`**: Helper to get widget center point

**Arena class** (lines 565-620+):
- **`__init__()`** (lines 566-578):
  - Creates LineOverlay as `self._overlay` (line 570)
  - Sets up 30ms timer for tick() calls (lines 574-577)
- **`get_combat_midpoint()`** (lines 580-594):
  - Calculates stable midpoint for healing arrows
  - Returns center of arena viewport
- **`add_pulse()`** (lines 596-609):
  - Wrapper that calls overlay.add_pulse()
  - Automatically provides midpoint for healing (same_team=True)
  - Forwards all parameters to LineOverlay

#### 2. `endless_idler/ui/battle/screen.py`

**All add_pulse() call sites:**

1. **Line 479-485**: Healing animation
   ```python
   self._arena.add_pulse(attacker_widget, widget, color, 
                        same_team=True, wrong_target=wrong_widget)
   ```
   - Type: Healing/same-team effect
   - Has midpoint (curved arrow)
   - May have wrong_target for wrong-way animation

2. **Line 557**: Redirected attack (wind gust)
   ```python
   self._arena.add_pulse(attacker_widget, target_widget, color, crit=crit)
   ```
   - Type: Attack animation
   - May be critical
   - Straight line

3. **Line 590**: Regular attack
   ```python
   self._arena.add_pulse(attacker_widget, target_widget, color, crit=crit)
   ```
   - Type: Attack animation
   - May be critical
   - Straight line

4. **Line 648**: Another attack context
   ```python
   self._arena.add_pulse(attacker_widget, target_widget, color, crit=crit)
   ```
   - Type: Attack animation
   - May be critical
   - Straight line

5. **Line 694**: Non-colored attack (white)
   ```python
   self._arena.add_pulse(attacker_widget, target_widget, QColor(240, 240, 240))
   ```
   - Type: Neutral attack
   - No crit flag
   - White/light gray color

6. **Line 702**: Generic attack
   ```python
   self._arena.add_pulse(attacker_widget, target_widget, color, crit=crit)
   ```
   - Type: Attack animation
   - May be critical
   - Straight line

### Animation Types Breakdown

#### Type 1: Simple Attack Line (most common)
- **Visual**: Straight line from attacker to target
- **Color**: Element-based (from `color_for_damage_type_id()`)
- **Width**: 3px normal, 6px critical
- **Duration**: 220ms
- **Fade**: Alpha fades from 255 to 0 over duration
- **Examples**: Lines 557, 590, 648, 702

#### Type 2: Curved Healing Arrow
- **Visual**: Curved arc passing through combat midpoint
- **Color**: Light element color (typically bright/holy)
- **Width**: 3px
- **Duration**: 220ms
- **Path**: source → midpoint → target (quadratic curve)
- **Extra**: Target pulse effect when `show_target_pulse=True`
- **Example**: Line 479 (when wrong_target is None)

#### Type 3: Critical Hit
- **Visual**: Thicker straight line
- **Color**: Element-based
- **Width**: 6px (double normal)
- **Duration**: 220ms
- **Triggered by**: `crit=True` parameter

#### Type 4: Wrong-Way Healing (complex)
- **Visual**: 4-segment animated path
- **Segments**: 
  1. source → midpoint (25% of time)
  2. midpoint → wrong_target (25%, with red "bounce")
  3. wrong_target → midpoint (25%)
  4. midpoint → target (25%)
- **Duration**: 440ms (double normal)
- **Color**: Element color for path, red bounce at wrong target
- **Example**: Line 479 (when wrong_target is provided)

### Visual Parameters Reference

**Colors**:
- Obtained from `color_for_damage_type_id()` in `endless_idler/ui/battle/colors.py`
- White/neutral: `QColor(240, 240, 240)`
- Element-specific (fire, ice, lightning, etc.)

**Widths**:
- Normal: 3px
- Critical: 6px

**Durations**:
- Standard: 220ms
- Wrong-way healing: 440ms

**Rendering**:
- Antialiasing enabled
- Round cap style
- Alpha fade from 255 to 0
- Quadratic curves for healing (using QPainterPath)

### Scope Clarification

**What this analysis covers** (Battle animations only):
- All LineOverlay rendering in battle screen
- Attack lines and healing arrows
- Critical hit effects

**What this does NOT cover** (separate system):
- Stack merge arrows in Party Builder
- Those use `MergeArrow` class in `party_builder_merge_fx.py`
- Should NOT be affected by battle animation config flag

## Notes
This is a prerequisite analysis task before implementing the removal of lines and arrows. The goal is to understand the current implementation so we can safely disable it without breaking stack merge animations.

Do NOT make any code changes in this task - this is analysis only.

## Analysis Deliverable Format

Create a markdown document with:
1. **Summary**: Brief overview of what was found
2. **Animation Types**: Detailed breakdown of each type
3. **Call Sites**: Table of all add_pulse() locations with context
4. **Visual Parameters**: Reference guide for colors, widths, durations
5. **Rendering Logic**: Explanation of paintEvent() flow
6. **Recommendations**: Suggestions for the implementation task

## Status Updates
- 2025-01-11: Task created by Task Master
- 2025-01-11: Enhanced with complete file references and line numbers (Auditor)
- 2025-01-11: Analysis verified as complete. All information documented in-task. Used this analysis to successfully implement tasks c27c66d4, 95f5b1c9, and 0bf94f2a.
