# Save system

Persistent state is stored in a single JSON save file managed by `endless_idler/save.py` (`SaveManager` / `RunSave`).

## Key fields

- `RunSave.character_progress`: Per-character level/EXP progression used by Idle mode (and debuffs applied from Battle).
- `RunSave.character_stats`: Per-character saved base stat overrides (applied when building combat/idle stats).
- `RunSave.character_deaths`: Per-character death counts used to apply death-based stat bonuses.

## Death tracking

The death bonus logic lives in `endless_idler/progression.py` (`record_character_death`).

Events that record deaths:

- Party character death during Battle: `endless_idler/ui/battle/screen.py`
- Manual run reset in the Party Builder: `endless_idler/ui/party_builder.py`
- Forced run reset after Battle (Party HP hits 0): `endless_idler/ui/battle/screen.py`

