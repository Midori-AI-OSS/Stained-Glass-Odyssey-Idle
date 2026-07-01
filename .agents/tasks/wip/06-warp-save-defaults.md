# 06 – Ensure Warp Defaults in new_run_save and Bootstrap

## What to Do
Verify that `new_run_save()` and the rest of the save bootstrap pipeline produce correct default values for the new warp fields. Since the fields use `field(default_factory=dict)` in the dataclass, no additional changes should be needed — but this task confirms it.

## Relevant Files
- `endless_idler/save.py` — `new_run_save()` (line 457), `_normalized_save()` (line 290)
- `endless_idler/save_bootstrap.py` — `bootstrap_party()` (line 34)
- `endless_idler/save.py` — `sanitize_save_characters()` (line 467) — does not touch warp fields; verify they survive sanitization unscathed.

## Pre-Execution Checks
- [ ] Confirm Tasks 01, 04 are complete.

## Steps

1. **Verify `new_run_save()`** (line 457): Returns `RunSave(tokens=DEFAULT_RUN_TOKENS)`. Since all four warp fields have `field(default_factory=dict)`, they automatically default to `{}` via dataclass machinery. No code change expected.

2. **Verify `_normalized_save()`** (line 290): Task 04 already adds warp normalization. After normalization, empty dicts stay empty dicts. Confirm this by running the acceptance check below.

3. **Verify `bootstrap_party()`** (line 34): Only touches `onsite`, `offsite`, `standby`, `stacks`. Does not read or write warp fields. No change expected.

4. **Verify `sanitize_save_characters()`** (line 467): Cleans character-related fields (bar, onsite, offsite, standby, stacks, inventory, character_progress, character_stats, character_initial_stats, character_deaths). Does not touch warp fields. Warp fields survive sanitization unscathed. No change expected.

5. If any verified path produces `None` instead of `{}` for a warp field, add explicit initialization. Otherwise, this task requires zero code changes — document by adding a note to this file: `VERIFIED: No code changes needed — all paths produce correct defaults.`

## Acceptance Criteria
- `uv run python -c "from endless_idler.save import new_run_save; s=new_run_save(); assert s.warp_pity == {}; assert s.warp_pull_total == {}; assert s.warp_last_rarity == {}; assert s.warp_character_obtained == {}; print('OK')"` prints `OK`.
- `_normalized_save(new_run_save())` does not mutate warp fields away from empty dicts.
- `save_bootstrap.bootstrap_party()` does not corrupt warp field defaults.
- `sanitize_save_characters()` leaves warp fields unchanged.
- `uv run ruff check .` passes.

## Dependencies
- Tasks 01, 04 (dataclass fields + normalization must exist)

## Audit Notes
- PASS: `new_run_save()` at line 457 returns `RunSave(tokens=DEFAULT_RUN_TOKENS)` — dataclass defaults handle warp fields automatically.
- FIXED: Added `sanitize_save_characters()` to verification scope. It touches many fields but not warp fields — must confirm this holds.
- PASS: `bootstrap_party()` confirmed to only touch `onsite`, `offsite`, `standby`, `stacks` (lines 34–89).
- INFO: This task is verification-only; zero code changes expected. Task 03 handles serialization, Task 04 handles normalization.
