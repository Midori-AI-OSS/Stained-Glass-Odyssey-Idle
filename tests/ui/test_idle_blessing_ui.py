from __future__ import annotations

import math
import random

from types import SimpleNamespace

import endless_idler.ui.cards.character_card as character_card_module
import endless_idler.ui.idle.screen as screen_module

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.ui.cards import IdleCharacterCard
from endless_idler.ui.components.progress_bar import AnimatedProgressBar
from endless_idler.ui.idle.blessing_meter import IdleBlessingMeterWidget
from endless_idler.ui.idle.blessing_meter import _blend_factor_for_progress
from endless_idler.ui.idle.screen import IdleScreenWidget
from endless_idler.ui.party_builder_common import MISMATCH_TOOLTIP_VALUE_COLOR
from endless_idler.ui.widgets.passive_progress_bar import PassiveProgressBar


class _FakeSignal:
    def connect(self, callback) -> None:
        del callback


class _FakeIdleState:
    def __init__(self, **kwargs) -> None:
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

    def persist(self, *, force: bool = False) -> None:
        del force
        self.persist_calls += 1


class _FakeIdleStateForCard:
    def __init__(
        self,
        *,
        misplacement_stat_multiplier: float = 1.0,
        misplacement_exp_multiplier: float = 1.0,
        exp_gain_per_second: float = 0.0,
    ) -> None:
        self._data: dict[str, float] = {
            "level": 7.0,
            "exp": 12.0,
            "next_exp": 30.0,
            "hp": 90.0,
            "max_hp": 100.0,
            "exp_multiplier": 1.0,
        }
        self._misplacement_stat_multiplier = float(misplacement_stat_multiplier)
        self._misplacement_exp_multiplier = float(misplacement_exp_multiplier)
        self._exp_gain_per_second = float(exp_gain_per_second)
        self._passive_bars: list[object] = []

    def get_char_data(self, char_id: str) -> dict[str, float]:
        del char_id
        return dict(self._data)

    def get_exp_gain_per_second(self, char_id: str) -> float:
        del char_id
        return self._exp_gain_per_second

    def get_party_level(self) -> int:
        return 1

    def get_misplacement_stat_multiplier(self, char_id: str) -> float:
        del char_id
        return self._misplacement_stat_multiplier

    def get_misplacement_exp_multiplier(self, char_id: str) -> float:
        del char_id
        return self._misplacement_exp_multiplier

    def get_passive_bars_for_character(self, char_id: str) -> list[object]:
        del char_id
        return list(self._passive_bars)


def test_blessing_blend_factor_boundaries() -> None:
    assert _blend_factor_for_progress(0.50) == 0.0
    assert math.isclose(
        _blend_factor_for_progress(0.575), 0.5, rel_tol=0.0, abs_tol=1e-12
    )
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

    meter.set_visual_state(
        progress=meter._display_progress, shimmer=0.0, reset_active=False
    )
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
        standby=[],
        stacks={},
        party_level=1,
        character_progress={},
        character_stats={},
        character_initial_stats={},
        inventory={},
        blessings={},
        passives={},
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

    mods_panel = screen.findChild(QFrame, "idleModsPanel")

    assert mods_panel is not None
    assert screen.findChild(QFrame, "idleBlessingPanel") is None
    assert not screen.findChildren(QLabel, "idleModsHelp")

    shared_help = "Onsite chars lose X%, offsite gain that + 1% per onsite"
    rr_help = "Boost: (Lvl+1)x EXP\nDrain: (5.5x Lvl) HP\nSpeed scales with level"
    shared_label = screen.findChild(QLabel, "idleSharedExpLabel")
    shared_slider = screen.findChild(QSlider, "idleSharedExpSlider")
    rr_label = screen.findChild(QLabel, "idleRRLabel")
    rr_slider = screen.findChild(QSlider, "idleRRSlider")
    assert shared_label is not None
    assert shared_slider is not None
    assert rr_label is not None
    assert rr_slider is not None
    assert shared_label.toolTip() == shared_help
    assert shared_slider.toolTip() == shared_help
    assert rr_label.toolTip() == rr_help
    assert rr_slider.toolTip() == rr_help


def test_idle_onsite_name_includes_level() -> None:
    _ = QApplication.instance() or QApplication([])

    card = IdleCharacterCard(
        context="onsite",
        char_id="test_char",
        plugin=CharacterPlugin(
            char_id="test_char",
            display_name="Nova",
            stars=5,
            damage_type_id="fire",
        ),
        idle_state=_FakeIdleStateForCard(),
        rng=random.Random(3),
        stack_count=4,
    )
    snapshot = card.snapshot()
    assert snapshot is not None
    data, stats = snapshot
    card.apply_snapshot(data, stats, maxima={})

    name_label = card.findChild(QLabel, "idleCharName")
    assert name_label is not None
    assert "Nova" in name_label.text()
    assert "(7)" in name_label.text()


def test_idle_offsite_name_includes_level() -> None:
    _ = QApplication.instance() or QApplication([])

    card = IdleCharacterCard(
        context="offsite",
        char_id="offsite_hero",
        plugin=None,
        idle_state=_FakeIdleStateForCard(),
        rng=random.Random(3),
        stack_count=5,
    )
    card.update_display()

    name_label = card.findChild(QLabel, "idleCharName")
    assert name_label is not None
    assert name_label.text() == "offsite_hero (7)"


def test_idle_offsite_tooltip_shows_penalized_values_without_text(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    card = IdleCharacterCard(
        context="offsite",
        char_id="offsite_hero",
        plugin=CharacterPlugin(
            char_id="offsite_hero",
            display_name="Offsite Hero",
            stars=5,
            damage_type_id="fire",
        ),
        idle_state=_FakeIdleStateForCard(
            misplacement_stat_multiplier=0.05,
            misplacement_exp_multiplier=0.25,
        ),
        rng=random.Random(3),
        stack_count=1,
    )
    card.update_display()
    tooltip_calls: list[tuple[str, str | None]] = []

    def _capture_tooltip(_owner, html: str, *, element_id: str | None = None) -> None:
        tooltip_calls.append((html, element_id))

    monkeypatch.setattr(character_card_module, "show_stained_tooltip", _capture_tooltip)
    card._show_tooltip()

    assert tooltip_calls
    tooltip_html, tooltip_element = tooltip_calls[-1]
    assert "Misplaced lane:" not in tooltip_html
    assert MISMATCH_TOOLTIP_VALUE_COLOR in tooltip_html
    assert "<b>0.25x</b>" in tooltip_html
    assert tooltip_element == "fire"


def test_idle_onsite_tooltip_shows_penalized_values_without_text() -> None:
    _ = QApplication.instance() or QApplication([])

    card = IdleCharacterCard(
        context="onsite",
        char_id="onsite_hero",
        plugin=CharacterPlugin(
            char_id="onsite_hero",
            display_name="Onsite Hero",
            stars=5,
            damage_type_id="fire",
        ),
        idle_state=_FakeIdleStateForCard(
            misplacement_stat_multiplier=0.05,
            misplacement_exp_multiplier=0.25,
        ),
        rng=random.Random(5),
        stack_count=1,
    )
    snapshot = card.snapshot()
    assert snapshot is not None
    data, stats = snapshot
    card.apply_snapshot(data, stats, maxima={})

    assert "Misplaced lane:" not in card._tooltip_html
    assert MISMATCH_TOOLTIP_VALUE_COLOR in card._tooltip_html
    assert "<b>0.25x</b>" in card._tooltip_html
    assert card.property("elementId") == "fire"


def test_idle_offsite_portrait_is_bottom_aligned_and_auto_sizes_to_target() -> None:
    _ = QApplication.instance() or QApplication([])

    card = IdleCharacterCard(
        context="offsite",
        char_id="offsite_hero",
        plugin=None,
        idle_state=_FakeIdleStateForCard(),
        rng=random.Random(3),
        stack_count=1,
    )

    portrait = card.findChild(QLabel, "idlePortrait")
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
    card._apply_offsite_portrait_size()
    assert 56 <= portrait.width() <= 72
    assert 56 <= portrait.height() <= 72


def test_idle_bars_are_bottom_anchored_for_onsite_and_offsite() -> None:
    _ = QApplication.instance() or QApplication([])

    offsite = IdleCharacterCard(
        context="offsite",
        char_id="offsite_hero",
        plugin=None,
        idle_state=_FakeIdleStateForCard(),
        rng=random.Random(3),
        stack_count=1,
    )
    offsite_body = offsite.layout().itemAt(1).layout()
    assert offsite_body is not None
    offsite_widgets = [
        offsite_body.itemAt(index).widget()
        for index in range(offsite_body.count())
        if offsite_body.itemAt(index).widget() is not None
    ]
    assert isinstance(offsite_widgets[-2], QWidget)
    assert isinstance(offsite_widgets[-1], QWidget)

    onsite = IdleCharacterCard(
        context="onsite",
        char_id="onsite_hero",
        plugin=CharacterPlugin(
            char_id="onsite_hero",
            display_name="Onsite Hero",
            stars=5,
            damage_type_id="fire",
        ),
        idle_state=_FakeIdleStateForCard(),
        rng=random.Random(5),
        stack_count=1,
    )
    onsite_body = onsite.layout().itemAt(1).layout()
    assert onsite_body is not None
    onsite_widgets = [
        onsite_body.itemAt(index).widget()
        for index in range(onsite_body.count())
        if onsite_body.itemAt(index).widget() is not None
    ]
    assert isinstance(onsite_widgets[-2], QWidget)
    assert isinstance(onsite_widgets[-1], QWidget)


def test_idle_card_shows_passive_bar_under_shard_bar_when_both_exist() -> None:
    _ = QApplication.instance() or QApplication([])

    idle_state = _FakeIdleStateForCard()
    idle_state._data["shard_reward_types"] = ("fire",)
    idle_state._data["shard_bar_ticks"] = 42.0
    idle_state._passive_bars = [
        SimpleNamespace(
            label="Trinity",
            progress=0.6,
            display_percent=0.0105,
            display_text="0.0105%",
            shimmer=0.8,
            style_id="trinity",
            element_id="generic",
            dual_element_ids=("dark", "light"),
        )
    ]

    card = IdleCharacterCard(
        context="onsite",
        char_id="onsite_hero",
        plugin=CharacterPlugin(
            char_id="onsite_hero",
            display_name="Onsite Hero",
            stars=5,
            damage_type_id="fire",
        ),
        idle_state=idle_state,
        rng=random.Random(5),
        stack_count=1,
    )
    snapshot = card.snapshot()
    assert snapshot is not None
    data, stats = snapshot
    card.apply_snapshot(data, stats, maxima={})

    body = card.layout().itemAt(1).layout()
    assert body is not None
    widgets = [
        body.itemAt(index).widget()
        for index in range(body.count())
        if body.itemAt(index).widget() is not None
        and not body.itemAt(index).widget().isHidden()
    ]
    shard_index = next(
        index
        for index, widget in enumerate(widgets)
        if widget.objectName() == "shardProgressBarWidget"
    )
    passive_index = next(
        index
        for index, widget in enumerate(widgets)
        if widget.objectName() == "passiveProgressBarWidget"
    )
    assert shard_index < passive_index


def test_idle_card_shows_passive_bar_under_exp_when_shard_bar_hidden() -> None:
    _ = QApplication.instance() or QApplication([])

    idle_state = _FakeIdleStateForCard()
    idle_state._passive_bars = [
        SimpleNamespace(
            label="Veil",
            progress=0.5,
            display_percent=0.5774,
            display_text="0.5774%",
            shimmer=0.0,
            style_id="default",
            element_id="dark",
            dual_element_ids=(),
        )
    ]

    card = IdleCharacterCard(
        context="offsite",
        char_id="offsite_hero",
        plugin=CharacterPlugin(
            char_id="offsite_hero",
            display_name="Offsite Hero",
            stars=5,
            damage_type_id="dark",
        ),
        idle_state=idle_state,
        rng=random.Random(3),
        stack_count=1,
    )
    card.update_display()

    body = card.layout().itemAt(1).layout()
    assert body is not None
    widgets = [
        body.itemAt(index).widget()
        for index in range(body.count())
        if body.itemAt(index).widget() is not None
        and not body.itemAt(index).widget().isHidden()
    ]
    exp_index = next(
        index
        for index, widget in enumerate(widgets)
        if widget.objectName() == "idleExpBar"
    )
    passive_index = next(
        index
        for index, widget in enumerate(widgets)
        if widget.objectName() == "passiveProgressBarWidget"
    )
    assert passive_index == exp_index + 1
    assert card.findChild(QWidget, "shardProgressBarWidget").isHidden()


def test_idle_card_stacks_multiple_passive_bars() -> None:
    _ = QApplication.instance() or QApplication([])

    idle_state = _FakeIdleStateForCard()
    idle_state._passive_bars = [
        SimpleNamespace(
            label="Trinity",
            progress=0.4,
            display_percent=0.0105,
            display_text="0.0105%",
            shimmer=0.4,
            style_id="trinity",
            element_id="generic",
            dual_element_ids=("dark", "light"),
        ),
        SimpleNamespace(
            label="Veil",
            progress=0.8,
            display_percent=0.5774,
            display_text="0.5774%",
            shimmer=0.0,
            style_id="default",
            element_id="dark",
            dual_element_ids=(),
        ),
        SimpleNamespace(
            label="Aegis",
            progress=0.8,
            display_percent=108.0,
            display_text="1.08x bonus",
            shimmer=0.0,
            style_id="default",
            element_id="light",
            dual_element_ids=(),
        ),
    ]

    card = IdleCharacterCard(
        context="onsite",
        char_id="onsite_hero",
        plugin=CharacterPlugin(
            char_id="onsite_hero",
            display_name="Onsite Hero",
            stars=5,
            damage_type_id="fire",
        ),
        idle_state=idle_state,
        rng=random.Random(5),
        stack_count=1,
    )
    snapshot = card.snapshot()
    assert snapshot is not None
    data, stats = snapshot
    card.apply_snapshot(data, stats, maxima={})

    passive_bars = card.findChildren(PassiveProgressBar, "passiveProgressBarWidget")
    visible_bars = [bar for bar in passive_bars if not bar.isHidden()]
    assert len(visible_bars) == 3
    assert visible_bars[0].format() == "TRINITY 0.0105%"
    assert visible_bars[1].format() == "VEIL 0.5774%"
    assert visible_bars[2].format() == "AEGIS 1.08x bonus"


def test_passive_progress_bar_uses_trinity_theme_and_keeps_effect_text() -> None:
    _ = QApplication.instance() or QApplication([])

    bar = PassiveProgressBar()
    bar.set_passive_data(
        label="Trinity",
        progress=1.5,
        display_percent=0.0105,
        display_text="0.0105%",
        shimmer=0.45,
        style_id="trinity",
        element_id="generic",
        dual_element_ids=("dark", "light"),
    )

    assert bar.property("styleId") == "trinity"
    assert bar.property("dualElementIds") == "dark,light"
    assert bar.format() == "TRINITY 0.0105%"
    assert bar._progress_bar._target_progress == 1.0
    assert bar._progress_bar._target_shimmer == 0.45


def test_idle_offsite_exp_bar_uses_tilde_for_tiny_nonzero_gain() -> None:
    _ = QApplication.instance() or QApplication([])

    card = IdleCharacterCard(
        context="offsite",
        char_id="offsite_hero",
        plugin=None,
        idle_state=_FakeIdleStateForCard(exp_gain_per_second=0.001),
        rng=random.Random(3),
        stack_count=1,
    )
    card.update_display()

    exp_bar = card.findChild(AnimatedProgressBar, "idleExpBar")
    assert exp_bar is not None
    assert exp_bar.format() == "EXP 12 / 30 ~0.00/s"


def test_idle_onsite_exp_bar_uses_tilde_for_tiny_nonzero_gain() -> None:
    _ = QApplication.instance() or QApplication([])

    card = IdleCharacterCard(
        context="onsite",
        char_id="onsite_hero",
        plugin=CharacterPlugin(
            char_id="onsite_hero",
            display_name="Onsite Hero",
            stars=5,
            damage_type_id="fire",
        ),
        idle_state=_FakeIdleStateForCard(exp_gain_per_second=0.001),
        rng=random.Random(5),
        stack_count=1,
    )
    snapshot = card.snapshot()
    assert snapshot is not None
    data, stats = snapshot
    card.apply_snapshot(data, stats, maxima={})

    exp_bar = card.findChild(AnimatedProgressBar, "idleExpBar")
    assert exp_bar is not None
    assert exp_bar.format() == "EXP 12 / 30 ~0.00/s"


def test_card_context_property_set_correctly() -> None:
    _ = QApplication.instance() or QApplication([])

    onsite_card = IdleCharacterCard(
        context="onsite",
        char_id="onsite_hero",
        plugin=None,
        idle_state=_FakeIdleStateForCard(),
        rng=random.Random(3),
        stack_count=1,
    )
    assert onsite_card.property("context") == "onsite"
    assert onsite_card.objectName() == "idleCharacterCard"

    offsite_card = IdleCharacterCard(
        context="offsite",
        char_id="offsite_hero",
        plugin=None,
        idle_state=_FakeIdleStateForCard(),
        rng=random.Random(3),
        stack_count=1,
    )
    assert offsite_card.property("context") == "offsite"
    assert offsite_card.objectName() == "idleCharacterCard"
