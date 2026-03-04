from __future__ import annotations

from importlib import import_module
from random import choice
from typing import Any

from plugins.damage_types._base import DamageTypeBase

ALL_DAMAGE_TYPES = [
    "Light",
    "Dark",
    "Wind",
    "Lightning",
    "Fire",
    "Ice",
]


def _load_cls(name: str) -> type[DamageTypeBase]:
    try:
        module = import_module(f"plugins.damage_types.{name.lower()}")
        return getattr(module, name)
    except Exception:
        module = import_module("plugins.damage_types.generic")
        return module.Generic


def random_damage_type() -> DamageTypeBase:
    return _load_cls(choice(ALL_DAMAGE_TYPES))()


def get_damage_type(source: Any) -> DamageTypeBase:
    """Return a damage type based on the given source.

    The function attempts the following, in order:
    1. If ``source`` has a ``damage_type`` attribute, return it. If that
       attribute is a string, load the corresponding damage type class.
    2. If ``source`` is a string, try to match one of the known damage types
       within it.
    3. Fall back to a random damage type.
    """

    if isinstance(source, DamageTypeBase):
        return source

    if hasattr(source, "damage_type"):
        damage_type = getattr(source, "damage_type")
        if isinstance(damage_type, DamageTypeBase):
            return damage_type
        if isinstance(damage_type, str):
            return load_damage_type(damage_type)

    if isinstance(source, str):
        lowered = source.lower()
        matches = [dtype for dtype in ALL_DAMAGE_TYPES if dtype.lower() in lowered]
        if matches:
            return _load_cls(choice(matches))()

    return random_damage_type()


def load_damage_type(name: str) -> DamageTypeBase:
    # Capitalize the first letter to match class names
    return _load_cls(name.capitalize())()


__all__ = [
    "ALL_DAMAGE_TYPES",
    "get_damage_type",
    "load_damage_type",
    "random_damage_type",
]
