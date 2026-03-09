# Blessing Save Schema

## Overview

Blessings are session-only and do NOT persist across idle sessions. Unlike shards, blessing state is calculated live from session start time and is never saved to or loaded from save files. Each new idle session starts with fresh blessing progress at step 0.

## No Persistent Blessing Data

Blessing data is intentionally excluded from save files:

- No blessing fields in `save_codec.py` character progress encoding/decoding
- No blessing initialization in `save.py` `RunSave` dataclass or `reset_character_progress_for_new_run()`
- Blessing state resets completely on every idle session start

## Session State Tracking in idle_state.py

### Session Start Timestamp

- `self._idle_session_started_at` (line 122): Captures `time.time()` when `IdleGameState` initializes
- This timestamp marks the beginning of the current blessing accumulation window

### Elapsed Seconds Calculation

- `_idle_blessing_elapsed_seconds()` (lines 919-921): Returns `max(0.0, now - self._idle_session_started_at)`
- Calculates real-time seconds since session start for live blessing math

### Step Count Derivation

- `get_idle_blessing_step_count()` (lines 923-926): Derives step count from elapsed time
- Formula: `max(0, int(elapsed // blessing.step_seconds))`
- Steps are calculated on-demand, never stored

## Live Blessing Calculation

The blessing multiplier is computed live from session state:

- `get_idle_blessing_multiplier()` (lines 928-931): Returns `blessing.get_multiplier(steps)`
- Multiplier is derived from step count, which derives from elapsed time
- No stored multiplier value exists

### Cycle Progress

- `get_idle_blessing_cycle_progress()` (lines 933-937): Returns progress within current step (0.0-1.0)
- Formula: `phase / blessing.step_seconds` where `phase = elapsed % blessing.step_seconds`
- Used for UI progress indicators

### Seconds to Next Step

- `get_idle_blessing_seconds_to_next_step()` (lines 939-946): Returns ceiling of seconds remaining in current step
- Used for UI countdown displays

## Save Codec: No Blessing Fields

Confirmed: `save_codec.py` contains no blessing-related fields in:

- `as_character_progress_dict()` (lines 90-145): No blessing encoding
- `normalized_character_progress()` (lines 175-226): No blessing normalization

Only `shard_bar_ticks` is handled (lines 124-126, 207-209) for shard persistence.

## Save File: No Blessing Data

Confirmed: `save.py` contains no blessing fields in:

- `RunSave` dataclass (lines 52-81): No blessing attributes
- `SaveManager.load()` (lines 92-170): No blessing loading
- `SaveManager.save()` (lines 172-203): No blessing serialization
- `_normalized_save()` (lines 230-384): No blessing normalization
- `reset_character_progress_for_new_run()` (lines 457-499): No blessing initialization

## Reset Behavior on Idle Session Start

When `IdleGameState` initializes:

1. `self._idle_session_started_at = float(self._time())` captures current timestamp
2. Blessing step count starts from 0
3. Blessing multiplier starts from base value
4. All previous session blessing progress is discarded

This is by design: blessings reward continuous idle session time, not cumulative across sessions.

## Testing Considerations for Session-Based State

Blessing tests must account for session-only behavior:

- Tests cannot rely on save/load to persist blessing state
- Session start time must be controlled or mocked for deterministic tests
- Elapsed time calculations must account for real-time progression
- Step count and multiplier tests should verify calculation correctness, not persistence
- UI progress indicators (`get_idle_blessing_cycle_progress()`) depend on live elapsed time

## Key Implementation Files

### idle_state.py

- Line 122: Session start timestamp initialization
- Lines 919-921: `_idle_blessing_elapsed_seconds()`
- Lines 923-926: `get_idle_blessing_step_count()`
- Lines 928-931: `get_idle_blessing_multiplier()`
- Lines 933-937: `get_idle_blessing_cycle_progress()`
- Lines 939-946: `get_idle_blessing_seconds_to_next_step()`
- Line 807-808: `_calculate_idle_exp_mult()` delegates to blessing multiplier

### blessings.py (referenced)

- `get_default_blessing()` returns `BlessingPlugin` instance
- `BlessingPlugin.step_seconds`: Duration of one blessing step
- `BlessingPlugin.get_multiplier(steps)`: Computes multiplier from step count
