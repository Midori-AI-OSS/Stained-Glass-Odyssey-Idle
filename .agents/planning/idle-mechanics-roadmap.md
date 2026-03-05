# Idle Mechanics Roadmap

## Summary

This planning doc captures the current mechanics baseline and the intended future mechanics discussed so far.
It is decision-oriented and separates implemented behavior from planned behavior to avoid confusion.

Date captured: 2026-03-05
Last updated: 2026-03-05

## Current Baseline (Fact-Checked)

- Active runtime path is Home + Idle.
- Battle/foe systems are legacy and not part of the active runtime flow.
- Stars currently scale combat stats, not rebirth/prestige gain formulas.
- Character plugin rarities are mostly 5-7 today, with metadata fallback behavior still allowing lower values when unspecified.
- Warp is currently a stub entry in the menu.
- No current energy subsystem exists for blessing channeling.
- No current Upgrade Stone currency exists in save/runtime models.
- Offsite EXP is currently sourced from onsite-driven pools in idle processing.

## Planned Mechanics (Target Design)

### Mech 1: Star Bands and Character Progression Weighting

Locked anchors:
- 1-4 stars are weapon parts only, not character rarity tiers.
- 5-7 stars are character rarity tiers.
- Character-star progression anchors remain:
  - 7 star = 2.5x
  - 6 star = 1.0x
  - 5 star = 0.5x

Planned intent:
- Character star rank (5-7 only) should affect rebirth/prestige gain-side progression values.

Pending:
- Exact rebirth/prestige gain terms affected by 5-7 star multipliers.
- Exact migration behavior for any character metadata that lands outside 5-7.

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

### Mech 5: Weapon Parts, Types, and Salvage Crafting

Planned intent:
- Build a long-term weapon progression layer that is independent from character rarity tiers.

Locked decisions:
- 1-4 stars are weapon parts.
- 5-7 stars are character rarities.
- Each character has one fixed `weapon_type_id`.
- Target weapon catalog size is approximately 20 types.
- Weapon parts are weapon-type bound:
  - a part belongs to a weapon type
  - it can be used by any character with that weapon type
- Weapon types are expected to affect stats/progression behavior.
- Unwanted parts can be salvaged into Salvage Dust.
- Crafting anchors currently locked:
  - 1 star craft cost = 100 Salvage Dust
  - 2 star craft cost = 500 Salvage Dust
- Craft duration baseline is 1 hour per star rank, then modified by buffs/debuffs.
- Craft duration floor is 5 seconds.
- If buffs would reduce craft duration below 5 seconds:
  - each extra second converts to +0.01% bonus odds for random side weapon parts
  - no cap is applied to overflow seconds or bonus odds
- Bonus-odds payout model:
  - use deterministic + remainder behavior when bonus odds exceed 100%
  - reduce remaining bonus odds by geometric decay (0.5x) after each awarded extra part
- Overflow bonus extra parts must be a different weapon type than the crafted target type.
- Overflow bonus extra-part star rank can match the crafted rank or be lower.

Pending:
- Exact 3 star and 4 star Salvage Dust craft costs.
- Exact formal equation for overflow seconds -> bonus odds conversion pipeline.
- Exact implementation order for deterministic payouts and 0.5x post-award decay.
- Exact distribution weights for "match-or-lower" extra-part star outcomes.
- Exact `weapon_type_id` list and naming for the ~20-type catalog.
- Exact stat/progression lanes impacted by weapon-type/weapon-part power.

## Open High-Impact Decisions

- Final star-to-weapon-power mapping for 1-4 weapon parts.
- Exact shard odds unit conversions and tick-to-time expectations.
- Exact rebirth drop formula and caps/floors policy.
- Final energy model details (drain, regen, minimums, persistence fields).
- Final Warp rarity math including YOLO normalization and 6/7 star distribution.
- Final Upgrade Stone extra-reward math.
- Final 3-4 star Salvage Dust costs.
- Final overflow craft-bonus math ordering and payout details.
- Final weapon-type stat/progression impact model.

## Notes

- This doc is a planning artifact, not current implementation state.
- Any implementation work should preserve the baseline/planned distinction until features are shipped.
