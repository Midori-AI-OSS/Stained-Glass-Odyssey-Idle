from __future__ import annotations

import threading
import time

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal


FIXED_TICK_RATE_HZ = 30
FIXED_TICK_INTERVAL_SECONDS = 1.0 / FIXED_TICK_RATE_HZ


@dataclass(frozen=True, slots=True)
class TickSnapshot:
    tick_count: int
    monotonic_seconds: float
    payload: dict[str, object]


TickSource = Callable[[int, float], dict[str, object]]
TickCallback = Callable[[TickSnapshot], None]


class SharedTickRuntime(QObject):
    tick = Signal(object)

    def __init__(self, *, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._subscribers: dict[str, TickCallback] = {}
        self._source_key = ""
        self._source: TickSource | None = None
        self._tick_count = 0
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._worker: threading.Thread | None = None
        self.tick.connect(self._dispatch_tick)

    @property
    def interval_seconds(self) -> float:
        return FIXED_TICK_INTERVAL_SECONDS

    @property
    def tick_count(self) -> int:
        with self._lock:
            return self._tick_count

    def configure_source(self, *, key: str, source: TickSource) -> None:
        clean_key = str(key).strip()
        if not clean_key:
            raise ValueError("Tick source key must be a non-empty string.")
        with self._lock:
            self._source_key = clean_key
            self._source = source
        self._ensure_worker_state()

    def clear_source(self, key: str) -> None:
        clean_key = str(key).strip()
        with self._lock:
            if clean_key and clean_key == self._source_key:
                self._source_key = ""
                self._source = None
        self._ensure_worker_state()

    def subscribe(self, *, key: str, callback: TickCallback) -> None:
        clean_key = str(key).strip()
        if not clean_key:
            raise ValueError("Tick subscriber key must be a non-empty string.")
        with self._lock:
            self._subscribers[clean_key] = callback
        self._ensure_worker_state()

    def unsubscribe(self, key: str) -> None:
        clean_key = str(key).strip()
        if not clean_key:
            return
        with self._lock:
            self._subscribers.pop(clean_key, None)
        self._ensure_worker_state()

    def has_subscriber(self, key: str) -> bool:
        clean_key = str(key).strip()
        if not clean_key:
            return False
        with self._lock:
            return clean_key in self._subscribers

    def is_running(self) -> bool:
        worker = self._worker
        return worker is not None and worker.is_alive()

    def stop(self) -> None:
        self._stop_worker()

    def _ensure_worker_state(self) -> None:
        with self._lock:
            has_source = self._source is not None
            has_subscribers = bool(self._subscribers)
        if has_source and has_subscribers:
            self._start_worker()
            return
        self._stop_worker()

    def _start_worker(self) -> None:
        with self._lock:
            if self._worker is not None and self._worker.is_alive():
                return
            self._stop_event.clear()
            worker = threading.Thread(
                target=self._run_loop,
                name="endless-idler-tick-runtime",
                daemon=True,
            )
            self._worker = worker
        worker.start()

    def _stop_worker(self) -> None:
        worker: threading.Thread | None
        with self._lock:
            worker = self._worker
            self._worker = None
            self._stop_event.set()
        if worker is not None and worker.is_alive():
            worker.join()

    def _run_loop(self) -> None:
        next_tick_at = time.perf_counter()
        while not self._stop_event.is_set():
            now = time.perf_counter()
            sleep_seconds = next_tick_at - now
            if sleep_seconds > 0.0:
                if self._stop_event.wait(sleep_seconds):
                    break
                continue

            snapshot = self._build_snapshot(now)
            if snapshot is not None:
                self.tick.emit(snapshot)
            next_tick_at += FIXED_TICK_INTERVAL_SECONDS
            if now - next_tick_at > FIXED_TICK_INTERVAL_SECONDS:
                next_tick_at = now + FIXED_TICK_INTERVAL_SECONDS

    def _build_snapshot(self, monotonic_seconds: float) -> TickSnapshot | None:
        with self._lock:
            source = self._source
            if source is None:
                return None
            self._tick_count += 1
            tick_count = self._tick_count
        payload = source(tick_count, monotonic_seconds)
        return TickSnapshot(
            tick_count=tick_count,
            monotonic_seconds=monotonic_seconds,
            payload=payload,
        )

    def _dispatch_tick(self, snapshot: TickSnapshot) -> None:
        with self._lock:
            subscribers = tuple(self._subscribers.items())
        for key, callback in subscribers:
            if not self.has_subscriber(key):
                continue
            callback(snapshot)
