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
class ManaPotion(Item):
    """Placeholder consumable that restores magical energy."""

    id: str = "mana_potion"
    name: str = "Mana Potion"
    description: str = "Placeholder consumable that restores a small amount of mana."
    category: ItemCategory = ItemCategory.CONSUMABLE
    rarity: Rarity = Rarity.COMMON
    image_pool: str = "generic"
