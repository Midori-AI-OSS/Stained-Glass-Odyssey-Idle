"""Passive plugin system.

Each passive is a Python file in `endless_idler/passives/` that defines
a `PassivePlugin` instance.
"""

from __future__ import annotations

from endless_idler.passives.plugin import PassivePlugin
from endless_idler.passives.runtime import PassiveTickContext
from endless_idler.passives.registry import discover_passive_plugins
from endless_idler.passives.registry import get_passive_by_id


__all__ = [
    "PassivePlugin",
    "PassiveTickContext",
    "discover_passive_plugins",
    "get_passive_by_id",
]
