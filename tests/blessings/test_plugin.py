"""Tests for BlessingPlugin dataclass."""

from __future__ import annotations

import math

import pytest

from endless_idler.blessings.plugin import BlessingPlugin


def test_blessing_plugin_creation() -> None:
    """Test creating a basic BlessingPlugin."""
    blessing = BlessingPlugin(
        blessing_id="test_blessing",
        display_name="Test Blessing",
        description="A test blessing for testing purposes.",
        step_seconds=60.0,
        multiplier_formula=lambda steps: 1.0 + (steps * 0.01),
        max_steps=None,
    )

    assert blessing.blessing_id == "test_blessing"
    assert blessing.display_name == "Test Blessing"
    assert blessing.description == "A test blessing for testing purposes."
    assert blessing.step_seconds == 60.0
    assert blessing.max_steps is None


def test_blessing_plugin_get_multiplier() -> None:
    """Test the get_multiplier method."""
    blessing = BlessingPlugin(
        blessing_id="linear_blessing",
        display_name="Linear Blessing",
        description="Linear 1% per step",
        step_seconds=60.0,
        multiplier_formula=lambda steps: 1.0 + (steps * 0.01),
        max_steps=None,
    )

    assert blessing.get_multiplier(0) == 1.0
    assert blessing.get_multiplier(10) == 1.1
    assert blessing.get_multiplier(50) == 1.5
    assert blessing.get_multiplier(100) == 2.0


def test_blessing_plugin_with_max_steps() -> None:
    """Test that max_steps caps the multiplier."""
    blessing = BlessingPlugin(
        blessing_id="capped_blessing",
        display_name="Capped Blessing",
        description="Capped at 10 steps",
        step_seconds=60.0,
        multiplier_formula=lambda steps: 1.0 + (steps * 0.1),
        max_steps=10,
    )

    assert blessing.get_multiplier(0) == 1.0
    assert blessing.get_multiplier(5) == 1.5
    assert blessing.get_multiplier(10) == 2.0
    # Should be capped at max_steps
    assert blessing.get_multiplier(20) == 2.0
    assert blessing.get_multiplier(100) == 2.0


def test_blessing_plugin_compound_formula() -> None:
    """Test a compound multiplier formula like the Odyssey blessing."""
    blessing = BlessingPlugin(
        blessing_id="compound_blessing",
        display_name="Compound Blessing",
        description="Compounds every 6 steps",
        step_seconds=300.0,
        multiplier_formula=lambda steps: 1.025 ** (steps / 6.0),
        max_steps=None,
    )

    # At step 0, multiplier should be 1.0
    assert math.isclose(blessing.get_multiplier(0), 1.0, rel_tol=1e-12)

    # At step 6, multiplier should be exactly 1.025
    assert math.isclose(blessing.get_multiplier(6), 1.025, rel_tol=1e-9)

    # At step 12, multiplier should be 1.025^2
    assert math.isclose(blessing.get_multiplier(12), 1.025**2, rel_tol=1e-9)


def test_blessing_plugin_immutable() -> None:
    """Test that BlessingPlugin is frozen/immutable."""
    blessing = BlessingPlugin(
        blessing_id="immutable_test",
        display_name="Immutable Test",
        description="Testing immutability",
        step_seconds=60.0,
        multiplier_formula=lambda steps: 1.0,
    )

    with pytest.raises(AttributeError):
        blessing.blessing_id = "new_id"

    with pytest.raises(AttributeError):
        blessing.step_seconds = 120.0
