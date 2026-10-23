from __future__ import annotations

import random

from contextlib import nullcontext
from types import SimpleNamespace
from typing import Any
from typing import cast

from PySide6.QtCore import QSize
from PySide6.QtCore import Qt

import endless_idler.ui.main_menu as main_menu_module

from endless_idler.save import RunSave
from endless_idler.ui.main_menu import MainMenuWindow


class _FakeSignal:
    def __init__(self) -> None:
        self._callback: Any = None

    def connect(self, callback: Any) -> None:
        self._callback = callback


class _FakeIdleScreen:
    created: list["_FakeIdleScreen"] = []

    def __init__(  # noqa: ANN001, ANN204
        self,
        *,
        save_store,
        tick_runtime=None,
        idle_state=None,
        owns_tick_source=True,
        plugins=None,
        parent=None,
    ) -> None:
        del tick_runtime
        del plugins
        del parent
        self.finished = _FakeSignal()
        self.lineup_signature = self.build_lineup_signature(save_store.current)
        self.received_idle_state = idle_state
        self.received_owns_tick_source = owns_tick_source
        self.shutdown_calls: list[bool] = []
        self.force_persist_calls = 0
        self.deleted = False
        _FakeIdleScreen.created.append(self)

    @staticmethod
    def build_lineup_signature(
        save: object,
    ) -> tuple[
        tuple[str, ...],
        tuple[str, ...],
        tuple[str, ...],
        tuple[tuple[str, int], ...],
        int,
    ]:
        onsite = tuple(str(item) for item in getattr(save, "onsite", []) if item)
        offsite = tuple(str(item) for item in getattr(save, "offsite", []) if item)
        standby = tuple(str(item) for item in getattr(save, "standby", []) if item)
        stacks = getattr(save, "stacks", {})
        stack_pairs = tuple(
            sorted(
                (char_id, int(stacks.get(char_id, 1)))
                for char_id in [*onsite, *offsite, *standby]
            )
        )
        party_level = int(getattr(save, "party_level", 1))
        return onsite, offsite, standby, stack_pairs, party_level

    def shutdown(self, *, persist: bool = True) -> None:
        self.shutdown_calls.append(bool(persist))

    def force_persist(self) -> None:
        self.force_persist_calls += 1

    def deleteLater(self) -> None:
        self.deleted = True


class _FakeLayoutScreen:
    def __init__(self) -> None:
        self.persist_calls = 0

    def persist_now(self) -> None:
        self.persist_calls += 1


class _FakeStack:
    def __init__(self, *, current_widget: object) -> None:
        self._current_widget = current_widget
        self.added: list[object] = []
        self.removed: list[object] = []
        self.set_current: list[object] = []

    def addWidget(self, widget: object) -> None:
        self.added.append(widget)

    def removeWidget(self, widget: object) -> None:
        self.removed.append(widget)

    def currentWidget(self) -> object:
        return self._current_widget

    def setCurrentWidget(self, widget: object) -> None:
        self._current_widget = widget
        self.set_current.append(widget)


class _FakeButton:
    def __init__(self, width: int) -> None:
        self._size_hint = QSize(width, 36)
        self.styles: list[Qt.ToolButtonStyle] = []

    def sizeHint(self) -> QSize:
        return QSize(self._size_hint)

    def setToolButtonStyle(self, style: Qt.ToolButtonStyle) -> None:
        self.styles.append(style)

    def updateGeometry(self) -> None:
        pass


class _FakeMargins:
    def __init__(self, left: int, right: int) -> None:
        self._left = left
        self._right = right

    def left(self) -> int:
        return self._left

    def right(self) -> int:
        return self._right


class _FakeLayout:
    def __init__(self, *, spacing: int, left: int, right: int) -> None:
        self._spacing = spacing
        self._margins = _FakeMargins(left, right)

    def spacing(self) -> int:
        return self._spacing

    def contentsMargins(self) -> _FakeMargins:
        return self._margins

    def invalidate(self) -> None:
        pass

    def activate(self) -> None:
        pass


class _FakeRect:
    def __init__(self, width: int) -> None:
        self._width = width

    def width(self) -> int:
        return self._width


class _FakeTopbar:
    def __init__(self, width: int) -> None:
        self._width = width

    def contentsRect(self) -> _FakeRect:
        return _FakeRect(self._width)

    def updateGeometry(self) -> None:
        pass


class _FakeRadioControl:
    def __init__(self, width: int, *, visible: bool = True) -> None:
        self._width = width
        self._visible = visible

    def isVisible(self) -> bool:
        return self._visible

    def sizeHint(self) -> QSize:
        return QSize(self._width, 40)


def _fake_save(
    *, onsite: list[str], offsite: list[str], standby: list[str] | None = None
) -> object:
    standby_list = list(standby or [])
    return SimpleNamespace(
        onsite=list(onsite),
        offsite=list(offsite),
        standby=standby_list,
        stacks={char_id: 1 for char_id in [*onsite, *offsite, *standby_list]},
        party_level=1,
    )


def _make_menu_like(
    *, save: object, idle_screen: object | None, placeholder: object
) -> Any:
    stack = _FakeStack(current_widget=placeholder)
    nav_calls: list[str] = []
    holder: Any = SimpleNamespace(
        _layout_screen=_FakeLayoutScreen(),
        _save_store=SimpleNamespace(current=save),
        _idle_screen=idle_screen,
        _idle_placeholder=placeholder,
        _stack=stack,
        _tick_runtime=object(),
        _idle_runtime_lock=nullcontext(),
        _idle_state=object(),
        _plugins=[],
        _PAGE_LAYOUT="layout",
        _PAGE_IDLE="idle",
        _set_active_nav=lambda key: nav_calls.append(str(key)),
        _show_home=lambda: None,
        _refresh_shared_idle_runtime=lambda: None,
    )
    holder._idle_lineup_signature = lambda: MainMenuWindow._idle_lineup_signature(
        holder
    )
    holder._dispose_idle_runtime = lambda *, persist: (
        MainMenuWindow._dispose_idle_runtime(holder, persist=persist)
    )
    holder._ensure_idle_runtime = lambda: MainMenuWindow._ensure_idle_runtime(holder)
    holder._nav_calls = nav_calls
    return holder


def test_show_idle_rebuilds_runtime_when_lineup_signature_changes(monkeypatch) -> None:
    monkeypatch.setattr(main_menu_module, "IdleScreenWidget", _FakeIdleScreen)
    _FakeIdleScreen.created.clear()

    placeholder = object()
    first_save = _fake_save(onsite=[], offsite=[])
    old_idle = _FakeIdleScreen(save_store=SimpleNamespace(current=first_save))
    new_save = _fake_save(onsite=["ally"], offsite=[])
    menu_like: Any = _make_menu_like(
        save=new_save, idle_screen=old_idle, placeholder=placeholder
    )

    MainMenuWindow._show_idle(menu_like)

    assert menu_like._layout_screen.persist_calls == 1
    assert old_idle.shutdown_calls == [True]
    assert old_idle.deleted is True
    assert menu_like._idle_screen is not old_idle
    assert isinstance(menu_like._idle_screen, _FakeIdleScreen)
    assert menu_like._idle_screen.received_idle_state is menu_like._idle_state
    assert menu_like._idle_screen.received_owns_tick_source is False
    assert menu_like._stack.set_current[-1] is menu_like._idle_screen
    assert menu_like._nav_calls == ["idle"]


def test_show_idle_reuses_runtime_when_lineup_signature_matches(monkeypatch) -> None:
    monkeypatch.setattr(main_menu_module, "IdleScreenWidget", _FakeIdleScreen)
    _FakeIdleScreen.created.clear()

    placeholder = object()
    save = _fake_save(onsite=["ally"], offsite=[])
    idle = _FakeIdleScreen(save_store=SimpleNamespace(current=save))
    menu_like: Any = _make_menu_like(
        save=save, idle_screen=idle, placeholder=placeholder
    )

    MainMenuWindow._show_idle(menu_like)

    assert menu_like._layout_screen.persist_calls == 1
    assert idle.shutdown_calls == []
    assert menu_like._idle_screen is idle
    assert menu_like._stack.set_current[-1] is idle
    assert len(_FakeIdleScreen.created) == 1


def test_show_layout_flushes_idle_before_switching(monkeypatch) -> None:
    monkeypatch.setattr(main_menu_module, "IdleScreenWidget", _FakeIdleScreen)
    _FakeIdleScreen.created.clear()

    placeholder = object()
    save = _fake_save(onsite=["ally"], offsite=[])
    idle = _FakeIdleScreen(save_store=SimpleNamespace(current=save))
    menu_like: Any = _make_menu_like(
        save=save, idle_screen=idle, placeholder=placeholder
    )

    MainMenuWindow._show_layout(menu_like)

    assert idle.force_persist_calls == 1
    assert menu_like._stack.set_current[-1] is menu_like._layout_screen
    assert menu_like._nav_calls == ["layout"]


def test_lineup_signature_changes_when_standby_changes() -> None:
    first = _fake_save(onsite=["ally"], offsite=["res"], standby=["bench_a"])
    second = _fake_save(onsite=["ally"], offsite=["res"], standby=["bench_b"])

    first_signature = main_menu_module.IdleScreenWidget.build_lineup_signature(first)
    second_signature = main_menu_module.IdleScreenWidget.build_lineup_signature(second)

    assert first_signature != second_signature


def test_build_idle_state_from_save_passes_standby_ids(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _CaptureIdleState:
        def __init__(self, **kwargs) -> None:  # noqa: ANN003
            captured.update(kwargs)

    monkeypatch.setattr(main_menu_module, "IdleGameState", _CaptureIdleState)
    holder: Any = SimpleNamespace(
        _plugins=[],
        _idle_rng=random.Random(),
    )
    save = SimpleNamespace(
        onsite=["ally"],
        offsite=["reserve"],
        standby=[None, "bench", None],
        party_level=1,
        stacks={"ally": 1, "reserve": 1, "bench": 1},
        character_progress={},
        character_stats={},
        character_initial_stats={},
        inventory={},
        idle_exp_bonus_seconds=0.0,
        idle_exp_penalty_seconds=0.0,
        idle_shared_exp_percentage=1,
        idle_risk_reward_level=0,
        battle_start_time=0.0,
        blessings={},
        passives=RunSave().passives,
    )

    MainMenuWindow._build_idle_state_from_save(holder, save)

    assert captured["standby_ids"] == ["bench"]
    assert captured["passives_data"] == RunSave().passives


def test_build_idle_state_from_save_restores_live_blessing_runtime(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _CaptureIdleState:
        def __init__(self, **kwargs) -> None:  # noqa: ANN003
            captured.update(kwargs)

    monkeypatch.setattr(main_menu_module, "IdleGameState", _CaptureIdleState)
    holder: Any = SimpleNamespace(
        _plugins=[],
        _idle_rng=random.Random(),
    )
    save = SimpleNamespace(
        onsite=["ally"],
        offsite=[],
        standby=[],
        party_level=1,
        stacks={"ally": 1},
        character_progress={},
        character_stats={},
        character_initial_stats={},
        inventory={},
        idle_exp_bonus_seconds=0.0,
        idle_exp_penalty_seconds=0.0,
        idle_shared_exp_percentage=1,
        idle_risk_reward_level=0,
        battle_start_time=0.0,
        blessings={"fire_blessing": {"steps": 2, "unlocked": True}},
        passives=RunSave().passives,
    )

    MainMenuWindow._build_idle_state_from_save(
        holder,
        save,
        runtime_snapshot={
            "elapsed_seconds": 123.4,
            "blessing_runtime": {
                "fire_blessing": {
                    "elapsed_seconds": 99.25,
                    "steps": 2,
                }
            },
        },
    )

    assert captured["battle_start_time"] == 123.4
    assert captured["blessings_data"]["fire_blessing"]["tick_elapsed_seconds"] == 99.25


def test_apply_idle_snapshot_to_save_writes_canonical_passives_only() -> None:
    save = SimpleNamespace(
        character_progress={},
        character_stats={},
        character_initial_stats={},
        blessings={},
        passives=RunSave().passives,
        idle_exp_bonus_seconds=0.0,
        idle_exp_penalty_seconds=0.0,
        idle_shared_exp_percentage=1,
        idle_risk_reward_level=0,
        layout_tick_cooldown_seconds=0.0,
    )
    holder: Any = SimpleNamespace(
        _save_store=SimpleNamespace(current=save),
        _tick_cooldown_lock=nullcontext(),
        _tick_cooldown_seconds=0.0,
    )

    MainMenuWindow._apply_idle_snapshot_to_save(
        holder,
        {
            "passives": RunSave().passives,
            "passive_runtime": {"lady_fire_infernal_momentum": {"ticks": 3}},
        },
    )

    assert save.passives == RunSave().passives
    assert not hasattr(save, "passive_runtime")


def test_apply_idle_snapshot_to_save_writes_inventory() -> None:
    save = SimpleNamespace(
        character_progress={},
        character_stats={},
        character_initial_stats={},
        blessings={},
        passives=RunSave().passives,
        inventory={},
        idle_exp_bonus_seconds=0.0,
        idle_exp_penalty_seconds=0.0,
        idle_shared_exp_percentage=1,
        idle_risk_reward_level=0,
        layout_tick_cooldown_seconds=0.0,
    )
    holder: Any = SimpleNamespace(
        _save_store=SimpleNamespace(current=save),
        _tick_cooldown_lock=nullcontext(),
        _tick_cooldown_seconds=0.0,
    )

    MainMenuWindow._apply_idle_snapshot_to_save(
        holder,
        {
            "inventory": {
                "fire_shard": 2,
                "dark_shard": -3,
            },
        },
    )

    assert save.inventory == {
        "fire_shard": 2,
        "dark_shard": 0,
    }


def test_topbar_navigation_compacts_and_restores_icon_only() -> None:
    holder: Any = cast(Any, SimpleNamespace())
    buttons = [_FakeButton(width) for width in (48, 52, 58)]
    holder._topbar_buttons = buttons
    holder._topbar_nav_full_buttons_width = 0
    holder._topbar_nav_compact = False
    holder._measure_topbar_nav_buttons_width = lambda: 158
    holder._topbar_navigation_available_width = lambda: 332
    holder._topbar_navigation_required_width = lambda: 340
    holder._topbar = _FakeTopbar(332)
    holder._topbar_layout = _FakeLayout(spacing=6, left=10, right=10)

    MainMenuWindow._update_topbar_navigation_mode(holder)

    assert holder._topbar_nav_compact is True
    assert holder._topbar_nav_full_buttons_width == 158
    assert all(
        button.styles[-1] == Qt.ToolButtonStyle.ToolButtonIconOnly for button in buttons
    )

    holder._topbar = _FakeTopbar(372)
    holder._topbar_navigation_available_width = lambda: 372

    MainMenuWindow._update_topbar_navigation_mode(holder)

    assert holder._topbar_nav_compact is False
    assert all(
        button.styles[-1] == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        for button in buttons
    )
