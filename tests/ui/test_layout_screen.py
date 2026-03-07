from __future__ import annotations

from PySide6.QtWidgets import QApplication

import endless_idler.ui.layout.screen as layout_module

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.save import STANDBY_SLOTS
from endless_idler.save import RunSave
from endless_idler.ui.layout.screen import LayoutScreenWidget


class _FakeSaveManager:
    def __init__(self, save: RunSave) -> None:
        self._save = save
        self.save_calls = 0

    def load(self) -> RunSave:
        return self._save

    def save(self, value: RunSave) -> None:
        self.save_calls += 1
        self._save = value


def _plugin(char_id: str, placement: str, stars: int) -> CharacterPlugin:
    return CharacterPlugin(
        char_id=char_id,
        display_name=char_id,
        placement=placement,
        stars=stars,
    )


def _save_with_unassigned(*char_ids: str) -> RunSave:
    save = RunSave(layout_owned_ordering="rarity_desc")
    standby = [None] * STANDBY_SLOTS
    for offset, char_id in enumerate(char_ids, start=1):
        if offset >= STANDBY_SLOTS - 1:
            break
        standby[offset] = char_id
    save.standby = standby
    return save


def test_layout_screen_uses_saved_order_setting(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_manager = _FakeSaveManager(_save_with_unassigned("lady_darkness", "persona_light_and_dark"))
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("lady_darkness", "onsite", 5),
            _plugin("persona_light_and_dark", "both", 6),
        ],
    )

    screen = LayoutScreenWidget()
    assert screen._ordering_combo.currentData() == "rarity_desc"
    screen.deleteLater()


def test_layout_screen_move_and_autosave_sets_tick_cooldown(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_manager = _FakeSaveManager(_save_with_unassigned("lady_darkness"))
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("lady_darkness", "onsite", 5),
            _plugin("persona_light_and_dark", "both", 6),
        ],
    )

    screen = LayoutScreenWidget()
    assert screen._move_from_unassigned_to_slot(
        char_id="lady_darkness",
        target_lane="onsite",
        target_index=0,
    )
    assert screen._save.onsite[0] == "lady_darkness"
    assert "lady_darkness" not in screen._standby_ids()

    screen._schedule_persist("Saving layout...")
    screen._persist_layout()

    assert screen._save.layout_tick_cooldown_seconds == layout_module.LAYOUT_TICK_COOLDOWN_SECONDS
    assert fake_manager.save_calls >= 2
    screen.deleteLater()
