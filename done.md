# Completed Work

## Pass 1: Rename + Canon Cleanup

Status: complete.

### Completed

- Renamed `endless_idler/characters/lady_of_fire.py` to `endless_idler/characters/lady_fire.py`.
- Renamed the canonical runtime id from `lady_of_fire` to `lady_fire`.
- Renamed Lady Fire's passive id from `lady_of_fire_infernal_momentum` to `lady_fire_infernal_momentum`.
- Renamed the asset directory from `endless_idler/assets/characters/lady_of_fire/` to `endless_idler/assets/characters/lady_fire/`.
- Renamed the portrait file to `endless_idler/assets/characters/lady_fire/lady_fire.png`.
- Updated `endless_idler/characters/persona_ice.py` so it only asserts that Lady Fire is Persona Ice's sister.
- Removed all live Python runtime references to `lady_of_fire`.

### Notes

- No compatibility shim was added for `lady_of_fire`.
- No save migration was added for `lady_of_fire`.
- Because startup save sanitization prunes unknown character ids, old saves that still contain `lady_of_fire` will be stripped on load and then persisted in canonical form.

### Verification

- Discovery and asset lookup:
  - `uv run python -c "from endless_idler.characters import discover_character_plugins; plugins = {plugin.char_id: plugin for plugin in discover_character_plugins()}; plugin = plugins['lady_fire']; print(plugin.char_id); print([str(path) for path in plugin.image_paths()])"`
- Lint:
  - `uv run ruff check endless_idler/characters/lady_fire.py endless_idler/characters/persona_ice.py`
- Targeted tests:
  - `uv run pytest -q tests/test_idle_bootstrap.py tests/inventory/test_save.py tests/test_save_layout_fields.py tests/ui/test_main_menu_idle_runtime.py`

Results:

- discovery resolved `lady_fire`
- asset lookup resolved `endless_idler/assets/characters/lady_fire/lady_fire.png`
- lint passed
- targeted pytest batch passed: `15 passed`

## Pass 2: General Passive Framework

Status: complete.

### Completed

- Replaced the public `endless_idler.passives` package API with a plugin-oriented surface.
- Added `endless_idler/passives/plugin.py` with the new `PassivePlugin` dataclass.
- Added `endless_idler/passives/loader.py` for module-level `passive` loading.
- Replaced `endless_idler/passives/registry.py` with package-root discovery, cached lookup, and duplicate-id protection.
- Kept `CharacterPlugin.passives` unchanged as the ownership and reference boundary.
- Left `base.py`, `triggers.py`, and `execution.py` in-tree as legacy combat helpers, but removed them from the public package API.
- Added root-level passive plugin modules for every passive id currently referenced by discovered character metadata.

### Notes

- Package-root discovery excludes framework and legacy helper modules explicitly.
- Pass 2 does not add save persistence, idle runtime integration, or Trinity logic yet.
- The new passive modules currently provide metadata-only plugin definitions so later passes can attach canonical schema and runtime behavior without redesigning discovery.

### Verification

- Passive package discovery:
  - `uv run python -c "from endless_idler.passives import PassivePlugin, discover_passive_plugins, get_passive_by_id; plugins = discover_passive_plugins(); print(PassivePlugin.__name__); print(len(plugins)); print(plugins[0].passive_id if plugins else 'none'); print(get_passive_by_id('lady_fire_infernal_momentum').passive_id)"`
- Character/passive alignment:
  - `uv run python -c "from endless_idler.characters import discover_character_plugins; from endless_idler.passives import get_passive_by_id; missing = sorted({passive_id for plugin in discover_character_plugins() for passive_id in plugin.passives if get_passive_by_id(passive_id) is None}); print(missing)"`
- Lint:
  - `uv run ruff check endless_idler/passives`

Results:

- passive package imported cleanly
- passive discovery returned 20 plugins
- all discovered character passive ids resolved through the new registry
- lint passed

## Pass 3: Passive Persistence + Schema

Status: complete.

### Completed

- Added canonical top-level `RunSave.passives` storage in `endless_idler/save.py`.
- Added `_get_default_passives()` so new saves seed every discovered passive id with canonical defaults.
- Added strict blessing-style passive validation and normalization in `endless_idler/save_codec.py`.
- Wired passive payload loading through `as_passives_dict()` and canonical save rewrite through `normalized_passives()`.
- Added canonical passive payload serialization to `SaveManager.save()`.
- Added strict save-schema tests for passive round-trip, missing ids, unknown ids, and extra fields.
- Added `RunSaveStore` crash-backup coverage for invalid passive payload recovery.
- Updated two stale save-schema assertions so the targeted suite reflects current repo save behavior.

### Notes

- `RunSave.passives` now includes all currently discovered passive ids.
- Because all current passive plugins still have empty `save_schema`, their canonical payloads are currently empty dicts.
- Pass 3 does not add runtime passive execution, runtime snapshot export, or Trinity-specific passive state yet.
- `list[int]` codec support was not added because no concrete passive schema required it in this pass.

### Verification

- Lint:
  - `uv run ruff check endless_idler/save.py endless_idler/save_codec.py tests/test_save_schema_cleanup.py tests/test_run_save_store.py`
- Targeted tests:
  - `uv run pytest -q tests/test_save_schema_cleanup.py tests/test_run_save_store.py`

Results:

- lint passed
- targeted save/recovery pytest batch passed: `19 passed`

## Pass 4: Idle Runtime Passive Integration

Status: complete.

### Completed

- Expanded `PassivePlugin` with a minimal runtime hook shape for future passive behavior.
- Added `endless_idler/passives/runtime.py` for active passive resolution, runtime state initialization, ticking, and export.
- Threaded `passives_data` into `IdleGameState` and made it the runtime owner of passive canonical state plus active transient runtime state.
- Added canonical passive export and active-only `passive_runtime` export to idle runtime snapshots.
- Threaded canonical passive save data through `MainMenuWindow` and `IdleScreenWidget` idle snapshot save-sync paths.
- Kept transient `passive_runtime` out of `RunSave` writes.
- Added targeted idle runtime and UI tests for the new passive snapshot/save-sync contract.

### Notes

- Canonical snapshot `passives` preserves the full `RunSave.passives` map shape.
- Transient snapshot `passive_runtime` only includes active passive ids resolved from the current lineup.
- Current passive plugins still have no gameplay behavior, so Pass 4 runtime ticking is structurally live but behaviorally no-op.
- Trinity-specific runtime behavior remains deferred to Pass 5.

### Verification

- Lint:
  - `uv run ruff check endless_idler/passives endless_idler/ui/idle/idle_state.py endless_idler/ui/main_menu.py endless_idler/ui/idle/screen.py tests/test_idle_passives.py tests/ui/test_main_menu_idle_runtime.py tests/ui/test_idle_layout_cooldown.py`
- Targeted tests:
  - `uv run pytest -q tests/test_idle_passives.py tests/ui/test_main_menu_idle_runtime.py tests/ui/test_idle_layout_cooldown.py tests/test_idle_blessing.py`

Results:

- lint passed
- targeted idle runtime pytest batch passed: `30 passed`
