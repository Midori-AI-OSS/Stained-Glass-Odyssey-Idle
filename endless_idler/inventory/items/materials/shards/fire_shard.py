"""Fire shard inventory item definition."""

from __future__ import annotations

from dataclasses import dataclass

from endless_idler.inventory.base import Item
from endless_idler.inventory.registry import register_item
from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemCategory


@register_item
@dataclass(frozen=True, slots=True)
class FireShard(Item):
    """Elemental shard infused with fire energy."""

    id: str = "fire_shard"
    name: str = "Fire Shard"
    description: str = "A refined shard that channels volatile fire-aligned energy."
    category: ItemCategory = ItemCategory.MATERIAL
    rarity: Rarity = Rarity.UNCOMMON
    image_pool: str = "fire"
