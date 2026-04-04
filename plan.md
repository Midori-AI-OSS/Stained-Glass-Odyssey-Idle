# Passive Framework Verification Plan

## Status

- Passes 1-5 are complete.
- Completed pass details and verification live in `done.md`.
- This file now tracks the remaining roadmap only.

## Purpose

This plan tracks only the remaining verification roadmap for the completed passive-framework and Trinity rebuild.

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
- Trinity deployment is `onsite` + `offsite` only.
- Putting any Trinity member into `standby` breaks Trinity immediately.
- If any Trinity member is missing:
  - all Trinity-only bonuses shut off immediately
  - all Trinity stacks clear immediately
- If the trio reforms later, Trinity restarts from zero.
- Trinity persistence must be canonical passive state, not a hidden `__trinity__` payload.
- Post-soft-cap behavior changes effect value, not stack gain cadence.
- Trinity soft-cap uses the harder log-style diminishing-returns shape after the 50% threshold.
- Trinity gameplay scaling uses the existing runtime `passive_modifier` only.
- Lady Darkness's 30% HP floor uses skip + clamp behavior.
- Lady Darkness bleed uses `raw / ((defense / 5) * mitigation)` after deriving raw percent-max-HP bleed.
- Lady Darkness converts current-tick actual post-mitigation HP loss into `+5% EXP gain per 1% HP lost`.
- Lady Light uses 50% of Lady Darkness effective `exp_multiplier` plus 50% of Persona Light and Dark effective `exp_multiplier`, including baseline `1.0x` source values.
- `persona_ice.py` wording must only assume that Persona Ice is Lady Fire's brother.

## Current Verified Repo State

- `lady_fire` is the live canonical Lady Fire runtime id and asset path.
- The passive package now exposes plugin discovery, registry lookup, canonical passive save state, and idle runtime passive plumbing.
- `RunSave.passives` now exists and is validated strictly like blessings.
- `IdleGameState` now owns canonical passive state plus active transient passive runtime state.
- Idle snapshots now export full canonical `passives` and active-only `passive_runtime`.
- `main_menu.py` and `ui/idle/screen.py` now sync canonical `passives` back into `RunSave` without persisting `passive_runtime`.
- Trinity gameplay behavior is now implemented on the rebuilt passive framework.
- New Trinity passive ids are backward-compatible with existing canonical passive payloads through default seeding, while unknown ids and non-canonical fields are still rejected.
- Passive canonical schema now supports `list[int]`, which Trinity uses for independent-expiry TTL pools.
- `trinity_synergy` now owns the shared Trinity pool canonically, and `lady_darkness_eclipsing_veil` owns the separate Darkness bleed pool canonically.
- Idle character-card bar ordering is now locked as:
  - HP
  - EXP
  - conditional shard bar when reward types exist
  - conditional passive bars only while the passive is actively working
  - if the shard bar is hidden, passive bars render directly under EXP
  - additional passive bars stack below the first passive bar

## Recovery Strategy Overview

The rebuild happens in six passes.

1. Pass 1: Rename + canon cleanup - complete
2. Pass 2: General passive framework - complete
3. Pass 3: Passive persistence + schema - complete
4. Pass 4: Idle runtime passive integration - complete
5. Pass 5: Trinity passive implementations - complete
6. Pass 6: Tests + verification - pending

This order stays deliberate.

- Pass 1 removed identifier ambiguity first.
- Pass 2 established the framework without depending on the dead combat shell.
- Pass 3 made passive state canonical and blessing-like in save data.
- Pass 4 gave `IdleGameState` ownership of passive execution and runtime export.
- Pass 5 implemented Trinity on the new framework.
- Pass 6 verifies both the framework and the recovered Trinity mechanics.

## Remaining Plan

- All six planned passes are complete.
- `done.md` now holds the completed verification record for the passive framework, Trinity behavior, and passive UI follow-up work.
- Any next work should start from a new task rather than extending the original recovery roadmap.

## Cross-Pass Guardrails

- Do not reopen the Lady Fire rename.
- Do not add compatibility shims unless explicitly requested later.
- Do not hide Trinity or passive state inside `character_progress`, `character_stats`, or `blessings`.
- Do not make the old combat passive shell the primary runtime path.
- Prefer the smallest framework that cleanly supports Trinity.
- Keep canonical save state strict and runtime state separate.

## Suggested Commit Boundaries

- Recovery roadmap complete; future commits should use task-specific scopes.
