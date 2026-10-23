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


def _format_odyssey_multiplier(multiplier: float) -> str:
    if abs(multiplier - 1.0) < 0.01:
        return f"x{multiplier:.6f}"
    return f"x{multiplier:.4f}"


def _format_odyssey_tooltip(steps: int, context: dict[str, object]) -> str:
    """Format tooltip for Odyssey's Blessing."""
    runtime = context.get("runtime", {}) if isinstance(context, dict) else {}
    if not isinstance(runtime, dict):
        runtime = {}
    try:
        current_steps = max(0, int(runtime.get("steps", steps)))
    except (TypeError, ValueError):
        current_steps = max(0, int(steps))
    try:
        progress = max(0.0, min(1.0, float(runtime.get("progress", 0.0))))
    except (TypeError, ValueError):
        progress = 0.0
    multiplier = _odyssey_multiplier_formula(current_steps)
    bonus_value = _format_odyssey_multiplier(multiplier)

    return (
        "<b>Odyssey's Blessing</b><br>"
        f"EXP gain: <b>{bonus_value}</b><br>"
        f"Progress: <b>{progress * 100.0:.1f}%</b>"
    )


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
    tooltip_formatter=_format_odyssey_tooltip,
)
