"""Inventory type definitions used by item plugins and save validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ItemCategory(StrEnum):
    """High-level classification for inventory items."""

    CONSUMABLE = "consumable"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    QUEST = "quest"


class Rarity(StrEnum):
    """Rarity tiers used by the inventory catalog."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass(frozen=True, slots=True)
class ItemStats:
    """Optional stat bonuses granted by equipment items."""

    attack: int = 0
    defense: int = 0
    magic: int = 0
    speed: int = 0
