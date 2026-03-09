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


blessing = BlessingPlugin(
    blessing_id="lunar_blessing",
    display_name="Lunar's Blessing",
    description=(
        "Lunar's Blessing grants experience bonuses over time. "
        "Each week, gain +1% experience gained and -1% experience needed per level. "
        "After reaching 50%, diminishing returns apply: each additional 10% requires 2x the time."
    ),
    step_seconds=LUNAR_STEP_SECONDS,
    multiplier_formula=_lunar_multiplier_formula,
    max_steps=None,
    target_damage_type=None,
    is_unlocked=True,
    is_persistent=True,
    save_schema={
        "steps": int,
        "total_minutes": int,
        "last_tick_time": float,
        "step_start_time": float,
    },
)
