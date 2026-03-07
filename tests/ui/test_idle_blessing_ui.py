from __future__ import annotations

import math
import random

from types import SimpleNamespace

import endless_idler.ui.idle.screen as screen_module

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QProgressBar

from endless_idler.ui.idle.screen import IdleScreenWidget
from endless_idler.ui.idle.widgets import IdleOffsiteCard
from endless_idler.ui.onsite.card import OnsiteCharacterCardBase
from endless_idler.ui.idle.blessing_meter import IdleBlessingMeterWidget
from endless_idler.ui.idle.blessing_meter import _blend_factor_for_progress


class _FakeSignal:
    def connect(self, callback) -> None:  # noqa: ANN001
        del callback


class _FakeIdleState:
    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        del kwargs
        self.tick_update = _FakeSignal()
        self._shared_exp = 1
        self._rr = 0

    def process_tick(self) -> None:
        return

    def get_idle_blessing_step_count(self) -> int:
        return 0

    def get_idle_blessing_cycle_progress(self) -> float:
        return 0.0

    def get_idle_blessing_seconds_to_next_step(self) -> int:
        return 300

    def get_idle_blessing_multiplier(self) -> float:
        return 1.0

    def set_shared_exp_percentage(self, value: int) -> None:
        self._shared_exp = int(value)

    def get_shared_exp_percentage(self) -> int:
        return int(self._shared_exp)

    def set_risk_reward_level(self, value: int) -> None:
        self._rr = int(value)

    def get_risk_reward_level(self) -> int:
        return int(self._rr)


class _FakeSaveStore:
    def __init__(self, save: object) -> None:
        self._current = save
        self.persist_calls = 0

    @property
    def current(self) -> object:
        return self._current

    def persist(self) -> None:
        self.persist_calls += 1


class _FakeIdleStateForOffsite:
    def __init__(self) -> None:
        self._data: dict[str, float] = {
            "level": 7.0,
            "exp": 12.0,
            "next_exp": 30.0,
            "hp": 90.0,
            "max_hp": 100.0,
            "exp_multiplier": 1.0,
        }

    def get_char_data(self, char_id: str) -> dict[str, float]:
        del char_id
        return dict(self._data)

    def get_exp_gain_per_second(self, char_id: str) -> float:
        del char_id
        return 0.0


def test_blessing_blend_factor_boundaries() -> None:
    assert _blend_factor_for_progress(0.50) == 0.0
    assert math.isclose(_blend_factor_for_progress(0.575), 0.5, rel_tol=0.0, abs_tol=1e-12)
    assert _blend_factor_for_progress(0.65) == 1.0


def test_blessing_meter_animation_timer_starts_and_settles() -> None:
    _ = QApplication.instance() or QApplication([])

    meter = IdleBlessingMeterWidget()
    meter.set_visual_state(progress=0.60, shimmer=1.0, reset_active=False)
    assert meter._frame_timer.isActive()

    phase_before = meter._shimmer_phase
    meter._on_animation_frame()
    assert meter._display_shimmer > 0.0
    assert meter._shimmer_phase != phase_before

    meter.set_visual_state(progress=meter._display_progress, shimmer=0.0, reset_active=False)
    for _ in range(180):
        if not meter._frame_timer.isActive():
            break
        meter._on_animation_frame()

    assert meter._display_shimmer <= 0.01
    assert not meter._frame_timer.isActive()


def test_idle_screen_panel_order_and_tooltip_text(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    fake_save = SimpleNamespace(
        onsite=[],
        offsite=[],
        stacks={},
        party_level=1,
        character_progress={},
        character_stats={},
        character_initial_stats={},
        idle_exp_bonus_seconds=0.0,
        idle_exp_penalty_seconds=0.0,
        idle_shared_exp_percentage=1,
        idle_risk_reward_level=0,
        battle_start_time=0.0,
        party_hp_current=1,
        party_hp_max=1,
    )

    monkeypatch.setattr(screen_module, "start_idle_heal_timer", lambda save: None)
    monkeypatch.setattr(screen_module, "discover_character_plugins", lambda: [])
    monkeypatch.setattr(screen_module, "IdleGameState", _FakeIdleState)

    screen = IdleScreenWidget(save_store=_FakeSaveStore(save=fake_save))

    blessing_panel = screen.findChild(QFrame, "idleBlessingPanel")
    mods_panel = screen.findChild(QFrame, "idleModsPanel")

    assert blessing_panel is not None
    assert mods_panel is not None

    parent = blessing_panel.parentWidget()
    assert parent is not None
    column_layout = parent.layout()
    assert column_layout is not None
    assert column_layout.indexOf(blessing_panel) < column_layout.indexOf(mods_panel)

    tooltip = screen._build_blessing_tooltip(multiplier=1.0, steps=0, seconds_to_next=300)
    assert "Applies to onsite source EXP gain only" not in tooltip
    assert "Offsite receives indirect bonus" not in tooltip


def test_idle_onsite_name_includes_level_and_stack_ui_removed() -> None:
    _ = QApplication.instance() or QApplication([])

    card = OnsiteCharacterCardBase(
        name="Nova",
        portrait_path=None,
        placeholder="Nova",
        stack_count=4,
        team_side="left",
        mode="idle",
        portrait_size=(32, 32),
        card_width=220,
    )

    assert card.findChild(QLabel, "onsiteStackPlus") is None
    assert card.findChild(QLabel, "onsiteCharStack") is None
    assert card.findChild(QLabel, "onsiteCharLevel") is None

    card.set_level(9)
    name_label = card.findChild(QLabel, "onsiteCharName")
    assert name_label is not None
    assert name_label.text() == "Nova (9)"


def test_idle_offsite_name_includes_level_and_stack_ui_removed() -> None:
    _ = QApplication.instance() or QApplication([])

    card = IdleOffsiteCard(
        char_id="offsite_hero",
        plugin=None,
        idle_state=_FakeIdleStateForOffsite(),
        rng=random.Random(3),
        stack_count=5,
    )
    card.update_display()

    assert card.findChild(QLabel, "idleStackPlus") is None
    assert card.findChild(QLabel, "idleOffsiteLevel") is None

    name_label = card.findChild(QLabel, "idleOffsiteName")
    assert name_label is not None
    assert name_label.text() == "offsite_hero (7)"


def test_idle_offsite_portrait_is_bottom_aligned_and_auto_sizes_to_target() -> None:
    _ = QApplication.instance() or QApplication([])

    card = IdleOffsiteCard(
        char_id="offsite_hero",
        plugin=None,
        idle_state=_FakeIdleStateForOffsite(),
        rng=random.Random(3),
        stack_count=1,
    )

    portrait = card.findChild(QLabel, "idleOffsitePortrait")
    assert portrait is not None
    assert portrait.width() == 72
    assert portrait.height() == 72

    root_layout = card.layout()
    assert root_layout is not None
    first_item = root_layout.itemAt(0)
    alignment = first_item.alignment()
    assert int(alignment & Qt.AlignmentFlag.AlignBottom) != 0
    assert int(alignment & Qt.AlignmentFlag.AlignVCenter) == 0
    assert int(alignment & Qt.AlignmentFlag.AlignTop) == 0

    card.setFixedSize(180, 80)
    card.resize(180, 80)
    card._apply_portrait_size()
    assert 56 <= portrait.width() <= 72
    assert 56 <= portrait.height() <= 72


def test_idle_bars_are_bottom_anchored_for_onsite_and_offsite() -> None:
    _ = QApplication.instance() or QApplication([])

    offsite = IdleOffsiteCard(
        char_id="offsite_hero",
        plugin=None,
        idle_state=_FakeIdleStateForOffsite(),
        rng=random.Random(3),
        stack_count=1,
    )
    offsite_body = offsite.layout().itemAt(1).layout()
    assert offsite_body is not None
    offsite_last = offsite_body.itemAt(offsite_body.count() - 1).widget()
    offsite_second_last = offsite_body.itemAt(offsite_body.count() - 2).widget()
    assert isinstance(offsite_second_last, QProgressBar)
    assert isinstance(offsite_last, QProgressBar)
    assert offsite_second_last.objectName() == "idleHpBar"
    assert offsite_last.objectName() == "idleExpBar"

    onsite_idle = OnsiteCharacterCardBase(
        name="Nova",
        portrait_path=None,
        placeholder="Nova",
        stack_count=1,
        team_side="left",
        mode="idle",
        portrait_size=(32, 32),
        card_width=220,
    )
    onsite_body = onsite_idle.layout().itemAt(1).layout()
    assert onsite_body is not None
    onsite_last = onsite_body.itemAt(onsite_body.count() - 1).widget()
    onsite_second_last = onsite_body.itemAt(onsite_body.count() - 2).widget()
    assert isinstance(onsite_second_last, QProgressBar)
    assert isinstance(onsite_last, QProgressBar)
    assert onsite_second_last.objectName() == "onsiteHpBar"
    assert onsite_last.objectName() == "onsiteExpBar"
