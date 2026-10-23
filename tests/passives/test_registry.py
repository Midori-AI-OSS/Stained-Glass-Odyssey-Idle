from __future__ import annotations

from pathlib import Path

import pytest

from endless_idler.passives import discover_passive_plugins
from endless_idler.passives import get_passive_by_id
from endless_idler.passives.plugin import PassivePlugin
from endless_idler.passives.registry import clear_registry
import endless_idler.passives.registry as registry_module


@pytest.fixture(autouse=True)
def _clear_passive_registry() -> None:
    clear_registry()
    yield
    clear_registry()


def _plugin(passive_id: str, *, tick_order: int = 0) -> PassivePlugin:
    return PassivePlugin(
        passive_id=passive_id,
        display_name=passive_id.replace("_", " ").title(),
        description=f"Passive {passive_id} for registry testing.",
        tick_order=tick_order,
    )


def test_discover_passive_plugins_returns_list() -> None:
    plugins = discover_passive_plugins()
    assert isinstance(plugins, list)


def test_get_passive_by_id_existing() -> None:
    passive = get_passive_by_id("trinity_synergy")
    assert passive is not None
    assert passive.passive_id == "trinity_synergy"
    assert passive.display_name == "Trinity Synergy"


def test_get_passive_by_id_nonexistent() -> None:
    assert get_passive_by_id("nonexistent_passive") is None


def test_registry_caches_results() -> None:
    plugins_one = discover_passive_plugins()
    plugins_two = discover_passive_plugins()

    assert plugins_one is plugins_two


def test_clear_registry_resets_cache() -> None:
    plugins_one = discover_passive_plugins()

    clear_registry()
    plugins_two = discover_passive_plugins()

    assert plugins_one is not plugins_two


def test_discovered_plugins_have_required_fields() -> None:
    for plugin in discover_passive_plugins():
        assert plugin.passive_id
        assert plugin.display_name
        assert plugin.description
        assert isinstance(plugin.save_schema, dict)
        assert callable(plugin.build_runtime_state)
        assert callable(plugin.tick)


def test_discovery_skips_excluded_and_private_modules(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for name in ("plugin.py", "_private.py", "visible.py"):
        (tmp_path / name).write_text("# test file\n", encoding="utf-8")

    seen: list[str] = []

    def _load(path: Path) -> PassivePlugin | None:
        seen.append(path.name)
        if path.name == "visible.py":
            return _plugin("visible_passive")
        return None

    monkeypatch.setattr(registry_module, "_PASSIVES_DIR", tmp_path)
    monkeypatch.setattr(registry_module, "load_passive_module", _load)

    plugins = registry_module.discover_passive_plugins()

    assert [plugin.passive_id for plugin in plugins] == ["visible_passive"]
    assert seen == ["visible.py"]


def test_discover_passive_plugins_rejects_duplicate_ids(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for name in ("alpha.py", "beta.py"):
        (tmp_path / name).write_text("# test file\n", encoding="utf-8")

    def _load(_path: Path) -> PassivePlugin | None:
        return _plugin("duplicate_passive")

    monkeypatch.setattr(registry_module, "_PASSIVES_DIR", tmp_path)
    monkeypatch.setattr(registry_module, "load_passive_module", _load)

    with pytest.raises(ValueError, match="Duplicate passive id 'duplicate_passive'"):
        registry_module.discover_passive_plugins()
