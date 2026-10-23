"""Inventory presentation helpers for inventory UI metadata."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from endless_idler.inventory.registry import get_item
from endless_idler.inventory.types import Rarity


_RARITY_STARS: dict[Rarity, int] = {
    Rarity.COMMON: 1,
    Rarity.UNCOMMON: 2,
    Rarity.RARE: 3,
    Rarity.EPIC: 4,
    Rarity.LEGENDARY: 5,
}

_ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets" / "items"


@dataclass(frozen=True, slots=True)
class OwnedInventoryItem:
    item_id: str
    name: str
    flavor_text: str
    category_label: str
    rarity_label: str
    quantity: int
    rarity_stars: int
    icon_path: Path


def resolve_item_rarity_stars(item_id: str) -> int:
    """Resolve inventory rarity stars from the registered item catalog."""

    item = get_item(item_id)
    if item is None:
        return 1
    return _RARITY_STARS.get(item.rarity, 1)


def build_owned_inventory_items(
    inventory: Mapping[str, int],
) -> tuple[OwnedInventoryItem, ...]:
    """Build deterministic owned inventory rows with strict icon mappings."""

    items: list[OwnedInventoryItem] = []
    owned_ids = sorted(
        item_id
        for item_id, quantity in inventory.items()
        if int(quantity) > 0 and item_id.strip()
    )
    for item_id in owned_ids:
        quantity = int(inventory[item_id])
        item = get_item(item_id)
        if item is None:
            raise ValueError(f"Missing inventory item definition for {item_id!r}.")

        icon_path = item.image_path()
        if icon_path is None:
            raise ValueError(
                f"Missing inventory icon mapping for {item_id!r} (pool={item.image_pool!r})."
            )
        if not icon_path.is_relative_to(_ASSET_ROOT):
            raise ValueError(
                f"Invalid inventory icon path for {item_id!r}: {icon_path}"
            )

        items.append(
            OwnedInventoryItem(
                item_id=item_id,
                name=item.name,
                flavor_text=item.description,
                category_label=item.category.value.upper(),
                rarity_label=item.rarity.value.upper(),
                quantity=quantity,
                rarity_stars=_RARITY_STARS.get(item.rarity, 1),
                icon_path=icon_path,
            )
        )

    items.sort(
        key=lambda owned: (
            -owned.rarity_stars,
            owned.name.casefold(),
            owned.item_id,
        )
    )
    return tuple(items)
