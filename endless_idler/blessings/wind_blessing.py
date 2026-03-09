"""Wind Blessing - An elemental blessing for wind damage.

Provides a small incremental bonus to wind damage every 5 minutes,
capped at 12 steps (1 hour) for a maximum of 0.12% bonus.
"""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin


WIND_STEP_SECONDS = 300.0


def _wind_multiplier_formula(steps: int) -> float:
    """Calculate the multiplier for Wind Blessing.

    Each step adds 0.01% to the multiplier.
    Formula: 1.0 + (steps * 0.0001)

    Args:
        steps: The number of 5-minute steps elapsed

    Returns:
        The cumulative multiplier
    """
    return 1.0 + (steps * 0.0001)


blessing = BlessingPlugin(
    blessing_id="wind_blessing",
    display_name="Wind Blessing",
    description=(
        "An elemental blessing that enhances wind damage. "
        "Each 5-minute step grants a 0.01% bonus, up to 12 steps."
    ),
    step_seconds=WIND_STEP_SECONDS,
    multiplier_formula=_wind_multiplier_formula,
    max_steps=12,
    target_damage_type="wind",
    is_unlocked=False,
)
