"""Tests for Odyssey's Blessing to ensure it matches the original behavior."""

from __future__ import annotations

import math

from endless_idler.blessings import get_default_blessing
from endless_idler.blessings.odyssey_blessing import ODYSSEY_STEP_SECONDS
from endless_idler.blessings.odyssey_blessing import _odyssey_multiplier_formula
from endless_idler.blessings.odyssey_blessing import blessing as odyssey_blessing
from endless_idler.blessings.registry import clear_registry


# Constants from the original implementation for comparison
ORIGINAL_STEP_SECONDS = 300.0
ORIGINAL_STEP_MULTIPLIER = 1.025 ** (1.0 / 6.0)


def test_odyssey_step_seconds_matches_original() -> None:
    """Test that the step seconds match the original constant."""
    assert ODYSSEY_STEP_SECONDS == ORIGINAL_STEP_SECONDS


def test_odyssey_multiplier_formula_matches_original() -> None:
    """Test that the multiplier formula produces the same results as the original."""
    # The original formula: IDLE_BLESSING_STEP_MULTIPLIER ** steps
    # where IDLE_BLESSING_STEP_MULTIPLIER = 1.025 ** (1.0 / 6.0)
    # This is equivalent to: (1.025 ** (1.0 / 6.0)) ** steps
    # Which equals: 1.025 ** (steps / 6.0)

    test_steps = [0, 1, 6, 12, 30, 60, 100]

    for steps in test_steps:
        original_result = ORIGINAL_STEP_MULTIPLIER**steps
        new_result = _odyssey_multiplier_formula(steps)
        assert math.isclose(
            new_result, original_result, rel_tol=1e-12, abs_tol=1e-12
        ), f"Mismatch at step {steps}: {new_result} != {original_result}"


def test_odyssey_at_step_6_is_exactly_1_025() -> None:
    """Test that at step 6, the multiplier is exactly 1.025."""
    result = _odyssey_multiplier_formula(6)
    assert math.isclose(result, 1.025, rel_tol=1e-12, abs_tol=1e-12)


def test_odyssey_at_step_0_is_exactly_1_0() -> None:
    """Test that at step 0, the multiplier is exactly 1.0."""
    result = _odyssey_multiplier_formula(0)
    assert math.isclose(result, 1.0, rel_tol=1e-12, abs_tol=1e-12)


def test_odyssey_compounds_correctly() -> None:
    """Test that the multiplier compounds correctly over multiple steps."""
    # After 6 steps: 1.025x
    assert math.isclose(_odyssey_multiplier_formula(6), 1.025, rel_tol=1e-9)

    # After 12 steps: 1.025^2
    assert math.isclose(_odyssey_multiplier_formula(12), 1.025**2, rel_tol=1e-9)

    # After 30 steps (1 hour): 1.025^5
    assert math.isclose(_odyssey_multiplier_formula(30), 1.025**5, rel_tol=1e-9)

    # After 60 steps (2 hours): 1.025^10
    assert math.isclose(_odyssey_multiplier_formula(60), 1.025**10, rel_tol=1e-9)


def test_get_default_blessing_is_odyssey() -> None:
    """Test that get_default_blessing returns Odyssey's Blessing."""
    clear_registry()
    blessing = get_default_blessing()

    assert blessing.blessing_id == "odyssey_blessing"
    assert blessing.display_name == "Odyssey's Blessing"
    assert blessing.step_seconds == ORIGINAL_STEP_SECONDS
    assert blessing.max_steps is None


def test_odyssey_get_multiplier_matches_formula() -> None:
    """Test that the plugin's get_multiplier method matches the formula function."""
    clear_registry()
    blessing = get_default_blessing()

    test_steps = [0, 1, 6, 12, 30, 60, 100]

    for steps in test_steps:
        expected = _odyssey_multiplier_formula(steps)
        actual = blessing.get_multiplier(steps)
        assert math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12), (
            f"Mismatch at step {steps}: {actual} != {expected}"
        )


def test_odyssey_step_count_calculation() -> None:
    """Test step count calculation matches original behavior."""
    # Simulate various elapsed times and verify step counts
    test_cases = [
        (0.0, 0),
        (299.9, 0),
        (300.0, 1),
        (600.0, 2),
        (1500.0, 5),
        (1800.0, 6),  # 30 minutes = 6 steps
        (3600.0, 12),  # 60 minutes = 12 steps
    ]

    for elapsed_seconds, expected_steps in test_cases:
        actual_steps = int(elapsed_seconds // ODYSSEY_STEP_SECONDS)
        assert actual_steps == expected_steps, (
            f"For {elapsed_seconds}s: expected {expected_steps} steps, "
            f"got {actual_steps}"
        )


def test_odyssey_cycle_progress() -> None:
    """Test cycle progress calculation."""
    # At start, progress should be 0
    assert _calculate_progress(0.0) == 0.0

    # At exactly step_seconds, progress wraps to 0
    assert _calculate_progress(ODYSSEY_STEP_SECONDS) == 0.0

    # At half step, progress is 0.5
    assert _calculate_progress(ODYSSEY_STEP_SECONDS / 2) == 0.5

    # At 3/4 step, progress is 0.75
    assert _calculate_progress(ODYSSEY_STEP_SECONDS * 0.75) == 0.75


def _calculate_progress(elapsed: float) -> float:
    """Helper to calculate cycle progress."""
    phase = elapsed % ODYSSEY_STEP_SECONDS
    return max(0.0, min(1.0, phase / ODYSSEY_STEP_SECONDS))


def test_odyssey_seconds_to_next_step() -> None:
    """Test seconds to next step calculation."""
    import math

    # At start, should be full step_seconds
    assert _seconds_to_next(0.0) == int(ODYSSEY_STEP_SECONDS)

    # At half step, should be half step_seconds
    half_step = ODYSSEY_STEP_SECONDS / 2
    assert _seconds_to_next(half_step) == int(math.ceil(half_step))

    # Just before step completes
    just_before = ODYSSEY_STEP_SECONDS - 0.1
    assert _seconds_to_next(just_before) == 1


def _seconds_to_next(elapsed: float) -> int:
    """Helper to calculate seconds to next step."""
    import math

    phase = elapsed % ODYSSEY_STEP_SECONDS
    remaining = ODYSSEY_STEP_SECONDS - phase
    if remaining <= 1e-9:
        remaining = ODYSSEY_STEP_SECONDS
    return max(0, int(math.ceil(remaining)))


def test_odyssey_tooltip_short_contract() -> None:
    tooltip = odyssey_blessing.format_tooltip(
        3,
        {
            "runtime": {
                "steps": 3,
                "progress": 0.5,
                "countdown_seconds": 120,
            }
        },
    )
    assert "EXP gain:" in tooltip
    assert "Progress:" in tooltip
    assert "Step:" not in tooltip
    assert "Countdown:" not in tooltip
    assert "every 5 minutes" not in tooltip
