# Passive Framework + Trinity Recovery Plan

## Status

- Pass 1 is complete.
- Pass 1 details and verification live in `done.md`.
- This file tracks the full roadmap, with Passes 2-6 still pending.

## Purpose

This plan rebuilds the lost Trinity branch as a clean forward implementation against the current repository state.

The locked direction is:
- rebuild a general passive framework first
- make passive persistence and runtime mirror blessings closely
- implement Trinity on top of that framework

This plan is optimized for:
- a correct end state in the current repo
- minimal compatibility baggage
- strict canonical save behavior
- clear implementation boundaries and verification points

This plan is not optimized for:
- recreating the old commit graph
- preserving obsolete identifiers
- reviving the dead combat-shaped passive shell as the main architecture

## Locked Decisions

- Keep the rebuild focused on a clean forward implementation, not historical branch recreation.
- `lady_fire` is the only canonical runtime id for Lady Fire.
- Do not add a compatibility shim for `lady_of_fire`.
- Do not add save migration for `lady_of_fire`.
- Keep `CharacterPlugin.passives` as the ownership and reference boundary for character-owned passives.
- Rebuild a general passive framework rather than adding Trinity-only glue.
- Make passive persistence and runtime mirror blessings very closely.
- Store canonical passive save data in top-level `RunSave.passives`.
- Key saved passive state by passive id.
- Keep runtime-only passive state out of canonical save.
- Export runtime-only passive state separately.
- Make `IdleGameState` the live execution owner for rebuilt passives.
- Do not use the old combat `PassiveTrigger` / `TriggerContext` / `_passive_instances` path as the main runtime architecture.
- Trinity remains idle-native.
- Trinity is the first major consumer of the rebuilt passive framework.
- Trinity-only effects require all three of:
  - `lady_darkness`
  - `lady_light`
  - `persona_light_and_dark`
- If any Trinity member is missing:
  - all Trinity-only bonuses shut off immediately
  - all Trinity stacks clear immediately
- If the trio reforms later, Trinity restarts from zero.
- Trinity persistence must be canonical passive state, not a hidden `__trinity__` payload.
- Post-soft-cap behavior changes effect value, not stack gain cadence.
- Lady Darkness's 30% HP floor uses skip + clamp behavior.
- `persona_ice.py` wording must only assume that Persona Ice is Lady Fire's brother.

## Current Verified Repo State

### Verified current state after Pass 1

- `endless_idler/characters/lady_fire.py` is now the live Lady Fire character module.
- `endless_idler/assets/characters/lady_fire/lady_fire.png` is now the live Lady Fire asset path.
- `lady_fire_infernal_momentum` is now the canonical Lady Fire passive id.
- `persona_ice.py` now only states that Lady Fire is Persona Ice's sister.
- Old saves containing `lady_of_fire` remain intentionally unsupported.
- Because startup save sanitization prunes unknown character ids and then persists canonical data, any save still using `lady_of_fire` will be stripped on load.

### Verified current architecture

- The passive package still exists under `endless_idler/passives/`, but it is mostly a combat-shaped shell.
- `passives/execution.py` still depends on `Stats._passive_instances`, and the idle runtime does not populate that path.
- `CharacterPlugin.passives` still exists and is still populated from character source metadata.
- AST metadata extraction for passive ids still exists in `endless_idler/characters/metadata.py`.
- Blessings already provide the best working model for discovery, plugin-owned save schema, strict canonical save validation, runtime-only transient export, and idle execution.
- `IdleGameState` in `endless_idler/ui/idle/idle_state.py` is still the real idle runtime authority.
- `endless_idler/ui/main_menu.py` and `endless_idler/ui/idle/screen.py` still copy idle snapshots back into `RunSave`.
- Save loading remains strict and canonical.
- Save migrations are still not part of `SaveManager.load()`.
- There is still no blessing-like passive plugin dataclass, passive loader, passive runtime module, or top-level `RunSave.passives` field.
- There are still no Trinity implementation modules under `endless_idler/passives/implementations/`.

## Recovered Target Behavior

These are the intended recovered mechanics that still define the rebuild target.

### Trinity gating

- Trinity is active only when all three members are present:
  - `lady_darkness`
  - `lady_light`
  - `persona_light_and_dark`
- Trinity-only bonuses must turn off immediately when the trio is incomplete.
- All Trinity stacks must clear immediately when the trio is incomplete.
- Re-forming the trio starts Trinity from zero again.

### Timing and stack model

- Idle tick rate remains fixed at 30 Hz.
- Main Trinity stacks:
  - gain 1 stack every 30 ticks
  - expire independently after 450 ticks
- Lady Darkness has a separate bleed-side timed stack pool:
  - same cadence: 1 stack every 30 ticks
  - same independent expiry: 450 ticks
- The timing follow-up means cadence stays constant.
- Only value and effect scaling change after the soft cap.

### Lady Light direction

- Lady Light is idle-native here, not combat-native.
- Lady Light provides conditional EXP transfer while full Trinity is active.
- Base transfer strength is:
  - 50% of Lady Darkness EXP-gain stat
  - plus 50% of Persona Light and Dark EXP-gain stat
- Each Trinity stack adds `+0.05%` to Lady Light transfer strength.
- Lady Light follows the same soft-cap style as the Darkness-side scaling.

### Lady Darkness direction

- `LadyDarknessEclipsingVeil` is idle-native bleed and EXP interaction.
- Lady Darkness EXP gain comes from real post-mitigation damage allies actually take.
- EXP source is not direct stack count.
- Lady Darkness stops damaging party members below 30% HP.

### Trinity mitigation

- Trinity bleed mitigation is `0.01%` reduction per stack.
- The soft-cap idea around 50% remains part of the design.

## Recovery Strategy Overview

The rebuild happens in six passes.

1. Pass 1: Rename + canon cleanup - complete
2. Pass 2: General passive framework - pending
3. Pass 3: Passive persistence + schema - pending
4. Pass 4: Idle runtime passive integration - pending
5. Pass 5: Trinity passive implementations - pending
6. Pass 6: Tests + verification - pending

This order stays deliberate.

- Pass 1 removed identifier ambiguity first.
- Pass 2 establishes the new framework without depending on the dead combat shell.
- Pass 3 makes passive state canonical and blessing-like in save data.
- Pass 4 gives `IdleGameState` ownership of passive execution and runtime export.
- Pass 5 implements Trinity on the new framework.
- Pass 6 verifies both the framework and the recovered Trinity mechanics.

## Detailed 6-Pass Plan

## Pass 1: Rename + Canon Cleanup

Status: complete. See `done.md` for the finished work and verification.

### Completed work

- Renamed the Lady Fire character module and canonical runtime id.
- Renamed the Lady Fire passive id prefix.
- Renamed the Lady Fire asset directory and portrait path.
- Updated Persona Ice wording to the canon-safe form.
- Verified discovery, asset resolution, lint, and targeted tests.

### Locked output from Pass 1

- `lady_fire` is now the only live runtime id.
- `lady_of_fire` is not supported as a compatibility alias.
- Startup save canonicalization will prune obsolete `lady_of_fire` entries.

---

## Pass 2: General Passive Framework

Status: complete. See `done.md` for the finished work and verification.

### Goal

Replace the dead combat-shaped passive shell with a blessing-like passive plugin framework that can support persistent idle-native passives.

### Completed work

- Replaced the public passive package API with `PassivePlugin` discovery and lookup.
- Added package-root passive plugin loading through module-level `passive` exports.
- Replaced the old class-registration registry with cached discovery-based lookup.
- Kept `CharacterPlugin.passives` unchanged as the ownership boundary.
- Left legacy combat helper modules in-tree but no longer exported them as the passive package API.
- Added metadata-only passive plugin modules for every passive id currently referenced by discovered character metadata.

### Locked output from Pass 2

- `endless_idler.passives` now means plugin discovery and lookup, not the old combat-trigger API.
- Passive lookup is package-root discovery with an explicit exclude list.
- Character passive membership still flows from `CharacterPlugin.passives`.
- Save persistence, idle runtime integration, and Trinity behavior remain deferred to later passes.

### Expected file cluster

- `endless_idler/passives/plugin.py`
- `endless_idler/passives/loader.py`
- `endless_idler/passives/registry.py`
- `endless_idler/passives/__init__.py`
- `endless_idler/passives/runtime.py` or equivalent idle-side runtime helpers
- `endless_idler/passives/implementations/__init__.py`
- possibly small cleanup or quarantine updates in:
  - `endless_idler/passives/base.py`
  - `endless_idler/passives/triggers.py`
  - `endless_idler/passives/execution.py`
- `endless_idler/characters/metadata.py`
- `endless_idler/characters/plugins.py`

### Key implementation work

- Add a `PassivePlugin` dataclass parallel to `BlessingPlugin`.
- Use filesystem discovery and a module-level exported `passive`, mirroring blessings where practical.
- Keep passive definitions separate from character plugin metadata.
- Preserve `CharacterPlugin.passives` as the ownership and lookup boundary.
- Define the minimum reusable passive interface needed for:
  - discovery
  - lookup by passive id
  - plugin-owned `save_schema`
  - canonical state seeding
  - idle runtime ticking or state advancement
  - canonical export
  - transient runtime export
- Keep deterministic passive discovery and registry ordering so snapshot behavior is stable.
- Treat the current combat shell as legacy inside the package rather than extending it as the new architecture.
- Avoid a generic trigger bus if narrow idle-native hooks are cleaner.

### Rationale

The current passive package still reflects an older combat-oriented architecture and does not own live idle runtime behavior. A blessing-like framework is the cleanest existing pattern already proven elsewhere in the repo.

### Risks

- Over-designing the passive interface before Trinity exists could add unnecessary abstractions.
- Reusing too much of the combat shell could drag the rebuild back into the wrong architecture.
- A weak registry boundary could make save-schema validation harder in Pass 3.

### Acceptance criteria

- Passive plugins can be discovered without importing character classes directly.
- Passive ids resolve through a real passive registry.
- Character metadata still owns passive membership through `CharacterPlugin.passives`.
- The new framework does not depend on `PassiveTrigger`, `TriggerContext`, or `Stats._passive_instances`.

### Suggested verification

- Discovery returns expected passive plugins.
- Duplicate passive ids fail deterministically.
- Character plugin metadata still exposes passive ids after the framework swap.

---

## Pass 3: Passive Persistence + Schema

Status: complete. See `done.md` for the finished work and verification.

### Goal

Add canonical blessing-like passive persistence so passive state survives save/load without using hidden payloads.

### Completed work

- Added top-level `RunSave.passives` with canonical defaults for every discovered passive id.
- Added blessing-style strict passive save validation and normalization in `save_codec.py`.
- Threaded passive payloads through `SaveManager.load()`, `SaveManager.save()`, and `_normalized_save()`.
- Added save-schema coverage for passive round-trip, strict rejection, and save-store crash recovery.

### Locked output from Pass 3

- Canonical saves now include top-level `passives`.
- Passive payload validation now matches blessing strictness exactly.
- Current passive payloads are canonical empty dicts until later passes add real schema fields.
- Runtime passive state remains out of scope until Pass 4.

### Expected file cluster

- `endless_idler/save.py`
- `endless_idler/save_codec.py`
- `endless_idler/run_save_store.py`
- passive registry or schema helpers introduced in Pass 2
- tests covering canonical save shape

### Key implementation work

- Add top-level `RunSave.passives` with a default canonical empty mapping.
- Add passive-state normalization and validation that mirrors blessing handling closely.
- Normalize saved passive payloads against plugin-owned `save_schema`.
- Strip unsupported passive ids from canonical save payloads.
- Fill missing saved fields using type-appropriate defaults.
- Exclude runtime-only transient fields from canonical save.
- Add narrow durable support for `list[int]` if Trinity expiry pools need it.
- Thread canonical passive state through the normal save/load path.
- Make sure the canonical save shape stays strict and predictable.

### Rationale

The plan is explicitly locked on top-level canonical passive persistence. Deferring this until after Trinity implementation would encourage temporary hacks and hidden payloads that then become harder to unwind.

### Risks

- Overly loose normalization could let bad passive state survive.
- Overly strict schema handling could break forward iteration if defaults are missing.
- If `list[int]` support is added too broadly, the codec may become less disciplined than intended.

### Acceptance criteria

- `RunSave` has a canonical `passives` field.
- Save/load round-trips passive state using plugin-owned schemas.
- Extra runtime fields are not serialized into canonical save output.
- Save loading does not rely on migration modules.

### Suggested verification

- Round-trip canonical passive save state through `SaveManager`.
- Confirm unknown passive ids are pruned.
- Confirm unsupported field types fail clearly.
- Confirm transient runtime payloads do not leak into saved JSON.

---

## Pass 4: Idle Runtime Passive Integration

Status: complete. See `done.md` for the finished work and verification.

### Goal

Make `IdleGameState` the runtime owner of passive state, passive ticking, and passive snapshot export.

### Completed work

- Added a dedicated passive runtime module and expanded `PassivePlugin` with a minimal runtime hook shape.
- Threaded canonical `passives` into `IdleGameState` and runtime snapshot export.
- Added active-only `passive_runtime` export in idle snapshots.
- Wired canonical passive save sync through `main_menu.py` and `ui/idle/screen.py`.
- Added targeted runtime/save-sync tests for passive snapshot behavior.

### Locked output from Pass 4

- `IdleGameState` now owns passive canonical state and active transient passive runtime state.
- Idle snapshots now export full canonical `passives` plus active-only `passive_runtime`.
- Canonical `passives` are written back into save objects; `passive_runtime` is not.
- Passive behavior remains no-op until Pass 5 adds real Trinity logic.

### Expected file cluster

- `endless_idler/ui/idle/idle_state.py`
- `endless_idler/ui/idle/screen.py`
- `endless_idler/ui/main_menu.py`
- passive runtime helpers from Pass 2
- save plumbing touched in Pass 3

### Key implementation work

- Seed passive canonical state into `IdleGameState` from `RunSave.passives`.
- Resolve active passive plugins from the current lineup and plugin metadata.
- Add runtime-owned passive state structures inside `IdleGameState`.
- Advance passive state each tick from idle runtime rather than from combat trigger dispatch.
- Add narrow passive runtime hooks where needed instead of a generic trigger bus.
- Export canonical passive state as `passives`.
- Export transient runtime-only state as `passive_runtime`.
- Thread canonical passive save data through:
  - `endless_idler/ui/main_menu.py`
  - `endless_idler/ui/idle/screen.py`
- Keep `passive_runtime` out of canonical save writes.

### Rationale

`IdleGameState` already owns the real live idle loop. Passive execution belongs there if passives are going to interact with idle EXP flow, ally damage, timing, and snapshot persistence.

### Risks

- Poor hook design could force Trinity into awkward, invasive runtime edits.
- Writing runtime-only state back into save would break the blessing-like persistence model.
- Passive runtime order may affect Trinity behavior if it is not explicitly stabilized.

### Acceptance criteria

- `IdleGameState` can initialize and carry passive state.
- Passive logic can advance each idle tick.
- Runtime snapshots expose both canonical `passives` and transient `passive_runtime`.
- Save writes only persist canonical passive data.

### Suggested verification

- Idle snapshots include canonical passive state and separate runtime state.
- Main menu and idle screen persist canonical passive data correctly.
- Reloading a run re-seeds passive state from saved canonical fields.

---

## Pass 5: Trinity Passive Implementations

### Goal

Implement Trinity as the first real consumer of the rebuilt passive framework.

### Expected file cluster

- `endless_idler/passives/trinity.py`
- `endless_idler/passives/implementations/trinity_synergy.py`
- `endless_idler/passives/implementations/lady_light_radiant_aegis.py`
- `endless_idler/passives/implementations/lady_darkness_eclipsing_veil.py`
- character passive membership surfaces if additional passive ids must be wired in

### Key implementation work

- Add a shared Trinity coordination layer that determines whether the trio is complete.
- Keep the shared Trinity state canonical and keyed by passive id, not by hidden reserved keys.
- Choose one canonical owner for shared Trinity coordination if needed so the state still fits the `CharacterPlugin.passives` ownership model.
- Implement immediate shutdown when the trio is incomplete.
- Implement immediate stack clearing when the trio is incomplete.
- Implement restart-from-zero behavior when the trio reforms.
- Implement the main Trinity stack pool:
  - gain 1 stack every 30 ticks
  - each stack expires independently after 450 ticks
- Implement the Lady Darkness bleed-side timed pool separately:
  - gain 1 stack every 30 ticks
  - each stack expires independently after 450 ticks
- Keep cadence fixed after the soft cap.
- Change only effect value after the soft cap.
- Implement Lady Light EXP transfer using the locked formula.
- Implement Trinity mitigation at `0.01%` per stack.
- Implement Lady Darkness EXP gain from real post-mitigation ally damage.
- Apply the 30% HP floor using skip + clamp behavior.

### Rationale

Trinity is the actual design target that justified rebuilding the passive framework in the first place. It should land only after the framework, save schema, and runtime ownership are already correct.

### Risks

- Trinity may tempt new shared-state shortcuts that violate the passive-id keyed save model.
- The cleanest runtime source for the EXP-gain stat still needs to be locked down during implementation.
- Damage-floor handling is easy to get subtly wrong if skip and clamp behavior are mixed up.

### Acceptance criteria

- Trinity bonuses exist only while the full trio is present.
- Breaking the trio clears stacks immediately.
- Reforming the trio restarts from zero.
- Stack cadence is 30 ticks and expiry is 450 ticks per independent stack.
- Lady Light and Lady Darkness behaviors match the locked design direction.
- Trinity state survives save/load through canonical passive persistence.

### Suggested verification

- Trio present and trio broken cases both behave correctly.
- Reloading preserves canonical Trinity state but not transient-only runtime fields.
- Soft-cap behavior changes value, not cadence.
- Lady Darkness stops applying damage below the 30% floor.

---

## Pass 6: Tests + Verification

### Goal

Verify both the general passive framework and the recovered Trinity behavior end to end.

### Expected file cluster

- `tests/passives/test_registry.py`
- `tests/passives/test_plugin.py`
- `tests/test_idle_passives.py`
- `tests/test_idle_trinity_runtime.py`
- `tests/test_passive_integration.py`
- save and UI runtime tests as needed

### Key implementation work

- Add passive discovery and registry tests.
- Add passive plugin schema and canonical export tests.
- Add save round-trip and schema rejection coverage for passive state.
- Add idle runtime tests for passive seeding, ticking, and snapshot export.
- Add Trinity tests for:
  - trio gating
  - immediate reset on trio break
  - restart-from-zero on trio reform
  - stack cadence
  - independent expiry
  - soft-cap behavior
  - Lady Light transfer
  - Lady Darkness damage floor and EXP gain
- Baseline unrelated failures before calling them regressions, especially `tests/test_shard_bars.py`.

### Rationale

The passive rebuild changes framework, save shape, idle runtime, and gameplay behavior. It needs layered verification, not just a single Trinity happy-path test.

### Risks

- If tests are added only at the Trinity layer, framework regressions may be missed.
- If baseline failures are not separated from new regressions, verification noise will be misleading.

### Acceptance criteria

- Passive framework behavior is covered separately from Trinity behavior.
- Canonical save behavior is enforced by tests.
- Idle runtime export and persistence are both covered.
- Trinity behavior is validated across lifecycle, timing, and persistence cases.

### Suggested verification

- Iteration:
  - targeted `uv run pytest` for touched modules
- Final validation:
  - `uv run ruff check .`
  - `uv run basedpyright`
  - `uv run pytest -q`

## Cross-Pass Guardrails

- Do not reopen the Lady Fire rename.
- Do not add compatibility shims unless explicitly requested later.
- Do not hide Trinity or passive state inside `character_progress`, `character_stats`, or `blessings`.
- Do not make the old combat passive shell the primary runtime path.
- Prefer the smallest framework that cleanly supports Trinity.
- Keep canonical save state strict and runtime state separate.

## Open Questions

These should still be checked during implementation rather than guessed up front.

1. What exact soft-cap function should Trinity use after the locked design rule?
2. What is the cleanest current runtime source for the Trinity-related EXP-gain stat?
3. Does passive persistence need a `SAVE_VERSION` bump even though loading cannot depend on migrations?
4. Does any non-Trinity passive need first-wave support so the general framework stays coherent?

## Suggested Commit Boundaries

- `[FEAT] add passive plugin foundation`
- `[FEAT] persist canonical passive state`
- `[FEAT] integrate passive runtime into idle state`
- `[FEAT] implement trinity idle passives`
- `[TEST] add passive and trinity coverage`
