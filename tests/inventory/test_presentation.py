from __future__ import annotations

from pathlib import Path

import pytest

from endless_idler.inventory.presentation import build_owned_inventory_items
from endless_idler.inventory.presentation import resolve_item_rarity_stars


def test_shards_resolve_to_four_star_rarity_for_inventory() -> None:
    shard_ids = (
        "dark_shard",
        "fire_shard",
        "ice_shard",
        "light_shard",
        "lightning_shard",
        "wind_shard",
    )

    for item_id in shard_ids:
        assert resolve_item_rarity_stars(item_id) == 4


def test_owned_inventory_items_include_only_positive_quantities() -> None:
    items = build_owned_inventory_items(
        {
            "fire_shard": 2,
            "ice_shard": 0,
            "light_shard": -1,
            "wind_shard": 3,
        }
    )

    assert [item.item_id for item in items] == ["fire_shard", "wind_shard"]
    assert [item.quantity for item in items] == [2, 3]
    assert all(item.icon_path.is_file() for item in items)


def test_owned_inventory_items_include_labels_for_ui_hierarchy() -> None:
    items = build_owned_inventory_items({"fire_shard": 2})

    assert len(items) == 1
    item = items[0]
    assert item.name == "Fire Shard"
    assert (
        item.flavor_text
        == "A refined shard that channels volatile fire-aligned energy."
    )
    assert item.category_label == "MATERIAL"
    assert item.rarity_label == "EPIC"


def test_owned_inventory_items_fail_without_icon_mapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _BrokenIconItem:
        rarity: str = "common"
        image_pool: str = "missing_pool"

        @staticmethod
        def image_path() -> Path | None:
            return None

    monkeypatch.setattr(
        "endless_idler.inventory.presentation.get_item",
        lambda item_id: _BrokenIconItem() if str(item_id) == "broken_item" else None,
    )

    with pytest.raises(ValueError, match="Missing inventory icon mapping"):
        _ = build_owned_inventory_items({"broken_item": 1})
