from __future__ import annotations

from dataclasses import FrozenInstanceError
from dataclasses import dataclass

import pytest

import endless_idler.inventory.base as inventory_base_module

from endless_idler.inventory import get_all_items
from endless_idler.inventory import get_item
from endless_idler.inventory import register_item
from endless_idler.inventory.base import Item
from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemCategory


def test_registry_returns_registered_placeholder_items() -> None:
    items = get_all_items()

    assert "health_potion" in items
    assert "power_stone" in items
    assert "light_shard" in items
    assert "radiant_shield" in items


def test_get_item_returns_new_item_instance() -> None:
    first = get_item("health_potion")
    second = get_item("health_potion")

    assert first is not None
    assert second is not None
    assert first.id == "health_potion"
    assert second.id == "health_potion"
    assert first is not second


def test_register_item_rejects_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="Duplicate item id: health_potion"):

        @dataclass(frozen=True, slots=True)
        class DuplicateHealthPotion(Item):
            id: str = "health_potion"
            name: str = "Duplicate Health Potion"
            description: str = "Invalid duplicate item for registry validation."
            category: ItemCategory = ItemCategory.CONSUMABLE
            rarity: Rarity = Rarity.COMMON

        _ = register_item(DuplicateHealthPotion)


def test_item_instances_are_immutable() -> None:
    item = get_item("radiant_shield")

    assert item is not None
    with pytest.raises(FrozenInstanceError):
        setattr(item, "name", "Changed")


def test_image_paths_are_sorted_and_non_image_files_are_ignored(
    tmp_path, monkeypatch
) -> None:
    image_root = tmp_path / "items"
    image_dir = image_root / "test_pool"
    image_dir.mkdir(parents=True)
    _ = (image_dir / "zeta.png").write_bytes(b"png")
    _ = (image_dir / "alpha.jpg").write_bytes(b"jpg")
    _ = (image_dir / "notes.txt").write_text("ignore", encoding="utf-8")

    monkeypatch.setattr(inventory_base_module, "_ITEM_ASSETS_DIR", image_root)

    @dataclass(frozen=True, slots=True)
    class TestItem(Item):
        id: str = "test_item_for_images"
        image_pool: str = "test_pool"

    item = TestItem()
    images = item.image_paths()

    assert [path.name for path in images] == ["alpha.jpg", "zeta.png"]
