from __future__ import annotations

import math

from endless_idler.blessings.lunar_blessing import LUNAR_STEP_SECONDS
from endless_idler.blessings.lunar_blessing import LUNAR_WEEK_SECONDS
from endless_idler.blessings.lunar_blessing import blessing
from endless_idler.blessings.lunar_blessing import get_lunar_progress_per_tick


def test_lunar_uses_five_minute_real_steps() -> None:
    assert math.isclose(LUNAR_STEP_SECONDS, 300.0, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(blessing.step_seconds, 300.0, rel_tol=0.0, abs_tol=1e-12)


def test_lunar_weekly_pacing_remains_equivalent() -> None:
    steps_per_week = int(LUNAR_WEEK_SECONDS // LUNAR_STEP_SECONDS)
    multiplier = blessing.get_multiplier(steps_per_week)
    progress = get_lunar_progress_per_tick(steps_per_week)

    assert math.isclose(multiplier, 1.01, rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(progress["progress_weeks"], 1.0, rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(progress["display_pct"], 1.0, rel_tol=1e-9, abs_tol=1e-9)


def test_lunar_tooltip_uses_five_minute_wording() -> None:
    tooltip = blessing.format_tooltip(0, {"save": type("S", (), {"blessings": {}})()})
    assert "Current 5-minute step" in tooltip


def test_lunar_tooltip_mentions_diminishing_when_active() -> None:
    steps_per_week = int(LUNAR_WEEK_SECONDS // LUNAR_STEP_SECONDS)
    steps_at_fifty_weeks = steps_per_week * 50
    tooltip = blessing.format_tooltip(
        steps_at_fifty_weeks,
        {"save": type("S", (), {"blessings": {"lunar_blessing": {}}})()},
    )
    assert "diminishing returns active" in tooltip
