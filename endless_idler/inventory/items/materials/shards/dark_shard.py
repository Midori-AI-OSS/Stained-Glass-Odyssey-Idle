"""Dark shard inventory item definition."""

from __future__ import annotations

from dataclasses import dataclass

from endless_idler.inventory.base import Item
from endless_idler.inventory.registry import register_item
from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemCategory


@register_item
@dataclass(frozen=True, slots=True)
class DarkShard(Item):
    """Elemental shard infused with dark energy."""

    id: str = "dark_shard"
    name: str = "Dark Shard"
    description: str = "A shadowed shard that binds dense dark-aligned energy."
    category: ItemCategory = ItemCategory.MATERIAL
    rarity: Rarity = Rarity.EPIC
    image_pool: str = "dark"
