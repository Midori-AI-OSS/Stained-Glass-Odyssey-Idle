"""Tests for warp banner auto-generation."""

from __future__ import annotations

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.warp.banners import detect_damage_types_for_character
from endless_idler.warp.banners import generate_banners
from endless_idler.warp.constants import BANNER_IDS


def _make_plugin(
    char_id: str = "test_char",
    stars: int = 5,
    damage_type_id: str = "fire",
    is_dual_type: bool = False,
    dual_damage_types: tuple[str, str] = ("", ""),
) -> CharacterPlugin:
    """Helper to build a CharacterPlugin with minimal config."""
    return CharacterPlugin(
        char_id=char_id,
        display_name=char_id.replace("_", " ").title(),
        stars=stars,
        damage_type_id=damage_type_id,
        damage_type_random=False,
        is_dual_type=is_dual_type,
        dual_damage_types=dual_damage_types,
    )


# ------------------------------------------------------------------
# detect_damage_types_for_character
# ------------------------------------------------------------------


def test_detect_single_elemental() -> None:
    """A normal fire character reports just ``["fire"]``."""
    plugin = _make_plugin(char_id="ally", damage_type_id="fire")
    assert detect_damage_types_for_character(plugin) == ["fire"]


def test_detect_generic_returns_empty() -> None:
    """Generic damage type returns an empty list (YOLO only)."""
    plugin = _make_plugin(char_id="generic_guy", damage_type_id="generic")
    assert detect_damage_types_for_character(plugin) == []


def test_detect_dual_type() -> None:
    """A dual-type character reports both damage types."""
    plugin = _make_plugin(
        char_id="lady_fire_and_ice",
        stars=6,
        is_dual_type=True,
        dual_damage_types=("fire", "ice"),
    )
    types = detect_damage_types_for_character(plugin)
    assert sorted(types) == ["fire", "ice"]


def test_detect_dual_type_with_generic_falls_through() -> None:
    """Dual-type with a generic component falls through to normal
    ``damage_type_id`` handling."""
    plugin = _make_plugin(
        char_id="half_generic",
        damage_type_id="fire",
        is_dual_type=True,
        dual_damage_types=("fire", "generic"),
    )
    # The dual-type check fails (generic in pair), so it falls through
    # to the standard damage_type_id check → "fire"
    assert detect_damage_types_for_character(plugin) == ["fire"]

    # With generic damage_type_id, neither path assigns → empty
    plugin2 = _make_plugin(
        char_id="fully_generic",
        damage_type_id="generic",
        is_dual_type=True,
        dual_damage_types=("fire", "generic"),
    )
    assert detect_damage_types_for_character(plugin2) == []


# ------------------------------------------------------------------
# generate_banners
# ------------------------------------------------------------------


def test_generate_produces_all_seven_banner_ids() -> None:
    """``generate_banners()`` returns every key in ``BANNER_IDS``."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="ally", damage_type_id="fire"),
    ]
    banners = generate_banners(plugins)
    assert sorted(banners.keys()) == sorted(BANNER_IDS)


def test_luna_excluded() -> None:
    """Luna (char_id ``\"luna\"``) must not appear in any banner pool."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="ally", damage_type_id="fire"),
        _make_plugin(char_id="luna", stars=7, damage_type_id="generic"),
    ]
    banners = generate_banners(plugins)
    for bid in BANNER_IDS:
        banner = banners[bid]
        five_ids = [c.char_id for c in banner.five_star_pool]
        six_ids = [c.char_id for c in banner.six_star_pool]
        assert "luna" not in five_ids, f"Luna found in {bid} 5★ pool"
        assert "luna" not in six_ids, f"Luna found in {bid} 6★ pool"


def test_dual_type_placement() -> None:
    """Dual fire/ice character appears in both fire and ice banners,
    but not in other elemental banners."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="ally", damage_type_id="fire"),
        _make_plugin(
            char_id="lady_fire_and_ice",
            stars=6,
            is_dual_type=True,
            dual_damage_types=("fire", "ice"),
        ),
    ]
    banners = generate_banners(plugins)

    # Should appear in fire and ice 6★ pools
    fire_six = [c.char_id for c in banners["fire"].six_star_pool]
    ice_six = [c.char_id for c in banners["ice"].six_star_pool]
    assert "lady_fire_and_ice" in fire_six
    assert "lady_fire_and_ice" in ice_six

    # Should NOT appear in other elemental 6★ pools
    for bid in ("wind", "lightning", "light", "dark"):
        six_ids = [c.char_id for c in banners[bid].six_star_pool]
        assert "lady_fire_and_ice" not in six_ids, (
            f"lady_fire_and_ice found in {bid} 6★ pool"
        )


def test_yolo_pool_is_superset() -> None:
    """YOLO banner's 5★ and 6★ pools contain all characters
    from all elemental banners combined."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="fire_guy", damage_type_id="fire"),
        _make_plugin(char_id="ice_guy", damage_type_id="ice"),
        _make_plugin(char_id="wind_girl", damage_type_id="wind"),
        _make_plugin(char_id="lightning_girl", damage_type_id="lightning"),
        _make_plugin(char_id="light_person", damage_type_id="light"),
        _make_plugin(char_id="dark_person", damage_type_id="dark"),
    ]
    banners = generate_banners(plugins)

    yolo_5 = {c.char_id for c in banners["yolo"].five_star_pool}
    elemental_5: set[str] = set()
    for bid in ("fire", "ice", "wind", "lightning", "light", "dark"):
        elemental_5.update(c.char_id for c in banners[bid].five_star_pool)

    assert yolo_5 == elemental_5, "YOLO 5★ pool should be the union of all elemental 5★ pools"


def test_non_matching_element_produces_empty_pools() -> None:
    """A banner whose element has no matching characters produces
    empty pools (not missing keys)."""
    # Only fire characters, no ice
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="fire_guy", damage_type_id="fire"),
    ]
    banners = generate_banners(plugins)

    # Ice banner should have empty pools (but exist)
    ice = banners["ice"]
    assert ice.five_star_pool == []
    assert ice.six_star_pool == []


def test_generic_characters_excluded_from_elemental() -> None:
    """Characters with ``damage_type_id == \"generic\"`` appear only
    in the YOLO banner, not in elemental banners."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="generic_guy", damage_type_id="generic"),
        _make_plugin(char_id="fire_guy", damage_type_id="fire"),
    ]
    banners = generate_banners(plugins)

    # YOLO should have the generic character
    yolo_5 = {c.char_id for c in banners["yolo"].five_star_pool}
    assert "generic_guy" in yolo_5

    # No elemental banner should have generic_guy
    for bid in ("fire", "ice", "wind", "lightning", "light", "dark"):
        five_ids = {c.char_id for c in banners[bid].five_star_pool}
        assert "generic_guy" not in five_ids, (
            f"generic_guy found in {bid} 5★ pool"
        )


def test_yolo_pool_contains_all_characters() -> None:
    """YOLO banner pools contain every eligible character (5★/6★, non-Luna)."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="char_a", damage_type_id="fire"),
        _make_plugin(char_id="char_b", stars=6, damage_type_id="ice"),
        _make_plugin(char_id="generic_guy", damage_type_id="generic"),
        _make_plugin(char_id="luna", stars=7, damage_type_id="generic"),
    ]
    banners = generate_banners(plugins)

    yolo_5 = {c.char_id for c in banners["yolo"].five_star_pool}
    yolo_6 = {c.char_id for c in banners["yolo"].six_star_pool}

    assert "char_a" in yolo_5
    assert "char_b" in yolo_6
    assert "generic_guy" in yolo_5
    assert "luna" not in yolo_5
    assert "luna" not in yolo_6


def test_banner_character_dataclass_fields() -> None:
    """BannerCharacter contains expected fields from the plugin."""
    plugin = _make_plugin(
        char_id="test_me",
        stars=5,
        damage_type_id="lightning",
        is_dual_type=False,
    )
    banners = generate_banners([plugin])
    five_pool = banners["yolo"].five_star_pool
    assert len(five_pool) == 1
    bc = five_pool[0]
    assert bc.char_id == "test_me"
    assert bc.stars == 5
    assert bc.damage_type_id == "lightning"
    assert bc.is_dual_type is False
    assert bc.dual_damage_types == ("", "")


def test_generate_banners_returns_bannerdefinition() -> None:
    """Each banner entry is a BannerDefinition with correct banner_id."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="fire_guy", damage_type_id="fire"),
    ]
    banners = generate_banners(plugins)
    for bid in BANNER_IDS:
        bd = banners[bid]
        assert bd.banner_id == bid
        assert hasattr(bd, "five_star_pool")
        assert hasattr(bd, "six_star_pool")


def test_ignores_below_5_star() -> None:
    """Characters below 5★ are excluded from all banner pools."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="weakling", stars=3, damage_type_id="fire"),
        _make_plugin(char_id="decent", stars=4, damage_type_id="fire"),
    ]
    banners = generate_banners(plugins)
    for bid in BANNER_IDS:
        assert banners[bid].five_star_pool == []
        assert banners[bid].six_star_pool == []


def test_ignores_above_6_star() -> None:
    """Characters above 6★ (like Luna at 7★) are excluded."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="too_strong", stars=8, damage_type_id="fire"),
        _make_plugin(char_id="luna", stars=7, damage_type_id="generic"),
    ]
    banners = generate_banners(plugins)
    for bid in BANNER_IDS:
        assert banners[bid].five_star_pool == []
        assert banners[bid].six_star_pool == []


def test_5_and_6_star_separate_pools() -> None:
    """5★ characters go into five_star_pool, 6★ into six_star_pool."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(char_id="five_char", stars=5, damage_type_id="fire"),
        _make_plugin(char_id="six_char", stars=6, damage_type_id="fire"),
    ]
    banners = generate_banners(plugins)
    yolo = banners["yolo"]
    assert [c.char_id for c in yolo.five_star_pool] == ["five_char"]
    assert [c.char_id for c in yolo.six_star_pool] == ["six_char"]


def test_dual_type_6_star_in_yolo() -> None:
    """Dual-type 6★ characters appear in YOLO 6★ pool."""
    plugins: list[CharacterPlugin] = [
        _make_plugin(
            char_id="dual_girl",
            stars=6,
            is_dual_type=True,
            dual_damage_types=("fire", "ice"),
        ),
    ]
    banners = generate_banners(plugins)
    yolo_6 = {c.char_id for c in banners["yolo"].six_star_pool}
    assert "dual_girl" in yolo_6
