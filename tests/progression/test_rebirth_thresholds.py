from __future__ import annotations

import math
import random

from pathlib import Path

import pytest

import endless_idler.characters.plugins as plugin_module

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.progression import calculate_prestige_stat_gain_rate
from endless_idler.progression import calculate_rebirth_exp_mult_gain
from endless_idler.progression import calculate_rebirth_exp_tax
from endless_idler.progression import calculate_rebirth_power
from endless_idler.progression import progression_star_multiplier
from endless_idler.progression import REBIRTH_LEVEL_THRESHOLD
from endless_idler.ui.idle.idle_state import IdleGameState
from endless_idler.ui.idle.screen import build_prestige_confirmation_html


def _plugin(*, char_id: str = "hero", stars: int = 6) -> CharacterPlugin:
    return CharacterPlugin(
        char_id=char_id,
        display_name=char_id.title(),
        stars=stars,
        placement="onsite",
    )


def _state(
    *,
    stars: int,
    progress_by_id: dict[str, dict[str, float | int]] | None = None,
) -> IdleGameState:
    return IdleGameState(
        char_ids=["hero"],
        offsite_ids=[],
        party_level=1,
        stacks={"hero": 1},
        plugins_by_id={"hero": _plugin(stars=stars)},
        rng=random.Random(7),
        progress_by_id=progress_by_id,
    )


def test_progression_star_multiplier_mapping() -> None:
    assert progression_star_multiplier(5) == 0.5
    assert progression_star_multiplier(6) == 1.0
    assert progression_star_multiplier(7) == 2.5


def test_progression_star_multiplier_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="expected one of 5, 6, 7"):
        progression_star_multiplier(4)


def test_discover_character_plugins_raises_aggregated_value_error_for_invalid_runtime_stars(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = (tmp_path / "alpha.py").write_text(
        "class Alpha:\n"
        + "    id = 'alpha'\n"
        + "    name = 'Alpha'\n"
        + "    gacha_rarity = 4\n",
        encoding="utf-8",
    )
    _ = (tmp_path / "omega.py").write_text(
        "class Omega:\n"
        + "    id = 'omega'\n"
        + "    name = 'Omega'\n"
        + "    gacha_rarity = 8\n",
        encoding="utf-8",
    )
    _ = (tmp_path / "valid.py").write_text(
        "class Valid:\n"
        + "    id = 'valid'\n"
        + "    name = 'Valid'\n"
        + "    gacha_rarity = 6\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(plugin_module, "_CHARACTERS_DIR", tmp_path)

    with pytest.raises(
        ValueError, match="Invalid progression stars for runtime character plugins"
    ):
        _ = discover_character_plugins()

    message = ""
    try:
        discover_character_plugins()
    except ValueError as exc:
        message = str(exc)
    else:
        pytest.fail(
            "discover_character_plugins() should have raised ValueError for invalid stars"
        )

    assert "alpha=4 (alpha.py)" in message
    assert "omega=8 (omega.py)" in message


def test_discover_character_plugins_accepts_valid_runtime_stars(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for char_id, stars in (("five", 5), ("six", 6), ("seven", 7)):
        _ = (tmp_path / f"{char_id}.py").write_text(
            "class Character:\n"
            + f"    id = '{char_id}'\n"
            + f"    name = '{char_id.title()}'\n"
            + f"    gacha_rarity = {stars}\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(plugin_module, "_CHARACTERS_DIR", tmp_path)

    plugins = discover_character_plugins()

    assert [plugin.char_id for plugin in plugins] == ["five", "seven", "six"]
    assert [plugin.stars for plugin in plugins] == [5, 7, 6]


@pytest.mark.parametrize("stars", [5, 6, 7])
def test_rebirth_character_applies_star_weighted_exp_reward_gain(stars: int) -> None:
    state = _state(
        stars=stars,
        progress_by_id={"hero": {"level": 510, "exp_multiplier": 1.0}},
    )

    assert state.rebirth_character("hero") is True

    data = state.get_char_data("hero")
    assert data is not None
    expected_power = calculate_rebirth_power(510)
    expected_gain = calculate_rebirth_exp_mult_gain(power=expected_power, stars=stars)

    assert math.isclose(
        float(data["rebirth_power"]), expected_power, rel_tol=1e-9, abs_tol=1e-9
    )
    assert math.isclose(
        float(data["exp_multiplier"]), 1.0 + expected_gain, rel_tol=1e-9, abs_tol=1e-9
    )
    assert int(data["rebirths"]) == 1


def test_rebirth_character_requires_level_500() -> None:
    locked_state = _state(
        stars=6,
        progress_by_id={"hero": {"level": REBIRTH_LEVEL_THRESHOLD - 1}},
    )
    unlocked_state = _state(
        stars=6,
        progress_by_id={"hero": {"level": REBIRTH_LEVEL_THRESHOLD}},
    )

    assert locked_state.rebirth_character("hero") is False
    assert unlocked_state.rebirth_character("hero") is True


def test_rebirth_tax_stays_baseline_until_tax_starts_and_then_eases() -> None:
    assert (
        calculate_rebirth_exp_tax(
            level=REBIRTH_LEVEL_THRESHOLD + 4,
            rebirth_power=1.0,
            stars=7,
        )
        == 1.0
    )

    tax_six = calculate_rebirth_exp_tax(
        level=REBIRTH_LEVEL_THRESHOLD + 5,
        rebirth_power=1.0,
        stars=6,
    )
    tax_seven = calculate_rebirth_exp_tax(
        level=REBIRTH_LEVEL_THRESHOLD + 5,
        rebirth_power=1.0,
        stars=7,
    )

    assert tax_six > 1.01
    assert tax_seven > 1.01
    assert tax_seven < tax_six


def test_prestige_weighting_changes_gain_magnitude_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _state(
        stars=7,
        progress_by_id={"hero": {"prestige_count": 1}},
    )
    data = state.get_char_data("hero")
    assert data is not None

    base_stats = {
        "atk": 100.0,
        "defense": 100.0,
        "crit_mod": 100.0,
        "dodge_odds": 0.05,
        "regain": 100.0,
    }
    monkeypatch.setattr(state._rng, "choices", lambda population, weights, k: ["atk"])

    state._apply_weighted_stat_upgrades(char_id="hero", base_stats=base_stats, level=1)

    expected_rate = calculate_prestige_stat_gain_rate(prestige_count=1, stars=7)
    assert math.isclose(
        base_stats["atk"], 100.0 * (1.0 + expected_rate), rel_tol=1e-9, abs_tol=1e-9
    )


def test_build_prestige_confirmation_html_uses_weighted_stat_gain_rate() -> None:
    html = build_prestige_confirmation_html(
        display_name="Hero",
        exp_multiplier=10.0,
        prestige_count=1,
        stars=7,
    )

    assert "Weighted Stat Gain Rate" in html
    assert "+0.50% \u2192 +1.00%" in html
    assert "double" not in html
