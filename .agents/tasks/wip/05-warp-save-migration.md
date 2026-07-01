# 05 – Create v13 Save Migration

## What to Do
Create a new save migration module `migration_v13_warp.py` that initializes empty warp fields for saves coming from version 12 or earlier.

## Relevant Files
- `endless_idler/save_migrations/migration_v13_warp.py` (new file)
- Reference: `endless_idler/save_migrations/migration_v12_lunar_reset.py` (pattern to follow)
- `endless_idler/save_migrations/base.py` — `SaveMigration` dataclass, `MigratableSave` protocol
- `endless_idler/save_migrations/__init__.py` — auto-discovers `migration_*` modules (line 16)

## Pre-Execution Checks
- [ ] Confirm Tasks 01 and 04 are complete (SAVE_VERSION=13 and RunSave fields).
- [ ] Read `migration_v12_lunar_reset.py` (25 lines) for exact style/import pattern.
- [ ] Read `base.py` (21 lines) to confirm `MigratableSave` protocol only has `version` and `blessings`.
- [ ] **IMPORTANT**: The `MigratableSave` protocol does NOT declare `warp_pity` etc. The migration function uses `setattr(save, "warp_pity", {})` on an opaque `MigratableSave` object. This works only if the object supports arbitrary attribute assignment (not a slotted dataclass). The test harness uses `_FakeSave` (regular dataclass, no slots). A `RunSave` with `slots=True` would reject `setattr` — but migrations are NOT applied directly to `RunSave` instances in production (currently `apply_migrations` is only called in test code, not wired into `SaveManager.load()`).

## Steps

1. Create `migration_v13_warp.py` following the v12 migration pattern (imports, function, module-level `migration` variable).

2. Define a migrate function `_add_warp_fields(save: MigratableSave) -> None`:
   - If `save.version >= 13`, return early (already migrated — idempotent).
   - Set defaults via `setattr`:
     ```python
     setattr(save, "warp_pity", {})
     setattr(save, "warp_pull_total", {})
     setattr(save, "warp_last_rarity", {})
     setattr(save, "warp_character_obtained", {})
     save.version = 13
     ```
   - Note: `warp_pity`, `warp_pull_total`, etc. are NOT in the `MigratableSave` protocol. Using `setattr` is the idiomatic approach for migrations that add new top-level fields beyond the protocol surface.

3. Create a module-level `migration` variable:
   ```python
   migration = SaveMigration(
       migration_id="v13_warp_fields",
       order=1300,
       migrate=_add_warp_fields,
   )
   ```
   - `order=1300` places it after v12 (order=1200). Uses 100-increment convention.

4. No changes needed in `__init__.py` — auto-discovery via `pkgutil.iter_modules` matching `migration_*` prefix (line 16) handles this automatically.

## Acceptance Criteria
- `uv run pytest tests/test_save_migrations_discovery.py -q` passes (existing tests, confirms discovery works).
- A `_FakeSave(version=12)` passed through `save_migrations.apply_migrations()` ends with `version=13` and four empty dict warp fields.
- The new migration file must be discoverable: `uv run python -c "from endless_idler.save_migrations import _discover_migrations; ids=[m.migration_id for m in _discover_migrations()]; assert 'v13_warp_fields' in ids; print('OK')"` prints `OK`.
- `uv run ruff check endless_idler/save_migrations/migration_v13_warp.py` passes.
- `uv run basedpyright` passes.

## Dependencies
- Task 01 (SAVE_VERSION 13 and RunSave fields must exist)

## Audit Notes
- PASS: `migration_v12_lunar_reset.py` pattern confirmed — 25 lines, simple function + module-level `migration` variable.
- PASS: `__init__.py` auto-discovery confirmed — `_module_names()` returns any name starting with `migration_` (line 16).
- FIXED: Added note that `MigratableSave` protocol only has `version` and `blessings`. `setattr` for warp fields works on objects without `__slots__` restriction (test harness uses `_FakeSave`).
- FIXED: `apply_migrations()` is NOT currently wired into `SaveManager.load()` — this matches existing v12 migration behavior. Both are tested in isolation.
- FIXED: Acceptance criteria updated — `_FakeSave` object (not a raw dict) is needed for `apply_migrations()`.
- INFO: `order=1300` uses 100-increment from v12's `order=1200`. Chronologically correct.
