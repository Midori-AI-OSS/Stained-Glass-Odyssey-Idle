# Blessing Save Schema

## Overview

Blessing state now persists in the main run save. Idle blessing progression is deterministic and tick-driven from the 30Hz runtime.

## Persisted Blessing Data

Blessings are serialized under `RunSave.blessings` in `save.py`:

- `steps` (`int`): Completed blessing steps
- `unlocked` (`bool`): Blessing unlock state
- `tick_elapsed_seconds` (`float`): Fractional progress toward the next step
- Plugin-specific persisted fields from each blessing `save_schema`

## Runtime Progression Model

`IdleGameState` updates blessings every tick via `_process_blessing_ticks(delta_seconds=IDLE_TICK_INTERVAL_SECONDS)`.

- Tick cadence: fixed 30Hz (`IDLE_TICK_INTERVAL_SECONDS = 1/30`)
- Progression source: accumulated tick delta time
- No wall-clock dependency for step advancement

For each persistent blessing:

1. Skip if not unlocked
2. Add tick delta to `tick_elapsed_seconds`
3. While elapsed >= `plugin.step_seconds`, increment `steps` and subtract one step window
4. Save the new `steps` + `tick_elapsed_seconds`

## UI Derivations

The idle blessing UI reads from the same deterministic runtime state:

- `get_idle_blessing_step_count()`
- `get_idle_blessing_multiplier()`
- `get_idle_blessing_cycle_progress()`
- `get_idle_blessing_seconds_to_next_step()`

These calculations now derive from accumulated tick time instead of `time.time()` session windows.
