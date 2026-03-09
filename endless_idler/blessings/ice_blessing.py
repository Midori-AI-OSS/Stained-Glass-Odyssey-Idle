"""Ice Blessing - A damage-type specific blessing for ice characters.

Provides a small multiplier bonus that grows with each 5-minute step,
capping at 12 steps (1 hour). Specializes in empowering ice damage dealers.
"""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin


ICE_STEP_SECONDS = 300.0
ICE_MAX_STEPS = 12


def _ice_multiplier_formula(steps: int) -> float:
    """Calculate the multiplier for Ice Blessing.

    Every step adds 0.01% to the multiplier.
    Formula: 1.0 + (steps * 0.0001)

    Args:
        steps: The number of 5-minute steps elapsed

    Returns:
        The cumulative multiplier
    """
    return 1.0 + (steps * 0.0001)


blessing = BlessingPlugin(
    blessing_id="ice_blessing",
    display_name="Ice Blessing",
    description=(
        "A blessing that empowers ice-wielding characters. "
        "Each step slightly increases damage output for ice-based attacks."
    ),
    step_seconds=ICE_STEP_SECONDS,
    multiplier_formula=_ice_multiplier_formula,
    max_steps=ICE_MAX_STEPS,
    target_damage_type="ice",
    is_unlocked=False,
)
