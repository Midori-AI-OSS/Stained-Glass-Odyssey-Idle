"""Light Blessing - A focused damage blessing for light-element characters.

Provides a 0.01% multiplier bonus every 5 minutes, capping at 12 steps (1 hour).
This blessing specifically boosts light-type damage output.
"""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin


LIGHT_STEP_SECONDS = 300.0


def _light_multiplier_formula(steps: int) -> float:
    """Calculate the multiplier for Light Blessing.

    Every step (5 minutes), the multiplier increases by 0.01%.
    Formula: 1.0 + (steps * 0.0001)

    Args:
        steps: The number of 5-minute steps elapsed

    Returns:
        The cumulative multiplier
    """
    return 1.0 + (steps * 0.0001)


blessing = BlessingPlugin(
    blessing_id="light_blessing",
    display_name="Light Blessing",
    description=(
        "A focused blessing that enhances light elemental damage. "
        "Gain 0.01% bonus to light damage every 5 minutes, up to 1 hour."
    ),
    step_seconds=LIGHT_STEP_SECONDS,
    multiplier_formula=_light_multiplier_formula,
    max_steps=None,
    target_damage_type="light",
    is_unlocked=False,
    is_persistent=True,
    save_schema={
        "steps": int,
        "unlocked": bool,
        "step_start_time": float,
    },
)
