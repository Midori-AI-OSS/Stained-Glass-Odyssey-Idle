"""Warp engine core — roll resolution, pity tracking, and YOLO logic."""

from __future__ import annotations

import random

from dataclasses import dataclass

from endless_idler.save import RunSave
from endless_idler.warp.banners import BannerCharacter
from endless_idler.warp.banners import BannerDefinition
from endless_idler.warp.constants import PITY_BASE_RATE
from endless_idler.warp.constants import PITY_HARD_GUARANTEE
from endless_idler.warp.constants import PITY_SLOPE
from endless_idler.warp.constants import PRISMATIC_FALLBACK_ID
from endless_idler.warp.constants import SEVEN_STAR_PROMO_RATE
from endless_idler.warp.constants import SIX_STAR_PROMO_RATE
from endless_idler.warp.constants import YOLO_RATE_MULTIPLIER


@dataclass(frozen=True, slots=True)
class WarpOutcome:
    """Result of a single warp pull.

    Attributes:
        rarity: ``5``, ``6``, ``7``, or ``None`` for non-character/prismatic result.
        character_id: The obtained character ID, or ``None``.
        pity_before: Pity counter before this pull.
        pity_after: Pity counter after this pull (0 if hit 5★+, else pity_before + 1).
    """

    rarity: int | None
    character_id: str | None
    pity_before: int
    pity_after: int


class WarpEngine:
    """Roll resolution engine with pity tracking and YOLO logic.

    Reads and writes warp state directly on the provided ``RunSave`` instance.
    """

    _save: RunSave
    _banner_id: str
    _banner: BannerDefinition
    _rng: random.Random

    def __init__(
        self,
        save: RunSave,
        banner_id: str,
        banner: BannerDefinition,
        *,
        rng: random.Random,
    ) -> None:
        self._save = save
        self._banner_id = banner_id
        self._banner = banner
        self._rng = rng

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def pull(self) -> WarpOutcome:
        """Execute a single warp pull and return the outcome.

        The pull follows the roll-resolution pipeline:

        1. Read current pity and increment the total-pull counter.
        2. Compute the base 5★ rate (``PITY_BASE_RATE + pity * PITY_SLOPE``).
        3. Apply YOLO rate multiplier if this is the *yolo* banner.
        4. Enforce the hard pity guarantee.
        5. Roll for 5★ → 6★ → 7★ in sequence.
        """
        save = self._save
        banner_id = self._banner_id
        banner = self._banner
        rng = self._rng

        pity = save.warp_pity.get(banner_id, 0)

        # Increment total pull counter
        save.warp_pull_total[banner_id] = (
            save.warp_pull_total.get(banner_id, 0) + 1
        )

        # Compute base 5★ rate
        p5 = PITY_BASE_RATE + pity * PITY_SLOPE

        # YOLO override
        is_yolo = banner_id == "yolo"
        s6: float = SIX_STAR_PROMO_RATE
        s7: float = SEVEN_STAR_PROMO_RATE
        if is_yolo:
            p5 = min(p5 * YOLO_RATE_MULTIPLIER, 1.0)
            s6 = min(SIX_STAR_PROMO_RATE * YOLO_RATE_MULTIPLIER, 1.0)
            s7 = min(SEVEN_STAR_PROMO_RATE * YOLO_RATE_MULTIPLIER, 1.0)

        # Hard guarantee
        if pity >= PITY_HARD_GUARANTEE:
            p5 = 1.0

        # ----- 5★ check -----
        if not (rng.random() < p5):
            self._increment_pity()
            return WarpOutcome(
                rarity=None,
                character_id=None,
                pity_before=pity,
                pity_after=pity + 1,
            )

        # ----- 6★ check -----
        if rng.random() < s6:
            # ----- 7★ check -----
            if rng.random() < s7 and self._is_luna_eligible():
                self._reset_pity()
                self._record_obtained("luna", 7)
                return WarpOutcome(
                    rarity=7,
                    character_id="luna",
                    pity_before=pity,
                    pity_after=0,
                )

            # 7★ failed or Luna not eligible → award a 6★ character
            char_id = self.select_from_pool(banner.six_star_pool)
            if char_id is not None:
                self._reset_pity()
                self._record_obtained(char_id, 6)
                return WarpOutcome(
                    rarity=6,
                    character_id=char_id,
                    pity_before=pity,
                    pity_after=0,
                )

            # 6★ pool empty → fall back to 5★ pool
            return self._award_five_star(pity)

        # ----- 5★ result (no 6★ promotion) -----
        return self._award_five_star(pity)

    def select_from_pool(self, pool: list[BannerCharacter]) -> str | None:
        """Pick a random character from *pool*, or *None* if the pool is empty."""
        if not pool:
            return None
        return self._rng.choice(pool).char_id

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record_obtained(self, character_id: str, rarity: int | None) -> None:
        """Record an obtained character and update last-pulled rarity."""
        banner_id = self._banner_id
        obtained = self._save.warp_character_obtained.setdefault(banner_id, [])
        obtained.append(character_id)
        self._save.warp_last_rarity[banner_id] = rarity

    def _reset_pity(self) -> None:
        """Reset the pity counter for the current banner to 0."""
        self._save.warp_pity[self._banner_id] = 0

    def _increment_pity(self) -> None:
        """Increment the pity counter for the current banner by 1."""
        banner_id = self._banner_id
        self._save.warp_pity[banner_id] = (
            self._save.warp_pity.get(banner_id, 0) + 1
        )

    def _is_luna_eligible(self) -> bool:
        """Return *True* if a 7★ Luna pull is allowed on this banner.

        Luna is always eligible on the YOLO banner.  On elemental banners
        she is eligible only when at least one non-generic character exists
        in either the 5★ or 6★ pool.
        """
        if self._banner_id == "yolo":
            return True
        banner = self._banner
        for char in banner.five_star_pool:
            if char.damage_type_id != "generic":
                return True
        for char in banner.six_star_pool:
            if char.damage_type_id != "generic":
                return True
        return False

    def _award_five_star(self, pity_before: int) -> WarpOutcome:
        """Award a 5★ (or prismatic fallback) and reset pity.

        Shared code path for both the *no-6★* branch and the *6★-pool-empty*
        fallback branch.
        """
        char_id = self.select_from_pool(self._banner.five_star_pool)
        rarity: int | None = 5
        if char_id is None:
            char_id = PRISMATIC_FALLBACK_ID
            rarity = None
        self._reset_pity()
        self._record_obtained(char_id, rarity)
        return WarpOutcome(
            rarity=rarity,
            character_id=char_id,
            pity_before=pity_before,
            pity_after=0,
        )
