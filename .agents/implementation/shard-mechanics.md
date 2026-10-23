# Shard Mechanics

## Overview

The shard system awards elemental shards during idle gameplay. Progress is advanced by tick-driven rolls and wraps on cycle completion.

## Tick Contract

- Runtime tick rate: **30Hz** (`IDLE_TICK_INTERVAL_SECONDS = 1/30`)
- Roll interval: every **30 ticks** (`SHARD_ROLL_INTERVAL_TICKS`) ≈ 1 second
- Cycle length: **300 shard progress steps** (`SHARD_BAR_CYCLE_TICKS`)

## Base Chance and Dampener

- Base chance: 0.01% (`SHARD_BASE_CHANCE_PERCENT = 0.0001`)
- Dampener starts at 1000 EXP/sec
- Bucket size: 100 EXP/sec
- Scale: 15000

Formula:

```
bucket = floor((exp_per_second - 1000.0) / 100.0)
bucket = max(0, bucket)
denominator = 1.0 + (15000.0 * bucket)
effective_chance = base_chance / denominator
```

## EMA Tracking

- EXP/sec smoothing window: 60 seconds
- Alpha: `1.0 - exp(-(1/30) / 60.0)`
- Stored per character in `shard_exp_s_ema`

## Reward Types

Allowed shard types:

- fire
- ice
- wind
- lightning
- light
- dark

Item IDs map as `{type}_shard`.

## Roll Flow

1. Every 30 ticks, eligible characters with positive EXP gain roll.
2. Success when `random() < (effective_chance / 100.0)`.
3. On success, increment `shard_bar_ticks` by one shard progress step.
4. When `shard_bar_ticks >= 300`, award one shard and wrap.
