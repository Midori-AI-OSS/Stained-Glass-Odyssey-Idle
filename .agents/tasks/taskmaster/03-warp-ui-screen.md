# Task 3: Warp UI Screen

**Status:** Not started  
**Dependencies:** Task 2 (needs `can_afford()` and `pull()` with cost deduction)  
**Blocks:** Task 4 (theme needs screen selectors), Task 5 (YOLO prefs UI extends this screen), Task 6 (main menu integration)

---

## What to Do

Create the Warp UI screen — a `WarpScreen` widget with banner selection tabs, detail panel, pull button, and results display.

---

## Pre-execution Checks

- [x] `endless_idler/warp/__init__.py` exists (empty file)
- [x] `endless_idler/warp/banners.py` has `generate_banners()` (line 82) and `BannerDefinition` (line 32)
- [x] `endless_idler/warp/constants.py` has `BANNER_IDS` (line 3)
- [x] `endless_idler/warp/engine.py` has `WarpEngine`, `WarpOutcome` (after Task 2: `can_afford()`, `pull()` with cost)
- [x] `endless_idler/characters/plugins.py` has `discover_character_plugins()`
- [x] `endless_idler/run_save_store.py` has `RunSaveStore` — `current` property for `RunSave`
- [x] `endless_idler/ui/theme/colors.py` has `color_for_damage_type_id()` (line 28)
- [x] Existing screen patterns: `endless_idler/ui/home.py` (`HomePage` at line 38), `endless_idler/ui/inventory.py` (`InventoryPage` at line 25)
- [x] `endless_idler/ui/components/inventory_slot.py` — reference for reusable component pattern
- [x] `.agents/instructions/reusable_ui_components.md` — must read before UI work

---

## Step-by-Step Instructions

### 1. Create package init file
**File:** `endless_idler/ui/warp/__init__.py` (new file)

```python
"""Warp screen package."""
```

### 2. Create the screen module
**File:** `endless_idler/ui/warp/screen.py` (new file)

#### Imports needed:

```python
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.run_save_store import RunSaveStore
from endless_idler.ui.theme.colors import color_for_damage_type_id
from endless_idler.warp.banners import BannerDefinition
from endless_idler.warp.banners import generate_banners
from endless_idler.warp.constants import BANNER_IDS
from endless_idler.warp.constants import BANNER_SHARD_MAP
from endless_idler.warp.engine import WarpEngine
from endless_idler.warp.engine import WarpOutcome
import random
```

#### Class skeleton:

```python
class WarpScreen(QWidget):
    """Warp (gacha pull) screen with banner tabs, detail panel, and pull button."""

    _BANNER_LABELS: dict[str, str] = {
        "fire": "Fire",
        "ice": "Ice",
        "wind": "Wind",
        "lightning": "Lightning",
        "light": "Light",
        "dark": "Dark",
        "yolo": "YOLO",
    }

    def __init__(
        self,
        *,
        save_store: RunSaveStore,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._save_store = save_store
        self.setObjectName("WarpScreenRoot")
        self._plugins = discover_character_plugins()
        self._banners = generate_banners(self._plugins)
        self._selected_banner_id: str = ""
        self._last_outcome: WarpOutcome | None = None
        self._rng = random.Random()

        self._build_ui()

    def _build_ui(self) -> None:
        # ... UI construction
```

#### UI Layout:

```
WarpScreenRoot (QVBoxLayout)
├── QTabBar (no objectName for now — theme will use type selector)
│   └── 7 tabs: Fire, Ice, Wind, Lightning, Light, Dark, YOLO
├── QFrame#WarpBannerPanel (QVBoxLayout or QHBoxLayout)
│   ├── QLabel banner name (e.g., "Fire Banner")
│   ├── QLabel pool summary (e.g., "5★: 3 characters, 6★: 1 character")
│   ├── QLabel#WarpCostLabel (e.g., "Cost: 160 Fire Shards")
│   ├── QLabel#WarpBalanceLabel (e.g., "Balance: 240 Fire Shards")
│   ├── QLabel pity count (e.g., "Pity: 42")
│   ├── QLabel pull total (e.g., "Total Pulls: 15")
│   └── QLabel last rarity (e.g., "Last: ★5")
├── QPushButton#WarpPullButton ("Pull (160 Shards)")
└── QFrame#WarpResultPanel (QVBoxLayout)
    ├── QLabel last pull result (e.g., "hero_a — ★5")
    └── QLabel obtained history (last 5 from warp_character_obtained)
```

#### Detailed method requirements:

**`_build_ui()`:**
1. Create root `QVBoxLayout` with margins `(16, 16, 16, 16)` and spacing 12
2. Create `QTabBar` — add 7 tabs using `BANNER_IDS` order, map IDs to labels via `_BANNER_LABELS`
3. `_build_banner_panel()` → returns `QFrame#WarpBannerPanel`
4. `_build_result_panel()` → returns `QFrame#WarpResultPanel`
5. Connect `tabBar.currentChanged.connect(self._on_banner_selected)`
6. After building UI, auto-select first tab that has a non-empty pool, or fall back to first tab

**`_build_banner_panel() → QFrame`:**
- Create `QFrame` with objectName `"WarpBannerPanel"`
- Layout: `QVBoxLayout` with margins and spacing matching Inventory pattern
- Contains labels for: name, pool info, cost, balance, pity, pull total, last rarity
- Use specific objectNames for themed labels (e.g., `"WarpCostLabel"`, `"WarpBalanceLabel"`)

**`_build_result_panel() → QFrame`:**
- Create `QFrame` with objectName `"WarpResultPanel"`
- Layout: `QVBoxLayout`
- Contains: last pull result label, obtained history label
- Initially shows "No pulls yet" placeholder

**`_on_banner_selected(index: int)`:**
- Map tab index to banner ID via `BANNER_IDS[index]`
- Update `self._selected_banner_id`
- Gray out tab if pool is empty (set tab enabled/disabled + style change)
- Call `_refresh_display()`

**`_build_engine() → WarpEngine`:**
```python
def _build_engine(self) -> WarpEngine:
    save = self._save_store.current
    banner = self._banners[self._selected_banner_id]
    return WarpEngine(save, self._selected_banner_id, banner, rng=self._rng)
```

**`_refresh_display()`:**
- Update banner panel labels based on current save state:
  - Banner name: `_BANNER_LABELS[banner_id] + " Banner"`
  - Pool info: `"5★: {len(5★_pool)} characters, 6★: {len(6★_pool)} characters"` or `"(empty)"` if both empty
  - Cost: `"Cost: {cost} {shard_label}"` (e.g., "Cost: 160 Fire Shards")
  - Balance: `"Balance: {inventory[shard_id]}"` — for YOLO, show total of all shards
  - Pity: `save.warp_pity.get(banner_id, 0)`
  - Pull total: `save.warp_pull_total.get(banner_id, 0)`
  - Last rarity: format from `save.warp_last_rarity.get(banner_id)` (5→"★5", 6→"★6", 7→"★7", None→"—")
- Enable/disable pull button based on `can_afford()`
- Update result panel with last outcome + obtained history (last 5)

**`_on_pull()`:**
1. Build engine via `_build_engine()`
2. Call `engine.pull()` (raises `ValueError` if can't afford — button should be disabled, but handle defensively)
3. Store result in `self._last_outcome`
4. Persist save: `self._save_store.persist()`
5. Call `_refresh_display()`

**`refresh_display()` (public):**
- Delegates to `_refresh_display()`
- Called from main menu when navigating to warp screen

**`_shard_label_for_banner(banner_id: str) → str`:**
- Returns display label like `"Fire Shards"` or `"Any Shards"` for YOLO
- Maps through `BANNER_SHARD_MAP`

**`_shard_balance_for_banner(banner_id: str) → int`:**
- Elemental: `inventory.get(shard_id, 0)`
- YOLO: `sum` of all shard types in `BANNER_SHARD_MAP.values()`

#### Empty pool handling:
- Tab for empty-pool banner: set `setEnabled(False)`, pool summary shows `"(empty)"`
- If all elemental tabs have empty pools and YOLO has characters, first non-empty tab auto-selected
- Pull button stays disabled if pool is empty

---

## Acceptance Criteria

1. 7 tabs navigate correctly, each shows matching banner info
2. Cost label shows correct shard cost and type
3. Balance label shows correct inventory count
4. Pull button disabled when `can_afford()` returns `False`
5. Pull button click → deduction, roll, result display
6. Pity, pull total, last rarity update after each pull
7. Obtained history shows last 5 character IDs
8. Empty pool banners show `"(empty)"` and tab is grayed out
9. Screen follows existing patterns (margins, spacing, objectNames)
10. No inline `setStyleSheet()` anywhere in the screen file

---

## Verification Commands

```bash
uv run basedpyright
uv run ruff check endless_idler/ui/warp/
```
