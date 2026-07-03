# Task 5: YOLO Preferences UI

**Status:** Not started  
**Dependencies:** Task 3 (needs `WarpScreen` to modify), Task 1 (needs `warp_yolo_preferences` field on `RunSave`)  
**Blocks:** None

---

## What to Do

Add a YOLO preferences collapsible panel to `WarpScreen` with 6 damage-type toggle buttons, max-3 selection enforcement, and save/load integration.

---

## Pre-execution Checks

- [x] `endless_idler/ui/warp/screen.py` will exist after Task 3
- [x] `RunSave.warp_yolo_preferences: list[str]` will exist after Task 1
- [x] Valid damage types for preferences: `fire`, `ice`, `wind`, `lightning`, `light`, `dark` (6 total)
- [x] `endless_idler/ui/theme/colors.py` has `color_for_damage_type_id()` at line 28 — use for button backgrounds/highlights
- [x] BANNER_IDS from `warp/constants.py` line 3-11 — minus `yolo` = the 6 types
- [x] QTabBar `currentChanged` signal provides tab index

---

## Step-by-Step Instructions

### 1. Add imports to `screen.py`
**File:** `endless_idler/ui/warp/screen.py`

Add these imports if not already present from Task 3:
```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from endless_idler.ui.theme.colors import color_for_damage_type_id
```

### 2. Add YOLO prefs panel to `_build_ui()`
**File:** `endless_idler/ui/warp/screen.py`, `_build_ui()` method

After the result panel, add the YOLO preferences section:

```python
        self._yolo_prefs_panel = self._build_yolo_prefs_panel()
        self._yolo_prefs_panel.setVisible(False)
        root.addWidget(self._yolo_prefs_panel)
```

### 3. Create `_build_yolo_prefs_panel()` method
**File:** `endless_idler/ui/warp/screen.py`

```python
    def _build_yolo_prefs_panel(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("WarpYoloPrefsPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("YOLO Shard Preferences", panel)
        header.setObjectName("WarpYoloPrefsHeader")
        layout.addWidget(header)

        hint = QLabel("Select up to 3 preferred shard types for YOLO pulls. "
                      "Preferred types are deducted first.", panel)
        hint.setObjectName("WarpYoloPrefsHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)
        layout.addLayout(buttons_row)

        self._yolo_pref_buttons: dict[str, QPushButton] = {}
        damage_types = ["fire", "ice", "wind", "lightning", "light", "dark"]

        for dt in damage_types:
            btn = QPushButton(dt.capitalize(), panel)
            btn.setObjectName("WarpYoloPrefButton")
            btn.setCheckable(True)
            btn.setProperty("damageType", dt)
            col = color_for_damage_type_id(dt)
            # Style via dynamic property — no setStyleSheet
            style = (
                f"QPushButton#WarpYoloPrefButton[damageType=\"{dt}\"] {{"
                f"  border-color: rgba({col.red()},{col.green()},{col.blue()},140);"
                f"}}"
            )
            # NOTE: Dynamic property styles go in the theme module (Task 4),
            # not as inline setStyleSheet. The button just needs the property set.
            btn.clicked.connect(
                lambda checked, t=dt: self._on_yolo_pref_toggled(t, checked)
            )
            buttons_row.addWidget(btn)
            self._yolo_pref_buttons[dt] = btn

        buttons_row.addStretch(1)
        layout.addStretch(1)
        return panel
```

### 4. Implement `_on_yolo_pref_toggled()`

```python
    def _on_yolo_pref_toggled(self, damage_type: str, checked: bool) -> None:
        save = self._save_store.current
        prefs = list(save.warp_yolo_preferences or [])

        if checked:
            if damage_type not in prefs:
                prefs.append(damage_type)
        else:
            if damage_type in prefs:
                prefs.remove(damage_type)

        # Enforce max 3: if user selects a 4th, deselect the first selected
        if len(prefs) > 3:
            removed = prefs.pop(0)
            btn = self._yolo_pref_buttons.get(removed)
            if btn is not None:
                btn.blockSignals(True)
                btn.setChecked(False)
                btn.blockSignals(False)

        save.warp_yolo_preferences = prefs
        self._save_store.persist()
```

### 5. Update `_on_banner_selected()` to show/hide YOLO prefs

In `_on_banner_selected()`:

```python
    def _on_banner_selected(self, index: int) -> None:
        banner_id = BANNER_IDS[index]
        self._selected_banner_id = banner_id

        # Show YOLO prefs panel only when YOLO tab is selected
        is_yolo = banner_id == "yolo"
        self._yolo_prefs_panel.setVisible(is_yolo)

        if is_yolo:
            self._restore_yolo_pref_buttons()

        self._refresh_display()
```

### 6. Implement `_restore_yolo_pref_buttons()`

```python
    def _restore_yolo_pref_buttons(self) -> None:
        """Read save.warp_yolo_preferences and update toggle button states."""
        save = self._save_store.current
        prefs = set(save.warp_yolo_preferences or [])
        for dt, btn in self._yolo_pref_buttons.items():
            btn.blockSignals(True)
            btn.setChecked(dt in prefs)
            btn.blockSignals(False)
```

### 7. Add theme selectors for YOLO prefs panel (update Task 4 theme)
**File:** `endless_idler/ui/theme/warp_widget.py`

Add selectors to the `STYLESHEET` string:

```
QFrame#WarpYoloPrefsPanel {
    background-color: rgba(13, 15, 22, 106);
    border: 1px solid rgba(255, 255, 255, 16);
    border-radius: 0px;
}

QLabel#WarpYoloPrefsHeader {
    color: rgba(237, 239, 245, 235);
    font-size: 14px;
    font-weight: 700;
}

QLabel#WarpYoloPrefsHint {
    color: rgba(210, 216, 231, 165);
    font-size: 11px;
}

QPushButton#WarpYoloPrefButton {
    background-color: rgba(18, 20, 28, 95);
    border: 1px solid rgba(255, 255, 255, 18);
    border-radius: 0px;
    padding: 8px 16px;
    color: rgba(237, 239, 245, 200);
    font-weight: 650;
    font-size: 12px;
}

QPushButton#WarpYoloPrefButton:hover {
    background-color: rgba(255, 255, 255, 12);
    border: 1px solid rgba(255, 255, 255, 30);
}

QPushButton#WarpYoloPrefButton:checked {
    border: 1px solid rgba(16, 185, 129, 140);
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 30),
        stop: 1 rgba(18, 20, 28, 85)
    );
    color: rgba(237, 239, 245, 240);
}

QPushButton#WarpYoloPrefButton:disabled {
    background-color: rgba(18, 20, 28, 50);
    border: 1px solid rgba(255, 255, 255, 8);
    color: rgba(237, 239, 245, 80);
}
```

For damage-type-specific colored highlights on checked buttons, use the `damageType` dynamic property (requires `_repolish()` when property changes). The theme module can add:

```
QPushButton#WarpYoloPrefButton:checked[damageType="fire"] {
    border-color: rgba(255, 90, 40, 160);
}
QPushButton#WarpYoloPrefButton:checked[damageType="ice"] {
    border-color: rgba(80, 200, 255, 160);
}
QPushButton#WarpYoloPrefButton:checked[damageType="wind"] {
    border-color: rgba(80, 230, 170, 160);
}
QPushButton#WarpYoloPrefButton:checked[damageType="lightning"] {
    border-color: rgba(255, 220, 0, 160);
}
QPushButton#WarpYoloPrefButton:checked[damageType="light"] {
    border-color: rgba(255, 220, 120, 160);
}
QPushButton#WarpYoloPrefButton:checked[damageType="dark"] {
    border-color: rgba(75, 45, 100, 160);
}
```

---

## Acceptance Criteria

1. YOLO preferences panel only visible when YOLO tab is selected
2. 6 toggle buttons, one per damage type (Fire, Ice, Wind, Lightning, Light, Dark)
3. Max 3 preferences enforced: selecting a 4th deselects the first (oldest) preference
4. Button states survive tab switches (restore on re-select of YOLO tab)
5. Preferences survive save/load (via `warp_yolo_preferences` field)
6. Preferences reflected in YOLO pull deduction order (tested separately in Task 2)
7. Checked buttons visually highlighted with emerald or damage-type-specific border
8. Unchecked buttons dimmed (by `:checked` pseudo-state contrast)
9. No inline `setStyleSheet()` — all styling in theme module via property selectors

---

## Verification Commands

```bash
uv run basedpyright
uv run ruff check endless_idler/ui/warp/
uv run pytest tests/test_warp_engine.py -q
```
