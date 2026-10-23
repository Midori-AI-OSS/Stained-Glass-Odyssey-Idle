from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from endless_idler.passives.plugin import PassivePlugin


def test_passive_plugin_creation_uses_expected_defaults() -> None:
    plugin = PassivePlugin(
        passive_id="test_passive",
        display_name="Test Passive",
        description="Passive used for framework testing.",
    )

    assert plugin.passive_id == "test_passive"
    assert plugin.display_name == "Test Passive"
    assert plugin.description == "Passive used for framework testing."
    assert plugin.save_schema == {}
    assert plugin.tick_order == 0


def test_passive_plugin_default_hooks_are_safe_and_fresh() -> None:
    plugin = PassivePlugin(
        passive_id="test_passive",
        display_name="Test Passive",
        description="Passive used for framework testing.",
    )

    first_state = plugin.build_runtime_state({"count": 3})
    second_state = plugin.build_runtime_state({"count": 9})

    assert first_state == {}
    assert second_state == {}
    assert first_state is not second_state
    assert plugin.tick(object()) is None


def test_passive_plugin_preserves_custom_hooks_and_schema() -> None:
    observed: dict[str, object] = {}

    def _build_runtime_state(saved_state: dict[str, object]) -> dict[str, object]:
        observed["saved_state"] = dict(saved_state)
        return {"built": saved_state.get("count", 0)}

    def _tick(context: object) -> None:
        observed["context"] = context

    plugin = PassivePlugin(
        passive_id="custom_passive",
        display_name="Custom Passive",
        description="Passive with custom hooks.",
        save_schema={"count": int},
        tick_order=-7,
        build_runtime_state=_build_runtime_state,
        tick=_tick,
    )

    marker = object()
    runtime_state = plugin.build_runtime_state({"count": 4})
    plugin.tick(marker)

    assert plugin.save_schema == {"count": int}
    assert plugin.tick_order == -7
    assert runtime_state == {"built": 4}
    assert observed["saved_state"] == {"count": 4}
    assert observed["context"] is marker


def test_passive_plugin_is_immutable() -> None:
    plugin = PassivePlugin(
        passive_id="immutable_passive",
        display_name="Immutable Passive",
        description="Passive used for immutability testing.",
    )

    with pytest.raises(FrozenInstanceError):
        plugin.passive_id = "updated_passive"
