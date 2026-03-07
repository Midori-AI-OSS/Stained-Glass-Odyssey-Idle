from __future__ import annotations

from PySide6.QtWidgets import QApplication

from endless_idler.tick_runtime import SharedTickRuntime


def test_shared_tick_runtime_subscribe_and_unsubscribe_controls_timer() -> None:
    _ = QApplication.instance() or QApplication([])

    runtime = SharedTickRuntime(interval_seconds=0.1)
    calls: list[int] = []

    runtime.subscribe(key="idle", callback=lambda: calls.append(1))
    assert runtime.has_subscriber("idle")
    assert runtime.is_running()

    runtime._on_timeout()
    assert calls == [1]
    assert runtime.tick_count == 1

    runtime.unsubscribe("idle")
    assert not runtime.has_subscriber("idle")
    assert not runtime.is_running()


def test_shared_tick_runtime_replaces_same_key_subscriber() -> None:
    _ = QApplication.instance() or QApplication([])

    runtime = SharedTickRuntime(interval_seconds=0.1)
    first_calls: list[int] = []
    second_calls: list[int] = []

    runtime.subscribe(key="idle", callback=lambda: first_calls.append(1))
    runtime.subscribe(key="idle", callback=lambda: second_calls.append(1))

    runtime._on_timeout()
    assert not first_calls
    assert second_calls == [1]
