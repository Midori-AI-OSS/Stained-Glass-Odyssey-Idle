from __future__ import annotations

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
