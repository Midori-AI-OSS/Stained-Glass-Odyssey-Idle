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
class RadiantShield(Item):
    """Placeholder equipment item that grants defensive bonuses."""

    id: str = "radiant_shield"
    name: str = "Radiant Shield"
    description: str = "Placeholder radiant shield with defensive stat bonuses."
    category: ItemCategory = ItemCategory.EQUIPMENT
    rarity: Rarity = Rarity.RARE
    stats: ItemStats = field(default_factory=lambda: ItemStats(defense=12, magic=3))
    image_pool: str = "light"
