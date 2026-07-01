# 09 – Warp Engine Core

## What to Do
Create `endless_idler/warp/engine.py` with the `WarpEngine` class implementing the roll resolution pipeline, pity tracking, and YOLO logic.

## Relevant Files
- `endless_idler/warp/engine.py` (new file)
- `endless_idler/warp/constants.py` — all rate/pity constants
- `endless_idler/warp/banners.py` — `BannerDefinition`, `generate_banners()`
- `endless_idler/save.py` — `RunSave` (reading/writing warp state via dict fields)

## Pre-Execution Checks
- [ ] Confirm Tasks 01-03 (save model) and Tasks 07-08 (constants + banners) are complete.
- [ ] Verify `RunSave` warp fields: `warp_pity` (`dict[str, int]`), `warp_pull_total` (`dict[str, int]`), `warp_last_rarity` (`dict[str, int | None]`), `warp_character_obtained` (`dict[str, list[str]]`).
- [ ] **YOLO probability math**: At max pity (179), base p5 = `PITY_BASE_RATE + 179 * PITY_SLOPE` = `0.00001 + 179 * (0.04999/159.0)` ≈ `0.0562`. With YOLO multiplier (50x), p5 ≈ `2.81` which exceeds 1.0 — clamp to 1.0. This means YOLO guarantees a 5★ at max pity at 179. The "ensure sum ≤ 1.0" normalization is already satisfied by clamping p5 to 1.0 (since p5 is the only direct probability; 6★/7★ are conditional on 5★).

## Steps

1. Create `endless_idler/warp/engine.py`.

2. Define `WarpOutcome` dataclass with:
   - `rarity: int | None` — `5`, `6`, `7`, or `None` for non-character/prismatic result
   - `character_id: str | None` — the obtained character, or `None`
   - `pity_before: int` — pity counter before this pull
   - `pity_after: int` — pity counter after this pull (0 if hit 5★+, else pity_before + 1)

3. Implement `WarpEngine` class:
   - `__init__(self, save: RunSave, banner_id: str, banner: BannerDefinition, *, rng: random.Random)`:
     - `self._save = save`
     - `self._banner_id = banner_id`
     - `self._banner = banner`
     - `self._rng = rng`

   - `pull(self) -> WarpOutcome`:
     1. Read current pity from `save.warp_pity.get(banner_id, 0)`.
     2. **Increment pull total**: `save.warp_pull_total[banner_id] = save.warp_pull_total.get(banner_id, 0) + 1`.
     3. **Compute base 5★ rate**: `p5 = PITY_BASE_RATE + pity * PITY_SLOPE`.
     4. **YOLO override** (if `banner_id == "yolo"`):
        - `p5 *= YOLO_RATE_MULTIPLIER`; clamp `p5` to max `1.0`.
        - `s6 = SIX_STAR_PROMO_RATE * YOLO_RATE_MULTIPLIER`; clamp to max `1.0`.
        - `s7 = SEVEN_STAR_PROMO_RATE * YOLO_RATE_MULTIPLIER`; clamp to max `1.0`.
        - Use `s6`/`s7` instead of the base constants for 6★/7★ checks.
     5. **Hard guarantee**: If `pity >= PITY_HARD_GUARANTEE`, force `p5 = 1.0`.
     6. **5★ check**: Roll `rng.random() < p5`.
        - **No 5★**: Increment pity via `_increment_pity()`. Return `WarpOutcome(rarity=None, character_id=None, pity_before=pity, pity_after=pity+1)`.
        - **Yes 5★**: Proceed to 6★ check.
     7. **6★ check**: Roll `rng.random() < (s6 if yolo else SIX_STAR_PROMO_RATE)`.
        - **No 6★**: Select random 5★ character from `banner.five_star_pool`. If pool is empty → prismatic fallback (`rarity=None`, `character_id=PRISMATIC_FALLBACK_ID`). Reset pity. Record. Return.
        - **Yes 6★**: Proceed to 7★ check.
     8. **7★ check**: Roll `rng.random() < (s7 if yolo else SEVEN_STAR_PROMO_RATE)`.
        - **Yes 7★**:
          - **Luna eligibility**: Luna is eligible if this is the YOLO banner (always), OR if the banner is elemental AND has at least one non-generic character in either pool (5★ or 6★).
          - If Luna eligible: return `WarpOutcome(rarity=7, character_id="luna", ...)`. Reset pity. Record. Update last_rarity.
          - If Luna NOT eligible: fall through to 6★ selection.
        - **No 7★** (or 7★ not eligible): Select random 6★ character from `banner.six_star_pool`. If pool is empty → fall back to 5★ selection. Reset pity. Record. Update last_rarity. Return.

   - `select_from_pool(self, pool: list[BannerCharacter]) -> str | None`:
     - Uniform random selection via `self._rng.choice(pool).char_id`.
     - Returns `None` if pool is empty.

   - `_record_obtained(self, character_id: str, rarity: int) -> None`:
     - Append `character_id` to `save.warp_character_obtained.setdefault(banner_id, [])`.
     - Set `save.warp_last_rarity[banner_id] = rarity`.

   - `_reset_pity(self) -> None`:
     - `save.warp_pity[banner_id] = 0`.

   - `_increment_pity(self) -> None`:
     - `save.warp_pity[banner_id] = save.warp_pity.get(banner_id, 0) + 1`

4. **Important constraints**:
   - Luna must NEVER be in any banner pool (already excluded in Task 08). She is only obtainable through the 7★ promotion path.
   - The pity counter resets on ANY 5★, 6★, or 7★ hit (character or prismatic).
   - `warp_character_obtained` records ALL obtained characters (including duplicates).
   - `warp_pull_total` counts EVERY pull attempt (including non-character results).
   - Prismatic fallback (`PRISMATIC_FALLBACK_ID`) is returned when banner pool is empty — pity still resets.

## Acceptance Criteria
- Calling `pull()` 180 times on an empty banner guarantees at least one 5★ hit (hard guarantee at pity 179).
- 7★ Luna pull probability at max pity: `p5(179) ≈ 0.0562`; then `0.0562 * 0.001 * 0.000001 ≈ 5.6e-11` per pull (astronomically low, effectively zero in simulation).
- Pity resets to 0 after any 5★/6★/7★ result (including prismatic).
- YOLO banner produces significantly higher 5★ rates. At max pity (179), YOLO p5 = 1.0 (guaranteed 5★).
- `uv run ruff check endless_idler/warp/engine.py` passes.
- `uv run basedpyright` passes.

## Dependencies
- Tasks 01, 02, 03 (save model with warp fields must exist; engine reads/writes SaveManager-managed state)
- Task 07 (constants)
- Task 08 (banners)

## Audit Notes
- PASS: File paths and dependency chain verified.
- FIXED: `_record_obtained()` signature corrected — needs `rarity` parameter to set `warp_last_rarity`. The original task description had `_record_obtained` getting rarity from `self`, which it doesn't have.
- FIXED: YOLO probability math clarified. At max pity, base p5 ≈ 0.0562; p5 * 50 = 2.81 → clamp to 1.0. This means YOLO guarantees 5★ at max pity. The "sum ≤ 1.0 normalization" is naturally handled by clamping p5 to 1.0 since 6★/7★ checks are conditional on 5★ hit.
- FIXED: Acceptance criteria's 7★ probability corrected from "≈ 1e-9" to "≈ 5.6e-11" (the math: 0.0562 * 0.001 * 0.000001 ≈ 5.62e-11).
- PASS: Prismatic fallback resets pity (confirmed in constraint list).
