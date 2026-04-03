"""Passive plugin registry.

Each passive lives as its own Python file in `endless_idler/passives/`.
This module discovers and registers passive plugins.
"""

from __future__ import annotations

from pathlib import Path

from endless_idler.passives.loader import load_passive_module
from endless_idler.passives.plugin import PassivePlugin


_PASSIVES_DIR = Path(__file__).resolve().parent
_EXCLUDED_MODULE_NAMES = frozenset(
    {
        "__init__.py",
        "plugin.py",
        "loader.py",
        "registry.py",
        "base.py",
        "triggers.py",
        "execution.py",
    }
)

_discovered_plugins: dict[str, PassivePlugin] | None = None
_discovered_list: list[PassivePlugin] | None = None


def discover_passive_plugins() -> list[PassivePlugin]:
    """Discover passive plugins from `endless_idler/passives/*.py` files."""
    global _discovered_plugins
    global _discovered_list

    if _discovered_list is not None:
        return _discovered_list

    plugins: dict[str, PassivePlugin] = {}
    sources_by_id: dict[str, str] = {}
    for path in sorted(_PASSIVES_DIR.glob("*.py")):
        if path.name in _EXCLUDED_MODULE_NAMES or path.stem.startswith("_"):
            continue

        passive = load_passive_module(path)
        if passive is None:
            continue

        existing_source = sources_by_id.get(passive.passive_id)
        if existing_source is not None:
            raise ValueError(
                f"Duplicate passive id '{passive.passive_id}' in "
                + f"{existing_source} and {path.name}."
            )

        sources_by_id[passive.passive_id] = path.name
        plugins[passive.passive_id] = passive

    _discovered_plugins = plugins
    _discovered_list = list(plugins.values())
    return _discovered_list


def get_passive_by_id(passive_id: str) -> PassivePlugin | None:
    """Get a passive plugin by its ID."""
    global _discovered_plugins

    if _discovered_plugins is None:
        discover_passive_plugins()

    return _discovered_plugins.get(passive_id) if _discovered_plugins else None


def clear_registry() -> None:
    """Clear the passive plugin registry cache."""
    global _discovered_plugins
    global _discovered_list
    _discovered_plugins = None
    _discovered_list = None
