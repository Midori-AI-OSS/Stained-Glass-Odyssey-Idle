"""Light shard inventory item definition."""

from __future__ import annotations

from dataclasses import dataclass

from endless_idler.inventory.base import Item
from endless_idler.inventory.registry import register_item
from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemCategory


@register_item
@dataclass(frozen=True, slots=True)
class LightShard(Item):
    """Elemental shard infused with radiant light energy."""

    id: str = "light_shard"
    name: str = "Light Shard"
    description: str = "A radiant shard that stores focused light-aligned energy."
    category: ItemCategory = ItemCategory.MATERIAL
    rarity: Rarity = Rarity.EPIC
    image_pool: str = "light"
