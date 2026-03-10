from __future__ import annotations

from PySide6.QtWidgets import QApplication

import endless_idler.ui.idle.screen as screen_module

from endless_idler.save import RunSave
from endless_idler.ui.idle.screen import IdleScreenWidget


class _FakeSignal:
    def connect(self, callback) -> None:  # noqa: ANN001
        del callback


class _FakeIdleState:
    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        del kwargs
        self.tick_update = _FakeSignal()
        self.process_calls = 0
        self._shared = 1
        self._rr = 0

    def process_tick(self) -> None:
        self.process_calls += 1

    def get_idle_blessing_step_count(self) -> int:
        return 0

    def get_idle_blessing_cycle_progress(self) -> float:
        return 0.0

    def get_idle_blessing_seconds_to_next_step(self) -> int:
        return 300

    def get_idle_blessing_multiplier(self) -> float:
        return 1.0

    def set_shared_exp_percentage(self, value: int) -> None:
        self._shared = int(value)

    def get_shared_exp_percentage(self) -> int:
        return self._shared

    def set_risk_reward_level(self, value: int) -> None:
        self._rr = int(value)

    def get_risk_reward_level(self) -> int:
        return self._rr

    def get_char_data(self, char_id: str) -> dict[str, float]:
        del char_id
        return {}

    def export_progress(self) -> dict[str, dict[str, float | int]]:
        return {}

    def export_character_stats(self) -> dict[str, dict[str, float]]:
        return {}

    def export_initial_stats(self) -> dict[str, dict[str, float]]:
        return {}

    def export_run_buff_seconds(self) -> tuple[float, float]:
        return (0.0, 0.0)


class _FakeSaveStore:
    def __init__(self, save: RunSave) -> None:
        self._current = save
        self.persist_calls = 0

    @property
    def current(self) -> RunSave:
        return self._current

    def persist(self, *, force: bool = False) -> None:
        del force
        self.persist_calls += 1


def test_idle_screen_applies_tick_cooldown_before_processing(monkeypatch) -> None:
    _ = QApplication.instance() or QApplication([])

    save = RunSave(layout_tick_cooldown_seconds=0.2)
    monkeypatch.setattr(screen_module, "start_idle_heal_timer", lambda value: None)
    monkeypatch.setattr(screen_module, "discover_character_plugins", lambda: [])
    monkeypatch.setattr(screen_module, "IdleGameState", _FakeIdleState)

    screen = IdleScreenWidget(save_store=_FakeSaveStore(save))
    fake_state = screen._idle_state
    assert isinstance(fake_state, _FakeIdleState)
    assert screen._tick_cooldown_seconds > 0.0

    screen._process_idle_tick()
    assert fake_state.process_calls == 0

    screen._tick_cooldown_seconds = 0.0
    screen._process_idle_tick()
    assert fake_state.process_calls == 1
    screen.shutdown()
