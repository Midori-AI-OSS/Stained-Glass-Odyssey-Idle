"""Ice shard inventory item definition."""

from __future__ import annotations

from dataclasses import dataclass

from endless_idler.inventory.base import Item
from endless_idler.inventory.registry import register_item
from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemCategory


@register_item
@dataclass(frozen=True, slots=True)
class IceShard(Item):
    """Elemental shard infused with ice energy."""

    id: str = "ice_shard"
    name: str = "Ice Shard"
    description: str = "A crystalline shard that condenses concentrated ice-aligned energy."
    category: ItemCategory = ItemCategory.MATERIAL
    rarity: Rarity = Rarity.UNCOMMON
    image_pool: str = "ice"
