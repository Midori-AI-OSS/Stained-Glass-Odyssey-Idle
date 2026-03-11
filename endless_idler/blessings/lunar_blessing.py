"""Lunar's Blessing - A global experience blessing.

Grants +1% exp gain AND -1% exp needed per level per week.
Progress accrues in tick-authoritative 1-minute micro-steps.
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
        steps: The number of 1-minute steps elapsed

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
        steps: The number of 1-minute steps elapsed

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


def _next_step_bonus_delta_pct(steps: int) -> float:
    current = get_lunar_progress_per_tick(steps)
    next_step = get_lunar_progress_per_tick(max(0, steps) + 1)
    return max(0.0, float(next_step["display_pct"]) - float(current["display_pct"]))


def _format_lunar_bonus_value(percent_delta: float) -> str:
    multiplier = 1.0 + (percent_delta / 100.0)
    return f"x{multiplier:.6f}"


def _format_lunar_tooltip(steps: int, context: dict[str, object]) -> str:
    """Format tooltip for Lunar's Blessing."""
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
    progress_data = get_lunar_progress_per_tick(current_steps)
    exp_gain = progress_data["exp_gain_pct"]
    exp_reduction = progress_data["exp_reduction_pct"]
    gain_value = _format_lunar_bonus_value(exp_gain)
    reduction_value = _format_lunar_bonus_value(-exp_reduction)

    return (
        "<b>Lunar's Blessing</b><br>"
        f"EXP gain: <b>{gain_value}</b><br>"
        f"EXP per level: <b>{reduction_value}</b><br>"
        f"Progress: <b>{progress * 100.0:.1f}%</b>"
    )


blessing = BlessingPlugin(
    blessing_id="lunar_blessing",
    display_name="Lunar's Blessing",
    description=(
        "Accumulates in 1-minute runtime steps to provide permanent global "
        "experience bonuses over long idle sessions."
    ),
    step_seconds=LUNAR_STEP_SECONDS,
    multiplier_formula=_lunar_multiplier_formula,
    max_steps=None,
    is_unlocked=True,
    unlock_condition="Reach level 100 with any character",
    is_persistent=True,
    save_schema={
        "steps": int,
        "unlocked": bool,
    },
    tooltip_formatter=_format_lunar_tooltip,
)
