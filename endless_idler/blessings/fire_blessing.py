"""Fire Blessing - Empowers fire characters with bonus experience.

Provides a +0.01% experience multiplier per step for fire damage type characters.
The blessing caps at 12 steps (60 minutes total), reaching a maximum of +0.12% bonus.
"""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin


FIRE_STEP_SECONDS = 300.0


def _fire_multiplier_formula(steps: int) -> float:
    """Calculate the multiplier for Fire Blessing.

    Each step adds 0.01% to the multiplier.
    Formula: 1.0 + (steps * 0.0001)

    Args:
        steps: The number of 5-minute steps elapsed

    Returns:
        The cumulative multiplier
    """
    return 1.0 + (steps * 0.0001)


blessing = BlessingPlugin(
    blessing_id="fire_blessing",
    display_name="Fire Blessing",
    description=(
        "Empowers fire characters with bonus experience while idle. "
        "The blessing grows stronger over time, reaching maximum power after 60 minutes."
    ),
    step_seconds=FIRE_STEP_SECONDS,
    multiplier_formula=_fire_multiplier_formula,
    max_steps=None,
    target_damage_type="fire",
    is_unlocked=False,
    is_persistent=True,
    save_schema={
        "steps": int,
        "unlocked": bool,
    },
)
