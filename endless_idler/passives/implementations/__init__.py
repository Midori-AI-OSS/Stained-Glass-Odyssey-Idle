"""Passive ability implementations.

This package contains concrete implementations of passive abilities
for various characters in the game.
"""

from endless_idler.passives.implementations.lady_darkness_eclipsing_veil import (
    LadyDarknessEclipsingVeil,
)
from endless_idler.passives.implementations.lady_light_radiant_aegis import (
    LadyLightRadiantAegis,
)
from endless_idler.passives.implementations.trinity_synergy import (
    TrinitySynergy,
)

__all__ = [
    "LadyDarknessEclipsingVeil",
    "LadyLightRadiantAegis",
    "TrinitySynergy",
]
