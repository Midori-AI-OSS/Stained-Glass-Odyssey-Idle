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


def _format_odyssey_tooltip(steps: int, context: dict) -> str:
    """Format tooltip for Odyssey's Blessing."""
    import time

    session_start = context.get("session_start_time")
    if session_start is None:
        return "<b>Odyssey's Blessing</b><br>Session data unavailable"

    elapsed = time.time() - session_start
    current_steps = int(elapsed // ODYSSEY_STEP_SECONDS)
    multiplier = _odyssey_multiplier_formula(current_steps)
    phase = elapsed % ODYSSEY_STEP_SECONDS
    seconds_to_next = int(ODYSSEY_STEP_SECONDS - phase)

    # Format seconds as MM:SS
    minutes = seconds_to_next // 60
    seconds = seconds_to_next % 60
    time_str = f"{minutes:02d}:{seconds:02d}"

    return (
        "<b>Odyssey's Blessing</b><br>"
        "Grows stronger the longer you play<br><br>"
        f"Current: <b>x{multiplier:.4f}</b><br>"
        f"Next blessing in: <b>{time_str}</b><br><br>"
        f"+{(1.025 ** (1.0 / 6.0) - 1.0) * 100.0:.3f}% every 5 minutes."
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
