# Idle Mechanics Roadmap

## Summary

This planning doc tracks forward-looking mechanics and unresolved design decisions.

Date captured: 2026-03-05
Last updated: 2026-04-05

## Planned Mechanics (Target Design)

### Warp Banner System

Planned intent:
- Build Warp into a banner-based progression/gacha system.

Locked decisions:
- Banner set is 7 total:
  - 6 elemental banners
  - 1 YOLO banner
- Normal non-character pulls award only Prismatic Shards; characters remain rare outcomes.
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
- Elemental banners consume 160 matching damage-type shards per pull.
- Non-elemental banners consume 160 total damage-type shards paid from up to three damage types chosen by the player.

Pending:
- Translate the locked formulas into Warp runtime constants/helpers during implementation.
- Add validation fixtures/simulations for pity progression and 6/7 star probability sanity checks.

### Damage-Type Shard Warp Payments

Planned intent:
- Keep Warp progression funded by the elemental shard system that is live today and ensure rebirth/progression rewards target that pool.
- Make damage-type shards the primary conduit for paying for Warp pulls while keeping the experience grounded in existing elemental damage types.

Locked decisions:
- Damage-type shards match the elemental shard types currently live (Fire, Ice, Wind, Lightning, Light, Dark) and serve as the exclusive Warp currency.
- Rebirth and related progression channels must guarantee a minimum damage-type shard inflow so players can cover the 160-shard pull costs locked above.
- Warp payment logic uses these damage-type shards, which means elemental banners require matching-shard payments and non-elemental banners can draw from up to three player-selected damage types.
- This damage-type shard pool directly drives Warp progression, superseding the prior Upgrade Stone framing.

Pending:
- Exact per-rebirth shard payout schedule (base drops, extras, and rounding behavior).
- How salvage/crafting/other long-term sources funnel into damage-type shard income for Warp.
- Interaction rules between shard income and long-running progression modifiers or buffs.

### Prismatic Shards, Prism Archetypes, and Prismatic Dust Crafting

Planned intent:
- Build a long-term prismatic progression layer that is independent from character rarity tiers.

Locked decisions:
- 1-4 stars are prismatic shards.
- 5-7 stars are character rarities.
- Each character has one fixed `prism_archetype_id`.
- Target prism archetype catalog size is approximately 20 types.
- Prismatic shards are prism-archetype bound:
  - a shard belongs to a prism archetype
  - it can be used by any character with that prism archetype
- Prism archetypes are expected to affect stats/progression behavior.
- Unwanted shards can be salvaged into Prismatic Dust.
- Star-to-prismatic-power mapping is locked to:
  - 1 star = 15%
  - 2 star = 45%
  - 3 star = 150%
  - 4 star = 500%
- Crafting anchors currently locked:
  - 1 star craft cost = 1000 Prismatic Dust
  - 2 star craft cost = 2500 Prismatic Dust
  - 3 star craft cost = 5000 Prismatic Dust
  - 4 star craft cost = 100000 Prismatic Dust
- Craft duration starts at 1 hour per star rank, then is modified by buffs/debuffs.
- Craft duration floor is 5 seconds.
- If buffs would reduce craft duration below 5 seconds:
  - each extra second converts to +0.01% bonus odds for random side prismatic shards
  - no cap is applied to overflow seconds or bonus odds
- Bonus-odds payout model:
  - use deterministic + remainder behavior when bonus odds exceed 100%
  - reduce remaining bonus odds by geometric decay (0.5x) after each awarded extra shard
- Overflow bonus extra shards must belong to a different prism archetype than the crafted target archetype.
- Overflow bonus extra-shard star rank can match the crafted rank or be lower.
- Damage-type shards can be crafted into Prismatic Dust with the following planning guidance:
  - base craft size is 100 shards over 48 hours
  - base rate is 28.8 minutes per shard
  - shard output should flow one at a time during the craft instead of only at completion
  - the player chooses the requested damage type for shard output
  - there is a small chance for output to become a different damage type
  - the player can choose smaller or larger craft sizes
  - smaller batches finish sooner overall but are less time-efficient per shard
  - larger batches take longer overall but are more time-efficient per shard

Pending:
- Exact formal equation for overflow seconds -> bonus odds conversion pipeline.
- Exact implementation order for deterministic payouts and 0.5x post-award decay.
- Exact distribution weights for "match-or-lower" extra-shard star outcomes.
- Exact `prism_archetype_id` list and naming for the ~20-type catalog.
- Initial prism archetype planning still needs a roster-grounded planning pass before the catalog is finalized.
- `prism_archetype_id` naming should:
  - lean on prism / glass / light motif language
  - use lowercase snake_case IDs
  - avoid direct element or damage-type names to prevent confusion with shard/payment terminology
- Exact stat/progression lanes impacted by prism-archetype/prismatic-shard power.

### Prism Archetypes

Planned starter set for art and identity:
- `halo_guardian` - barrier/taunt/protection. Fits Lady Light, Carly, Persona Light and Dark.
- `lunar_blade` - precise moonlit duelist/control. Fits Ryne, Luna.
- `eclipse_veil` - light/shadow duality, concealment, debuffs. Fits Lady Darkness, Persona Light and Dark.
- `prism_weaver` - refracted magic, support, artifice, coordination. Fits Lady Echo, Jennifer Feltmann, Becca, Ally.
- `shardstorm_vanguard` - fast burst, storm/glass/lightning energy. Fits Lady Storm, Lady Lightning, Lady Wind, Ixia.

## Open High-Impact Decisions

- Exact prismatic shard odds unit conversions and tick-to-time expectations.
- Exact rebirth drop formula and caps/floors policy.
- Warp implementation sequencing and simulation verification for locked rarity math.
- Final damage-type shard extra-reward math.
- Final overflow craft-bonus math ordering and payout details.
- Final prism-archetype stat/progression impact model.

### Future Upgrade / Prismatic Blessings

Planned intent:
- Reserve a separate future progression lane for upgrade/prismatic blessings tied to prismatic systems.

Pending:
- Exact blessing structure, unlock path, and how it interfaces with prismatic shards or Prismatic Dust.

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
