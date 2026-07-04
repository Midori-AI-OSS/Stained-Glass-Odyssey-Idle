# Blessing Architecture

## Overview

- Blessings provide idle EXP multipliers that grow over time
- Session-based: resets on new idle session start
- Currently only Odyssey's Blessing exists

## Plugin Architecture

- Modeled after character plugin system
- File location: `endless_idler/blessings/`
- Infrastructure files: `__init__.py`, `plugin.py`, `registry.py`, `loader.py`
- Blessing implementations: individual `.py` files (e.g., `odyssey_blessing.py`)

## BlessingPlugin Dataclass

| Field | Type | Description |
|-------|------|-------------|
| `blessing_id` | `str` | Unique identifier for the blessing |
| `display_name` | `str` | Human-readable name |
| `description` | `str` | What the blessing does |
| `step_seconds` | `float` | Interval between steps in seconds |
| `multiplier_formula` | `Callable[[int], float]` | Function that returns multiplier for step count |
| `max_steps` | `int \| None` | Optional cap on steps (None = unlimited) |

## Discovery and Registry

- Registry scans `blessings/*.py` (excluding infrastructure)
- Caches discovered blessings in dict
- `blessing` module-level variable convention
- `get_default_blessing()` returns Odyssey's Blessing

## Loader Mechanism

- Uses importlib for dynamic loading
- Validates `blessing` variable exists
- Returns `None` on load failure or invalid blessing

## Current Implementation

Odyssey's Blessing (`odyssey_blessing.py`):

| Property | Value |
|----------|-------|
| Step interval | 300 seconds (5 minutes) |
| Multiplier | 2.5% compound every 30 minutes |
| Formula | `1.025 ** (steps / 6.0)` |
| Max steps | None (unlimited growth) |

## Integration with Idle State

IdleGameState manages blessing calculation:

| Method | Purpose |
|--------|---------|
| `_idle_session_started_at` | Timestamp captured on init |
| `_idle_blessing_elapsed_seconds()` | Seconds since session start |
| `get_idle_blessing_step_count()` | Steps = elapsed // step_seconds |
| `get_idle_blessing_multiplier()` | Live multiplier calculation |
| `get_idle_blessing_cycle_progress()` | Progress within current step (0.0-1.0) |
| `get_idle_blessing_seconds_to_next_step()` | Countdown to next multiplier increase |

Multiplier is calculated live each tick, not stored. Reset occurs when new IdleGameState is initialized.
