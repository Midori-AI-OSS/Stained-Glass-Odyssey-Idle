"""Blessing plugin registry.

Each blessing lives as its own Python file in `endless_idler/blessings/`.
This module discovers and registers blessing plugins.
"""

from __future__ import annotations

from pathlib import Path

from endless_idler.blessings.loader import load_blessing_module
from endless_idler.blessings.plugin import BlessingPlugin


_BLESSINGS_DIR = Path(__file__).resolve().parent


_discovered_plugins: dict[str, BlessingPlugin] | None = None
_discovered_list: list[BlessingPlugin] | None = None


def discover_blessing_plugins() -> list[BlessingPlugin]:
    """Discover blessing plugins from `endless_idler/blessings/*.py` files."""
    global _discovered_plugins
    global _discovered_list

    if _discovered_list is not None:
        return _discovered_list

    plugins: dict[str, BlessingPlugin] = {}
    for path in sorted(_BLESSINGS_DIR.glob("*.py")):
        if path.name in {"__init__.py", "plugin.py", "registry.py", "loader.py"}:
            continue

        blessing = load_blessing_module(path)
        if blessing is not None:
            plugins[blessing.blessing_id] = blessing

    _discovered_plugins = plugins
    _discovered_list = list(plugins.values())
    return _discovered_list


def get_blessing_by_id(blessing_id: str) -> BlessingPlugin | None:
    """Get a blessing plugin by its ID.

    Args:
        blessing_id: The unique identifier for the blessing

    Returns:
        The BlessingPlugin if found, None otherwise
    """
    global _discovered_plugins

    if _discovered_plugins is None:
        discover_blessing_plugins()

    return _discovered_plugins.get(blessing_id) if _discovered_plugins else None


def get_default_blessing() -> BlessingPlugin:
    """Get the default blessing plugin (Odyssey's Blessing).

    Returns:
        The default BlessingPlugin

    Raises:
        RuntimeError: If no blessings are available
    """
    blessing = get_blessing_by_id("odyssey_blessing")
    if blessing is None:
        raise RuntimeError(
            "No default blessing available. Ensure odyssey_blessing.py exists."
        )
    return blessing


def clear_registry() -> None:
    """Clear the blessing plugin registry cache.

    This is primarily useful for testing to ensure fresh discovery.
    """
    global _discovered_plugins
    global _discovered_list
    _discovered_plugins = None
    _discovered_list = None
