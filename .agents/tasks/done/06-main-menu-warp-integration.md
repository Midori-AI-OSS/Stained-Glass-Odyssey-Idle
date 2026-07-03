# Task 6: Main Menu Integration

**Status:** Not started  
**Dependencies:** Task 3 (needs `WarpScreen` class)  
**Blocks:** Task 7 (verification needs navigation working)

---

## What to Do

Replace the stub warp button in `MainMenuWindow` with a real navigation button that shows the `WarpScreen`, and integrate it into the stacked widget navigation system.

---

## Pre-execution Checks

- [x] `endless_idler/ui/main_menu.py` exists (898 lines) — `MainMenuWindow` at line 45
- [x] Stub warp button at lines 136-142: `_make_stub_button(label="Warp", icon_name="compass", on_click=self._stub_warp)`
- [x] `_stub_warp` method at line 887-888: calls `_show_not_implemented("Warp")`
- [x] `_show_not_implemented` at line 896-898: used by `_stub_warp`, `_stub_guidebook`, `_stub_feedback`
- [x] `_make_nav_button` at line 240-259: creates checked/auto-exclusive navigation button
- [x] `_make_stub_button` at line 261-276: creates non-exclusive stub button with `appStub` property
- [x] Existing nav pages: `_PAGE_HOME` (line 48), `_PAGE_IDLE` (49), `_PAGE_INVENTORY` (50), `_PAGE_LAYOUT` (51), `_PAGE_SETTINGS` (52)
- [x] Screen creation in `__init__`:
  - `_home_screen` at line 185
  - `_layout_screen` at line 192
  - `_inventory_screen` at line 195
  - `_settings_screen` at line 196
  - `_idle_placeholder` at line 205
- [x] `_stack.addWidget()` calls at lines 207-211
- [x] `_show_home()` at line 351-353: set stack, set active nav
- [x] `_show_idle()` at line 355-362: persist layout, ensure idle, set stack
- [x] `_show_inventory()` at line 370-373: refresh, set stack, set active nav
- [x] `_show_layout()` at line 364-368: persist idle, set stack, set active nav
- [x] `_show_settings()` at line 375-383: sync radio, set stack, set active nav
- [x] `closeEvent` at line 229-238: must not need to shutdown warp screen (no persistent resources)
- [x] `WarpScreen` imports: `from endless_idler.ui.warp.screen import WarpScreen` (will exist after Task 3)

---

## Step-by-Step Instructions

### 1. Add `_PAGE_WARP` constant
**File:** `endless_idler/ui/main_menu.py`, after line 52 (`_PAGE_SETTINGS = "settings"`)

Add:
```python
    _PAGE_WARP = "warp"
```

### 2. Add import for `WarpScreen`
**File:** `endless_idler/ui/main_menu.py`, after line 38 (the `from endless_idler.ui.layout import LayoutScreenWidget` import)

Add (sorted alphabetically into the `endless_idler.ui` import group):
```python
from endless_idler.ui.warp.screen import WarpScreen
```

Place it after `from endless_idler.ui.settings import SettingsPage` (line 42).  Import-alphabetically, `warp` (w) follows `settings` (s).

### 3. Replace stub button with nav button
**File:** `endless_idler/ui/main_menu.py`, lines 136-142

Replace:
```python
        topbar_layout.addWidget(
            self._make_stub_button(
                label="Warp",
                icon_name="compass",
                on_click=self._stub_warp,
            )
        )
```
With:
```python
        topbar_layout.addWidget(
            self._make_nav_button(
                label="Warp",
                icon_name="compass",
                page_key=self._PAGE_WARP,
                on_click=self._show_warp,
            )
        )
```

### 4. Create `WarpScreen` in `__init__`
**File:** `endless_idler/ui/main_menu.py`, after `_settings_screen` creation (after line 204, before `_idle_placeholder`)

Add:
```python
        self._warp_screen = WarpScreen(
            save_store=self._save_store,
            parent=self,
        )
```

### 5. Add warp screen to stack
**File:** `endless_idler/ui/main_menu.py`, after `self._stack.addWidget(self._settings_screen)` (line 211)

Add:
```python
        self._stack.addWidget(self._warp_screen)
```

### 6. Add `_show_warp()` method
**File:** `endless_idler/ui/main_menu.py`, after `_show_layout()` (line 368), before `_show_inventory()` (line 370)

Add:
```python
    def _show_warp(self) -> None:
        if self._idle_screen is not None:
            self._idle_screen.force_persist()
        self._warp_screen.refresh_display()
        self._stack.setCurrentWidget(self._warp_screen)
        self._set_active_nav(self._PAGE_WARP)
```

### 7. Remove `_stub_warp` method
**File:** `endless_idler/ui/main_menu.py`, lines 887-888

Delete:
```python
    def _stub_warp(self) -> None:
        self._show_not_implemented("Warp")
```

### 8. Check `_show_not_implemented` usage
**File:** `endless_idler/ui/main_menu.py`

Verify `_show_not_implemented` is still used by `_stub_guidebook` (line 890-891) and `_stub_feedback` (line 893-894). If yes, leave the method in place. If `_stub_warp` was the only caller, remove `_show_not_implemented` too — but only if no other callers exist.

From the file:
- Line 890-891: `_stub_guidebook` → uses `_show_not_implemented`
- Line 893-894: `_stub_feedback` → uses `_show_not_implemented`

So `_show_not_implemented` must remain. Only remove `_stub_warp`.

---

## Acceptance Criteria

1. Warp button in top bar navigates to `WarpScreen`
2. `refresh_display()` is called before showing the warp screen
3. Warp button shows as checked (active) when warp screen is visible
4. Other nav buttons still work correctly (Home, Idle, Layout, Inventory, Settings, etc.)
5. `_show_not_implemented` still works for Guidebook and Feedback stub buttons
6. `_stub_warp` method is removed
7. Closing the app does not error on warp screen cleanup
8. `uv run basedpyright` clean
9. `uv run ruff check endless_idler/ui/main_menu.py` clean

---

## Verification Commands

```bash
uv run basedpyright
uv run ruff check endless_idler/ui/main_menu.py
uv run python -c "from endless_idler.ui.main_menu import MainMenuWindow; print('Import OK')"
```
