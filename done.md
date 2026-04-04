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

## Pass 5: Trinity Passive Implementations

Status: complete.

### Completed

- Extended passive save-schema support so passives can persist homogeneous `list[int]` fields in canonical save data.
- Updated passive default seeding so new passive schema fields can seed `list[int]` defaults alongside scalar `int`, `float`, and `bool` fields.
- Relaxed passive load handling so older canonical passive payloads seed newly discovered passive ids with defaults instead of failing on missing ids, while still rejecting unknown passive ids and extra/non-canonical fields.
- Added `tick_order` to `PassivePlugin` and updated passive runtime ticking to include passives with non-default saved state even when they are no longer currently active.
- Added `endless_idler/passives/_trinity.py` as the shared Trinity coordination helper.
- Added the concrete root-level passive plugin modules:
  - `endless_idler/passives/trinity_synergy.py`
  - `endless_idler/passives/lady_light_radiant_aegis.py`
  - `endless_idler/passives/lady_darkness_eclipsing_veil.py`
- Wired character passive ownership through discovered character metadata:
  - `lady_darkness` -> `lady_darkness_eclipsing_veil`
  - `lady_light` -> `lady_light_radiant_aegis`
  - `persona_light_and_dark` -> `trinity_synergy`
- Extended `IdleGameState` with the minimum Trinity-facing runtime hooks:
  - deployed-members lookup for `onsite` + `offsite` only
  - passive canonical-state accessor by passive id
  - passive runtime-state accessor by passive id
  - additive passive EXP-multiplier bonus accumulation per character
  - effective EXP-multiplier lookup that includes passive bonuses
  - runtime stat reconstruction for passive-side damage calculations
  - deterministic passive HP-loss helper with HP-floor skip + clamp logic
- Made Trinity deployed-only instead of merely lineup-presence-based, so placing any Trinity member into standby breaks the effect immediately.
- Implemented `trinity_synergy` as the canonical owner of the shared Trinity pool using persisted TTL state:
  - `stack_ttls`
  - `stack_progress_ticks`
- Implemented the main Trinity stack engine:
  - gain 1 stack every 30 ticks
  - each stack expires independently after 450 ticks
  - immediate reset when the trio is incomplete
  - restart from zero when the trio reforms
- Implemented `lady_darkness_eclipsing_veil` as the canonical owner of the separate Darkness-side bleed pool using persisted TTL state:
  - `bleed_stack_ttls`
  - `bleed_progress_ticks`
- Implemented the Darkness bleed-side stack engine with the same 30-tick gain cadence and 450-tick independent expiry model.
- Implemented Trinity soft-cap behavior with the harder log-style diminishing returns shape after the 50% threshold.
- Implemented Trinity mitigation state at `0.01%` per stack, with cadence unchanged by the soft cap and value scaling driven by passive-side calculations.
- Implemented Lady Light's transfer behavior using the locked EXP-multiplier source rather than live EXP/tick:
  - 50% of Lady Darkness effective `exp_multiplier`
  - 50% of Persona Light and Dark effective `exp_multiplier`
  - baseline `1.0x` source values are included
  - each Trinity stack adds `+0.05%` transfer strength
  - Lady Light scaling uses the existing runtime `passive_modifier`
- Implemented Lady Darkness bleed behavior using the locked target-stat formula and floor behavior:
  - raw bleed starts from percent max HP per active Darkness bleed stack
  - actual damage uses `raw / ((defense / 5) * mitigation)`
  - target HP floor is 30%
  - floor handling uses skip + clamp rather than post-hit correction
- Implemented Lady Darkness EXP conversion as a current-tick-only EXP-multiplier bonus based on actual post-mitigation HP loss:
  - `+5% EXP gain per 1% HP lost`
  - conversion uses actual applied HP loss, not stack count alone
  - conversion scales with the existing runtime `passive_modifier`
- Added targeted save, runtime, and UI coverage for the new passive schema, new Trinity save state, deployed-only gating, stack cadence, persistence, and runtime save-sync expectations.

### Notes

- No `SAVE_VERSION` bump was added in this pass.
- Canonical passive compatibility for newly added passives is handled by seeding missing discovered passive ids with defaults during passive load/normalization.
- Trinity stack persistence uses remaining TTL lists rather than absolute expiry tick stamps, so independent expiry survives save/load without relying on a persisted global tick counter.
- `trinity_synergy` owns the shared canonical Trinity pool, while `lady_darkness_eclipsing_veil` owns the separate Darkness bleed pool canonically under its own passive id.
- `lady_light_radiant_aegis` is intentionally runtime-only from a canonical-state perspective; it derives its behavior from live Trinity state and current effective source multipliers.
- Passive gameplay scaling in this pass uses the existing runtime `passive_modifier` only.
- `resolve_active_passive_ids()` still includes standby members in the runtime passive set, but Trinity's own deployed-only check now clears or disables Trinity behavior immediately whenever a member is not in `onsite` or `offsite`.
- `get_exp_gain_per_tick()` now performs a zero-delta passive refresh before calculating previewed idle gain so Trinity-derived EXP changes reflect the current tick's passive state without double-advancing timers.
- Broader `uv run basedpyright` still reports the pre-existing unresolved-import/type-check baseline in copied character modules and related legacy files; Pass 5 did not attempt to resolve that unrelated baseline.
- Broader `tests/test_shard_bars.py` still fails against the pre-existing 300-tick shard-bar behavior; the underlying shard-bar code in `idle_state.py` is unchanged from `HEAD~1`.

### Verification

- Lint:
  - `uv run ruff check endless_idler/passives endless_idler/save.py endless_idler/save_codec.py endless_idler/ui/idle/idle_state.py endless_idler/characters/lady_darkness.py endless_idler/characters/lady_light.py endless_idler/characters/persona_light_and_dark.py tests/test_save_schema_cleanup.py tests/test_run_save_store.py tests/test_idle_passives.py tests/ui/test_main_menu_idle_runtime.py tests/ui/test_idle_layout_cooldown.py`
- Targeted tests:
  - `uv run pytest -q tests/test_save_schema_cleanup.py tests/test_run_save_store.py tests/test_idle_passives.py tests/ui/test_main_menu_idle_runtime.py tests/ui/test_idle_layout_cooldown.py`
- Adjacent idle regression check:
  - `uv run pytest -q tests/test_idle_blessing.py`
- Broader type-check baseline check:
  - `uv run basedpyright`
- Broader unrelated idle baseline check:
  - `uv run pytest -q tests/test_idle_blessing.py tests/test_shard_bars.py`
- Historical shard-bar sanity check:
  - `git show HEAD~1:endless_idler/ui/idle/idle_state.py | rg -n "SHARD_BAR_CYCLE_TICKS|while ticks >= SHARD_BAR_CYCLE_TICKS|shard_bar_ticks"`

Results:

- targeted lint passed
- targeted Pass 5 pytest batch passed: `37 passed`
- adjacent idle blessing regression batch passed: `21 passed`
- `basedpyright` still reports the pre-existing unresolved-import/type baseline in copied character modules and other unrelated files
- `tests/test_shard_bars.py` still fails as a pre-existing unrelated baseline; shard-bar implementation lines in `idle_state.py` matched `HEAD~1`

## Post-Pass 5: Idle Passive Progress Bars

Status: complete.

### Completed

- Added `PassiveBarDisplayData` plus `IdleGameState.get_passive_bars_for_character()` so idle cards can consume display-ready passive bar data without reaching into raw runtime payloads.
- Added reusable `endless_idler/ui/widgets/passive_progress_bar.py` on top of `AnimatedProgressBar`.
- Added `endless_idler/ui/theme/passive_progress_bar_widget.py` and registered it through `endless_idler/ui/theme/registry.py`.
- Updated `IdleCharacterCard` to place bars in the locked order:
  - HP
  - EXP
  - shard bar when available
  - passive bars when active
- Kept shard bars conditional instead of forcing a placeholder for cards with no shard reward types.
- Implemented passive-bar visibility so bars only render when the passive is active and exposes a meaningful current effect or stack-power signal.
- Replaced cadence-style fill/drain passive bars with impact bars that fill from computed stack power toward the likely effective soft target.
- Implemented Trinity bar styling with a light/dark gradient and subtle power-based shimmer.
- Implemented default passive-bar element coloring from the owning character, with Lady Darkness explicitly using dark styling.
- Added a visible Lady Light impact bar using Trinity stack power for fill and full passive contribution for text.
- Fixed `AnimatedProgressBar` so custom gradient colors actually affect rendering and exposed a `format()` helper for testable text assertions.
- Added targeted UI/state tests for passive-bar ordering, stacking, Trinity styling, and the new card-facing passive-bar accessor.

### Notes

- Passive bar text format is now effect-specific player-facing text.
- Passive bar fill now tracks passive power rather than stack cadence countdown.
- Fill normalizes against a computed likely soft target so it stays truthful if runtime tuning changes later.
- Trinity text reports mitigation percent, Lady Darkness text reports bleed strength, and Lady Light text reports total passive bonus as `x bonus`.
- Passive bars appear below the shard bar when the shard bar exists, otherwise directly below the EXP bar.

### Verification

- Lint:
  - `uv run ruff check endless_idler/ui/components/progress_bar.py endless_idler/ui/widgets/passive_progress_bar.py endless_idler/ui/theme/passive_progress_bar_widget.py endless_idler/ui/theme/registry.py endless_idler/ui/cards/character_card.py endless_idler/ui/idle/idle_state.py tests/test_idle_passives.py tests/ui/test_idle_blessing_ui.py`
- Targeted tests:
  - `uv run pytest -q tests/test_idle_passives.py tests/ui/test_idle_blessing_ui.py`
