"""Inventory package with plugin-style item registration and typed exports."""

from __future__ import annotations

from endless_idler.inventory.base import Item
from endless_idler.inventory.base import ItemBase
from endless_idler.inventory.registry import get_all_items
from endless_idler.inventory.registry import get_item
from endless_idler.inventory.registry import get_item_ids
from endless_idler.inventory.registry import load_item_plugins
from endless_idler.inventory.registry import register_item
from endless_idler.inventory.types import ItemCategory
from endless_idler.inventory.types import ItemStats
from endless_idler.inventory.types import Rarity

__all__ = [
    "Item",
    "ItemBase",
    "ItemCategory",
    "ItemStats",
    "Rarity",
    "get_all_items",
    "get_item",
    "get_item_ids",
    "load_item_plugins",
    "register_item",
]
