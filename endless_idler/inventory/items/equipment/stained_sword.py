"""PLACEHOLDER ITEM - DO NOT USE IN GAME YET.

This placeholder exists only to validate the inventory plugin system.
It is planned to be removed or replaced before live gameplay uses items.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from endless_idler.inventory.base import Item
from endless_idler.inventory.registry import register_item
from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemStats
from endless_idler.inventory.types import ItemCategory


@register_item
@dataclass(frozen=True, slots=True)
class StainedSword(Item):
    """Placeholder equipment item that grants offensive bonuses."""

    id: str = "stained_sword"
    name: str = "Stained Sword"
    description: str = "Placeholder stained glass sword with offensive stat bonuses."
    category: ItemCategory = ItemCategory.EQUIPMENT
    rarity: Rarity = Rarity.RARE
    stats: ItemStats = field(default_factory=lambda: ItemStats(attack=10, speed=2))
    image_pool: str = "lightning"
