# 02 – Warp Save Codec Helpers

## What to Do
Add serialization/normalization helper functions in `endless_idler/save_codec.py` to handle the four new warp field types.

## Relevant Files
- `endless_idler/save_codec.py` — parse/normalize helpers

## Pre-Execution Checks
- [ ] Confirm `from __future__ import annotations` is at top (line 8). Required for `int | None` return type.
- [ ] Familiarize with existing `as_int_dict` (lines 134–151), `as_str_list` (lines 109–118), and `as_optional_str_list` (lines 121–131) for pattern reference.

## Steps

1. Add a helper `as_str_list_dict(value: object) -> dict[str, list[str]]`:
   - If not a dict, return `{}`.
   - For each key (must be `str`, stripped, non-empty), value must be a `list`.
   - Each list item is a string; strip and skip empties.
   - Only include entries with at least one valid string.

2. Add a helper `as_noneable_int_dict(value: object) -> dict[str, int | None]`:
   - If not a dict, return `{}`.
   - For each key (must be `str`, stripped, non-empty), value is `None` if raw value is `None`, or attempt `int(raw)`.
   - **Reject `bool`**: if `isinstance(raw, bool)`, skip the entry (even though `bool` is technically an `int`).
   - If int conversion fails, skip the entry.
   - **Allow zero**: Unlike `as_int_dict`, this helper accepts `0` as a valid value (pity resets to 0).

3. Export both new helpers from the module so `save.py` can import them (follow the existing import pattern — each function explicitly named in separate import lines).

> **Note on reusing `as_int_dict`**: `as_int_dict` drops values `<= 0` (line 148). For `warp_pity` and `warp_pull_total`, this is acceptable: missing key defaults to 0 via `.get(banner_id, 0)`, so dropping zero-valued entries from JSON is semantically correct.

> **Note**: `as_noneable_int_dict` is needed for `warp_last_rarity` (values can be `None` or `int`) and must accept `0` for pity resets.

## Acceptance Criteria
- `uv run python -c "from endless_idler.save_codec import as_str_list_dict, as_noneable_int_dict; print(as_str_list_dict({'a': ['x','y'], 'b': []}), as_noneable_int_dict({'a': 5, 'b': None, 'c': True, 'd': 0}))"` produces `{'a': ['x', 'y']} {'a': 5, 'b': None, 'd': 0}` (bool/True is rejected, 0 is kept).
- `uv run ruff check endless_idler/save_codec.py` passes.
- `uv run basedpyright` passes (no new errors).

## Dependencies
- None (independent of other warp tasks; can be done in parallel with 01)

## Audit Notes
- PASS: File paths verified. `save_codec.py` exists. `from __future__ import annotations` present.
- FIXED: Clarified that `as_noneable_int_dict` must accept `0` (unlike `as_int_dict` which drops `<= 0`). Pity reset sets value to 0.
- FIXED: Acceptance criteria updated to include a `0` value test case (`'d': 0`) to confirm zero is preserved.
- INFO: File currently 597 lines — adding ~50 lines pushes close to soft max. Consider placing new helpers before existing helpers to keep related code together.
