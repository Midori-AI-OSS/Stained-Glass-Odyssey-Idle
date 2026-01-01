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
