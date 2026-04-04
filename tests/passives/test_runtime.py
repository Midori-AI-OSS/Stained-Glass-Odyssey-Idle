from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from endless_idler.passives.plugin import PassivePlugin
import endless_idler.passives.runtime as runtime_module


def _plugin(
    passive_id: str,
    *,
    save_schema: dict[str, object] | None = None,
    tick_order: int = 0,
    build_runtime_state: Any = None,
    tick: Any = None,
) -> PassivePlugin:
    return PassivePlugin(
        passive_id=passive_id,
        display_name=passive_id.replace("_", " ").title(),
        description=f"Passive {passive_id} for runtime testing.",
        save_schema=dict(save_schema or {}),
        tick_order=tick_order,
        build_runtime_state=build_runtime_state or (lambda _saved_state: {}),
        tick=tick or (lambda _context: None),
    )


def test_default_canonical_state_supports_known_field_types() -> None:
    plugin = _plugin(
        "typed_passive",
        save_schema={
            "count": int,
            "ratio": float,
            "enabled": bool,
            "ttls": list[int],
            "ignored": str,
        },
    )

    assert runtime_module._default_canonical_state(plugin) == {
        "count": 0,
        "ratio": 0.0,
        "enabled": False,
        "ttls": [],
    }


def test_ordered_passive_ids_to_tick_sorts_and_keeps_stateful_inactive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plugins = {
        "active_late": _plugin("active_late", tick_order=10),
        "inactive_early": _plugin(
            "inactive_early",
            save_schema={"count": int},
            tick_order=-5,
        ),
        "stateless_missing": _plugin("stateless_missing", tick_order=-10),
    }
    monkeypatch.setattr(runtime_module, "get_passive_by_id", plugins.get)

    ordered = runtime_module._ordered_passive_ids_to_tick(
        active_passive_ids=["active_late"],
        canonical_passives={
            "inactive_early": {"count": 2},
            "stateless_missing": {},
        },
        runtime_passives={"inactive_runtime": {"cached": True}},
    )

    assert ordered == ["inactive_early", "active_late"]


def test_resolve_active_passive_ids_dedupes_and_filters_unregistered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registered = {
        "alpha": _plugin("alpha"),
        "shared": _plugin("shared"),
        "beta": _plugin("beta"),
        "standby_only": _plugin("standby_only"),
    }
    monkeypatch.setattr(runtime_module, "get_passive_by_id", registered.get)

    active_ids = runtime_module.resolve_active_passive_ids(
        char_ids=["onsite"],
        offsite_ids=["offsite"],
        standby_ids=["standby"],
        plugins_by_id={
            "onsite": SimpleNamespace(passives=["alpha", "shared", "missing", ""]),
            "offsite": SimpleNamespace(passives=["shared", "beta"]),
            "standby": SimpleNamespace(passives=["standby_only"]),
        },
    )

    assert active_ids == ["alpha", "shared", "beta", "standby_only"]


def test_initialize_passive_state_uses_normalized_canonical_and_builds_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plugins = {
        "alpha": _plugin(
            "alpha",
            save_schema={"count": int},
            build_runtime_state=lambda saved_state: {"built": saved_state["count"]},
        ),
        "beta": _plugin("beta"),
    }
    monkeypatch.setattr(runtime_module, "get_passive_by_id", plugins.get)
    monkeypatch.setattr(
        runtime_module,
        "normalized_passives",
        lambda _value: {"alpha": {"count": 2}, "beta": {}},
    )

    canonical, runtime = runtime_module.initialize_passive_state(
        passives_data={"ignored": {}},
        active_passive_ids=["alpha", "missing"],
    )

    assert canonical == {"alpha": {"count": 2}, "beta": {}}
    assert runtime == {"alpha": {"built": 2}}


def test_tick_active_passives_builds_runtime_and_ticks_stateful_inactive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []

    def _clear_tick(context: runtime_module.PassiveTickContext) -> None:
        events.append(
            f"{context.passive_id}:{context.tick_count}:{context.delta_seconds}:{context.elapsed_seconds}"
        )
        context.canonical_state["count"] = 0
        context.runtime_state["cleared"] = True

    def _active_tick(context: runtime_module.PassiveTickContext) -> None:
        events.append(
            f"{context.passive_id}:{context.tick_count}:{context.delta_seconds}:{context.elapsed_seconds}"
        )
        context.runtime_state["ticked"] = True

    plugins = {
        "stale_state": _plugin(
            "stale_state",
            save_schema={"count": int},
            tick_order=-10,
            build_runtime_state=lambda _saved_state: {"from_build": "stale"},
            tick=_clear_tick,
        ),
        "active_state": _plugin(
            "active_state",
            tick_order=5,
            build_runtime_state=lambda _saved_state: {"from_build": "active"},
            tick=_active_tick,
        ),
    }
    monkeypatch.setattr(runtime_module, "get_passive_by_id", plugins.get)

    canonical_passives = {
        "stale_state": {"count": 3},
        "active_state": {},
    }
    runtime_passives: dict[str, dict[str, object]] = {}

    runtime_module.tick_active_passives(
        active_passive_ids=["active_state"],
        canonical_passives=canonical_passives,
        runtime_passives=runtime_passives,
        idle_state=object(),
        delta_seconds=-1.0,
        tick_count=-7,
        elapsed_seconds=-2.5,
    )

    assert events == ["stale_state:0:0.0:0.0", "active_state:0:0.0:0.0"]
    assert canonical_passives["stale_state"] == {"count": 0}
    assert runtime_passives["stale_state"] == {
        "from_build": "stale",
        "cleared": True,
    }
    assert runtime_passives["active_state"] == {
        "from_build": "active",
        "ticked": True,
    }


def test_export_helpers_normalize_and_copy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        runtime_module,
        "normalized_passives",
        lambda value: {"alpha": {"count": max(0, int(value["alpha"]["count"]))}},
    )

    canonical = {"alpha": {"count": -3}}
    exported_passives = runtime_module.export_passives(canonical_passives=canonical)
    exported_runtime = runtime_module.export_active_passive_runtime(
        active_passive_ids=["alpha", "beta"],
        runtime_passives={
            "alpha": {"count": 1},
            "beta": {"flag": True},
            "ignored": {"count": 99},
        },
    )

    canonical["alpha"]["count"] = 7

    assert exported_passives == {"alpha": {"count": 0}}
    assert exported_runtime == {
        "alpha": {"count": 1},
        "beta": {"flag": True},
    }
