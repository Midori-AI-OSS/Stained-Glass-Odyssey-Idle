"""Lightning shard inventory item definition."""

from __future__ import annotations

from dataclasses import dataclass

from endless_idler.inventory.base import Item
from endless_idler.inventory.registry import register_item
from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemCategory


@register_item
@dataclass(frozen=True, slots=True)
class LightningShard(Item):
    """Elemental shard infused with lightning energy."""

    id: str = "lightning_shard"
    name: str = "Lightning Shard"
    description: str = "A charged shard crackling with lightning-aligned energy."
    category: ItemCategory = ItemCategory.MATERIAL
    rarity: Rarity = Rarity.UNCOMMON
    image_pool: str = "lightning"
