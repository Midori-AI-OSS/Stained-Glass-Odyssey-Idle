# Task 7: Verification & Polish

**Status:** Not started  
**Dependencies:** Tasks 1–6 (all must be complete before verification)  
**Blocks:** None (final task)

---

## What to Do

Run the full verification suite — linters, type checker, tests — fix any issues found, and perform a manual checklist covering save/load roundtrip, shard earning, warp navigation, pull flows, and YOLO preferences.

---

## Pre-execution Checks

- [x] Tasks 1–6 are complete
- [x] `uv sync --group ci` has been run at least once this session
- [x] `endless_idler/save_migrations/migration_v14_yolo_prefs.py` exists (from Task 1)
- [x] `endless_idler/warp/constants.py` has `SHARD_COST_PER_PULL` and `BANNER_SHARD_MAP` (from Task 2)
- [x] `endless_idler/warp/engine.py` has `can_afford()`, `_deduct_cost()`, `_deduct_yolo()`, `_deduct_elemental()` (from Task 2)
- [x] `endless_idler/ui/warp/screen.py` exists with `WarpScreen` (from Task 3)
- [x] `endless_idler/ui/theme/warp_widget.py` exists and is registered (from Task 4)
- [x] YOLO prefs panel integrated into `WarpScreen` (from Task 5)
- [x] `endless_idler/ui/main_menu.py` has warp navigation integrated (from Task 6)

---

## Step-by-Step Instructions

### 1. Run Ruff (linter)

```bash
uv run ruff check .
```

- Fix any `F` (Pyflakes), `E`/`W` (pycodestyle), or `I` (isort) violations
- Pay special attention to unused imports from removed `_stub_warp`
- If `as_str_list` import was added but unused, remove it (but it should be used in `load()`)

### 2. Run Basedpyright (type checker)

```bash
uv run basedpyright
```

Common issues to watch for:
- Missing import of `as_str_list` in `save.py` (Task 1, step 2)
- Type mismatch on `WarpEngine` creation in `WarpScreen._build_engine()`: ensure `rng` parameter is passed
- `_yolo_pref_buttons` dict type annotation in `WarpScreen`
- `color_for_damage_type_id` usage in theme buttons
- Migration file type compatibility with `MigratableSave` protocol

### 3. Run full test suite

```bash
uv run pytest -q
```

Fix any test failures. Expected potential issues:
- Existing warp tests: `tests/test_warp_engine.py` — tests like `test_pity_resets_after_five_star` call `engine.pull()` without pre-seeding `save.inventory` with shards. **Fix**: seed inventory in `_make_engine()` helper (line 52-65) or in individual tests by adding `save.inventory["fire_shard"] = 160` before pulling.
- Save migration tests: `tests/test_save_migrations_discovery.py` — verify it discovers and runs `v14_yolo_prefs` migration
- `tests/test_warp_banners.py` — should be unaffected

### 4. Run warp-specific tests

```bash
uv run pytest tests/test_warp_engine.py tests/test_warp_banners.py -q
```

Expected to pass or need inventory seeding as noted above.

### 5. Verify migration auto-discovery

```bash
uv run python -c "
from endless_idler.save_migrations import _discover_migrations
migrations = _discover_migrations()
ids = [m.migration_id for m in migrations]
print('Migrations found:', ids)
assert 'v14_yolo_prefs' in ids, 'Missing v14_yolo_prefs migration'
assert 'v13_warp_fields' in ids
print('OK — migration auto-discovery working')
"
```

### 6. Verify save version is 14

```bash
uv run python -c "
from endless_idler.save import SAVE_VERSION
assert SAVE_VERSION == 14, f'Expected SAVE_VERSION=14, got {SAVE_VERSION}'
print(f'SAVE_VERSION={SAVE_VERSION} OK')
"
```

### 7. Verify theme builds

```bash
uv run python -c "
from endless_idler.ui.theme.registry import build_stained_glass_stylesheet
result = build_stained_glass_stylesheet()
assert 'WarpScreenRoot' in result
assert 'WarpBannerPanel' in result
assert 'WarpPullButton' in result
assert 'WarpResultPanel' in result
assert 'WarpYoloPrefsPanel' in result
assert 'WarpYoloPrefButton' in result
print('OK — all warp selectors present in stylesheet')
"
```

### 8. Verify imports are clean

```bash
uv run python -c "
from endless_idler.ui.warp.screen import WarpScreen
from endless_idler.ui.theme.warp_widget import STYLESHEET
from endless_idler.save_migrations.migration_v14_yolo_prefs import migration
from endless_idler.warp.engine import WarpEngine
from endless_idler.warp.constants import SHARD_COST_PER_PULL, BANNER_SHARD_MAP
print('OK — all new modules import cleanly')
"
```

### 9. Manual verification checklist

Run the application and verify:

- [ ] Fresh save: `warp_yolo_preferences` defaults to `[]`
- [ ] Shards earned from idle runs appear in inventory
- [ ] Warp button in top bar navigates to warp screen
- [ ] 7 tabs show correct banner info (Fire, Ice, Wind, Lightning, Light, Dark, YOLO)
- [ ] Empty-pool tabs are grayed out with "(empty)" pool summary
- [ ] Pull with insufficient shards → button disabled or error raised
- [ ] Pull with sufficient shards → shards deducted, result displayed, pity updated
- [ ] YOLO tab shows preferences panel
- [ ] Selecting 3 YOLO prefs works, 4th selection deselects oldest
- [ ] YOLO prefs survive closing/reopening the warp screen
- [ ] YOLO pull deducts from preferred types first, then fallback
- [ ] Save/load preserves all warp state including `warp_yolo_preferences`
- [ ] Other screens (Home, Idle, Layout, Inventory, Settings) still work
- [ ] Guidebook and Feedback stub buttons still show "not implemented"

### 10. If any gaps found

- Fix the issues directly
- If a fix requires scope beyond these tasks, note it in the run log (`/tmp/agents-artifacts/agent-output.md`) as a blocker or follow-up
- Re-run verification steps 1-4 after fixes

---

## Acceptance Criteria (pass/fail gates)

| Gate | Command/Check | Expected |
|------|--------------|----------|
| Ruff | `uv run ruff check .` | Zero violations |
| Basedpyright | `uv run basedpyright` | Zero errors |
| Pytest full | `uv run pytest -q` | All tests pass |
| Warp tests | `uv run pytest tests/test_warp_engine.py tests/test_warp_banners.py -q` | All pass |
| Migration discovery | Verify `v14_yolo_prefs` found | Present |
| SAVE_VERSION | Verify `SAVE_VERSION == 14` | `14` |
| Theme builds | Verify selectors in stylesheet | All present |
| Imports clean | Import all new modules | No ImportError |

---

## Verification Commands

```bash
# Run everything in sequence:
uv sync --group ci
uv run ruff check .
uv run basedpyright
uv run pytest -q
uv run pytest tests/test_warp_engine.py tests/test_warp_banners.py -q
```
