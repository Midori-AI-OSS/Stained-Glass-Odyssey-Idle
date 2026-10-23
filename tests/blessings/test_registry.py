"""Tests for blessing registry."""

from __future__ import annotations

from endless_idler.blessings import discover_blessing_plugins
from endless_idler.blessings import get_blessing_by_id
from endless_idler.blessings import get_default_blessing
from endless_idler.blessings.registry import clear_registry


def test_discover_blessing_plugins_returns_list() -> None:
    """Test that discover_blessing_plugins returns a list."""
    clear_registry()
    plugins = discover_blessing_plugins()
    assert isinstance(plugins, list)


def test_get_default_blessing_returns_odyssey() -> None:
    """Test that get_default_blessing returns Odyssey's Blessing."""
    clear_registry()
    blessing = get_default_blessing()
    assert blessing.blessing_id == "odyssey_blessing"
    assert blessing.display_name == "Odyssey's Blessing"


def test_get_blessing_by_id_existing() -> None:
    """Test getting a blessing by ID."""
    clear_registry()
    blessing = get_blessing_by_id("odyssey_blessing")
    assert blessing is not None
    assert blessing.blessing_id == "odyssey_blessing"
    assert blessing.display_name == "Odyssey's Blessing"


def test_get_blessing_by_id_nonexistent() -> None:
    """Test getting a nonexistent blessing returns None."""
    clear_registry()
    blessing = get_blessing_by_id("nonexistent_blessing")
    assert blessing is None


def test_registry_caches_results() -> None:
    """Test that the registry caches discovered plugins."""
    clear_registry()

    # First discovery
    plugins1 = discover_blessing_plugins()

    # Second discovery should return cached result
    plugins2 = discover_blessing_plugins()

    # Should be the same list object (cached)
    assert plugins1 is plugins2


def test_clear_registry_resets_cache() -> None:
    """Test that clear_registry resets the internal cache."""
    clear_registry()

    # First discovery
    plugins1 = discover_blessing_plugins()

    # Clear registry
    clear_registry()

    # Second discovery should be a new list
    plugins2 = discover_blessing_plugins()

    # Should be different list objects
    assert plugins1 is not plugins2


def test_discovered_plugins_have_required_fields() -> None:
    """Test that all discovered plugins have required fields."""
    clear_registry()
    plugins = discover_blessing_plugins()

    for plugin in plugins:
        assert plugin.blessing_id
        assert plugin.display_name
        assert plugin.description
        assert plugin.step_seconds > 0
        assert callable(plugin.multiplier_formula)
