# Character system

## Character plugins

Playable characters are defined as plugin modules under `endless_idler/characters/`.

The game inspects these modules using AST parsing (without importing them) to extract metadata like:

- `id`
- `name`
- `gacha_rarity`
- `damage_type`
- `placement`

Metadata extraction lives in `endless_idler/characters/metadata.py`.

## Placement (onsite vs offsite)

Each character plugin can define a `placement` value:

- `onsite`: can only be equipped in onsite party slots
- `offsite`: can only be equipped in offsite party slots
- `both`: can be equipped in either

The party builder enforces this in `endless_idler/ui/party_builder_slot.py` (`DropSlot._allows_char_id`).

Becca (`becca`), Lady Light (`lady_light`), and Echo (`lady_echo`) are currently marked as `offsite`.

## Progression

### Idle leveling

Idle mode uses `endless_idler/ui/idle/idle_state.py` (`IdleGameState`) to:

- Track per-character level/EXP progress and persist it in `RunSave.character_progress`
- Apply automatic stat growth to each character's saved base stats (`RunSave.character_stats`)

On level up, most stats are upgraded via weighted random selection, but:

- `mitigation` and `vitality` are not eligible for the level-up upgrade pool
- `mitigation` and `vitality` instead gain `+0.001` (±50%) once every 10–15 levels, per character

### Death bonuses

Each character tracks a persistent death counter in `RunSave.character_deaths`.

On a character death (in battle) or on a run reset:

- That character's death count is incremented
- That character's saved base stats are multiplied by `+0.01%` (`x1.0001`) per death
- The death bonus excludes: `passive_pot`, `vitality`, `mitigation`, and EXP-gain related keys
