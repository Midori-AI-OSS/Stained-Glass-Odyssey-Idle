1: # Idle Mechanics Roadmap
2: 
3: ## Summary
4: 
5: This planning doc tracks forward-looking mechanics and unresolved design decisions.
6: 
7: Date captured: 2026-03-05
8: Last updated: 2026-03-11
9: 
10: ## Planned Mechanics (Target Design)
11: 
12: ### 3: Warp Banner System
13: 
14: Planned intent:
15: - Build Warp into a banner-based progression/gacha system.
16: 
17: Locked decisions:
18: - Banner set is 7 total:
19:   - 6 elemental banners
20:   - 1 YOLO banner
21: - Failed pulls on all banners grant item rewards for non-character progression systems
22:   (city, housing, gear, or equivalent development paths).
23: - Pity is per-banner, with a single pity track per banner.
24: - 5 star odds follow the Endless linear pity curve:
25:   - `p5(pity) = 0.00001 + pity * ((0.05 - 0.00001) / 159)`
26:   - hard guarantee at `pity >= 179`
27: - High-tier roll order is: 5 star pity branch first, then 6 star branch.
28: - 6 star base chance remains 0.01% (1 in 10,000).
29: - 7 star is derived from successful 6 star branch promotion (not a primary roll tier):
30:   - `p_promote = 0.00001%` of successful 6 star branch outcomes
31:   - implied base 7 star odds are approximately 1 in 100,000,000,000 pulls before modifiers
32: - 7 star constraints:
33:   - current 7 star pool is a single character (Luna)
34:   - current 7 star character uses Generic (non-normal) damage typing
35:   - 7 star outcomes can never be banner-featured
36:   - on elemental banners, if same-element eligibility fails, no 7 star can occur on that pull
37: - Pity resets on any 5 star, 6 star, or 7 star outcome.
38: - YOLO banner applies 50x to raw rates (including 7 star), then normalizes to a valid distribution.
39: 
40: Pending:
41: - Translate the locked formulas into Warp runtime constants/helpers during implementation.
42: - Add validation fixtures/simulations for pity progression and 6/7 star probability sanity checks.
43: 
44: ### Rebirth Currency for Warp: Upgrade Stones
45: 
46: Planned intent:
47: - Rebirth should always feed Warp currency.
48: 
49: Locked decisions:
50: - Every rebirth grants 1 guaranteed Upgrade Stone.
51: - Rebirth can grant additional stones.
52: - Extra-stone behavior should become harder for each additional extra in the same rebirth event.
53: - Extra-stone logic is tied to progression factors, including:
54:   - crit_mod
55:   - rebirth count
56:   - town level
57:   - character level
58: 
59: Pending:
60: - Exact extra-stone formula and deterministic rounding behavior.
61: - Exact diminishing-returns algorithm for repeated extras in one rebirth.
62: 
63: ### 4: Prismatic Shards, Prism Archetypes, and Prismatic Dust Crafting
64: 
65: Planned intent:
66: - Build a long-term weapon progression layer that is independent from character rarity tiers.
67: 
68: Locked decisions:
69: - 1-4 stars are prismatic shards.
70: - 5-7 stars are character rarities.
71: - Each character has one fixed `prism_archetype_id`.
72: - Target prism archetype catalog size is approximately 20 types.
73: - Prismatic shards are prism-archetype bound:
74:   - a shard belongs to a prism archetype
75:   - it can be used by any character with that prism archetype
76: - Prism archetypes are expected to affect stats/progression behavior.
77: - Unwanted shards can be salvaged into Prismatic Dust.
78: - Crafting anchors currently locked:
79:   - 1 star craft cost = 100 Prismatic Dust
80:   - 2 star craft cost = 500 Prismatic Dust
81: - Craft duration starts at 1 hour per star rank, then is modified by buffs/debuffs.
82: - Craft duration floor is 5 seconds.
83: - If buffs would reduce craft duration below 5 seconds:
84:   - each extra second converts to +0.01% bonus odds for random side prism archetypes
85:   - no cap is applied to overflow seconds or bonus odds
86: - Bonus-odds payout model:
87:   - use deterministic + remainder behavior when bonus odds exceed 100%
88:   - reduce remaining bonus odds by geometric decay (0.5x) after each awarded extra part
89: - Overflow bonus extra shards must be a different prism archetype than the crafted target type.
90: - Overflow bonus extra-shard star rank can match the crafted rank or be lower.
91: 
92: Pending:
93: - Exact 3 star and 4 star Prismatic Dust craft costs.
94: - Exact formal equation for overflow seconds -> bonus odds conversion pipeline.
95: - Exact implementation order for deterministic payouts and 0.5x post-award decay.
96: - Exact distribution weights for "match-or-lower" extra-shard star outcomes.
97: - Exact `prism_archetype_id` list and naming for the ~20-type catalog.
98: - Exact stat/progression lanes impacted by prism-archetype/prismatic-shard power.
99: 
100: ## Open High-Impact Decisions
101: 
102: - Final star-to-prism-power mapping for 1-4 prismatic shards.
103: - Exact shard odds unit conversions and tick-to-time expectations.
104: - Exact rebirth drop formula and caps/floors policy.
105: - Warp implementation sequencing and simulation verification for locked rarity math.
106: - Final Upgrade Stone extra-reward math.
107: - Final 3-4 star Prismatic Dust costs.
108: - Final overflow craft-bonus math ordering and payout details.
109: - Final prism-archetype stat/progression impact model.
110: 
111: Note: Future "upgrade blessings" with prismatic shards/shards planned separately.
112: 
113: ### Future: Drop Table System
114: 
115: Planned intent:
116: - JSON loadable drop tables for rolling loot drops.
117: - Easy to update and modify without code changes.
118: 
119: Pending:
120: - JSON schema design
121: - Table loading infrastructure
122: - Integration points with existing systems
123: 
124: ## Notes
125: 
126: - This doc is a planning artifact and is intentionally future-facing.
127: 
128: ---
129: 
130: ## Run Log
131: 
132: Role: Coder Quick
133: Files Touched: .agents/planning/idle-mechanics-roadmap.md
134: Intent: Retheme weapon/salvage terminology to prismatic terminology per scope.
135: Actions Taken: Applied term mapping substitutions and removed 'Mech' prefixes from targeted headings.
136: Results: All required textual changes implemented; numeric values preserved.
137: Blockers/Follow-ups: None.
