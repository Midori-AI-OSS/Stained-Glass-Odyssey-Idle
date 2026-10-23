"""Base inventory item protocols and reusable dataclass definitions."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from endless_idler.inventory.types import Rarity
from endless_idler.inventory.types import ItemStats
from endless_idler.inventory.types import ItemCategory


_IMAGE_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
)

_INVENTORY_DIR = Path(__file__).resolve().parent
_ITEM_ASSETS_DIR = _INVENTORY_DIR.parent / "assets" / "items"


class ItemBase(Protocol):
    """Protocol implemented by all inventory item definitions."""

    id: str
    name: str
    description: str
    category: ItemCategory
    rarity: Rarity
    stats: ItemStats | None
    image_pool: str

    @property
    def image_dir(self) -> Path:
        """Return the configured image directory for this item."""
        raise NotImplementedError

    def image_paths(self) -> list[Path]:
        """Return sorted image files available for this item."""
        raise NotImplementedError

    def image_path(self) -> Path | None:
        """Return the deterministic primary image path for this item."""
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class Item(ABC):
    """Immutable base item definition used by the registry.

    Item instances are value objects describing catalog entries. Runtime stack
    counts live in save data, so the item definition itself remains immutable.
    """

    id: str = ""
    name: str = ""
    description: str = ""
    category: ItemCategory = ItemCategory.QUEST
    rarity: Rarity = Rarity.COMMON
    stats: ItemStats | None = None
    image_pool: str = "generic"

    @property
    def image_dir(self) -> Path:
        return _ITEM_ASSETS_DIR / self.image_pool

    def image_paths(self) -> list[Path]:
        if not self.image_dir.is_dir():
            return []

        images: list[Path] = []
        for path in self.image_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in _IMAGE_EXTENSIONS:
                continue
            images.append(path)

        images.sort()
        return images

    def image_path(self) -> Path | None:
        images = self.image_paths()
        if not images:
            return None
        return images[0]
