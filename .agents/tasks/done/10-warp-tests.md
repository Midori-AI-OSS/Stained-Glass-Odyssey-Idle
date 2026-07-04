# 10 – Warp Validation Tests

## What to Do
Create comprehensive tests for the warp engine, banner generation, and save round-tripping.

## Relevant Files
- `tests/` directory — existing test patterns (pytest, fixtures)
- Create `tests/test_warp_banners.py` and `tests/test_warp_engine.py`
- Reference: `tests/test_save_migrations_discovery.py` (pytest, imports, monkeypatch pattern)
- Reference: `tests/test_save_schema_cleanup.py` (save load/save round-trip pattern with `monkeypatch, tmp_path`)

## Pre-Execution Checks
- [ ] Confirm ALL previous tasks (01–09) are complete.
- [ ] Confirm `endless_idler/warp/` package fully functional.
- [ ] Read existing test patterns: tests use `from __future__ import annotations`, pytest-style functions, `monkeypatch` for env overrides, `tmp_path` for temp files.

## Steps

1. Create `tests/test_warp_banners.py`:
   - **Test banner generation produces 7 banners**: verify `generate_banners()` outputs all 7 `BANNER_IDS`.
   - **Test Luna excluded**: verify Luna (char_id `"luna"`) does not appear in any banner's 5★ or 6★ pool.
   - **Test dual-type placement**: verify `lady_fire_and_ice` appears in both `fire` and `ice` banners, not in other elemental banners.
   - **Test YOLO pool is superset**: verify YOLO banner's 5★/6★ pools contain all characters from all elemental banners combined.
   - **Test empty/non-matching banner**: verify that banner generation handles the case where no characters match a given element (produce empty pools, not missing keys). Note: all 6 elemental banners currently have characters, but verify structurally.
   - **Test generic characters excluded from elemental**: verify any characters with `damage_type_id == "generic"` do not appear in elemental banners (only YOLO).

2. Create `tests/test_warp_engine.py`:
   - **Test pity curve shape**: Run 10,000 simulated pulls, record pity values at which 5★ occurred. Verify the empirical CDF roughly matches the expected `p5(pity)` formula. Verify no pull exceeds hard guarantee at pity 179. Use `random.Random(0)` for reproducibility.
   - **Test 7★ odds are astronomically low**: Run 100,000 simulated pulls on a banner with a 5★ character. Count 7★ hits. Verify count is 0 (expected value ≈ 5.6e-6 per 100k pulls). Do not run 1M pulls — keep test fast.
   - **Test pity reset**: Verify pity counter resets to 0 after any 5★, 6★, or 7★ hit.
   - **Test pity increments**: Verify pity increments by 1 on non-5★ pulls.
   - **Test pull_total increments**: Verify `warp_pull_total` counts every call to `pull()` regardless of outcome.
   - **Test last_rarity tracking**: Verify `warp_last_rarity` records the correct rarity of the most recent pull per banner.
   - **Test obtained list**: Verify `warp_character_obtained` accumulates character IDs for successful pulls (including duplicates).
   - **Test YOLO rate boost**: Compare 5★ hit rates between a normal elemental banner and the YOLO banner over many pulls. YOLO should be significantly higher. At max pity, YOLO guarantees 5★ every pull.
   - **Test prismatic fallback**: When a banner has empty 5★ and 6★ pools, verify `WarpOutcome.rarity` is `None` and `character_id` is `"prismatic_shard"`, and pity still resets.
   - **Test prismatic falls back to 5★ if 6★ pool empty**: When banner has 5★ characters but empty 6★ pool, and a 6★ promotion rolls, verify it falls back to 5★ selection.
   - **Test 7★ eligibility — elemental without characters**: Create a mock elemental banner with empty pools. Verify Luna is NOT returned (7★ ineligible).
   - **Test 7★ eligibility — YOLO**: Verify Luna IS eligible on YOLO banner (always eligible).
   - **Test save round-trip**: Create a `RunSave`, perform several pulls, save/load via `SaveManager`, verify all four warp state fields survive.
   - **Test multiple banner state isolation**: Pull on two different banners. Verify pity, pull_total, last_rarity are per-banner independent.
   - **Test hard guarantee at pity 179**: Seed the RNG to always fail the 5★ check for pulls 0–178. Verify pull 179 is a guaranteed 5★.

3. **Statistical testing notes**:
   - Use `random.Random(0)` for deterministic seeds.
   - For large simulations (10k+ pulls), keep individual test runtime under 5 seconds.
   - Use `pytest.approx` for floating-point comparisons.
   - Prefer covering all branches; use `# pragma: no cover` only if truly unreachable.

## Acceptance Criteria
- `uv run pytest tests/test_warp_engine.py tests/test_warp_banners.py -q -x` passes all tests.
- `uv run ruff check tests/test_warp_engine.py tests/test_warp_banners.py` passes.
- `uv run basedpyright` passes (no new errors).

## Dependencies
- All previous tasks (01–09) must be complete.

## Audit Notes
- PASS: Existing test directory confirmed at `tests/`. Test patterns (pytest, monkeypatch, tmp_path) confirmed via `test_save_schema_cleanup.py` and `test_save_migrations_discovery.py`.
- FIXED: Added more specific test cases: pity increments, prismatic fallback to 5★ when 6★ pool empty, multiple banner state isolation, hard guarantee at pity 179.
- FIXED: 7★ odds test reduced from 1M to 100k pulls for test speed. Expected ≈ 0 hits (5.6e-6 per 100k).
- FIXED: Added generic-excluded-from-elemental test for banner generation.
- INFO: Tests on `test_warp_engine.py` will need mock banner pools to test edge cases (empty pools, single-character pools). Use `BannerCharacter` dataclass from `endless_idler.warp.banners` to construct test fixtures.
