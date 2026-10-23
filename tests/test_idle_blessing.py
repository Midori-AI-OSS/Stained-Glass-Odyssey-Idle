from __future__ import annotations

import math
import random
from typing import cast

import endless_idler.ui.idle.idle_state as idle_state_module

from endless_idler.blessings.lunar_blessing import LUNAR_STEP_SECONDS
from endless_idler.blessings.lunar_blessing import LUNAR_WEEK_SECONDS
from endless_idler.characters.placement_rules import MISPLACED_EXP_MULTIPLIER
from endless_idler.characters.placement_rules import MISPLACED_STAT_MULTIPLIER
from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.ui.idle.idle_state import IdleGameState
from endless_idler.ui.idle.idle_state import IDLE_BLESSING_STEP_MULTIPLIER
from endless_idler.ui.idle.idle_state import MIN_EXP_GAIN_PER_TICK


IDLE_BLESSING_STEP_SECONDS = 300.0


def _set_elapsed_seconds(state: IdleGameState, seconds: float) -> None:
    with state._lock:
        state._elapsed_seconds = max(0.0, float(seconds))


def _plugins_by_id(
    *, onsite_placement: str = "onsite", offsite_placement: str = "offsite"
) -> dict[str, CharacterPlugin]:
    onsite = CharacterPlugin(
        char_id="onsite", display_name="Onsite", placement=onsite_placement
    )
    offsite = CharacterPlugin(
        char_id="offsite", display_name="Offsite", placement=offsite_placement
    )
    return {"onsite": onsite, "offsite": offsite}


def _plugins_for_ids(
    *, onsite_ids: list[str], offsite_ids: list[str]
) -> dict[str, CharacterPlugin]:
    plugins: dict[str, CharacterPlugin] = {}
    for char_id in onsite_ids:
        plugins[char_id] = CharacterPlugin(
            char_id=char_id, display_name=char_id, placement="onsite"
        )
    for char_id in offsite_ids:
        plugins[char_id] = CharacterPlugin(
            char_id=char_id, display_name=char_id, placement="offsite"
        )
    return plugins


def _build_state(
    *,
    plugins: dict[str, CharacterPlugin] | None = None,
    char_ids: list[str] | None = None,
    offsite_ids: list[str] | None = None,
    exp_gain_scale: float = 1.0,
    blessings_data: dict[str, dict[str, object]] | None = None,
) -> IdleGameState:
    onsite_ids = list(char_ids) if char_ids is not None else ["onsite"]
    reserve_ids = list(offsite_ids) if offsite_ids is not None else ["offsite"]
    stacks = {char_id: 1 for char_id in [*onsite_ids, *reserve_ids]}
    return IdleGameState(
        char_ids=onsite_ids,
        offsite_ids=reserve_ids,
        party_level=1,
        stacks=stacks,
        plugins_by_id=cast(dict[str, object], plugins or _plugins_by_id()),
        rng=random.Random(7),
        exp_gain_scale=exp_gain_scale,
        blessings_data=blessings_data,
    )


def test_blessing_multiplier_compounds_to_target_after_30_minutes(monkeypatch) -> None:
    del monkeypatch
    state = _build_state()
    assert math.isclose(
        state.get_idle_blessing_multiplier(), 1.0, rel_tol=0.0, abs_tol=1e-12
    )

    _set_elapsed_seconds(state, 299.9)
    assert state.get_idle_blessing_step_count() == 0

    _set_elapsed_seconds(state, 300.0)
    assert state.get_idle_blessing_step_count() == 1

    _set_elapsed_seconds(state, 1800.0)
    assert state.get_idle_blessing_step_count() == 6
    assert math.isclose(
        state.get_idle_blessing_multiplier(), 1.025, rel_tol=1e-9, abs_tol=1e-9
    )


def test_blessing_resets_with_new_idle_session(monkeypatch) -> None:
    del monkeypatch
    first_state = _build_state()
    _set_elapsed_seconds(first_state, 600.0)
    assert first_state.get_idle_blessing_multiplier() > 1.0

    second_state = _build_state()
    assert second_state.get_idle_blessing_step_count() == 0
    assert math.isclose(
        second_state.get_idle_blessing_multiplier(), 1.0, rel_tol=0.0, abs_tol=1e-12
    )


def test_onsite_blessing_applies_to_offsite_indirectly(monkeypatch) -> None:
    del monkeypatch
    state = _build_state()
    onsite_base = state.get_exp_gain_per_tick("onsite")
    offsite_base = state.get_exp_gain_per_tick("offsite")
    assert onsite_base > 0.0
    assert offsite_base > 0.0

    _set_elapsed_seconds(state, 300.0)
    onsite_blessed = state.get_exp_gain_per_tick("onsite")
    offsite_blessed = state.get_exp_gain_per_tick("offsite")

    onsite_ratio = onsite_blessed / onsite_base
    offsite_ratio = offsite_blessed / offsite_base
    assert math.isclose(
        onsite_ratio, IDLE_BLESSING_STEP_MULTIPLIER, rel_tol=1e-9, abs_tol=1e-9
    )
    assert math.isclose(
        offsite_ratio, IDLE_BLESSING_STEP_MULTIPLIER, rel_tol=1e-9, abs_tol=1e-9
    )
    assert not math.isclose(
        offsite_ratio,
        IDLE_BLESSING_STEP_MULTIPLIER**2,
        rel_tol=1e-4,
        abs_tol=1e-4,
    )


def test_blessing_countdown_wraps_every_five_minutes(monkeypatch) -> None:
    del monkeypatch
    state = _build_state()
    assert state.get_idle_blessing_seconds_to_next_step() == int(
        IDLE_BLESSING_STEP_SECONDS
    )

    _set_elapsed_seconds(state, 271.0)
    assert state.get_idle_blessing_seconds_to_next_step() == 29

    _set_elapsed_seconds(state, 295.0)
    assert state.get_idle_blessing_seconds_to_next_step() == 5

    _set_elapsed_seconds(state, 300.0)
    assert state.get_idle_blessing_seconds_to_next_step() == int(
        IDLE_BLESSING_STEP_SECONDS
    )


def test_misplaced_onsite_character_uses_exp_and_stat_penalties(monkeypatch) -> None:
    now = {"value": 140_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    valid_state = _build_state(
        plugins=_plugins_by_id(onsite_placement="onsite"),
        offsite_ids=[],
    )
    misplaced_state = _build_state(
        plugins=_plugins_by_id(onsite_placement="offsite"),
        offsite_ids=[],
    )

    valid_gain = valid_state.get_exp_gain_per_tick("onsite")
    misplaced_gain = misplaced_state.get_exp_gain_per_tick("onsite")
    assert valid_gain > 0.0
    assert math.isclose(
        misplaced_gain / valid_gain,
        MISPLACED_EXP_MULTIPLIER,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )

    valid_data = valid_state.get_char_data("onsite")
    misplaced_data = misplaced_state.get_char_data("onsite")
    assert isinstance(valid_data, dict)
    assert isinstance(misplaced_data, dict)
    valid_hp = float(valid_data["max_hp"])
    misplaced_hp = float(misplaced_data["max_hp"])
    assert valid_hp > 0.0
    assert misplaced_hp < valid_hp
    assert math.isclose(
        misplaced_hp / valid_hp,
        MISPLACED_STAT_MULTIPLIER,
        rel_tol=0.02,
        abs_tol=0.02,
    )


def test_misplaced_offsite_character_uses_exp_penalty(monkeypatch) -> None:
    now = {"value": 150_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    valid_state = _build_state(
        plugins=_plugins_by_id(offsite_placement="offsite"),
    )
    misplaced_state = _build_state(
        plugins=_plugins_by_id(offsite_placement="onsite"),
    )

    valid_gain = valid_state.get_exp_gain_per_tick("offsite")
    misplaced_gain = misplaced_state.get_exp_gain_per_tick("offsite")
    assert valid_gain > 0.0
    assert math.isclose(
        misplaced_gain / valid_gain,
        MISPLACED_EXP_MULTIPLIER,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )


def test_shared_exp_slider_does_not_reduce_onsite_gain_when_offsite_empty(
    monkeypatch,
) -> None:
    now = {"value": 160_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state(offsite_ids=[])
    state.set_shared_exp_percentage(1)
    gain_at_min_share = state.get_exp_gain_per_tick("onsite")
    state.set_shared_exp_percentage(95)
    gain_at_max_share = state.get_exp_gain_per_tick("onsite")

    assert gain_at_min_share > 0.0
    assert math.isclose(
        gain_at_min_share, gain_at_max_share, rel_tol=1e-9, abs_tol=1e-9
    )


def test_shared_exp_slider_still_redistributes_when_offsite_exists(monkeypatch) -> None:
    now = {"value": 170_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state()
    state.set_shared_exp_percentage(1)
    onsite_gain_min_share = state.get_exp_gain_per_tick("onsite")
    offsite_gain_min_share = state.get_exp_gain_per_tick("offsite")

    state.set_shared_exp_percentage(95)
    onsite_gain_max_share = state.get_exp_gain_per_tick("onsite")
    offsite_gain_max_share = state.get_exp_gain_per_tick("offsite")

    assert onsite_gain_max_share < onsite_gain_min_share
    assert offsite_gain_max_share > offsite_gain_min_share


def test_exp_gain_floor_applies_to_tiny_positive_values(monkeypatch) -> None:
    now = {"value": 180_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state(offsite_ids=[], exp_gain_scale=1e-8)
    state.set_shared_exp_percentage(95)

    per_tick_gain = state.get_exp_gain_per_tick("onsite")
    assert math.isclose(
        per_tick_gain, MIN_EXP_GAIN_PER_TICK, rel_tol=0.0, abs_tol=1e-12
    )

    before_data = state.get_char_data("onsite")
    assert isinstance(before_data, dict)
    before = float(before_data["exp"])
    state.process_tick()
    after_data = state.get_char_data("onsite")
    assert isinstance(after_data, dict)
    after = float(after_data["exp"])
    assert math.isclose(
        after - before, MIN_EXP_GAIN_PER_TICK, rel_tol=0.0, abs_tol=1e-12
    )


def test_onsite_pool_is_split_equally_by_onsite_count(monkeypatch) -> None:
    now = {"value": 190_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    single_plugins = _plugins_for_ids(onsite_ids=["onsite_a"], offsite_ids=[])
    split_plugins = _plugins_for_ids(
        onsite_ids=["onsite_a", "onsite_b"], offsite_ids=[]
    )

    single_state = _build_state(
        plugins=single_plugins,
        char_ids=["onsite_a"],
        offsite_ids=[],
    )
    split_state = _build_state(
        plugins=split_plugins,
        char_ids=["onsite_a", "onsite_b"],
        offsite_ids=[],
    )

    single_gain = single_state.get_exp_gain_per_tick("onsite_a")
    split_gain_a = split_state.get_exp_gain_per_tick("onsite_a")
    split_gain_b = split_state.get_exp_gain_per_tick("onsite_b")

    assert single_gain > 0.0
    assert math.isclose(split_gain_a, split_gain_b, rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(split_gain_a * 2.0, single_gain, rel_tol=1e-9, abs_tol=1e-9)


def test_recipient_modifiers_apply_to_allocated_onsite_share(monkeypatch) -> None:
    now = {"value": 200_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    plugins = _plugins_for_ids(onsite_ids=["onsite_a", "onsite_b"], offsite_ids=[])
    state = _build_state(
        plugins=plugins,
        char_ids=["onsite_a", "onsite_b"],
        offsite_ids=[],
    )

    with state._lock:
        state._char_data["onsite_a"]["exp_multiplier"] = 1.0
        state._char_data["onsite_b"]["exp_multiplier"] = 2.0
        state._char_data["onsite_a"]["passive_modifier"] = 1.0
        state._char_data["onsite_b"]["passive_modifier"] = 1.0

    gain_a = state.get_exp_gain_per_tick("onsite_a")
    gain_b = state.get_exp_gain_per_tick("onsite_b")

    assert gain_a > 0.0
    assert math.isclose(gain_b / gain_a, 2.0, rel_tol=1e-9, abs_tol=1e-9)


def test_recipient_modifiers_apply_to_allocated_offsite_share(monkeypatch) -> None:
    now = {"value": 210_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    plugins = _plugins_for_ids(onsite_ids=["onsite_a"], offsite_ids=["offsite_a"])
    state = _build_state(
        plugins=plugins,
        char_ids=["onsite_a"],
        offsite_ids=["offsite_a"],
    )

    with state._lock:
        state._char_data["offsite_a"]["exp_multiplier"] = 1.0
        state._char_data["offsite_a"]["passive_modifier"] = 1.0
    gain_x1 = state.get_exp_gain_per_tick("offsite_a")

    with state._lock:
        state._char_data["offsite_a"]["exp_multiplier"] = 3.0
    gain_x3 = state.get_exp_gain_per_tick("offsite_a")

    assert gain_x1 > 0.0
    assert math.isclose(gain_x3 / gain_x1, 3.0, rel_tol=1e-9, abs_tol=1e-9)


def test_damage_type_blessing_uses_blessing_ids_for_specific_damage_type(
    monkeypatch,
) -> None:
    now = {"value": 220_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    plugins = {
        "onsite": CharacterPlugin(
            char_id="onsite",
            display_name="Onsite",
            placement="onsite",
            damage_type_id="fire",
        )
    }
    state = _build_state(
        plugins=plugins,
        char_ids=["onsite"],
        offsite_ids=[],
        blessings_data={
            "fire": {"steps": 999, "unlocked": True},
            "fire_blessing": {"steps": 10, "unlocked": True},
        },
    )

    bonus = state._damage_type_blessing_bonus("onsite")
    assert math.isclose(bonus, 1.001, rel_tol=1e-12, abs_tol=1e-12)


def test_damage_type_blessing_generic_sums_unlocked_blessing_ids_only(
    monkeypatch,
) -> None:
    now = {"value": 230_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    plugins = {
        "onsite": CharacterPlugin(
            char_id="onsite",
            display_name="Onsite",
            placement="onsite",
            damage_type_id="generic",
        )
    }
    state = _build_state(
        plugins=plugins,
        char_ids=["onsite"],
        offsite_ids=[],
        blessings_data={
            "fire": {"steps": 999, "unlocked": True},
            "ice": {"steps": 999, "unlocked": True},
            "fire_blessing": {"steps": 4, "unlocked": True},
            "ice_blessing": {"steps": 6, "unlocked": True},
            "wind_blessing": {"steps": 100, "unlocked": False},
        },
    )

    bonus = state._damage_type_blessing_bonus("onsite")
    assert math.isclose(bonus, 1.001, rel_tol=1e-12, abs_tol=1e-12)


def test_lunar_exp_gain_bonus_applies_to_idle_gain(monkeypatch) -> None:
    now = {"value": 240_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    steps_per_week = int(LUNAR_WEEK_SECONDS // LUNAR_STEP_SECONDS)
    baseline = _build_state(offsite_ids=[])
    lunar_boosted = _build_state(
        offsite_ids=[],
        blessings_data={
            "lunar_blessing": {"steps": steps_per_week, "unlocked": True},
        },
    )

    baseline_gain = baseline.get_exp_gain_per_tick("onsite")
    boosted_gain = lunar_boosted.get_exp_gain_per_tick("onsite")

    assert baseline_gain > 0.0
    assert math.isclose(
        boosted_gain / baseline_gain,
        1.01,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )


def test_lunar_exp_reduction_applies_to_next_level_requirement(monkeypatch) -> None:
    now = {"value": 250_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    steps_per_week = int(LUNAR_WEEK_SECONDS // LUNAR_STEP_SECONDS)
    starred_plugins = {
        "onsite": CharacterPlugin(
            char_id="onsite",
            display_name="Onsite",
            placement="onsite",
            stars=5,
        )
    }
    baseline = _build_state(plugins=starred_plugins, offsite_ids=[])
    lunar_reduced = _build_state(
        plugins=starred_plugins,
        offsite_ids=[],
        blessings_data={
            "lunar_blessing": {"steps": steps_per_week, "unlocked": True},
        },
    )

    baseline._level_up("onsite")
    lunar_reduced._level_up("onsite")

    baseline_data = baseline.get_char_data("onsite")
    reduced_data = lunar_reduced.get_char_data("onsite")
    assert isinstance(baseline_data, dict)
    assert isinstance(reduced_data, dict)
    assert math.isclose(
        float(reduced_data["next_exp"]) / float(baseline_data["next_exp"]),
        0.99,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )


def test_locked_persistent_blessing_does_not_accrue_or_preaccumulate(
    monkeypatch,
) -> None:
    now = {"value": 260_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state(
        blessings_data={
            "fire_blessing": {
                "steps": 7,
                "unlocked": False,
                "tick_elapsed_seconds": 299.0,
            }
        }
    )

    state._process_blessing_ticks(delta_seconds=5.0)
    fire_data = state.export_blessings()["fire_blessing"]
    assert int(fire_data["steps"]) == 7
    assert "tick_elapsed_seconds" not in fire_data


def test_unlocked_persistent_blessing_accrues_normally(monkeypatch) -> None:
    now = {"value": 270_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state(
        blessings_data={
            "fire_blessing": {
                "steps": 2,
                "unlocked": True,
                "tick_elapsed_seconds": 299.0,
            }
        }
    )

    state._process_blessing_ticks(delta_seconds=2.0)
    fire_data = state.export_blessings()["fire_blessing"]
    assert int(fire_data["steps"]) == 3
    assert "tick_elapsed_seconds" not in fire_data


def test_unlock_transition_starts_accrual_without_retroactive_catchup(
    monkeypatch,
) -> None:
    now = {"value": 280_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state(
        blessings_data={
            "fire_blessing": {
                "steps": 4,
                "unlocked": False,
                "tick_elapsed_seconds": 299.0,
            }
        }
    )

    state._process_blessing_ticks(delta_seconds=0.0)
    locked_data = state.export_blessings()["fire_blessing"]
    assert int(locked_data["steps"]) == 4
    assert "tick_elapsed_seconds" not in locked_data

    state._blessings_data["fire_blessing"]["unlocked"] = True

    state._process_blessing_ticks(delta_seconds=1.0)
    unlocked_data = state.export_blessings()["fire_blessing"]
    assert int(unlocked_data["steps"]) == 4

    state._process_blessing_ticks(delta_seconds=298.0)
    before_step_data = state.export_blessings()["fire_blessing"]
    assert int(before_step_data["steps"]) == 4

    state._process_blessing_ticks(delta_seconds=1.0)
    after_step_data = state.export_blessings()["fire_blessing"]
    assert int(after_step_data["steps"]) == 5


def test_runtime_snapshot_exposes_blessing_phase_without_persisting_elapsed(
    monkeypatch,
) -> None:
    now = {"value": 290_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state(
        blessings_data={
            "fire_blessing": {
                "steps": 2,
                "unlocked": True,
                "tick_elapsed_seconds": 123.4,
            }
        }
    )
    snapshot = state.export_runtime_snapshot()
    runtime = snapshot.get("blessing_runtime")
    assert isinstance(runtime, dict)
    fire_runtime = runtime.get("fire_blessing")
    assert isinstance(fire_runtime, dict)
    assert int(fire_runtime["steps"]) == 2
    assert math.isclose(float(fire_runtime["progress"]), 123.4 / 300.0, rel_tol=1e-9)
    assert int(fire_runtime["countdown_seconds"]) == 177

    blessings = snapshot.get("blessings")
    assert isinstance(blessings, dict)
    fire_save = blessings.get("fire_blessing")
    assert isinstance(fire_save, dict)
    assert "tick_elapsed_seconds" not in fire_save


def test_runtime_snapshot_tracks_odyssey_step_progress_from_tick_elapsed(
    monkeypatch,
) -> None:
    now = {"value": 300_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state()
    _ = state.process_tick()
    snapshot = state.export_runtime_snapshot()
    runtime = snapshot.get("blessing_runtime")
    assert isinstance(runtime, dict)
    odyssey = runtime.get("odyssey_blessing")
    assert isinstance(odyssey, dict)
    assert int(odyssey["steps"]) == 0
    assert math.isclose(float(odyssey["progress"]), 1.0 / 9000.0, rel_tol=1e-9)
    assert int(odyssey["countdown_seconds"]) == 300
