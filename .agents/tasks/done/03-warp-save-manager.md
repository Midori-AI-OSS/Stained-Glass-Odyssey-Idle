# 03 – Wire Warp Fields Into SaveManager

## What to Do
Wire the four new warp fields through `SaveManager.load()` and `SaveManager.save()` so they round-trip through JSON.

## Relevant Files
- `endless_idler/save.py` — `SaveManager.load()` (line 146), `SaveManager.save()` (line 229)
- `endless_idler/save_codec.py` — helpers created in Task 02

## Pre-Execution Checks
- [ ] Confirm Tasks 01 and 02 are complete (dataclass fields + codec helpers exist).
- [ ] Confirm import section at top of `save.py` has room. Add two new imports after existing `save_codec` imports (after line 30).

## Steps

1. **Add imports** at top of `save.py` (after line 30, following the existing sorted-import pattern):
   ```
   from endless_idler.save_codec import as_noneable_int_dict
   from endless_idler.save_codec import as_str_list_dict
   ```

2. **In `load()`** — Add the four warp fields to the `RunSave(...)` constructor call inside the `load()` method.
   Insert after the `layout_owned_ordering=_normalize_layout_owned_ordering(...)` argument (currently line 223–225):
   ```python
   warp_pity=as_int_dict(data.get("warp_pity", {})),
   warp_pull_total=as_int_dict(data.get("warp_pull_total", {})),
   warp_last_rarity=as_noneable_int_dict(data.get("warp_last_rarity", {})),
   warp_character_obtained=as_str_list_dict(data.get("warp_character_obtained", {})),
   ```

3. **In `save()`** — Add the four warp fields to the `payload` dict.
   Insert after `"layout_owned_ordering": save.layout_owned_ordering,` (currently line 255):
   ```python
   "warp_pity": save.warp_pity,
   "warp_pull_total": save.warp_pull_total,
   "warp_last_rarity": save.warp_last_rarity,
   "warp_character_obtained": save.warp_character_obtained,
   ```

## Acceptance Criteria
- A `RunSave` with populated warp fields survives `SaveManager.save()` → `SaveManager.load()` round-trip.
- `uv run ruff check endless_idler/save.py` passes.
- `uv run basedpyright` passes (no new errors).

## Dependencies
- Task 01 (dataclass fields must exist)
- Task 02 (codec helpers must exist)

## Audit Notes
- PASS: File paths and line numbers verified against current `save.py`.
- FIXED: Added exact insertion points — after `layout_owned_ordering` in both `load()` (line 225) and `save()` (line 255), matching the dataclass field ordering.
- FIXED: Added explicit import lines needed — `as_str_list_dict` and `as_noneable_int_dict` from `save_codec`.
- PASS: `as_int_dict` is already imported (line 25). Used for both `warp_pity` and `warp_pull_total`.
