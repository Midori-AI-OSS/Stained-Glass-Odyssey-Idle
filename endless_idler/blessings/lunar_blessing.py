"""Lunar's Blessing - A global experience blessing.

Grants +1% exp gain AND -1% exp needed per level per week.
Progress displays per minute for visual feedback.
Diminishing returns after 50%: each additional 10% requires 2x time.
"""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin


LUNAR_STEP_SECONDS = 60.0
LUNAR_WEEK_SECONDS = 604800.0
LUNAR_WEEKS_PER_STEP = 1.0
LUNAR_DIMINISHING_THRESHOLD = 50.0
LUNAR_DIMINISHING_STEP_SIZE = 10.0


def _lunar_multiplier_formula(steps: int) -> float:
    """Calculate the multiplier for Lunar's Blessing.

    Grants +1% exp gain per week, with diminishing returns after 50%.
    Also grants -1% exp needed per level per week (handled separately).

    Args:
        steps: The number of minute steps elapsed

    Returns:
        The cumulative multiplier (1.0 + bonus percentage)
    """
    total_minutes = steps * LUNAR_STEP_SECONDS / 60.0
    total_weeks = total_minutes / (LUNAR_WEEK_SECONDS / 60.0)
    bonus_pct = _calculate_lunar_bonus(total_weeks)
    return 1.0 + (bonus_pct / 100.0)


def _calculate_lunar_bonus(weeks: float) -> float:
    """Calculate the bonus percentage with diminishing returns.

    Base: +1% per week up to 50%.
    Diminishing: After 50%, each additional 10% requires 2x time to gain 1% bonus.

    Args:
        weeks: Total weeks of progress

    Returns:
        Bonus percentage (0-100+)
    """
    if weeks <= LUNAR_DIMINISHING_THRESHOLD:
        return weeks

    base_bonus = LUNAR_DIMINISHING_THRESHOLD
    remaining_weeks = weeks - LUNAR_DIMINISHING_THRESHOLD

    current_step = 0
    weeks_needed = LUNAR_DIMINISHING_STEP_SIZE
    bonus_increment = LUNAR_DIMINISHING_STEP_SIZE

    while remaining_weeks >= weeks_needed:
        remaining_weeks -= weeks_needed
        base_bonus += bonus_increment
        current_step += 1
        weeks_needed = LUNAR_DIMINISHING_STEP_SIZE * (2**current_step)

    return base_bonus


def get_lunar_progress_per_tick(steps: int) -> dict[str, float]:
    """Get detailed progress information for Lunar's Blessing.

    Args:
        steps: The number of minute steps elapsed

    Returns:
        Dictionary with exp_gain_pct, exp_reduction_pct, progress_weeks, and display_pct
    """
    total_minutes = steps * (LUNAR_STEP_SECONDS / 60.0)
    total_weeks = total_minutes / (LUNAR_WEEK_SECONDS / 60.0)
    bonus_pct = _calculate_lunar_bonus(total_weeks)

    return {
        "exp_gain_pct": bonus_pct,
        "exp_reduction_pct": bonus_pct,
        "progress_weeks": total_weeks,
        "display_pct": bonus_pct,
    }


def _format_lunar_tooltip(steps: int, context: dict) -> str:
    """Format tooltip for Lunar's Blessing."""
    import time
    from typing import Any

    save = context.get("save")
    if save is None:
        return "<b>Lunar's Blessing</b><br>Save data unavailable"

    blessing_data = save.blessings.get("lunar_blessing", {})
    step_start_time = blessing_data.get("step_start_time", 0.0)
    current_time = time.time()

    if step_start_time <= 0.0:
        seconds_until_next = int(LUNAR_STEP_SECONDS)
    else:
        elapsed = current_time - step_start_time
        seconds_until_next = max(0, int(LUNAR_STEP_SECONDS - elapsed))

    progress_data = get_lunar_progress_per_tick(steps)
    exp_gain = progress_data["exp_gain_pct"]
    exp_reduction = progress_data["exp_reduction_pct"]
    weeks = progress_data["progress_weeks"]

    LUNAR_WEEK_MINUTES = LUNAR_WEEK_SECONDS / 60.0
    per_minute_gain = (1.0 / LUNAR_WEEK_MINUTES) * 100
    per_minute_reduction = (1.0 / LUNAR_WEEK_MINUTES) * 100

    # Format time as MM:SS
    minutes = seconds_until_next // 60
    seconds = seconds_until_next % 60
    time_str = f"{minutes:02d}:{seconds:02d}"

    return (
        "<b>Lunar's Blessing</b><br>"
        f"<b>+{exp_gain:.1f}%</b> experience gained<br>"
        f"<b>-{exp_reduction:.1f}%</b> experience needed per level<br>"
        f"+{per_minute_gain:.4f}% per minute<br>"
        f"-{per_minute_reduction:.4f}% per minute<br><br>"
        f"Progress: <b>{weeks:.2f}</b> weeks<br>"
        f"Next tick in: <b>{time_str}</b>"
    )


blessing = BlessingPlugin(
    blessing_id="lunar_blessing",
    display_name="Lunar's Blessing",
    description="Accumulates over a week to provide permanent global experience bonuses.",
    step_seconds=LUNAR_STEP_SECONDS,
    multiplier_formula=_lunar_multiplier_formula,
    max_steps=None,
    is_unlocked=False,
    unlock_condition="Reach level 100 with any character",
    is_persistent=True,
    save_schema={
        "steps": int,
        "total_minutes": int,
        "last_tick_time": float,
        "step_start_time": float,
        "unlocked": bool,
    },
    tooltip_formatter=_format_lunar_tooltip,
)
