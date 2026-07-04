"""PLACEHOLDER ITEM - DO NOT USE IN GAME YET.

This placeholder exists only to validate the inventory plugin system.
It is planned to be removed or replaced before live gameplay uses items.
"""

from __future__ import annotations

from dataclasses import dataclass

from endless_idler.inventory.base import Item
from endless_idler.inventory.registry import register_item
from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemCategory


@register_item
@dataclass(frozen=True, slots=True)
class WisdomStone(Item):
    """Placeholder stone material associated with magical insight."""

    id: str = "wisdom_stone"
    name: str = "Wisdom Stone"
    description: str = "Placeholder stone material associated with magical insight."
    category: ItemCategory = ItemCategory.MATERIAL
    rarity: Rarity = Rarity.RARE
    image_pool: str = "light"
