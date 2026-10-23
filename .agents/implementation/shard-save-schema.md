# Shard Save Schema

## Overview

Shard save/load persists character shard progress bar state across sessions. The `shard_bar_ticks` field tracks progress toward a completed shard cycle (0-299 runtime range).

## Field Definition

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `shard_bar_ticks` | int | 0-299 | Current progress toward next shard award. Wraps to 0 on cycle completion. |

- Stored per-character in progress dictionaries
- Wraps using modulo: `shard_bar_ticks % SHARD_BAR_CYCLE_TICKS`
- Default/init value: `0`

## Implementation Files

### save_codec.py

Codec methods for shard field encoding/decoding:

- `as_character_progress_dict()` (line 124): Extracts `shard_bar_ticks` from raw progress, clamps to `max(0, shard_bar_ticks)`
- `normalized_character_progress()` (line 207): Reads `shard_bar_ticks` from save data, defaults to 0

### save.py

Initialization (line 497): Sets `"shard_bar_ticks": 0` as default for new characters.

### idle_state.py

State management for idle/offsite characters:
- Lines 168, 221-223, 268: Handles `shard_bar_ticks` in idle state initialization
- Lines 1126-1128, 1150: Manages shard progress for expedition/offsite characters
- Lines 1078-1152: `export_progress()` handles character export

## Export Format

```json
{
  "character_id": {
    "shard_bar_ticks": 67
  }
}
```

## Test Coverage

- **tests/test_shard_bars.py**: Core shard bar save/load tests
  - Line 37, 55, 73: Tests progress initialization with `shard_bar_ticks`
  - Line 47, 84: Verifies default value of 0
  - Lines 89-104: Tests export progress and character progress dict handling
