# Standby Mechanics

## Standby Slot System

- 10 slots defined in `save.py` (`STANDBY_SLOTS = 10`)
- Stored as `standby: list[str | None]`
- Positions 0 and 9 are always None (boundaries)
- Integrated into IdleGameState via `standby_ids` parameter

## Standby EXP Gain

Formula: `0.01% of total offsite EXP` per tick

```
total_offsite_exp = offsite_count * (offsite_drip_share + offsite_baseline_bonus)
total_standby_exp = 0.0001 * total_offsite_exp
```

- Split equally among all Standby characters
- Processes every tick (100% rate)
- Applies `_recipient_exp_modifier_for_char()` for death debuffs, etc.
- NO shard progress for Standby

## Standby HP Healing

- Uses `regain` stat from `base_stats`
- Formula: `regain * 0.0005` HP per tick
- Default regain = 100.0 → 0.05 HP/tick
- Capped at `max_hp`

## Persistence

- Save: `"standby": save.standby` in payload
- Load: `standby=as_optional_str_list(data.get("standby", []))`
- Normalized on load (positions 0 and 9 forced to None)

## Related Files

- `endless_idler/ui/idle/idle_state.py` - Tick processing
- `endless_idler/ui/idle/screen.py` - State initialization
- `endless_idler/ui/layout/screen.py` - UI handling
- `endless_idler/save.py` - Persistence
