# Systems State

Date captured: 2026-03-05
Last updated: 2026-03-07

## Runtime

- Active runtime path is Home + Idle + Layout.
- Battle/foe systems are legacy and are not part of the active runtime flow.
- Layout is a shipped menu entry.
- Layout uses dedicated drag/drop party management and not the old shop/reroll/sell/merge/fight/reward flow.

## Save + Party Setup

- Brand-new saves bootstrap with Trinity members active:
  - `lady_darkness`
  - `lady_light`
  - `persona_light_and_dark`
- `persona_light_and_dark` is placed in a random valid lane at bootstrap.
- Existing saves are not auto-repaired by bootstrap.
- Layout ordering options are shipped as:
  - `save_order`
  - `rarity_desc`
  - `alphabetical`
  - `recent`
- `recent` ordering is a reversed display heuristic, not persisted acquisition history.
- Layout edits use debounced autosave and apply an idle cooldown before the next idle tick window.

## Blessing Runtime Gaps

- No live energy subsystem exists yet for blessing channeling.
