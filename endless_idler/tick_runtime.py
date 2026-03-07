from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal


TickCallback = Callable[[], None]


class SharedTickRuntime(QObject):
    tick = Signal(int)

    def __init__(
        self,
        *,
        interval_seconds: float,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._subscribers: dict[str, TickCallback] = {}
        self._tick_count = 0
        self._interval_seconds = max(0.001, float(interval_seconds))
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self._on_timeout)

    @property
    def interval_seconds(self) -> float:
        return self._interval_seconds

    @property
    def tick_count(self) -> int:
        return self._tick_count

    def set_interval_seconds(self, value: float) -> None:
        self._interval_seconds = max(0.001, float(value))
        if self._timer.isActive():
            self._timer.start(self._interval_ms())

    def subscribe(self, *, key: str, callback: TickCallback) -> None:
        clean_key = str(key).strip()
        if not clean_key:
            raise ValueError("Tick subscriber key must be a non-empty string.")
        self._subscribers[clean_key] = callback
        if not self._timer.isActive():
            self._timer.start(self._interval_ms())

    def unsubscribe(self, key: str) -> None:
        clean_key = str(key).strip()
        if not clean_key:
            return
        self._subscribers.pop(clean_key, None)
        if not self._subscribers:
            self._timer.stop()

    def has_subscriber(self, key: str) -> bool:
        clean_key = str(key).strip()
        if not clean_key:
            return False
        return clean_key in self._subscribers

    def is_running(self) -> bool:
        return self._timer.isActive()

    def start(self) -> None:
        if not self._subscribers:
            return
        self._timer.start(self._interval_ms())

    def stop(self) -> None:
        self._timer.stop()

    def _interval_ms(self) -> int:
        return max(1, int(round(self._interval_seconds * 1000.0)))

    def _on_timeout(self) -> None:
        self._tick_count += 1
        subscribers = tuple(self._subscribers.items())
        for key, callback in subscribers:
            if key not in self._subscribers:
                continue
            callback()
        self.tick.emit(self._tick_count)
