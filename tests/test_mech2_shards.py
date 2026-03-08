from __future__ import annotations

import random

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.save_codec import as_character_progress_dict
from endless_idler.ui.idle.idle_state import IdleGameState
from endless_idler.ui.idle.idle_state import SHARD_ROLL_INTERVAL_TICKS


def _build_state(
    *,
    char_id: str,
    progress: dict[str, dict[str, float | int]] | None = None,
    inventory: dict[str, int] | None = None,
) -> IdleGameState:
    plugins_by_id = {
        plugin.char_id: plugin
        for plugin in discover_character_plugins()
    }
    plugin = plugins_by_id.get(char_id)
    if plugin is None:
        raise ValueError(f"Missing runtime plugin for test character {char_id!r}.")
    return IdleGameState(
        char_ids=[char_id],
        offsite_ids=[],
        party_level=1,
        stacks={char_id: 1},
        plugins_by_id={char_id: plugin},
        rng=random.Random(7),
        progress_by_id=progress or {},
        inventory=inventory,
    )


def test_shard_roll_completes_bar_and_awards_single_type_item(monkeypatch) -> None:
    inventory: dict[str, int] = {}
    state = _build_state(
        char_id="ally",
        progress={"ally": {"shard_bar_ticks": 99}},
        inventory=inventory,
    )
    monkeypatch.setattr(state._rng, "random", lambda: 0.0)

    for _ in range(SHARD_ROLL_INTERVAL_TICKS):
        state.process_tick()

    data = state.get_char_data("ally")
    assert isinstance(data, dict)
    assert int(data["shard_bar_ticks"]) == 0
    assert inventory == {"fire_shard": 1}


def test_dual_type_shard_award_uses_random_constituent(monkeypatch) -> None:
    inventory: dict[str, int] = {}
    state = _build_state(
        char_id="lady_storm",
        progress={"lady_storm": {"shard_bar_ticks": 99}},
        inventory=inventory,
    )
    monkeypatch.setattr(state._rng, "random", lambda: 0.0)
    monkeypatch.setattr(state._rng, "choice", lambda options: options[0])

    for _ in range(SHARD_ROLL_INTERVAL_TICKS):
        state.process_tick()

    assert inventory == {"wind_shard": 1}


def test_generic_damage_type_character_is_not_shard_eligible(monkeypatch) -> None:
    inventory: dict[str, int] = {}
    state = _build_state(
        char_id="luna",
        progress={"luna": {"shard_bar_ticks": 0}},
        inventory=inventory,
    )
    monkeypatch.setattr(state._rng, "random", lambda: 0.0)

    for _ in range(SHARD_ROLL_INTERVAL_TICKS * 3):
        state.process_tick()

    data = state.get_char_data("luna")
    assert isinstance(data, dict)
    assert int(data["shard_bar_ticks"]) == 0
    assert inventory == {}


def test_export_progress_includes_shard_bar_ticks() -> None:
    state = _build_state(
        char_id="persona_ice",
        progress={"persona_ice": {"shard_bar_ticks": 7}},
    )

    progress = state.export_progress()
    assert int(progress["persona_ice"]["shard_bar_ticks"]) == 7


def test_as_character_progress_dict_keeps_shard_bar_ticks() -> None:
    parsed = as_character_progress_dict(
        {"ally": {"level": 1, "exp": 0.0, "next_exp": 30.0, "shard_bar_ticks": "12"}}
    )

    assert int(parsed["ally"]["shard_bar_ticks"]) == 12
