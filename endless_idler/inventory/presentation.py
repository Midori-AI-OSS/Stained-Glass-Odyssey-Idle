"""Inventory presentation helpers for rarity-driven UI metadata."""

from __future__ import annotations

from endless_idler.inventory.registry import get_item
from endless_idler.inventory.types import Rarity


_RARITY_STARS: dict[Rarity, int] = {
    Rarity.COMMON: 1,
    Rarity.UNCOMMON: 2,
    Rarity.RARE: 3,
    Rarity.EPIC: 4,
    Rarity.LEGENDARY: 5,
}


def resolve_item_rarity_stars(item_id: str) -> int:
    """Resolve inventory rarity stars from the registered item catalog."""

    item = get_item(item_id)
    if item is None:
        return 1
    return _RARITY_STARS.get(item.rarity, 1)
