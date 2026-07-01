# 01 – Warp Save Dataclass Fields

## What to Do
Add four new warp-related fields to the `RunSave` dataclass in `endless_idler/save.py` and bump the save version.

## Relevant Files
- `endless_idler/save.py` — `RunSave` dataclass, `SAVE_VERSION` constant

## Pre-Execution Checks
- [ ] Confirm `from __future__ import annotations` is at top of `save.py` (line 1). Required for `int | None` union syntax.
- [ ] Confirm `layout_owned_ordering` is at line 134. File may have shifted — verify with `grep -n "layout_owned_ordering" endless_idler/save.py`.
- [ ] Confirm `SAVE_VERSION` is at line 33 and currently reads `12`.

## Steps

1. Bump `SAVE_VERSION` from `12` to `13` (currently line 33).
2. Add the following `field(default_factory=...)` entries to `RunSave`, placed **immediately after** the `layout_owned_ordering` field:

| Field name | Type annotation | Default factory |
|---|---|---|
| `warp_pity` | `dict[str, int]` | `dict` |
| `warp_pull_total` | `dict[str, int]` | `dict` |
| `warp_last_rarity` | `dict[str, int \| None]` | `dict` |
| `warp_character_obtained` | `dict[str, list[str]]` | `dict` |

3. Ensure all fields use `slots=True` compatible syntax: `field(default_factory=dict)` — no lambda needed. `dict` is callable and yields `{}`.

## Acceptance Criteria
- `SAVE_VERSION` reads `13`.
- `RunSave()` instantiates with `warp_pity == {}`, `warp_pull_total == {}`, `warp_last_rarity == {}`, `warp_character_obtained == {}`.
- `uv run python -c "from endless_idler.save import RunSave; s=RunSave(); print(s.warp_pity, s.warp_pull_total, s.warp_last_rarity, s.warp_character_obtained)"` prints four empty dicts.

## Dependencies
- None (first task)

## Audit Notes
- PASS: File paths verified — `save.py` exists at correct path. `layout_owned_ordering` at line 134, `SAVE_VERSION` at line 33. `from __future__ import annotations` present.
- PASS: `int | None` syntax already used in codebase (e.g. `list[str | None]`).
- PASS: File currently 592 lines — adding ~6 lines stays under hard max of 1000.
- PASS: `field(default_factory=dict)` is slots-safe. `dict` is the callable, no lambda needed.
- INFO: The `import field` is already imported on line 8 of save.py.
