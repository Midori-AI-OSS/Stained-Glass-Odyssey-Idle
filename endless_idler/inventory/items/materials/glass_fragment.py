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
class GlassFragment(Item):
    """Placeholder crafting material formed from stained glass shards."""

    id: str = "glass_fragment"
    name: str = "Glass Fragment"
    description: str = "Placeholder crafting material carved from broken stained glass."
    category: ItemCategory = ItemCategory.MATERIAL
    rarity: Rarity = Rarity.COMMON
    image_pool: str = "generic"
