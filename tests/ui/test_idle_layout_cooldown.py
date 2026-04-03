from __future__ import annotations

from contextlib import nullcontext
from typing import cast

from PySide6.QtWidgets import QApplication

import endless_idler.ui.idle.screen as screen_module

from endless_idler.save import RunSave
from endless_idler.run_save_store import RunSaveStore
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

    def process_tick(self) -> dict[str, object]:
        self.process_calls += 1
        return self.export_runtime_snapshot()

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

    def export_runtime_snapshot(self) -> dict[str, object]:
        return {
            "progress": {},
            "character_stats": {},
            "initial_stats": {},
            "blessings": {},
            "exp_bonus_seconds": 0.0,
            "exp_penalty_seconds": 0.0,
            "shared_exp_percentage": self._shared,
            "risk_reward_level": self._rr,
        }


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

    screen = IdleScreenWidget(
        save_store=cast(RunSaveStore, cast(object, _FakeSaveStore(save)))
    )
    fake_state = screen._idle_state
    assert isinstance(fake_state, _FakeIdleState)
    assert screen._tick_cooldown_seconds > 0.0

    screen._produce_tick_payload(1, 0.0)
    assert fake_state.process_calls == 0

    screen._tick_cooldown_seconds = 0.0
    screen._produce_tick_payload(2, 0.0)
    assert fake_state.process_calls == 1
    screen.shutdown()


def test_idle_screen_snapshot_applies_canonical_passives_only() -> None:
    save = RunSave()
    holder = type(
        "_Holder",
        (),
        {
            "_save": save,
            "_tick_cooldown_lock": nullcontext(),
            "_tick_cooldown_seconds": 0.0,
            "_coerce_float": staticmethod(IdleScreenWidget._coerce_float),
            "_coerce_int": staticmethod(IdleScreenWidget._coerce_int),
        },
    )()

    IdleScreenWidget._apply_snapshot_to_save(
        holder,
        {
            "passives": {"lady_fire_infernal_momentum": {}},
            "passive_runtime": {"lady_fire_infernal_momentum": {"ticks": 5}},
        },
    )

    assert save.passives == {"lady_fire_infernal_momentum": {}}
    assert not hasattr(save, "passive_runtime")
