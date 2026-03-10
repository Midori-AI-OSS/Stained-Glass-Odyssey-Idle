# Systems State

Date captured: 2026-03-05
Last updated: 2026-03-10

## Runtime

- Active runtime path is Home + Idle + Layout.
- Idle runtime uses a fixed **30Hz** background tick engine (`SharedTickRuntime`).
- Tick processing runs off the UI thread and publishes one `TickSnapshot` event payload per tick.
- UI thread is reserved for rendering, input, and snapshot consumption.
- Legacy `ui/legacy/` runtime/battle modules were removed.

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

## Persistence

- Runtime autosaves enqueue writes via `AsyncSaveQueue` through `RunSaveStore.persist(force=False)`.
- `persist(force=True)` flushes the queue synchronously.
- Shutdown paths call save-store flush/shutdown to drain queued writes.

## Blessing Runtime

- Persistent blessing data is stored in `RunSave.blessings`.
- Blessing progression advances deterministically from 30Hz tick deltas (`tick_elapsed_seconds`), not wall-clock timestamps.
