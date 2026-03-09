"""Odyssey's Blessing - The default idle blessing.

Provides a 2.5% multiplier bonus every 30 minutes (6 steps of 5 minutes each).
The blessing compounds over time, encouraging longer idle sessions.
"""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin


ODYSSEY_STEP_SECONDS = 300.0


def _odyssey_multiplier_formula(steps: int) -> float:
    """Calculate the multiplier for Odyssey's Blessing.

    Every 6 steps (30 minutes), the multiplier increases by 2.5%.
    Formula: 1.025 ** (steps / 6.0)

    Args:
        steps: The number of 5-minute steps elapsed

    Returns:
        The cumulative multiplier
    """
    return 1.025 ** (steps / 6.0)


blessing = BlessingPlugin(
    blessing_id="odyssey_blessing",
    display_name="Odyssey's Blessing",
    description=(
        "The idle experience multiplier that grows over time. "
        "Every 30 minutes, gain a 2.5% bonus to all experience earned."
    ),
    step_seconds=ODYSSEY_STEP_SECONDS,
    multiplier_formula=_odyssey_multiplier_formula,
    max_steps=None,
    is_persistent=False,
    save_schema={},
)
