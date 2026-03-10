from __future__ import annotations

import queue
import threading

from collections.abc import Callable


SaveTask = Callable[[], None]


class AsyncSaveQueue:
    def __init__(self) -> None:
        self._tasks: queue.Queue[SaveTask | None] = queue.Queue()
        self._closed = False
        self._lock = threading.Lock()
        self._worker = threading.Thread(
            target=self._run,
            name="endless-idler-save-queue",
            daemon=True,
        )
        self._worker.start()

    def enqueue(self, task: SaveTask) -> None:
        with self._lock:
            if self._closed:
                raise RuntimeError("Save queue is already closed.")
            self._tasks.put(task)

    def flush(self) -> None:
        done = threading.Event()

        def _mark_done() -> None:
            done.set()

        self.enqueue(_mark_done)
        done.wait()

    def shutdown(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._tasks.put(None)
        self._worker.join()

    def _run(self) -> None:
        while True:
            task = self._tasks.get()
            if task is None:
                self._tasks.task_done()
                break
            try:
                task()
            finally:
                self._tasks.task_done()
