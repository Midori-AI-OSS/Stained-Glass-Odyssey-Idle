"""Blessing plugin system.

A blessing provides passive idle bonuses that accumulate over time.
Each blessing is a Python file in `endless_idler/blessings/` that defines
a BlessingPlugin instance.
"""

from __future__ import annotations

from endless_idler.blessings.plugin import BlessingPlugin
from endless_idler.blessings.registry import discover_blessing_plugins
from endless_idler.blessings.registry import get_blessing_by_id
from endless_idler.blessings.registry import get_default_blessing


__all__ = [
    "BlessingPlugin",
    "discover_blessing_plugins",
    "get_blessing_by_id",
    "get_default_blessing",
]
