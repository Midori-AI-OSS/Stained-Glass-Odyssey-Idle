from __future__ import annotations

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QWidget

import endless_idler.ui.layout.screen as layout_module

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.save import STANDBY_SLOTS
from endless_idler.save import RunSave
from endless_idler.ui.layout.screen import LayoutScreenWidget
from endless_idler.ui.theme.layout_screen_widget import STYLESHEET as LAYOUT_SCREEN_STYLESHEET


class _FakeSaveManager:
    def __init__(self, save: RunSave) -> None:
        self._save = save
        self.save_calls = 0

    def load(self) -> RunSave:
        return self._save

    def save(self, value: RunSave) -> None:
        self.save_calls += 1
        self._save = value


class _FakeIdleState:
    def __init__(self, *, by_id: dict[str, dict[str, object]], party_level: int) -> None:
        self._by_id = by_id
        self._party_level = party_level

    def get_char_data(self, char_id: str) -> dict[str, object] | None:
        data = self._by_id.get(char_id)
        return dict(data) if isinstance(data, dict) else None

    def get_party_level(self) -> int:
        return self._party_level


class _FakeIdleScreen:
    def __init__(self, idle_state: _FakeIdleState) -> None:
        self._idle_state = idle_state


def _plugin(char_id: str, placement: str, stars: int, *, damage_type_id: str = "generic") -> CharacterPlugin:
    return CharacterPlugin(
        char_id=char_id,
        display_name=char_id,
        placement=placement,
        stars=stars,
        damage_type_id=damage_type_id,
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
    assert screen._ordering_key() == "rarity_desc"
    assert screen._ordering_cycle_button is not None
    assert screen._ordering_cycle_button.property("orderMode") == "rarity_desc"
    assert screen._ordering_cycle_button.text() == "Sort: Rarity"
    assert screen._ordering_cycle_button.parent() is screen._unassigned_panel
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


def test_layout_order_cycle_button_updates_saved_order(monkeypatch) -> None:
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
    assert screen._ordering_cycle_button is not None
    screen._ordering_cycle_button.click()

    assert screen._ordering_key() == "alphabetical"
    assert screen._save.layout_owned_ordering == "alphabetical"
    assert screen._ordering_cycle_button.property("orderMode") == "alphabetical"
    assert screen._ordering_cycle_button.text() == "Sort: A-Z"
    screen.deleteLater()


def test_layout_standby_renders_only_populated_cards(monkeypatch) -> None:
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
    standby_slots = [
        frame
        for frame in screen.findChildren(QFrame)
        if frame.objectName() == "LayoutStandbySlot"
    ]
    assert not standby_slots
    placeholders = [
        label
        for label in screen.findChildren(QLabel)
        if label.objectName() == "LayoutStandbySlotPlaceholder"
    ]
    assert not placeholders
    standby_chips = [
        frame
        for frame in screen.findChildren(QFrame)
        if frame.objectName() == "LayoutCharacterChip"
        and frame.property("layoutChipRole") == "unassigned"
    ]
    assert len(standby_chips) == 2
    screen.deleteLater()


def test_layout_lane_rows_use_fixed_onsite_offsite_box_counts(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_manager = _FakeSaveManager(_save_with_unassigned())
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
    assert len(screen._onsite_slots) == 4
    assert len(screen._offsite_slots) == 6
    assert all(slot.width() == layout_module.LAYOUT_SLOT_WIDTH for slot in screen._onsite_slots)
    assert all(slot.width() == layout_module.LAYOUT_SLOT_WIDTH for slot in screen._offsite_slots)
    screen.deleteLater()


def test_layout_applies_damage_type_outline_properties_to_slot_and_chip(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_manager = _FakeSaveManager(_save_with_unassigned("arcane_char"))
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("arcane_char", "onsite", 5, damage_type_id="arcane"),
        ],
    )

    screen = LayoutScreenWidget()
    assert screen._move_from_unassigned_to_slot(
        char_id="arcane_char",
        target_lane="onsite",
        target_index=0,
    )
    screen._refresh_views()

    slot = screen._onsite_slots[0]
    assert slot.property("elementId") == "arcane"

    chips = [child for child in slot.findChildren(QFrame) if child.objectName() == "LayoutCharacterChip"]
    assert chips
    assert chips[0].property("elementId") == "arcane"
    effect = chips[0].graphicsEffect()
    assert isinstance(effect, QGraphicsDropShadowEffect)
    color = effect.color()
    assert (color.red(), color.green(), color.blue()) == (255, 80, 200)
    screen.deleteLater()


def test_layout_unassigned_includes_owned_characters_not_in_standby_slots(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    save = _save_with_unassigned("lady_darkness")
    save.character_progress["water_char"] = {"level": 1, "exp": 0.0, "next_exp": 30.0}
    fake_manager = _FakeSaveManager(save)
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("lady_darkness", "onsite", 5),
            _plugin("water_char", "offsite", 4, damage_type_id="water"),
        ],
    )

    screen = LayoutScreenWidget()
    ordered = screen._ordered_unassigned_ids()
    assert "lady_darkness" in ordered
    assert "water_char" in ordered
    screen.deleteLater()


def test_layout_standby_panel_uses_compact_fixed_height(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_manager = _FakeSaveManager(_save_with_unassigned("lady_darkness"))
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("lady_darkness", "onsite", 5),
        ],
    )

    screen = LayoutScreenWidget()
    panel = screen._unassigned_panel
    assert panel.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Fixed
    assert panel.minimumHeight() == panel.maximumHeight()
    assert panel.height() == layout_module.LAYOUT_STANDBY_PANEL_HEIGHT
    assert layout_module.LAYOUT_STANDBY_PANEL_HEIGHT == layout_module.LAYOUT_STANDBY_SLOT_HEIGHT + 60
    screen.deleteLater()


def test_layout_standby_hides_autosave_status_text(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_manager = _FakeSaveManager(_save_with_unassigned("lady_darkness"))
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("lady_darkness", "onsite", 5),
        ],
    )

    screen = LayoutScreenWidget()
    labels = [label for label in screen.findChildren(QLabel) if label.text() == "Autosave enabled"]
    save_status_widgets = [
        label for label in screen.findChildren(QLabel) if label.objectName() == "LayoutSaveStatus"
    ]
    assert not labels
    assert not save_status_widgets
    screen.deleteLater()


def test_layout_chip_shows_old_shop_placement_marker(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_manager = _FakeSaveManager(_save_with_unassigned("offsite_char"))
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("offsite_char", "offsite", 4, damage_type_id="water"),
        ],
    )

    screen = LayoutScreenWidget()
    chips = [child for child in screen.findChildren(QFrame) if child.objectName() == "LayoutCharacterChip"]
    assert chips
    squares = [child for child in chips[0].findChildren(QFrame) if child.objectName() == "LayoutPlacementSquare"]
    assert len(squares) == 2

    onsite_marker = next(square for square in squares if square.property("placementSlot") == "onsite")
    offsite_marker = next(square for square in squares if square.property("placementSlot") == "offsite")
    assert onsite_marker.property("filled") is False
    assert offsite_marker.property("filled") is True
    screen.deleteLater()


def test_layout_slot_constants_apply_large_size_bump() -> None:
    assert layout_module.LAYOUT_SLOT_WIDTH == 124
    assert layout_module.LAYOUT_SLOT_HEIGHT == 144


def test_layout_theme_uses_white_markers_and_no_inner_chip_outline() -> None:
    assert "QFrame#LayoutCharacterChip {" in LAYOUT_SCREEN_STYLESHEET
    assert "border: 0px;" in LAYOUT_SCREEN_STYLESHEET
    assert 'QFrame#LayoutPlacementSquare[filled="true"]' in LAYOUT_SCREEN_STYLESHEET
    assert "background-color: rgba(255, 255, 255, 215);" in LAYOUT_SCREEN_STYLESHEET
    assert 'placementSlot="onsite"][filled="true"]' not in LAYOUT_SCREEN_STYLESHEET
    assert 'placementSlot="offsite"][filled="true"]' not in LAYOUT_SCREEN_STYLESHEET


def test_layout_chip_uses_stained_tooltip_only(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_manager = _FakeSaveManager(_save_with_unassigned("lady_darkness"))
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("lady_darkness", "onsite", 5),
        ],
    )

    screen = LayoutScreenWidget()
    chips = [child for child in screen.findChildren(QFrame) if child.objectName() == "LayoutCharacterChip"]
    assert chips
    assert chips[0].toolTip() == ""
    screen.deleteLater()


def test_layout_chip_tooltip_refreshes_from_current_save_data(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    save = _save_with_unassigned("lady_darkness")
    save.character_progress["lady_darkness"] = {"level": 1, "exp": 0.0, "next_exp": 30.0}
    fake_manager = _FakeSaveManager(save)
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("lady_darkness", "onsite", 5),
        ],
    )

    tooltip_calls: list[tuple[str, str | None]] = []

    def _capture_tooltip(_owner, html: str, *, element_id: str | None = None) -> None:
        tooltip_calls.append((html, element_id))

    monkeypatch.setattr(layout_module, "show_stained_tooltip", _capture_tooltip)
    monkeypatch.setattr(layout_module, "hide_stained_tooltip", lambda: None)

    screen = LayoutScreenWidget()
    chips = [child for child in screen.findChildren(QFrame) if child.objectName() == "LayoutCharacterChip"]
    assert chips
    chip = chips[0]

    chip._show_tooltip()
    first_html = tooltip_calls[-1][0]

    screen._save.character_progress["lady_darkness"] = {
        "level": 7,
        "exp": 56.0,
        "next_exp": 90.0,
        "exp_multiplier": 2.0,
    }
    screen._save.stacks["lady_darkness"] = 3
    chip._show_tooltip()
    second_html = tooltip_calls[-1][0]

    assert first_html != second_html
    assert "x3" in second_html
    assert chip._tooltip_refresh_timer.interval() == layout_module.LAYOUT_TOOLTIP_REFRESH_INTERVAL_MS
    screen.deleteLater()


def test_layout_chip_tooltip_prefers_live_idle_state_data(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    save = _save_with_unassigned("lady_darkness")
    save.character_progress["lady_darkness"] = {"level": 1, "exp": 0.0, "next_exp": 30.0}
    save.stacks["lady_darkness"] = 1
    fake_manager = _FakeSaveManager(save)
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("lady_darkness", "onsite", 5),
        ],
    )

    live_idle_state = _FakeIdleState(
        by_id={
            "lady_darkness": {
                "level": 9,
                "exp": 120.0,
                "exp_multiplier": 3.0,
                "max_hp_level_bonus_version": 0,
                "stack": 4,
                "base_stats": {},
                "hp": 777,
            }
        },
        party_level=12,
    )
    host = QWidget()
    host._idle_screen = _FakeIdleScreen(live_idle_state)

    screen = LayoutScreenWidget(parent=host)
    plugin = screen._plugin_by_id["lady_darkness"]
    html, _ = screen._build_tooltip_data("lady_darkness", plugin)
    assert "x4" in html
    assert ">9<" in html
    screen.deleteLater()
    host.deleteLater()


def test_layout_chip_child_enter_event_triggers_tooltip_refresh(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_manager = _FakeSaveManager(_save_with_unassigned("lady_darkness"))
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("lady_darkness", "onsite", 5),
        ],
    )

    tooltip_calls: list[str] = []

    def _capture_tooltip(_owner, html: str, *, element_id: str | None = None) -> None:
        del element_id
        tooltip_calls.append(html)

    monkeypatch.setattr(layout_module, "show_stained_tooltip", _capture_tooltip)
    monkeypatch.setattr(layout_module, "hide_stained_tooltip", lambda: None)

    screen = LayoutScreenWidget()
    chips = [child for child in screen.findChildren(QFrame) if child.objectName() == "LayoutCharacterChip"]
    assert chips
    chip = chips[0]
    name_label = next(
        label for label in chip.findChildren(QLabel) if label.objectName() == "LayoutCharacterName"
    )

    chip.eventFilter(name_label, QEvent(QEvent.Type.Enter))
    assert tooltip_calls
    screen.deleteLater()


def test_layout_chip_refresh_loop_stops_when_not_hovered(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_manager = _FakeSaveManager(_save_with_unassigned("lady_darkness"))
    monkeypatch.setattr(layout_module, "SaveManager", lambda: fake_manager)
    monkeypatch.setattr(
        layout_module,
        "discover_character_plugins",
        lambda: [
            _plugin("lady_darkness", "onsite", 5),
        ],
    )

    hide_calls: list[None] = []
    monkeypatch.setattr(layout_module, "show_stained_tooltip", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(layout_module, "hide_stained_tooltip", lambda: hide_calls.append(None))

    screen = LayoutScreenWidget()
    chips = [child for child in screen.findChildren(QFrame) if child.objectName() == "LayoutCharacterChip"]
    assert chips
    chip = chips[0]
    chip._tooltip_refresh_timer.start()
    chip._refresh_tooltip_while_hovered()
    assert not chip._tooltip_refresh_timer.isActive()
    assert hide_calls
    screen.deleteLater()
