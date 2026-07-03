# Task 4: Warp UI Theme

**Status:** Not started  
**Dependencies:** Task 3 (needs WarpScreen with actual objectNames to style)  
**Blocks:** None (independent of other remaining tasks)

---

## What to Do

Create the warp theme module (`endless_idler/ui/theme/warp_widget.py`) with glass-morphism gradient styling matching existing theme patterns, and register it in the theme registry.

---

## Pre-execution Checks

- [x] `endless_idler/ui/theme/` exists with multiple theme modules (home, inventory, settings, layout, etc.)
- [x] Theme pattern: each module has a `STYLESHEET` string variable exported
- [x] `endless_idler/ui/theme/registry.py` imports each `STYLESHEET` and adds to `sections` tuple (line 51-69)
- [x] `endless_idler/ui/theme/colors.py` has `color_for_damage_type_id()` (line 28) — returns `QColor`
- [x] Existing glass-morphism gradient pattern from `home_widget.py` lines 10-16:
  ```
  background-color: qlineargradient(
      x1: 0, y1: 0, x2: 0, y2: 1,
      stop: 0 rgba(18, 20, 28, 0),
      stop: 0.08 rgba(18, 20, 28, 86),
      stop: 0.92 rgba(18, 20, 28, 86),
      stop: 1 rgba(18, 20, 28, 0)
  );
  ```
- [x] Damage type hex colors from `colors.py` lines 6-18:
  - fire: `(255, 90, 40)` → `#FF5A28`
  - ice: `(80, 200, 255)` → `#50C8FF`
  - lightning: `(255, 220, 0)` → `#FFDC00`
  - wind: `(80, 230, 170)` → `#50E6AA`
  - light: `(255, 220, 120)` → `#FFDC78`
  - dark: `(75, 45, 100)` → `#4B2D64`
- [x] `QPushButton#WarpPullButton` objectName used in Task 3 screen
- [x] `QPushButton#WarpPullButton:disabled` pseudo-state selector
- [x] `QLabel#WarpCostLabel`, `QLabel#WarpBalanceLabel` from Task 3
- [x] No `!important` rule (AGENTS.md prohibits it for normal UI components)

---

## Step-by-Step Instructions

### 1. Create theme module
**File:** `endless_idler/ui/theme/warp_widget.py` (new file)

#### Pattern: Use glass-morphism gradients matching existing theme modules

```python
from __future__ import annotations


STYLESHEET = """
QWidget#WarpScreenRoot {
    background: transparent;
}

QFrame#WarpBannerPanel {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(18, 20, 28, 0),
        stop: 0.08 rgba(18, 20, 28, 86),
        stop: 0.92 rgba(18, 20, 28, 86),
        stop: 1 rgba(18, 20, 28, 0)
    );
    border: 1px solid rgba(255, 255, 255, 14);
    border-radius: 0px;
}

QFrame#WarpResultPanel {
    background-color: rgba(13, 15, 22, 106);
    border: 1px solid rgba(255, 255, 255, 16);
    border-radius: 0px;
}

QPushButton#WarpPullButton {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 50),
        stop: 1 rgba(18, 20, 28, 95)
    );
    border: 1px solid rgba(16, 185, 129, 140);
    border-radius: 0px;
    color: rgba(237, 239, 245, 240);
    font-weight: 700;
    font-size: 14px;
    padding: 12px 24px;
    min-height: 40px;
}

QPushButton#WarpPullButton:hover {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 70),
        stop: 1 rgba(18, 20, 28, 115)
    );
}

QPushButton#WarpPullButton:pressed {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 30),
        stop: 1 rgba(18, 20, 28, 75)
    );
}

QPushButton#WarpPullButton:disabled {
    background-color: rgba(18, 20, 28, 70);
    border: 1px solid rgba(255, 255, 255, 10);
    color: rgba(237, 239, 245, 90);
}

QTabBar {
    background-color: transparent;
}

QTabBar::tab {
    background-color: rgba(18, 20, 28, 135);
    border: 1px solid rgba(255, 255, 255, 18);
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    padding: 8px 12px;
    margin-right: 0px;
    font-weight: 650;
    color: rgba(237, 239, 245, 180);
}

QTabBar::tab:hover {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 24);
}

QTabBar::tab:selected {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 20),
        stop: 1 rgba(18, 20, 28, 75)
    );
    border: 1px solid rgba(16, 185, 129, 140);
    color: rgba(237, 239, 245, 235);
}

QLabel#WarpCostLabel {
    color: rgba(237, 239, 245, 210);
    font-size: 13px;
    font-weight: 650;
}

QLabel#WarpBalanceLabel {
    color: rgba(237, 239, 245, 210);
    font-size: 13px;
    font-weight: 650;
}
""".strip()
```

#### Styling notes:
- Reuse existing `HomeTabs::tab` pattern from `home_widget.py` (lines 36-58) for the QTabBar tabs
- Use emerald gradient (`rgba(16, 185, 129, ...)`) for selected tab and pull button — consistent with `HomeTabs::tab:selected` (line 53)
- No `!important` overrides
- If damage-type-specific tab colors are needed, use dynamic property selectors on QTabBar::tab like `QTabBar::tab[element="fire"] { border-color: rgba(255, 90, 40, ...); }` — set via `setProperty("element", "fire")` in screen code and `_repolish()` pattern

### 2. Register in theme registry
**File:** `endless_idler/ui/theme/registry.py`

#### Add import (alphabetical order, after `tooltip_widget` import or before it):

```python
from endless_idler.ui.theme.warp_widget import (
    STYLESHEET as WARP_WIDGET_STYLESHEET,
)
```

#### Add to `sections` tuple in `build_stained_glass_stylesheet()` (alphabetically):

Inside the `sections = (...)` tuple (line 52-69), add `WARP_WIDGET_STYLESHEET` before `SHARD_PROGRESS_BAR_WIDGET_STYLESHEET` (or after, maintaining sort order).

Sorted section order:
```
APP_SHELL_WIDGET_STYLESHEET,
BLESSING_PANEL_WIDGET_STYLESHEET,
CARD_BACKGROUND_STYLESHEET,
HOME_WIDGET_STYLESHEET,
IDLE_CHARACTER_CARD_STYLESHEET,
IDLE_SCREEN_WIDGET_STYLESHEET,
IDLE_BLESSING_METER_WIDGET_STYLESHEET,
INVENTORY_WIDGET_STYLESHEET,
LAYOUT_SCREEN_WIDGET_STYLESHEET,
PARTY_HP_HEADER_STYLESHEET,
PASSIVE_PROGRESS_BAR_WIDGET_STYLESHEET,
PROGRESS_BAR_STYLESHEET,
RADIO_CONTROL_WIDGET_STYLESHEET,
SETTINGS_WIDGET_STYLESHEET,
SHARD_PROGRESS_BAR_WIDGET_STYLESHEET,
TOOLTIP_WIDGET_STYLESHEET,
WARP_WIDGET_STYLESHEET,   # <-- INSERT HERE (alphabetical: W comes after T)
```

---

## Acceptance Criteria

1. `STYLESHEET` string is the only export from `warp_widget.py`
2. No inline `setStyleSheet()` anywhere in `endless_idler/ui/warp/screen.py`
3. Theme builds without errors: `uv run python -c "from endless_idler.ui.theme.registry import build_stained_glass_stylesheet; build_stained_glass_stylesheet()"`
4. Visual consistency with Home, Inventory, and Settings screens (same glass-morphism gradient pattern)
5. Pull button has clear enabled/disabled visual states
6. Tab styling matches `HomeTabs` pattern
7. `uv run ruff check endless_idler/ui/theme/` clean

---

## Verification Commands

```bash
uv run python -c "from endless_idler.ui.theme.registry import build_stained_glass_stylesheet; result = build_stained_glass_stylesheet(); assert 'WarpScreenRoot' in result; print('OK')"
uv run basedpyright
uv run ruff check endless_idler/ui/theme/
```
