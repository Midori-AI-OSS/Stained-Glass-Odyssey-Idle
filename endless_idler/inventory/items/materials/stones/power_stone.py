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
class PowerStone(Item):
    """Placeholder stone material associated with physical strength."""

    id: str = "power_stone"
    name: str = "Power Stone"
    description: str = "Placeholder stone material associated with raw strength."
    category: ItemCategory = ItemCategory.MATERIAL
    rarity: Rarity = Rarity.RARE
    image_pool: str = "fire"
