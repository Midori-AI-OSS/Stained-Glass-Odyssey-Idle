from __future__ import annotations

import math
import random

import endless_idler.ui.idle.idle_state as idle_state_module

from endless_idler.characters.placement_rules import MISPLACED_EXP_MULTIPLIER
from endless_idler.characters.placement_rules import MISPLACED_STAT_MULTIPLIER
from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.ui.idle.idle_state import IdleGameState
from endless_idler.ui.idle.idle_state import IDLE_BLESSING_STEP_MULTIPLIER
from endless_idler.ui.idle.idle_state import MIN_EXP_GAIN_PER_TICK


IDLE_BLESSING_STEP_SECONDS = 300.0


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
) -> IdleGameState:
    onsite_ids = list(char_ids) if char_ids is not None else ["onsite"]
    reserve_ids = list(offsite_ids) if offsite_ids is not None else ["offsite"]
    stacks = {char_id: 1 for char_id in [*onsite_ids, *reserve_ids]}
    return IdleGameState(
        char_ids=onsite_ids,
        offsite_ids=reserve_ids,
        party_level=1,
        stacks=stacks,
        plugins_by_id=plugins or _plugins_by_id(),
        rng=random.Random(7),
        exp_gain_scale=exp_gain_scale,
    )


def test_blessing_multiplier_compounds_to_target_after_30_minutes(monkeypatch) -> None:
    now = {"value": 10_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state()
    assert math.isclose(
        state.get_idle_blessing_multiplier(), 1.0, rel_tol=0.0, abs_tol=1e-12
    )

    now["value"] += 299.9
    assert state.get_idle_blessing_step_count() == 0

    now["value"] += 0.1
    assert state.get_idle_blessing_step_count() == 1

    now["value"] += 1500.0
    assert state.get_idle_blessing_step_count() == 6
    assert math.isclose(
        state.get_idle_blessing_multiplier(), 1.025, rel_tol=1e-9, abs_tol=1e-9
    )


def test_blessing_resets_with_new_idle_session(monkeypatch) -> None:
    now = {"value": 50_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    first_state = _build_state()
    now["value"] += 600.0
    assert first_state.get_idle_blessing_multiplier() > 1.0

    second_state = _build_state()
    assert second_state.get_idle_blessing_step_count() == 0
    assert math.isclose(
        second_state.get_idle_blessing_multiplier(), 1.0, rel_tol=0.0, abs_tol=1e-12
    )


def test_onsite_blessing_applies_to_offsite_indirectly(monkeypatch) -> None:
    now = {"value": 90_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state()
    onsite_base = state.get_exp_gain_per_tick("onsite")
    offsite_base = state.get_exp_gain_per_tick("offsite")
    assert onsite_base > 0.0
    assert offsite_base > 0.0

    now["value"] += 300.0
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
    now = {"value": 120_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state()
    assert state.get_idle_blessing_seconds_to_next_step() == int(
        IDLE_BLESSING_STEP_SECONDS
    )

    now["value"] += 271.0
    assert state.get_idle_blessing_seconds_to_next_step() == 29

    now["value"] += 24.0
    assert state.get_idle_blessing_seconds_to_next_step() == 5

    now["value"] += 5.0
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

    before = float(state.get_char_data("onsite")["exp"])
    state.process_tick()
    after = float(state.get_char_data("onsite")["exp"])
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

    data_a = state.get_char_data("onsite_a")
    data_b = state.get_char_data("onsite_b")
    assert isinstance(data_a, dict)
    assert isinstance(data_b, dict)
    data_a["exp_multiplier"] = 1.0
    data_b["exp_multiplier"] = 2.0
    data_a["passive_modifier"] = 1.0
    data_b["passive_modifier"] = 1.0

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

    offsite_data = state.get_char_data("offsite_a")
    assert isinstance(offsite_data, dict)
    offsite_data["exp_multiplier"] = 1.0
    offsite_data["passive_modifier"] = 1.0
    gain_x1 = state.get_exp_gain_per_tick("offsite_a")

    offsite_data["exp_multiplier"] = 3.0
    gain_x3 = state.get_exp_gain_per_tick("offsite_a")

    assert gain_x1 > 0.0
    assert math.isclose(gain_x3 / gain_x1, 3.0, rel_tol=1e-9, abs_tol=1e-9)
