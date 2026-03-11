# Idle Mechanics Roadmap

## Summary

This planning doc tracks forward-looking mechanics and unresolved design decisions.

Date captured: 2026-03-05
Last updated: 2026-03-11

## Planned Mechanics (Target Design)

### Mech 3: Rebirth Shard Drops

Planned intent:
- Rebirths are an additional shard source alongside shard bars.

Locked decisions:
- Keep both shard sources:
  - shard bars
  - rebirth drops
- Rebirth drop starting concept is 1 in 6, then modified by progression factors.
- Generic (Luna) rebirth shard outcome is random elemental.
- HP drain was removed from this plan.
- Standby EXP gain model:
  - Standby characters (not in Onsite/Offsite) gain 0.01% of total offsite EXP
  - processed at 50% tick rate (every other tick, effectively 0.005% per actual tick)

Pending:
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
- Pity is per-banner, with a single pity track per banner.
- 5 star odds follow the Endless linear pity curve:
  - `p5(pity) = 0.00001 + pity * ((0.05 - 0.00001) / 159)`
  - hard guarantee at `pity >= 179`
- High-tier roll order is: 5 star pity branch first, then 6 star branch.
- 6 star base chance remains 0.01% (1 in 10,000).
- 7 star is derived from successful 6 star branch promotion (not a primary roll tier):
  - `p_promote = 0.00001%` of successful 6 star branch outcomes
  - implied base 7 star odds are approximately 1 in 100,000,000,000 pulls before modifiers
- 7 star constraints:
  - current 7 star pool is a single character (Luna)
  - current 7 star character uses Generic (non-normal) damage typing
  - 7 star outcomes can never be banner-featured
  - on elemental banners, if same-element eligibility fails, no 7 star can occur on that pull
- Pity resets on any 5 star, 6 star, or 7 star outcome.
- YOLO banner applies 50x to raw rates (including 7 star), then normalizes to a valid distribution.

Pending:
- Translate the locked formulas into Warp runtime constants/helpers during implementation.
- Add validation fixtures/simulations for pity progression and 6/7 star probability sanity checks.

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
- Craft duration starts at 1 hour per star rank, then is modified by buffs/debuffs.
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
- Warp implementation sequencing and simulation verification for locked rarity math.
- Final Upgrade Stone extra-reward math.
- Final 3-4 star Salvage Dust costs.
- Final overflow craft-bonus math ordering and payout details.
- Final weapon-type stat/progression impact model.

Note: Blessing Channeling was removed from Mech 3. Future "upgrade blessings" with weapon parts/shards planned separately.

### Future: Drop Table System

Planned intent:
- JSON loadable drop tables for rolling loot drops.
- Easy to update and modify without code changes.

Pending:
- JSON schema design
- Table loading infrastructure
- Integration points with existing systems

## Notes

- This doc is a planning artifact and is intentionally future-facing.
