# 07 – Warp Constants Module

## What to Do
Create `endless_idler/warp/constants.py` with all warp engine constants.

## Relevant Files
- `endless_idler/warp/constants.py` (new file)
- `endless_idler/warp/__init__.py` (new file — package marker)

## Pre-Execution Checks
- [ ] Confirm `endless_idler/warp/` directory structure. Create if missing.
- [ ] Read `AGENTS.md` style guidelines — one import per line, sort shortest-to-longest, blank lines between groups.

## Steps

1. Create `endless_idler/warp/__init__.py` as an empty package marker (no content).

2. Create `endless_idler/warp/constants.py` with the following constants:

   **Banner IDs** (a tuple of str for the 7 banners):
   ```python
   BANNER_IDS: tuple[str, ...] = (
       "fire",
       "ice",
       "wind",
       "lightning",
       "light",
       "dark",
       "yolo",
   )
   ```

   **Pity formula** (linear curve from spec):
   ```python
   PITY_BASE_RATE: float = 0.00001          # 0.001% base for a 5★
   PITY_SLOPE: float = 0.04999 / 159.0      # increment per pity count
   PITY_HARD_GUARANTEE: int = 179           # 5★ guaranteed at pity >= 179
   ```

   **Promotion rates**:
   ```python
   SIX_STAR_PROMO_RATE: float = 0.001       # 0.1% of 5★ hits promote to 6★
   SEVEN_STAR_PROMO_RATE: float = 0.000001  # 0.0001% of 6★ hits promote to 7★
   ```

   **YOLO multiplier**:
   ```python
   YOLO_RATE_MULTIPLIER: int = 50
   ```

   **Rarity enum/labels**:
   ```python
   RARITY_NONE: int | None = None   # fallback / non-character result
   RARITY_5 = 5
   RARITY_6 = 6
   RARITY_7 = 7
   ```

   **Prismatic fallback ID** (used when no character matches a banner):
   ```python
   PRISMATIC_FALLBACK_ID: str = "prismatic_shard"
   ```

## Acceptance Criteria
- Module imports without error: `uv run python -c "from endless_idler.warp.constants import BANNER_IDS, PITY_BASE_RATE; print(len(BANNER_IDS), PITY_BASE_RATE)"` → `7 1e-05`
- `uv run ruff check endless_idler/warp/constants.py endless_idler/warp/__init__.py` passes.
- `uv run basedpyright` passes.

## Dependencies
- None (can be done in parallel with save model tasks)

## Audit Notes
- PASS: No contradictions with existing codebase. New package under `endless_idler/warp/`.
- FIXED: Added `Pre-Execution Checks` section.
- PASS: `RARITY_NONE` type `int | None = None` — annotation describes usage type (sentinel for non-character result), even though the constant itself is always `None`. Acceptable.
- INFO: `PITY_SLOPE = 0.04999 / 159.0` computes at import time. The result `0.000314402...` is deterministic. Consider making it a pre-computed constant if floating-point reproducibility across platforms is critical (Python float is IEEE 754 so deterministic).
