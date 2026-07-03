# Task 1: Save Schema Extension — YOLO Preferences

**Status:** Not started  
**Dependencies:** None  
**Blocks:** Task 2 (warp engine needs the field), Task 5 (YOLO prefs UI)

---

## What to Do

Add a `warp_yolo_preferences: list[str]` field to `RunSave` in `endless_idler/save.py`, bump the save version from 13 to 14, wire serialization/deserialization, add normalization, and create the migration.

---

## Pre-execution Checks

- [x] `endless_idler/save.py` exists, `RunSave` dataclass at line 107, `SAVE_VERSION = 13` at line 35
- [x] `endless_idler/save_codec.py` has `as_str_list()` at line 155 (returns `list[str]`)
- [x] `endless_idler/save_migrations/migration_v13_warp.py` exists as reference pattern (22 lines, auto-discovered)
- [x] `endless_idler/save_migrations/__init__.py` auto-discovers modules named `migration_*`
- [x] Existing warp fields: `warp_pity` (line 137), `warp_pull_total` (138), `warp_last_rarity` (139), `warp_character_obtained` (140)
- [x] Valid damage types: `fire`, `ice`, `wind`, `lightning`, `light`, `dark` (from `BANNER_IDS` in `warp/constants.py` line 3-11, minus `yolo`)
- [x] Existing tests: `tests/test_warp_engine.py::test_save_round_trip` (line 522) and `test_save_round_trip_persists_json` (line 550)

---

## Step-by-Step Instructions

### 1. Bump `SAVE_VERSION`
**File:** `endless_idler/save.py`, line 35

Change:
```python
SAVE_VERSION = 13
```
To:
```python
SAVE_VERSION = 14
```

### 2. Add `as_str_list` import
**File:** `endless_idler/save.py`, after line 26 (`from endless_idler.save_codec import as_optional_str_list`)

Add:
```python
from endless_idler.save_codec import as_str_list
```

Sort imports: `as_str_list` should go after `as_optional_str_list` and before `as_noneable_int_dict` alphabetically.

### 3. Add field to `RunSave` dataclass
**File:** `endless_idler/save.py`, after line 140 (`warp_character_obtained: dict[str, list[str]] = field(default_factory=dict)`)

Add:
```python
    warp_yolo_preferences: list[str] = field(default_factory=list)
```

### 4. Wire into `SaveManager.load()` deserialization
**File:** `endless_idler/save.py`, inside the `RunSave(...)` constructor call in `load()` (after line 239, the `warp_character_obtained=...` line)

Add:
```python
            warp_yolo_preferences=as_str_list(
                data.get("warp_yolo_preferences", [])
            ),
```

### 5. Wire into `SaveManager.save()` payload dict
**File:** `endless_idler/save.py`, inside `save()`, in the `payload = {...}` dict (after line 273, `"warp_character_obtained": save.warp_character_obtained,`)

Add:
```python
            "warp_yolo_preferences": save.warp_yolo_preferences,
```

### 6. Add normalization in `_normalized_save()`
**File:** `endless_idler/save.py`, inside `_normalized_save()`, after the `warp_character_obtained` normalization block (after line 446, the end of that `for` loop)

Add a new normalization block before the `return RunSave(...)`:

```python
    VALID_DAMAGE_TYPES = {"fire", "ice", "wind", "lightning", "light", "dark"}
    warp_yolo_preferences: list[str] = []
    seen: set[str] = set()  # reuse existing seen or create new
    for pref in getattr(save, "warp_yolo_preferences", []) or []:
        if not isinstance(pref, str):
            continue
        cleaned = pref.strip().lower()
        if not cleaned or cleaned not in VALID_DAMAGE_TYPES:
            continue
        if cleaned not in seen:
            seen.add(cleaned)
            warp_yolo_preferences.append(cleaned)
```

Important: The `seen` set used here for deduplication must use a fresh variable name like `_pref_seen` to avoid collision with the existing `seen` variable at line 351.

### 7. Pass normalized field into the `RunSave(...)` constructor
**File:** `endless_idler/save.py`, inside the `return RunSave(...)` in `_normalized_save()` (after line 504, `warp_character_obtained=warp_character_obtained,`)

Add:
```python
        warp_yolo_preferences=warp_yolo_preferences,
```

### 8. Create migration file
**File:** `endless_idler/save_migrations/migration_v14_yolo_prefs.py` (new file)

Pattern from `migration_v13_warp.py`:

```python
from __future__ import annotations

from endless_idler.save_migrations.base import MigratableSave
from endless_idler.save_migrations.base import SaveMigration


def _add_yolo_prefs(save: MigratableSave) -> None:
    if save.version >= 14:
        return

    setattr(save, "warp_yolo_preferences", [])
    save.version = 14


migration = SaveMigration(
    migration_id="v14_yolo_prefs",
    order=1400,
    migrate=_add_yolo_prefs,
)
```

This will be auto-discovered by `save_migrations/__init__.py` (line 16 in `_module_names()`: `name.startswith("migration_")`).

---

## Acceptance Criteria

1. `uv run basedpyright` passes with no new errors
2. Roundtrip test: save with `warp_yolo_preferences=["fire", "ice"]`, load, verify field survives
3. v13 migration test: load a save with `"version": 13` (no `warp_yolo_preferences` key), verify field defaults to `[]`
4. Normalization filters out invalid damage types (e.g., `"water"`, `"arcane"`), deduplicates, lowercases
5. All existing warp and save tests still pass

---

## Verification Commands

```bash
uv run basedpyright
uv run pytest tests/test_warp_engine.py tests/test_save_migrations_discovery.py -q
```
