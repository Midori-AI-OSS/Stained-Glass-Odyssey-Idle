from __future__ import annotations

import math
import random

import endless_idler.ui.idle.idle_state as idle_state_module

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.ui.idle.idle_state import IdleGameState
from endless_idler.ui.idle.idle_state import IDLE_BLESSING_STEP_MULTIPLIER


def _plugins_by_id() -> dict[str, CharacterPlugin]:
    onsite = CharacterPlugin(char_id="onsite", display_name="Onsite", placement="onsite")
    offsite = CharacterPlugin(char_id="offsite", display_name="Offsite", placement="offsite")
    return {"onsite": onsite, "offsite": offsite}


def _build_state() -> IdleGameState:
    return IdleGameState(
        char_ids=["onsite"],
        offsite_ids=["offsite"],
        party_level=1,
        stacks={"onsite": 1, "offsite": 1},
        plugins_by_id=_plugins_by_id(),
        rng=random.Random(7),
    )


def test_blessing_multiplier_compounds_to_target_after_30_minutes(monkeypatch) -> None:
    now = {"value": 10_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state()
    assert math.isclose(state.get_idle_blessing_multiplier(), 1.0, rel_tol=0.0, abs_tol=1e-12)

    now["value"] += 299.9
    assert state.get_idle_blessing_step_count() == 0

    now["value"] += 0.1
    assert state.get_idle_blessing_step_count() == 1

    now["value"] += 1500.0
    assert state.get_idle_blessing_step_count() == 6
    assert math.isclose(state.get_idle_blessing_multiplier(), 1.025, rel_tol=1e-9, abs_tol=1e-9)


def test_blessing_resets_with_new_idle_session(monkeypatch) -> None:
    now = {"value": 50_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    first_state = _build_state()
    now["value"] += 600.0
    assert first_state.get_idle_blessing_multiplier() > 1.0

    second_state = _build_state()
    assert second_state.get_idle_blessing_step_count() == 0
    assert math.isclose(second_state.get_idle_blessing_multiplier(), 1.0, rel_tol=0.0, abs_tol=1e-12)


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
    assert math.isclose(onsite_ratio, IDLE_BLESSING_STEP_MULTIPLIER, rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(offsite_ratio, IDLE_BLESSING_STEP_MULTIPLIER, rel_tol=1e-9, abs_tol=1e-9)
    assert not math.isclose(
        offsite_ratio,
        IDLE_BLESSING_STEP_MULTIPLIER ** 2,
        rel_tol=1e-4,
        abs_tol=1e-4,
    )


def test_blessing_countdown_wraps_every_five_minutes(monkeypatch) -> None:
    now = {"value": 120_000.0}
    monkeypatch.setattr(idle_state_module.time, "time", lambda: now["value"])

    state = _build_state()
    assert state.get_idle_blessing_seconds_to_next_step() == 300

    now["value"] += 271.0
    assert state.get_idle_blessing_seconds_to_next_step() == 29

    now["value"] += 24.0
    assert state.get_idle_blessing_seconds_to_next_step() == 5

    now["value"] += 5.0
    assert state.get_idle_blessing_seconds_to_next_step() == 300

