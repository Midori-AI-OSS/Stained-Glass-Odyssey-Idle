"""Banner auto-generation logic.

Scans character plugins and groups them by damage type and star rating
to produce banner rosters for each elemental pool and the YOLO pool.

Future-proofing note:
    Characters with ``damage_type_random == True`` are excluded from elemental
    banners and appear only in the YOLO pool. No such characters exist in the
    current roster, so this codepath is untested.
"""

from __future__ import annotations

from dataclasses import dataclass

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.combat.damage_types import normalize_damage_type_id
from endless_idler.warp.constants import BANNER_IDS


@dataclass(frozen=True, slots=True)
class BannerCharacter:
    char_id: str
    display_name: str
    stars: int
    damage_type_id: str
    is_dual_type: bool
    dual_damage_types: tuple[str, str]


@dataclass(frozen=True, slots=True)
class BannerDefinition:
    banner_id: str
    five_star_pool: list[BannerCharacter]
    six_star_pool: list[BannerCharacter]


def detect_damage_types_for_character(
    plugin: CharacterPlugin,
) -> list[str]:
    """Return the list of damage-type IDs a character contributes to.

    - **Dual-type characters** (``is_dual_type`` with two non-empty,
      non-``"generic"`` entries in ``dual_damage_types``): returned as-is.
    - **Composite damage type IDs** (e.g. ``"fire / ice"``): split on
      ``" / "`` and returned as separate entries.
    - **Single damage type** (non-``"generic"``): returned as a one-element
      list.
    - **Generic / empty**: returned as an empty list (character only appears
      in the YOLO banner).
    """

    if plugin.is_dual_type:
        t0 = plugin.dual_damage_types[0].strip()
        t1 = plugin.dual_damage_types[1].strip()
        if t0 and t1 and t0 != "generic" and t1 != "generic":
            return [t0, t1]

    normalized = normalize_damage_type_id(plugin.damage_type_id)

    if " / " in normalized:
        parts = [p.strip() for p in normalized.split(" / ") if p.strip()]
        return parts

    if normalized and normalized != "generic":
        return [normalized]

    return []


def _to_banner_character(plugin: CharacterPlugin) -> BannerCharacter:
    return BannerCharacter(
        char_id=plugin.char_id,
        display_name=plugin.display_name,
        stars=plugin.stars,
        damage_type_id=plugin.damage_type_id,
        is_dual_type=plugin.is_dual_type,
        dual_damage_types=plugin.dual_damage_types,
    )


def generate_banners(
    plugins: list[CharacterPlugin],
) -> dict[str, BannerDefinition]:
    """Build banner rosters from a list of character plugins.

    Returns a dict keyed by banner ID (matching ``BANNER_IDS``), each
    containing a ``BannerDefinition`` with ``five_star_pool`` and
    ``six_star_pool`` lists.
    """

    # Filter to banner-eligible characters (5★ and 6★ only)
    eligible_5: list[CharacterPlugin] = []
    eligible_6: list[CharacterPlugin] = []

    for plugin in plugins:
        if plugin.char_id == "luna":
            continue
        if plugin.stars > 6 or plugin.stars < 5:
            continue
        if plugin.stars == 5:
            eligible_5.append(plugin)
        elif plugin.stars == 6:
            eligible_6.append(plugin)

    # Build the YOLO banner first (superset of all)
    yolo_5 = [_to_banner_character(p) for p in eligible_5]
    yolo_6 = [_to_banner_character(p) for p in eligible_6]

    # Pre-compute damage types for each character
    damage_map_5: dict[str, list[str]] = {
        p.char_id: detect_damage_types_for_character(p) for p in eligible_5
    }
    damage_map_6: dict[str, list[str]] = {
        p.char_id: detect_damage_types_for_character(p) for p in eligible_6
    }

    def _pool_for_element(
        element: str,
        pool: list[CharacterPlugin],
        damage_map: dict[str, list[str]],
    ) -> list[BannerCharacter]:
        result: list[BannerCharacter] = []
        for p in pool:
            types = damage_map.get(p.char_id, [])
            if element in types:
                result.append(_to_banner_character(p))
        return result

    banners: dict[str, BannerDefinition] = {}

    for bid in BANNER_IDS:
        if bid == "yolo":
            banners[bid] = BannerDefinition(
                banner_id=bid,
                five_star_pool=yolo_5,
                six_star_pool=yolo_6,
            )
        else:
            banners[bid] = BannerDefinition(
                banner_id=bid,
                five_star_pool=_pool_for_element(bid, eligible_5, damage_map_5),
                six_star_pool=_pool_for_element(bid, eligible_6, damage_map_6),
            )

    return banners
