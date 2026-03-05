# Idle Mechanics Roadmap

## Summary

This planning doc captures the current mechanics baseline and the intended future mechanics discussed so far.
It is decision-oriented and separates implemented behavior from planned behavior to avoid confusion.

Date captured: 2026-03-05

## Current Baseline (Fact-Checked)

- Active runtime path is Home + Idle.
- Battle/foe systems are legacy and not part of the active runtime flow.
- Stars currently scale combat stats, not rebirth/prestige gain formulas.
- Warp is currently a stub entry in the menu.
- No current energy subsystem exists for blessing channeling.
- No current Upgrade Stone currency exists in save/runtime models.
- Offsite EXP is currently sourced from onsite-driven pools in idle processing.

## Planned Mechanics (Target Design)

### Mech 1: Star-Weighted Rebirth and Prestige Gains

Locked anchors:
- 7 star = 2.5x
- 6 star = 1.0x
- 5 star = 0.5x

Planned intent:
- Star rank should affect rebirth/prestige gain-side progression values.

Pending:
- Exact 1-4 star mapping.
- Exact rebirth/prestige gain terms affected by star multiplier.

### Mech 2: Blessing Upgrade Layer and Shard Progression

Planned intent:
- Introduce blessing systems as pluginized modules, similar to character plugin structure.
- Add shard progression bars as a long-term growth system.

Locked decisions:
- Bars are per-character, not global.
- 100 ticks completes a bar cycle.
- Completion grants consumable shard output.
- Pacing target is very slow (years-scale direction).
- High-EXP dampener concept for shard odds:
  - p_eff = p_base / (1 + 15000 * floor((exp_s - 1000) / 100))

Pending:
- Exact unit definition for p_base (percent vs probability conversion details).
- Exact years-scale balancing targets.

### Mech 3: Rebirth Shard Drops and Blessing Channeling

Planned intent:
- Rebirths are an additional shard source alongside shard bars.
- Blessings are activated via character channeling outside normal party assignment.

Locked decisions:
- Keep both shard sources:
  - shard bars
  - rebirth drops
- Rebirth drop baseline concept is 1 in 6, then modified by progression factors.
- Generic (Luna) rebirth shard outcome is random elemental.
- Blessing management occurs via Home menu assignment flow.
- Assigned channeling characters are removed from party assignment while channeling.
- HP drain was removed from this plan.
- Channeling now uses Energy drain.
- Lower Energy means lower background EXP gain.
- Background gain model:
  - background characters gain 0.01% of total offsite EXP
  - processed at 50% tick rate (every other tick)
- Energy-to-EXP scaling direction is linear from 0 to 100 Energy.

Pending:
- Exact energy stat schema and persistence.
- Exact energy drain formula and cadence.
- Exact rebirth-drop modifier formula (blessings, stars, rebirths, prestige, crit_mod).
- Exact outcome handling across all type contexts.

### Mech 4: Warp Banner System

Planned intent:
- Build Warp into a banner-based progression/gacha system.

Locked decisions:
- Banner set is 7 total:
  - 6 elemental banners
  - 1 YOLO banner
- Failed pulls on all banners grant item rewards for non-character progression systems
  (city, housing, gear, or equivalent development paths).
- Pity is per-banner.
- Every 10 pulls adds +1% to 5 star odds on that banner.
- Pity resets when a 5 star drops on that banner.
- YOLO banner uses a 50x buff concept affecting all rarity odds.

Pending:
- Final normalization math for YOLO all-rarity behavior.
- Final 6 star and 7 star odds math, to be aligned with Endless Autofighter reference behavior.

### Rebirth Currency for Warp: Upgrade Stones

Planned intent:
- Rebirth should always feed Warp currency.

Locked decisions:
- Every rebirth grants 1 guaranteed Upgrade Stone.
- Rebirth can grant additional stones.
- Extra-stone behavior should become harder for each additional extra in the same rebirth event.
- Extra-stone logic is tied to progression factors, including:
  - crit_mod
  - rebirth count
  - town level
  - character level

Pending:
- Exact extra-stone formula and deterministic rounding behavior.
- Exact diminishing-returns algorithm for repeated extras in one rebirth.

## Open High-Impact Decisions

- Final 1-4 star multiplier table.
- Exact shard odds unit conversions and tick-to-time expectations.
- Exact rebirth drop formula and caps/floors policy.
- Final energy model details (drain, regen, minimums, persistence fields).
- Final Warp rarity math including YOLO normalization and 6/7 star distribution.
- Final Upgrade Stone extra-reward math.

## Notes

- This doc is a planning artifact, not current implementation state.
- Any implementation work should preserve the baseline/planned distinction until features are shipped.
