"""Dark Blessing - An unlocked blessing for dark damage dealers.

Provides a linear multiplier bonus every 5 minutes (300 seconds).
Starts locked and must be unlocked through gameplay.
Maxes out at 12 steps (1 hour) for a 0.12% bonus.
"""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin


DARK_BLESSING_STEP_SECONDS = 300.0


def _dark_blessing_multiplier_formula(steps: int) -> float:
    """Calculate the multiplier for Dark Blessing.

    Every step adds 0.01% to the multiplier.
    Formula: 1.0 + (steps * 0.0001)

    Args:
        steps: The number of 5-minute steps elapsed

    Returns:
        The cumulative multiplier
    """
    return 1.0 + (steps * 0.0001)


blessing = BlessingPlugin(
    blessing_id="dark_blessing",
    display_name="Dark Blessing",
    description=(
        "A shadowy blessing that empowers dark damage dealers. "
        "Gains 0.01% bonus per 5-minute step, up to 12 steps."
    ),
    step_seconds=DARK_BLESSING_STEP_SECONDS,
    multiplier_formula=_dark_blessing_multiplier_formula,
    max_steps=12,
    target_damage_type="dark",
    is_unlocked=False,
)
