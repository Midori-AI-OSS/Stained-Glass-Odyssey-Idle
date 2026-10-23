"""Inventory item registration and lookup helpers."""

from __future__ import annotations

import importlib

from collections.abc import Iterable
from pkgutil import walk_packages
from typing import TypeVar
from typing import cast

from endless_idler.inventory.base import Item


ItemType = TypeVar("ItemType", bound=Item)

_ITEM_REGISTRY: dict[str, type[Item]] = {}
_item_plugins_loaded = False


def register_item(item_class: type[ItemType]) -> type[ItemType]:
    """Register an inventory item class by its declared ID."""

    item_id = item_class().id.strip()
    if not item_id:
        raise ValueError(
            f"Item class {item_class.__name__} must define a non-empty id."
        )
    existing = _ITEM_REGISTRY.get(item_id)
    if existing is not None and existing is not item_class:
        raise ValueError(f"Duplicate item id: {item_id}")
    _ITEM_REGISTRY[item_id] = item_class
    return item_class


def load_item_plugins() -> None:
    """Discover and import all inventory item plugin modules."""

    global _item_plugins_loaded

    if _item_plugins_loaded:
        return

    package = importlib.import_module("endless_idler.inventory.items")
    package_paths = getattr(package, "__path__", None)
    if package_paths is None:
        _item_plugins_loaded = True
        return

    search_paths = cast(Iterable[str], package_paths)
    for module_info in walk_packages(search_paths, prefix=f"{package.__name__}."):
        if module_info.ispkg:
            continue
        _ = importlib.import_module(module_info.name)

    _item_plugins_loaded = True


def get_all_items() -> dict[str, type[Item]]:
    """Return a copy of the full registered item catalog."""

    load_item_plugins()
    return dict(_ITEM_REGISTRY)


def get_item(item_id: str) -> Item | None:
    """Instantiate a registered item by ID."""

    load_item_plugins()
    item_class = _ITEM_REGISTRY.get(item_id)
    if item_class is None:
        return None
    return item_class()


def get_item_ids() -> set[str]:
    """Return the set of registered item IDs for save validation."""

    load_item_plugins()
    return set(_ITEM_REGISTRY)
