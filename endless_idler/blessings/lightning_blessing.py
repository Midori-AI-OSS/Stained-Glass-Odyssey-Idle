"""Lightning Blessing - An unlocked blessing for lightning damage dealers.

Provides a linear multiplier bonus every 5 minutes (300 seconds).
Starts locked and must be unlocked through gameplay.
Maxes out at 12 steps (1 hour) for a 0.12% bonus.
"""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin


LIGHTNING_BLESSING_STEP_SECONDS = 300.0


def _lightning_blessing_multiplier_formula(steps: int) -> float:
    """Calculate the multiplier for Lightning Blessing.

    Every step adds 0.01% to the multiplier.
    Formula: 1.0 + (steps * 0.0001)

    Args:
        steps: The number of 5-minute steps elapsed

    Returns:
        The cumulative multiplier
    """
    return 1.0 + (steps * 0.0001)


blessing = BlessingPlugin(
    blessing_id="lightning_blessing",
    display_name="Lightning Blessing",
    description=(
        "An electrifying blessing that empowers lightning damage dealers. "
        "Gains 0.01% bonus per 5-minute step, up to 12 steps."
    ),
    step_seconds=LIGHTNING_BLESSING_STEP_SECONDS,
    multiplier_formula=_lightning_blessing_multiplier_formula,
    max_steps=None,
    target_damage_type="lightning",
    is_unlocked=False,
    is_persistent=True,
    save_schema={
        "steps": int,
        "unlocked": bool,
    },
)
