# Blessing Plugins Developer Guide

This guide explains how to create blessing plugins for Stained Glass Odyssey Idle.

## File Location

Create your blessing file in:

```
endless_idler/blessings/your_blessing.py
```

Blessing files are automatically discovered by the registry system.

## Required Structure

Every blessing module must:

1. Import the `BlessingPlugin` class
2. Define a `blessing` variable at module level (this is the convention)
3. Assign a `BlessingPlugin` instance to that variable

```python
"""Your Blessing - Brief description."""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin


blessing = BlessingPlugin(
    blessing_id="your_blessing_id",
    display_name="Your Blessing Name",
    description="What this blessing does.",
    step_seconds=300.0,
    multiplier_formula=_your_multiplier_formula,
    max_steps=None,
)
```

## BlessingPlugin Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `blessing_id` | `str` | Unique identifier. Use snake_case. Example: `"warriors_favor"` |
| `display_name` | `str` | Human-readable name shown in UI. Example: `"Warrior's Favor"` |
| `description` | `str` | Explains what the blessing does. Keep under 100 characters. |
| `step_seconds` | `float` | Interval between steps in seconds. Common: `60.0` (1 min), `300.0` (5 min), `600.0` (10 min) |
| `multiplier_formula` | `Callable[[int], float]` | Function taking step count, returning multiplier |
| `max_steps` | `int \| None` | Optional cap on steps. `None` for uncapped. |

## Multiplier Formula Patterns

### Linear Growth

Simple additive bonus per step:

```python
def _linear_multiplier(steps: int) -> float:
    """1% per step linear growth."""
    return 1.0 + (steps * 0.01)
```

At step 10: multiplier = 1.10 (10% bonus)
At step 100: multiplier = 2.00 (100% bonus)

### Compound Growth

Multiplicative bonus that compounds over time:

```python
def _compound_multiplier(steps: int) -> float:
    """2.5% bonus every 6 steps (compound)."""
    return 1.025 ** (steps / 6.0)
```

At step 6: multiplier = 1.025
At step 12: multiplier = 1.051
At step 60: multiplier = 1.132

### Capped Growth

Use `max_steps` to prevent infinite scaling:

```python
def _capped_multiplier(steps: int) -> float:
    """5% per step, but capped in plugin config."""
    return 1.0 + (steps * 0.05)

blessing = BlessingPlugin(
    blessing_id="capped_blessing",
    display_name="Capped Blessing",
    description="Capped at 20 steps (100% max bonus).",
    step_seconds=60.0,
    multiplier_formula=_capped_multiplier,
    max_steps=20,
)
```

The `max_steps` field caps steps before calling the formula.

## Complete Example: Simple Linear Blessing

```python
"""Warrior's Favor - A simple 1% per step blessing."""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin


def _warrior_multiplier(steps: int) -> float:
    """Calculate Warrior's Favor multiplier.

    Gains 1% bonus per minute of idle time.

    Args:
        steps: Number of 60-second steps elapsed

    Returns:
        The cumulative multiplier
    """
    return 1.0 + (steps * 0.01)


blessing = BlessingPlugin(
    blessing_id="warriors_favor",
    display_name="Warrior's Favor",
    description="Gain 1% experience bonus for every minute of idle time.",
    step_seconds=60.0,
    multiplier_formula=_warrior_multiplier,
    max_steps=60,  # Cap at 60% bonus
)
```

## Testing Requirements

Create tests in `tests/blessings/test_your_blessing.py`:

```python
"""Tests for Warrior's Favor blessing."""

from __future__ import annotations

from endless_idler.blessings.warriors_favor import blessing


def test_warriors_favor_step_seconds() -> None:
    """Test step interval is 60 seconds."""
    assert blessing.step_seconds == 60.0


def test_warriors_favor_multiplier_at_step_0() -> None:
    """Test multiplier starts at 1.0."""
    assert blessing.get_multiplier(0) == 1.0


def test_warriors_favor_linear_growth() -> None:
    """Test 1% per step linear growth."""
    assert blessing.get_multiplier(10) == 1.10
    assert blessing.get_multiplier(50) == 1.50


def test_warriors_favor_max_steps_cap() -> None:
    """Test max_steps caps the multiplier."""
    # At max_steps (60), multiplier is 1.60
    assert blessing.get_multiplier(60) == 1.60
    # Beyond max_steps, should stay capped
    assert blessing.get_multiplier(100) == 1.60
```

Run tests with:

```bash
uv run pytest tests/blessings/test_your_blessing.py -v
```

## Registry Refresh for Testing

When testing the registry (discovery and loading), clear the cache between tests:

```python
from endless_idler.blessings.registry import clear_registry


def test_registry_finds_your_blessing() -> None:
    """Test that registry discovers your blessing."""
    clear_registry()
    from endless_idler.blessings.registry import get_all_blessings

    blessings = get_all_blessings()
    blessing_ids = [b.blessing_id for b in blessings]

    assert "warriors_favor" in blessing_ids
```

Always call `clear_registry()` before registry tests to ensure fresh discovery.

## Reference Implementations

- **Working example**: `endless_idler/blessings/odyssey_blessing.py`
- **Test patterns**: `tests/blessings/test_odyssey_blessing.py`
- **Plugin tests**: `tests/blessings/test_plugin.py`

## Naming Conventions

- **File name**: `snake_case.py` matching the blessing
- **blessing_id**: `snake_case` unique identifier
- **Formula function**: `_snake_case_multiplier` (private, prefixed with underscore)
- **Constants**: `UPPER_SNAKE_CASE` for step seconds and other magic numbers

## Best Practices

1. Document your multiplier formula clearly
2. Test boundary conditions (step 0, max_steps, beyond max_steps)
3. Use `math.isclose()` for floating-point comparisons in tests
4. Keep descriptions concise but informative
5. Choose step_seconds that match your design intent (shorter = more responsive, longer = more impactful)
