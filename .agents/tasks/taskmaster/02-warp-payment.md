# Task 2: Warp Payment Module

**Status:** Not started  
**Dependencies:** Task 1 (needs `warp_yolo_preferences` on `RunSave` for YOLO deduction logic)  
**Blocks:** Task 3 (warp UI needs payment checks), Task 5 (YOLO prefs affect deduction order)

---

## What to Do

Add shard-cost logic to the warp engine: cost constant, banner-to-shard mapping, affordability checks, deduction logic (elemental and YOLO with preference ordering), and integrate into the `pull()` method.

---

## Pre-execution Checks

- [x] `endless_idler/warp/constants.py` exists (27 lines), currently has `BANNER_IDS`, pity constants, rate multipliers
- [x] `endless_idler/warp/engine.py` exists (210 lines), `WarpEngine` class at line 38, `pull()` at line 66
- [x] `endless_idler/save.py` `RunSave` has `inventory: dict[str, int]` at line 121 (shard counts live here)
- [x] Shard item IDs are named `{element}_shard` (verified via inventory system — `get_all_items()`, `get_item_ids()`)
- [x] `endless_idler/warp/constants.py` `BANNER_IDS` contains `"yolo"` (line 10)
- [x] `WarpEngine.__init__` takes `save: RunSave`, `banner_id: str`, `banner: BannerDefinition`, `rng: random.Random`
- [x] `pull()` returns `WarpOutcome`, currently has no cost check

---

## Step-by-Step Instructions

### 1. Add `SHARD_COST_PER_PULL` constant
**File:** `endless_idler/warp/constants.py`, at the top (after line 1 docstring, before `BANNER_IDS`)

Add:
```python
SHARD_COST_PER_PULL = 160
```

### 2. Add `BANNER_SHARD_MAP` dict
**File:** `endless_idler/warp/constants.py`, after `SHARD_COST_PER_PULL`

Add:
```python
BANNER_SHARD_MAP: dict[str, str] = {
    "fire": "fire_shard",
    "ice": "ice_shard",
    "wind": "wind_shard",
    "lightning": "lightning_shard",
    "light": "light_shard",
    "dark": "dark_shard",
}
```

Note: `"yolo"` is intentionally excluded from this map — YOLO pulls use a different deduction method.

Update the module docstring to mention these new constants.

### 3. Add import of new constants
**File:** `endless_idler/warp/engine.py`, add imports from constants (lines 12-18):

Add:
```python
from endless_idler.warp.constants import BANNER_SHARD_MAP
from endless_idler.warp.constants import SHARD_COST_PER_PULL
```

### 4. Add payment methods to `WarpEngine`
**File:** `endless_idler/warp/engine.py`, add these methods to the `WarpEngine` class (after `__init__`, before `pull()`):

#### `get_cost()` — static/class method or instance method

```python
    @staticmethod
    def get_cost() -> int:
        """Return the shard cost for a single pull."""
        return SHARD_COST_PER_PULL
```

#### `can_afford()` — checks if player has enough shards

```python
    def can_afford(self) -> bool:
        """Return True if the player has enough shards for this banner."""
        cost = self.get_cost()
        inventory = self._save.inventory

        if self._banner_id == "yolo":
            available = self._yolo_available_shards()
            total = sum(available.values())
            return total >= cost
        else:
            shard_id = BANNER_SHARD_MAP.get(self._banner_id)
            if shard_id is None:
                return False
            return inventory.get(shard_id, 0) >= cost
```

#### `_yolo_available_shards()` — return dict of available shards

```python
    def _yolo_available_shards(self) -> dict[str, int]:
        """Return a mapping of shard_item_id → count for all damage types
        that have >0 shards in inventory."""
        inventory = self._save.inventory
        result: dict[str, int] = {}
        for shard_id in BANNER_SHARD_MAP.values():
            count = inventory.get(shard_id, 0)
            if count > 0:
                result[shard_id] = count
        return result
```

#### `_deduct_yolo(cost)` — deduct from preferred types first

```python
    def _deduct_yolo(self, cost: int) -> None:
        """Deduct *cost* shards from YOLO-eligible shard types.

        Deduction order:
        1. Preferred types from ``save.warp_yolo_preferences`` (in order)
        2. Remaining available types (any order)

        Raises ``ValueError`` if total available shards < cost.
        """
        inventory = self._save.inventory
        available = self._yolo_available_shards()
        total = sum(available.values())
        if total < cost:
            raise ValueError(
                f"Insufficient shards for YOLO pull: need {cost}, have {total}"
            )

        # Build ordered list: preferred types first, then fallback
        prefs = self._save.warp_yolo_preferences or []
        preferred_ids = [
            f"{pref}_shard" for pref in prefs if f"{pref}_shard" in available
        ]
        fallback_ids = [
            sid for sid in available if sid not in set(preferred_ids)
        ]

        remaining = cost
        for shard_id in preferred_ids + fallback_ids:
            if remaining <= 0:
                break
            take = min(inventory.get(shard_id, 0), remaining)
            inventory[shard_id] -= take
            remaining -= take
```

#### `_deduct_elemental(cost)` — deduct from matching shard type

```python
    def _deduct_elemental(self, cost: int) -> None:
        """Deduct *cost* shards from the banner's matching shard type.

        Raises ``ValueError`` if insufficient shards.
        """
        shard_id = BANNER_SHARD_MAP.get(self._banner_id)
        if shard_id is None:
            raise ValueError(
                f"No shard type mapped for banner '{self._banner_id}'"
            )
        inventory = self._save.inventory
        balance = inventory.get(shard_id, 0)
        if balance < cost:
            raise ValueError(
                f"Insufficient {shard_id}: need {cost}, have {balance}"
            )
        inventory[shard_id] = balance - cost
```

#### `_deduct_cost()` — dispatcher

```python
    def _deduct_cost(self) -> None:
        """Deduct the pull cost from inventory, dispatching to the
        correct deduction method based on banner type."""
        cost = self.get_cost()
        if self._banner_id == "yolo":
            self._deduct_yolo(cost)
        else:
            self._deduct_elemental(cost)
```

### 5. Integrate into `pull()`
**File:** `endless_idler/warp/engine.py`, at the top of `pull()` (line 66), before the pity read:

Add a cost check that raises `ValueError` if unaffordable:

```python
    def pull(self) -> WarpOutcome:
        """Execute a single warp pull and return the outcome.

        Deducts shard cost before rolling.  Raises ``ValueError`` if
        the player cannot afford the pull.

        The pull follows the roll-resolution pipeline:
        ... (existing docstring)
        """
        if not self.can_afford():
            raise ValueError(
                f"Cannot afford pull on banner '{self._banner_id}': "
                f"need {self.get_cost()} shards"
            )

        self._deduct_cost()

        save = self._save
        # ... rest of existing pull() logic unchanged
```

### 6. Update module-level docstring
**File:** `endless_idler/warp/engine.py`, line 1

Change:
```python
"""Warp engine core — roll resolution, pity tracking, and YOLO logic."""
```
To:
```python
"""Warp engine core — cost deduction, roll resolution, pity tracking, and YOLO logic."""
```

---

## Acceptance Criteria

1. `can_afford()` returns `False` when inventory has < 160 matching shards
2. `can_afford()` returns `False` when YOLO banner has < 160 total shards across all types
3. `pull()` raises `ValueError` when `can_afford()` returns `False`
4. Elemental deduct: pulls 160 from the matching shard type, raises if insufficient
5. YOLO deduct: pulls from preferred types in order, then fallback to remaining types
6. YOLO deduct: raises `ValueError` if total available shards < 160
7. Inventory shard counts are correctly decremented after a successful pull
8. Existing warp tests still pass (pre-seed inventory with 160+ shards before pulls)
9. `uv run basedpyright` clean

---

## Verification Commands

```bash
uv run pytest tests/test_warp_engine.py -q
uv run basedpyright
```

### Notes for existing tests

The existing test suite (`tests/test_warp_engine.py`) creates `RunSave()` instances and calls `pull()` directly. These will now fail without inventory shards. Update the test fixtures/helpers:

- In `_make_engine()` (line 52-65): seed `save.inventory` with 160 matching shards before creating the engine
- For elementals: `save.inventory["fire_shard"] = 160`
- For YOLO: `save.inventory["fire_shard"] = 160` (or add enough across types)
- Update `test_save_round_trip` and `test_save_round_trip_persists_json` similarly

If updating tests is out of scope for this task, add a `TODO` comment noting the tests need inventory seeding post-Task-2.
