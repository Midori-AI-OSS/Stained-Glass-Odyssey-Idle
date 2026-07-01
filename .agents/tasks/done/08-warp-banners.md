# 08 – Warp Banner Auto-Generation

## What to Do
Create `endless_idler/warp/banners.py` with banner auto-generation logic that scans character plugins and groups them by damage type and star rating.

## Relevant Files
- `endless_idler/warp/banners.py` (new file)
- `endless_idler/warp/constants.py` — `BANNER_IDS`
- `endless_idler/characters/plugins.py` — `CharacterPlugin`, `discover_character_plugins()`
- `endless_idler/combat/damage_types.py` — `normalize_damage_type_id()` (line 12) for parsing composite damage types

## Pre-Execution Checks
- [ ] Confirm Task 07 is complete (constants with `BANNER_IDS`).
- [ ] Familiarize with `CharacterPlugin` dataclass fields (plugins.py lines 35–51): `char_id`, `display_name`, `stars`, `damage_type_id`, `damage_type_random`, `is_dual_type`, `dual_damage_types`.
- [ ] **Key data point**: Run `uv run python -c "from endless_idler.characters.plugins import discover_character_plugins; [print(p.char_id, p.stars, repr(p.damage_type_id), p.is_dual_type, p.dual_damage_types) for p in discover_character_plugins()]"` to see current character pool. There are 22 characters: 17 at 5★, 4 at 6★ (lady_fire_and_ice, lady_storm, persona_light_and_dark, ryne), 1 at 7★ (luna).
- [ ] **Dual-type format**: `lady_fire_and_ice` has `damage_type_id='fire / ice'` (with spaces around `/`). Use `normalize_damage_type_id()` from `endless_idler.combat.damage_types` to parse these consistently.

## Steps

1. Create `endless_idler/warp/banners.py`.

2. Define a `BannerCharacter` dataclass with:
   - `char_id: str`
   - `display_name: str`
   - `stars: int` (5 or 6)
   - `damage_type_id: str`
   - `is_dual_type: bool`
   - `dual_damage_types: tuple[str, str]`

3. Define a `BannerDefinition` dataclass with:
   - `banner_id: str` (matches `BANNER_IDS`)
   - `five_star_pool: list[BannerCharacter]` — 5★ characters
   - `six_star_pool: list[BannerCharacter]` — 6★ characters

4. Implement `generate_banners(plugins: list[CharacterPlugin]) -> dict[str, BannerDefinition]`:
   - **Skip Luna**: `char_id == "luna"` → never in banner pools (only obtainable via 7★ promotion).
   - **Skip non-banner stars**: Exclude characters with `stars > 6` (7★ is promo-only) and `stars < 5` (e.g., slime at rarity 0). Currently `discover_character_plugins()` already filters to 5-7 via `validate_progression_stars`, so only `luna` (7★) needs the explicit skip.
   - **Group by element**: For each elemental banner (`fire`, `ice`, `wind`, `lightning`, `light`, `dark`), include 5★/6★ characters whose damage type matches.
   - **Dual-type characters**: Use `detect_damage_types_for_character()` (see below) to determine which banners a character appears in. A dual-type character (e.g., `lady_fire_and_ice`) appears in ALL matching elemental banners (both fire and ice).
   - **Generic-type characters**: Characters with `damage_type_id == "generic"` are excluded from elemental banners. They only appear in YOLO.
   - **Damage type random**: `damage_type_random == True` characters — no known examples exist currently. If found, document the decision in module docstring (suggest: exclude from elemental, include in YOLO only).
   - **YOLO banner** (`"yolo"`): Pools ALL 5★ and 6★ characters regardless of element or damage type. This is a superset of all elemental banners combined.
   - **Empty pools**: If a banner has empty pools (no characters match that element), produce the `BannerDefinition` with empty lists. The engine handles fallback (prismatic shard).
   - Always produce entries for all 7 `BANNER_IDS`, even if some pools are empty.

5. Implement `detect_damage_types_for_character(plugin: CharacterPlugin) -> list[str]`:
   - If `plugin.is_dual_type` is `True` and `plugin.dual_damage_types` contains two non-empty, non-generic strings, return `[plugin.dual_damage_types[0], plugin.dual_damage_types[1]]`.
   - Otherwise, use `normalize_damage_type_id(plugin.damage_type_id)`:
     - If the result contains ` / ` (space-slash-space, from composite types like `"fire / ice"`), split by ` / ` and return the individual normalized IDs.
     - If single type and not `"generic"`, return `[single_type]`.
     - If `"generic"`, return `[]` (character only appears in YOLO).
   - Strip any empty strings from result.

## Acceptance Criteria
- `uv run python -c "from endless_idler.characters.plugins import discover_character_plugins; from endless_idler.warp.banners import generate_banners; banners = generate_banners(discover_character_plugins()); [print(bid, len(b.five_star_pool), len(b.six_star_pool)) for bid, b in sorted(banners.items())]"` prints 7 lines. Expected approximate distribution:
  - fire: 2–3 five_star, 1 six_star (lady_fire_and_ice)
  - ice: 1 five_star (persona_ice), 1 six_star (lady_fire_and_ice)
  - wind: 3 five_star, 1 six_star (lady_storm)
  - lightning: 3 five_star, 1 six_star (lady_storm)
  - light: 4 five_star, 2 six_star (persona_light_and_dark, ryne)
  - dark: 3 five_star, 1 six_star (persona_light_and_dark)
  - yolo: 17 five_star (all 5★), 4 six_star (all 6★)
- Luna (char_id `"luna"`) does NOT appear in any banner pool (5★ or 6★).
- `lady_fire_and_ice` (6★ fire/ice dual) appears in both `fire` and `ice` banner pools.
- `uv run ruff check endless_idler/warp/banners.py` passes.

## Dependencies
- Task 07 (constants module with `BANNER_IDS` must exist)

## Audit Notes
- PASS: File paths and imports verified. `discover_character_plugins()`, `normalize_damage_type_id()`, and `CharacterPlugin` all confirmed in codebase.
- FIXED: Added reference to `normalize_damage_type_id()` from `combat/damage_types.py` — needed for parsing `"fire / ice"` format correctly.
- FIXED: Dual-type detection clarified. Prefer `plugin.dual_damage_types` tuple (already extracted by metadata) over parsing `damage_type_id`. Fall back to `normalize_damage_type_id` for other cases.
- FIXED: Added expected character counts per banner based on current 22-character pool. These serve as a sanity check.
- FIXED: Clarified that `damage_type_random` has no known current examples — add docstring note for future-proofing.
- INFO: `ryne` (6★, damage_type='light') is the only non-dual 6★. She appears in `light` banner and YOLO.
