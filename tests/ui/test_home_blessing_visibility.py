from __future__ import annotations

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QWidget

from endless_idler.blessings.registry import get_blessing_by_id
from endless_idler.save import RunSave
from endless_idler.ui.home import HomePage
from endless_idler.ui.theme.colors import color_for_damage_type_id


class _FakeSaveStore:
    current: RunSave

    def __init__(self, save: RunSave) -> None:
        self.current = save


class _FakeIdleState:
    def __init__(self, save: RunSave) -> None:
        self._save = save

    def get_char_data(self, char_id: str) -> dict[str, object]:
        if char_id not in self._save.onsite and char_id not in self._save.offsite:
            return {}
        return {
            "level": 7,
            "exp": 12.0,
            "next_exp": 30.0,
            "hp": 90.0,
            "max_hp": 100.0,
            "exp_multiplier": 1.0,
        }

    def get_party_level(self) -> int:
        return 1

    def get_exp_gain_per_second(self, char_id: str) -> float:
        del char_id
        return 0.0

    def get_misplacement_stat_multiplier(self, char_id: str) -> float:
        del char_id
        return 1.0

    def get_misplacement_exp_multiplier(self, char_id: str) -> float:
        del char_id
        return 1.0

    def get_passive_bars_for_character(self, char_id: str) -> list[object]:
        del char_id
        return []

    def export_runtime_snapshot(self) -> dict[str, object]:
        return {
            "progress": {},
            "character_stats": {},
            "initial_stats": {},
            "blessings": dict(self._save.blessings),
            "passives": dict(self._save.passives),
            "exp_bonus_seconds": 0.0,
            "exp_penalty_seconds": 0.0,
            "shared_exp_percentage": 1,
            "risk_reward_level": 0,
        }


def test_lunar_blessing_visible_when_save_entry_missing() -> None:
    _ = QApplication.instance() or QApplication([])

    save = RunSave()
    _ = save.blessings.pop("lunar_blessing", None)
    page = HomePage(save_store=_FakeSaveStore(save))
    page._update_timer.stop()

    assert "lunar_blessing" in page._blessing_panels
    assert page._update_timer.interval() == 33


def test_lunar_blessing_hidden_when_explicitly_locked() -> None:
    _ = QApplication.instance() or QApplication([])

    save = RunSave()
    save.blessings.setdefault("lunar_blessing", {})["unlocked"] = False
    page = HomePage(save_store=_FakeSaveStore(save))
    page._update_timer.stop()

    assert "lunar_blessing" not in page._blessing_panels


def test_lunar_blessing_visible_with_missing_unlock_field() -> None:
    _ = QApplication.instance() or QApplication([])

    save = RunSave()
    save.blessings["lunar_blessing"] = {"steps": 0}
    page = HomePage(save_store=_FakeSaveStore(save))
    page._update_timer.stop()

    assert "lunar_blessing" in page._blessing_panels


def test_odyssey_tooltip_polish_fields() -> None:
    plugin = get_blessing_by_id("odyssey_blessing")
    assert plugin is not None

    tooltip = plugin.format_tooltip(
        0, {"runtime": {"steps": 0, "progress": 0.25, "countdown_seconds": 299}}
    )
    assert "EXP gain:" in tooltip
    assert "Progress:" in tooltip
    assert "Step:" not in tooltip
    assert "Countdown:" not in tooltip
    assert "Weeks:" not in tooltip


def test_damage_type_blessing_bar_uses_element_color() -> None:
    _ = QApplication.instance() or QApplication([])

    save = RunSave()
    save.blessings["fire_blessing"] = {"unlocked": True, "steps": 0}
    page = HomePage(save_store=_FakeSaveStore(save))
    page._update_timer.stop()

    fire_panel = page._blessing_panels["fire_blessing"]
    fire_color = color_for_damage_type_id("fire")
    expected_fire_rgba = (
        fire_color.red(),
        fire_color.green(),
        fire_color.blue(),
        170,
    )

    assert fire_panel.property("elementId") == "fire"
    assert fire_panel._progress_bar._color_thresholds == [
        (0.0, expected_fire_rgba),
        (0.5, expected_fire_rgba),
        (1.0, expected_fire_rgba),
    ]

    lunar_panel = page._blessing_panels["lunar_blessing"]
    assert lunar_panel.property("elementId") == "lunar"
    assert lunar_panel._progress_bar._color_thresholds == []


def test_home_upgrades_tab_shows_compact_cards() -> None:
    _ = QApplication.instance() or QApplication([])

    save = RunSave()
    save.onsite = ["luna"]
    save.offsite = ["atlas"]
    save.stacks = {"luna": 2, "atlas": 1}
    page = HomePage(
        save_store=_FakeSaveStore(save),
        idle_state_provider=lambda: _FakeIdleState(save),
    )
    page._update_timer.stop()

    page._tabs.setCurrentIndex(1)
    page._update_home_display()

    assert page._content_stack.currentIndex() == 1
    cards = page._upgrade_cards
    assert len(cards) == 2
    assert all(card.width() == 420 for card in cards)
    assert all(card.findChild(QWidget, "idleExpBar").isHidden() for card in cards)
