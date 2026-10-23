"""Wind shard inventory item definition."""

from __future__ import annotations

from dataclasses import dataclass

from endless_idler.inventory.base import Item
from endless_idler.inventory.registry import register_item
from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemCategory


@register_item
@dataclass(frozen=True, slots=True)
class WindShard(Item):
    """Elemental shard infused with wind energy."""

    id: str = "wind_shard"
    name: str = "Wind Shard"
    description: str = (
        "A feather-light shard carrying concentrated wind-aligned energy."
    )
    category: ItemCategory = ItemCategory.MATERIAL
    rarity: Rarity = Rarity.EPIC
    image_pool: str = "wind"
