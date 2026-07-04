from __future__ import annotations

from endless_idler.inventory import get_all_items
from endless_idler.inventory import get_item
from endless_idler.inventory.items.equipment.radiant_shield import RadiantShield
from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemCategory


def test_placeholder_item_catalog_uses_expected_folders() -> None:
    expected_item_ids = {
        "experience_boost",
        "health_potion",
        "mana_potion",
        "essence_drop",
        "glass_fragment",
        "power_stone",
        "wisdom_stone",
        "dark_shard",
        "fire_shard",
        "ice_shard",
        "light_shard",
        "lightning_shard",
        "radiant_shield",
        "stained_sword",
        "wind_shard",
    }

    assert set(get_all_items()) == expected_item_ids


def test_items_expose_required_typed_fields() -> None:
    sword = get_item("stained_sword")
    potion = get_item("health_potion")

    assert sword is not None
    assert potion is not None
    assert sword.category is ItemCategory.EQUIPMENT
    assert sword.rarity is Rarity.RARE
    assert potion.category is ItemCategory.CONSUMABLE
    assert potion.rarity is Rarity.COMMON
    assert sword.id == "stained_sword"
    assert potion.id == "health_potion"


def test_equipment_items_expose_stats_payload() -> None:
    shield = get_item("radiant_shield")

    assert shield is not None
    assert isinstance(shield, RadiantShield)
    assert shield.stats is not None
    assert shield.stats.defense == 12
    assert shield.stats.magic == 3


def test_items_expose_deterministic_image_paths() -> None:
    fire_shard = get_item("fire_shard")
    shield = get_item("radiant_shield")

    assert fire_shard is not None
    assert shield is not None
    assert fire_shard.image_pool == "fire"
    assert shield.image_pool == "light"

    fire_image = fire_shard.image_path()
    shield_image = shield.image_path()

    assert fire_image is not None
    assert shield_image is not None
    assert fire_image.name == "fire1.png"
    assert shield_image.name == "light1.png"
