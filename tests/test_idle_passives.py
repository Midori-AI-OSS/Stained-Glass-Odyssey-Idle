from __future__ import annotations

import math
import random

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.passives._trinity import apply_log_soft_cap
from endless_idler.save import RunSave
from endless_idler.ui.idle.idle_state import IdleGameState


def _stats(*, max_hp: float, defense: float, mitigation: float) -> dict[str, float]:
    return {
        "max_hp": max_hp,
        "atk": 200.0,
        "defense": defense,
        "crit_mod": 100.0,
        "effect_hit_rate": 1.0,
        "mitigation": mitigation,
        "regain": 0.0,
        "dodge_odds": 0.05,
        "effect_resistance": 0.05,
        "vitality": 1.0,
        "atk_speed": 1.0,
    }


def _trinity_plugins() -> dict[str, CharacterPlugin]:
    return {
        "lady_darkness": CharacterPlugin(
            char_id="lady_darkness",
            display_name="Lady Darkness",
            stars=5,
            placement="onsite",
            passives=["lady_darkness_eclipsing_veil"],
            base_stats=_stats(max_hp=1000.0, defense=200.0, mitigation=1.0),
        ),
        "lady_light": CharacterPlugin(
            char_id="lady_light",
            display_name="Lady Light",
            stars=5,
            placement="offsite",
            passives=["lady_light_radiant_aegis"],
            base_stats=_stats(max_hp=1000.0, defense=200.0, mitigation=1.0),
        ),
        "persona_light_and_dark": CharacterPlugin(
            char_id="persona_light_and_dark",
            display_name="Persona Light and Dark",
            stars=6,
            placement="both",
            passives=["trinity_synergy"],
            base_stats=_stats(max_hp=1700.0, defense=240.0, mitigation=4.0),
            is_dual_type=True,
            dual_damage_types=("light", "dark"),
        ),
    }


def _build_trinity_state(
    *,
    onsite_ids: list[str] | None = None,
    offsite_ids: list[str] | None = None,
    standby_ids: list[str] | None = None,
    stacks: dict[str, int] | None = None,
    passives_data: dict[str, dict[str, object]] | None = None,
) -> IdleGameState:
    onsite = list(onsite_ids or ["lady_darkness"])
    offsite = list(offsite_ids or ["lady_light", "persona_light_and_dark"])
    standby = list(standby_ids or [])
    all_ids = [*onsite, *offsite, *standby]
    stack_map = stacks or {char_id: 1 for char_id in all_ids}
    return IdleGameState(
        char_ids=onsite,
        offsite_ids=offsite,
        standby_ids=standby,
        party_level=1,
        stacks=stack_map,
        plugins_by_id=_trinity_plugins(),
        rng=random.Random(7),
        passives_data=passives_data or RunSave().passives,
    )


def test_runtime_snapshot_exports_full_canonical_passives_and_active_runtime() -> None:
    save = RunSave()
    state = _build_trinity_state(passives_data=save.passives)

    snapshot = state.export_runtime_snapshot()

    passives = snapshot.get("passives")
    assert isinstance(passives, dict)
    assert passives == save.passives

    passive_runtime = snapshot.get("passive_runtime")
    assert isinstance(passive_runtime, dict)
    assert set(passive_runtime) == {
        "trinity_synergy",
        "lady_light_radiant_aegis",
        "lady_darkness_eclipsing_veil",
    }


def test_apply_log_soft_cap_is_linear_until_threshold_then_diminishes() -> None:
    below_threshold = apply_log_soft_cap(0.25)
    at_threshold = apply_log_soft_cap(0.5)
    above_threshold = apply_log_soft_cap(0.75)
    much_above_threshold = apply_log_soft_cap(2.0)

    assert math.isclose(below_threshold, 0.25, rel_tol=1e-12)
    assert math.isclose(at_threshold, 0.5, rel_tol=1e-12)
    assert 0.5 < above_threshold < 0.75
    assert above_threshold - 0.5 < 0.25
    assert much_above_threshold < 2.0


def test_trinity_gating_breaks_when_member_moves_to_standby() -> None:
    state = _build_trinity_state(
        offsite_ids=["lady_light"],
        standby_ids=["persona_light_and_dark"],
    )

    for _ in range(45):
        snapshot = state.process_tick()

    passives = snapshot["passives"]
    assert passives["trinity_synergy"]["stack_ttls"] == []
    assert passives["lady_darkness_eclipsing_veil"]["bleed_stack_ttls"] == []

    runtime = snapshot["passive_runtime"]
    assert runtime["trinity_synergy"]["active"] is False
    assert runtime["lady_light_radiant_aegis"]["active"] is False
    assert runtime["lady_darkness_eclipsing_veil"]["active"] is False


def test_trinity_stacks_build_on_30_tick_cadence_and_expire_independently() -> None:
    state = _build_trinity_state()

    for _ in range(450):
        snapshot = state.process_tick()

    trinity = snapshot["passives"]["trinity_synergy"]
    darkness = snapshot["passives"]["lady_darkness_eclipsing_veil"]
    assert len(trinity["stack_ttls"]) == 15
    assert len(darkness["bleed_stack_ttls"]) == 15
    assert min(trinity["stack_ttls"]) == 30
    assert max(trinity["stack_ttls"]) == 450
    assert min(darkness["bleed_stack_ttls"]) == 30
    assert max(darkness["bleed_stack_ttls"]) == 450

    snapshot = state.process_tick()
    trinity = snapshot["passives"]["trinity_synergy"]
    darkness = snapshot["passives"]["lady_darkness_eclipsing_veil"]
    assert len(trinity["stack_ttls"]) == 15
    assert len(darkness["bleed_stack_ttls"]) == 15
    assert min(trinity["stack_ttls"]) == 29
    assert max(trinity["stack_ttls"]) == 449
    assert min(darkness["bleed_stack_ttls"]) == 29
    assert max(darkness["bleed_stack_ttls"]) == 449


def test_trinity_state_round_trips_from_saved_ttl_lists() -> None:
    save = RunSave()
    save.passives["trinity_synergy"] = {
        "stack_ttls": [200, 12],
        "stack_progress_ticks": 9,
    }
    save.passives["lady_darkness_eclipsing_veil"] = {
        "bleed_stack_ttls": [101, 33],
        "bleed_progress_ticks": 4,
    }
    state = _build_trinity_state(passives_data=save.passives)

    snapshot = state.export_runtime_snapshot()
    assert snapshot["passives"]["trinity_synergy"] == {
        "stack_ttls": [200, 12],
        "stack_progress_ticks": 9,
    }
    assert snapshot["passives"]["lady_darkness_eclipsing_veil"] == {
        "bleed_stack_ttls": [101, 33],
        "bleed_progress_ticks": 4,
    }


def test_trinity_break_clears_saved_stacks_and_reform_restarts_from_zero() -> None:
    seeded = RunSave().passives
    seeded["trinity_synergy"] = {
        "stack_ttls": [200, 100],
        "stack_progress_ticks": 19,
    }
    seeded["lady_darkness_eclipsing_veil"] = {
        "bleed_stack_ttls": [210, 140],
        "bleed_progress_ticks": 11,
    }

    broken = _build_trinity_state(
        offsite_ids=["lady_light"],
        standby_ids=["persona_light_and_dark"],
        passives_data=seeded,
    )
    broken_snapshot = broken.process_tick()
    assert broken_snapshot["passives"]["trinity_synergy"] == {
        "stack_ttls": [],
        "stack_progress_ticks": 0,
    }
    assert broken_snapshot["passives"]["lady_darkness_eclipsing_veil"] == {
        "bleed_stack_ttls": [],
        "bleed_progress_ticks": 0,
    }

    restored = _build_trinity_state(passives_data=broken_snapshot["passives"])
    for _ in range(29):
        restored.process_tick()
    before_gain = restored.export_runtime_snapshot()["passives"]["trinity_synergy"]
    assert before_gain["stack_ttls"] == []
    assert before_gain["stack_progress_ticks"] == 29

    after_gain = restored.process_tick()["passives"]["trinity_synergy"]
    assert after_gain["stack_ttls"] == [450]
    assert after_gain["stack_progress_ticks"] == 0


def test_lady_light_uses_full_exp_multiplier_transfer_from_sources() -> None:
    state = _build_trinity_state()
    trinity_gain = state.get_exp_gain_per_tick("lady_light")
    broken_gain = _build_trinity_state(
        offsite_ids=["lady_light"],
        standby_ids=["persona_light_and_dark"],
    ).get_exp_gain_per_tick("lady_light")
    runtime = state.export_runtime_snapshot()["passive_runtime"]
    light_runtime = runtime["lady_light_radiant_aegis"]
    assert light_runtime["active"] is True
    assert math.isclose(
        float(light_runtime["source_dark_exp_multiplier"]),
        1.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )
    assert math.isclose(
        float(light_runtime["source_persona_exp_multiplier"]),
        1.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )
    assert math.isclose(
        float(light_runtime["base_transfer"]),
        1.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )
    assert math.isclose(
        float(light_runtime["exp_multiplier_bonus"]),
        1.05,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )
    assert trinity_gain > broken_gain


def test_trinity_mitigation_respects_runtime_passive_modifier() -> None:
    low_modifier = _build_trinity_state(
        stacks={
            "lady_darkness": 1,
            "lady_light": 1,
            "persona_light_and_dark": 1,
        }
    )
    boosted_modifier = _build_trinity_state(
        stacks={
            "lady_darkness": 1,
            "lady_light": 1,
            "persona_light_and_dark": 20,
        }
    )

    for _ in range(30):
        low_modifier.process_tick()
        boosted_modifier.process_tick()

    low_runtime = low_modifier.export_runtime_snapshot()["passive_runtime"][
        "trinity_synergy"
    ]
    boosted_runtime = boosted_modifier.export_runtime_snapshot()["passive_runtime"][
        "trinity_synergy"
    ]

    assert float(boosted_runtime["mitigation_percent"]) > float(
        low_runtime["mitigation_percent"]
    )


def test_lady_light_stack_bonus_fraction_grows_with_trinity_stacks() -> None:
    low_state = _build_trinity_state()
    high_state = _build_trinity_state()

    for _ in range(30):
        low_state.process_tick()
    for _ in range(300):
        high_state.process_tick()

    low_runtime = low_state.export_runtime_snapshot()["passive_runtime"][
        "lady_light_radiant_aegis"
    ]
    high_runtime = high_state.export_runtime_snapshot()["passive_runtime"][
        "lady_light_radiant_aegis"
    ]

    assert int(high_runtime["trinity_stack_count"]) > int(
        low_runtime["trinity_stack_count"]
    )
    assert float(high_runtime["stack_bonus_fraction"]) > float(
        low_runtime["stack_bonus_fraction"]
    )


def test_lady_darkness_bleed_respects_floor_and_converts_damage_to_exp_bonus() -> None:
    state = _build_trinity_state()

    for _ in range(30):
        snapshot = state.process_tick()

    runtime = snapshot["passive_runtime"]["lady_darkness_eclipsing_veil"]
    assert runtime["stack_count"] == 1
    assert float(runtime["hp_loss_fraction"]) > 0.0
    assert float(runtime["exp_multiplier_bonus"]) > 0.0

    light_data = state.get_char_data("lady_light")
    persona_data = state.get_char_data("persona_light_and_dark")
    assert isinstance(light_data, dict)
    assert isinstance(persona_data, dict)
    assert float(light_data["hp"]) >= float(light_data["max_hp"]) * 0.3
    assert float(persona_data["hp"]) >= float(persona_data["max_hp"]) * 0.3


def test_get_exp_gain_per_tick_refreshes_current_tick_passive_effects() -> None:
    state = _build_trinity_state()

    initial = state.get_exp_gain_per_tick("lady_darkness")
    for _ in range(30):
        state.process_tick()
    after_bleed = state.get_exp_gain_per_tick("lady_darkness")

    assert after_bleed > initial


def test_stateful_passives_tick_while_inactive_to_clear_stale_runtime() -> None:
    state = _build_trinity_state()

    for _ in range(30):
        state.process_tick()

    active_runtime = state.export_runtime_snapshot()["passive_runtime"]
    assert active_runtime["trinity_synergy"]["active"] is True
    assert active_runtime["lady_darkness_eclipsing_veil"]["active"] is True
    assert active_runtime["lady_light_radiant_aegis"]["active"] is True

    broken_state = _build_trinity_state(
        offsite_ids=["lady_light"],
        standby_ids=["persona_light_and_dark"],
        passives_data=state.export_runtime_snapshot()["passives"],
    )

    broken_snapshot = broken_state.process_tick()
    broken_runtime = broken_snapshot["passive_runtime"]

    assert broken_runtime["trinity_synergy"]["active"] is False
    assert broken_runtime["trinity_synergy"]["stack_count"] == 0
    assert broken_runtime["lady_darkness_eclipsing_veil"]["active"] is False
    assert broken_runtime["lady_darkness_eclipsing_veil"]["stack_count"] == 0
    assert broken_runtime["lady_light_radiant_aegis"]["active"] is False
    assert broken_runtime["lady_light_radiant_aegis"]["exp_multiplier_bonus"] == 0.0


def test_passive_bar_accessor_returns_only_displayable_active_bars() -> None:
    state = _build_trinity_state()

    trinity_bars = state.get_passive_bars_for_character("persona_light_and_dark")
    darkness_bars = state.get_passive_bars_for_character("lady_darkness")
    light_bars = state.get_passive_bars_for_character("lady_light")

    assert len(trinity_bars) == 1
    assert trinity_bars[0].passive_id == "trinity_synergy"
    assert trinity_bars[0].label == "Trinity"
    assert trinity_bars[0].style_id == "trinity"
    assert trinity_bars[0].dual_element_ids == ("dark", "light")
    assert math.isclose(trinity_bars[0].progress, 0.0, rel_tol=0.0, abs_tol=1e-9)
    assert trinity_bars[0].display_text == "0%"

    assert darkness_bars == []

    assert len(light_bars) == 1
    assert light_bars[0].passive_id == "lady_light_radiant_aegis"
    assert light_bars[0].label == "Aegis"
    assert light_bars[0].element_id == "light"
    assert light_bars[0].display_text == "1.05x EXP"


def test_passive_bar_accessor_uses_stack_power_fill_and_effect_text() -> None:
    state = _build_trinity_state()

    for _ in range(30):
        state.process_tick()

    trinity_bar = state.get_passive_bars_for_character("persona_light_and_dark")[0]
    darkness_bar = state.get_passive_bars_for_character("lady_darkness")[0]
    light_bar = state.get_passive_bars_for_character("lady_light")[0]

    assert math.isclose(trinity_bar.progress, 1.0 / 15.0, rel_tol=1e-9, abs_tol=1e-9)
    assert trinity_bar.display_text == "0.0105%"

    assert math.isclose(darkness_bar.progress, 1.0 / 15.0, rel_tol=1e-9, abs_tol=1e-9)
    assert darkness_bar.display_text == "0.5774%"

    assert math.isclose(light_bar.progress, 1.0 / 15.0, rel_tol=1e-9, abs_tol=1e-9)
    assert light_bar.display_text == "1.05x EXP"


def test_passive_bar_accessor_reaches_full_fill_at_sustained_stack_cap() -> None:
    state = _build_trinity_state()

    for _ in range(450):
        state.process_tick()

    trinity_bar = state.get_passive_bars_for_character("persona_light_and_dark")[0]
    darkness_bar = state.get_passive_bars_for_character("lady_darkness")[0]
    light_bar = state.get_passive_bars_for_character("lady_light")[0]

    assert math.isclose(trinity_bar.progress, 1.0, rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(darkness_bar.progress, 1.0, rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(light_bar.progress, 1.0, rel_tol=1e-9, abs_tol=1e-9)
