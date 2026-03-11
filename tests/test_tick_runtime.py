from __future__ import annotations

import time

from PySide6.QtWidgets import QApplication

from endless_idler.tick_runtime import SharedTickRuntime
from endless_idler.tick_runtime import TickSnapshot


def _pump_events(seconds: float) -> None:
    app = QApplication.instance() or QApplication([])
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents()
        time.sleep(0.005)


def test_shared_tick_runtime_subscribe_and_unsubscribe_controls_worker() -> None:
    runtime = SharedTickRuntime()
    calls: list[int] = []

    runtime.configure_source(
        key="idle-source",
        source=lambda tick_count, _mono: {"tick_count": tick_count},
    )
    runtime.subscribe(key="idle-ui", callback=lambda snapshot: calls.append(snapshot.tick_count))
    _pump_events(0.15)

    assert runtime.has_subscriber("idle-ui")
    assert runtime.is_running()
    assert calls

    runtime.unsubscribe("idle-ui")
    _pump_events(0.05)
    assert not runtime.has_subscriber("idle-ui")
    assert not runtime.is_running()


def test_shared_tick_runtime_replaces_same_key_subscriber() -> None:
    runtime = SharedTickRuntime()
    first_calls: list[int] = []
    second_calls: list[int] = []

    runtime.configure_source(
        key="idle-source",
        source=lambda tick_count, _mono: {"tick_count": tick_count},
    )
    runtime.subscribe(key="idle", callback=lambda _snapshot: first_calls.append(1))
    runtime.subscribe(key="idle", callback=lambda _snapshot: second_calls.append(1))
    runtime._dispatch_tick(TickSnapshot(tick_count=1, monotonic_seconds=0.0, payload={}))

    assert not first_calls
    assert second_calls == [1]
    runtime.stop()
