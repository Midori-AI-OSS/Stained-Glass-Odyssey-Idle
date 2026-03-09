# Shard Mechanics

## Overview

The shard system awards elemental shards to characters during idle gameplay. Shards are accumulated via a progress bar that fills as characters gain EXP. When the bar completes a cycle, the character receives one shard of an eligible elemental type.

## Shard Bar Cycle

- Cycle length: 100 ticks (`SHARD_BAR_CYCLE_TICKS`)
- Roll interval: every 10 ticks (`SHARD_ROLL_INTERVAL_TICKS`)
- Roll timing: `tick_count % 10 == 0`
- One shard awarded per completed cycle

## Base Chance and Dampener

- Base chance: 0.01% (0.0001 or `1e-4` as `SHARD_BASE_CHANCE_PERCENT`)
- High-EXP dampener reduces chance as EXP/second increases

### Dampener Formula

```
bucket = floor((exp_per_second - 1000.0) / 100.0)
bucket = max(0, bucket)
denominator = 1.0 + (15000.0 * bucket)
effective_chance = base_chance / denominator
```

- Dampener activates at 1000+ EXP/second (`SHARD_DAMPENER_START_EXP_PER_SECOND`)
- Bucket size: 100 EXP/second (`SHARD_DAMPENER_BUCKET_SIZE`)
- Scale factor: 15000 (`SHARD_DAMPENER_SCALE`)
- Final chance clamped to [0, base_chance]

## Damage Type to Shard Mapping

Mapping is determined per-character via `_reward_types_for_char()`:

| Damage Type | Shard Reward Behavior |
|-------------|----------------------|
| Single element (e.g., "fire") | Awards that element's shards only |
| Dual element (e.g., "fire/ice") | Randomly picks one constituent element per award |
| Generic | Can award any of the 6 elemental types (random selection) |

- Empty tuple returned for unrecognized damage types (character not shard-eligible)

## Allowed Shard Types

Six elemental types defined in `SHARD_ALLOWED_TYPES`:

- fire
- ice
- wind
- lightning
- light
- dark

## Inventory Integration

Shard items use the pattern `{type}_shard`:

- `fire_shard`
- `ice_shard`
- `wind_shard`
- `lightning_shard`
- `light_shard`
- `dark_shard`

Mapping defined in `SHARD_ITEM_ID_BY_TYPE` dictionary.

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `SHARD_ROLL_INTERVAL_TICKS` | 10 | Ticks between shard roll attempts |
| `SHARD_BAR_CYCLE_TICKS` | 100 | Ticks to complete one shard cycle |
| `SHARD_BASE_CHANCE_PERCENT` | 0.0001 | Base 0.01% roll chance |
| `SHARD_EXP_SMOOTHING_SECONDS` | 60.0 | EMA smoothing window for EXP/sec |
| `SHARD_DAMPENER_START_EXP_PER_SECOND` | 1000.0 | EXP/sec threshold for dampener |
| `SHARD_DAMPENER_BUCKET_SIZE` | 100.0 | Bucket size for dampener calculation |
| `SHARD_DAMPENER_SCALE` | 15000.0 | Scale factor for dampener denominator |
| `IDLE_TICK_INTERVAL_SECONDS` | 0.1 | Duration of one tick |

## EXP/Second Tracking

- Uses exponential moving average (EMA) with alpha: `1.0 - exp(-0.1 / 60.0)` ≈ 0.00166
- Smooths awarded EXP per second to stabilize dampener calculations
- Stored per-character in `shard_exp_s_ema`

## Roll Flow

1. Every 10 ticks, eligible characters with positive EXP gain roll for shard progress
2. Roll succeeds if `random() < (effective_chance / 100.0)`
3. On success: increment `shard_bar_ticks`
4. When `shard_bar_ticks >= 100`: award one shard, wrap ticks to 0, repeat
