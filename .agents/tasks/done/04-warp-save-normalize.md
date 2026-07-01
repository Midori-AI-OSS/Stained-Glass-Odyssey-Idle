# 04 – Normalize Warp Fields in _normalized_save

## What to Do
Add normalization logic for warp fields in the `_normalized_save()` function so corrupted data loaded from disk gets cleaned up.

## Relevant Files
- `endless_idler/save.py` — `_normalized_save()` function (currently line 290)

## Pre-Execution Checks
- [ ] Confirm Tasks 01 and 02 are complete.
- [ ] Verify `return RunSave(...)` call at the bottom of `_normalized_save` (currently lines 393–446). The warp fields must be added after `layout_owned_ordering` (line 443–445).

## Steps

1. Extract the four warp field values from `save` using `getattr` with empty dict defaults, following the defensive pattern already used for `blessings` (line 414) and `passives` (line 415):
   ```python
   warp_pity=dict(getattr(save, "warp_pity", {}))
   warp_pull_total=dict(getattr(save, "warp_pull_total", {}))
   warp_last_rarity=dict(getattr(save, "warp_last_rarity", {}))
   warp_character_obtained=dict(getattr(save, "warp_character_obtained", {}))
   ```

2. Normalize each:
   - `warp_pity`: iterate `items()`, strip keys. Keep only entries where key is non-empty `str` and value is `>= 0` int. Drop negative values (missing key defaults to 0 at read time).
   - `warp_pull_total`: same as `warp_pity` — keep `>= 0` int values with non-empty str keys.
   - `warp_last_rarity`: iterate `items()`, strip keys. Keep entries where key is non-empty `str` and value is either `None` OR an `int` that is NOT a `bool`. Drop `bool` values (True/False), drop non-numeric strings, drop negatives.
   - `warp_character_obtained`: iterate `items()`, strip keys. For each value (must be `list`), filter to only non-empty strings. Drop entries where the filtered list is empty. Drop entries with empty string keys.

   **Important**: Normalization must create new dicts, not mutate in place. Follow existing normalization pattern (e.g., `stacks` at lines 363–369 creates a new dict).

3. Pass the normalized values into the `return RunSave(...)` constructor call.
   Insert after the `layout_owned_ordering` argument (currently lines 443–445):
   ```python
   warp_pity=warp_pity,
   warp_pull_total=warp_pull_total,
   warp_last_rarity=warp_last_rarity,
   warp_character_obtained=warp_character_obtained,
   ```

## Acceptance Criteria
- A `RunSave` with `warp_pity={"fire_banner": -5, "fire": 3}` normalizes to `warp_pity={"fire": 3}` (negative value entry dropped, positive kept).
- A `RunSave` with `warp_pity={"": 5, "  ": 3}` normalizes to `warp_pity={}` (empty/whitespace keys dropped).
- `warp_last_rarity={"fire_banner": None, "ice": 5, "wind": True}` normalizes to `{"fire_banner": None, "ice": 5}` (bool True is dropped).
- `warp_character_obtained={"fire": ["ally", "", "  "], "ice": []}` normalizes to `{"fire": ["ally"]}` (empty string items and empty lists dropped).
- `uv run ruff check endless_idler/save.py` passes.
- `uv run basedpyright` passes.

## Dependencies
- Task 01 (dataclass fields)
- Task 02 (codec helpers)

## Audit Notes
- PASS: File path and line number verified (`_normalized_save` at line 290, `return RunSave(...)` at line 393).
- FIXED: Added explicit insertion point after `layout_owned_ordering` in `RunSave(...)` constructor call.
- FIXED: Clarified normalization rules — `bool` rejection for `warp_last_rarity`, empty key handling, new dict creation (immutable pattern).
- FIXED: Expanded acceptance criteria to cover edge cases (empty keys, mixed valid/invalid in same dict).
- PASS: `getattr` defensive pattern matches existing `blessings`/`passives` pattern at lines 414–415.
