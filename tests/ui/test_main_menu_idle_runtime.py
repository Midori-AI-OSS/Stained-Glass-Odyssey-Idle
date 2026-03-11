from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace

import endless_idler.ui.main_menu as main_menu_module

from endless_idler.ui.main_menu import MainMenuWindow


class _FakeSignal:
    def connect(self, callback) -> None:  # noqa: ANN001
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
        self.deleted = False
        _FakeIdleScreen.created.append(self)

    @staticmethod
    def build_lineup_signature(save: object) -> tuple[tuple[str, ...], tuple[str, ...], tuple[tuple[str, int], ...], int]:
        onsite = tuple(str(item) for item in getattr(save, "onsite", []) if item)
        offsite = tuple(str(item) for item in getattr(save, "offsite", []) if item)
        stacks = getattr(save, "stacks", {})
        stack_pairs = tuple(sorted((char_id, int(stacks.get(char_id, 1))) for char_id in [*onsite, *offsite]))
        party_level = int(getattr(save, "party_level", 1))
        return onsite, offsite, stack_pairs, party_level

    def shutdown(self, *, persist: bool = True) -> None:
        self.shutdown_calls.append(bool(persist))

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


def _fake_save(*, onsite: list[str], offsite: list[str]) -> object:
    return SimpleNamespace(
        onsite=list(onsite),
        offsite=list(offsite),
        stacks={char_id: 1 for char_id in [*onsite, *offsite]},
        party_level=1,
    )


def _make_menu_like(*, save: object, idle_screen: object | None, placeholder: object) -> object:
    stack = _FakeStack(current_widget=placeholder)
    nav_calls: list[str] = []
    holder = SimpleNamespace(
        _layout_screen=_FakeLayoutScreen(),
        _save_store=SimpleNamespace(current=save),
        _idle_screen=idle_screen,
        _idle_placeholder=placeholder,
        _stack=stack,
        _tick_runtime=object(),
        _idle_runtime_lock=nullcontext(),
        _idle_state=object(),
        _plugins=[],
        _PAGE_IDLE="idle",
        _set_active_nav=lambda key: nav_calls.append(str(key)),
        _show_home=lambda: None,
        _refresh_shared_idle_runtime=lambda: None,
    )
    holder._idle_lineup_signature = lambda: MainMenuWindow._idle_lineup_signature(holder)
    holder._dispose_idle_runtime = lambda *, persist: MainMenuWindow._dispose_idle_runtime(holder, persist=persist)
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
    menu_like = _make_menu_like(save=new_save, idle_screen=old_idle, placeholder=placeholder)

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
    menu_like = _make_menu_like(save=save, idle_screen=idle, placeholder=placeholder)

    MainMenuWindow._show_idle(menu_like)

    assert menu_like._layout_screen.persist_calls == 1
    assert idle.shutdown_calls == []
    assert menu_like._idle_screen is idle
    assert menu_like._stack.set_current[-1] is idle
    assert len(_FakeIdleScreen.created) == 1
