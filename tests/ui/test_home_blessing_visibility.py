from __future__ import annotations

from PySide6.QtWidgets import QApplication

from endless_idler.blessings.registry import get_blessing_by_id
from endless_idler.save import RunSave
from endless_idler.ui.home import HomePage
from endless_idler.ui.theme.colors import color_for_damage_type_id


class _FakeSaveStore:
    current: RunSave

    def __init__(self, save: RunSave) -> None:
        self.current = save


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
