from __future__ import annotations

import math

from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


WIN_STACK_SECONDS = 5 * 60
LOSS_STACK_SECONDS = 15 * 60


def _format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:d}:{sec:02d}"


class BuffStackTile(QFrame):
    def __init__(self, *, kind: str, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("rewardsBuffContainer")
        self.setProperty("kind", kind)

        self._remaining_seconds = 0.0
        self._stack_seconds = 60
        self._title_text = title

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        self.setLayout(layout)

        self._title = QLabel(title)
        self._title.setObjectName("rewardsBuffTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._title)

        self._time = QLabel("--")
        self._time.setObjectName("rewardsBuffTime")
        self._time.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._time)

        self._stacks = QLabel("")
        self._stacks.setObjectName("rewardsBuffStacks")
        self._stacks.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._stacks)

        self.setVisible(False)

    def set_timer(self, *, remaining_seconds: float, stack_seconds: int) -> None:
        self._remaining_seconds = float(max(0.0, float(remaining_seconds)))
        self._stack_seconds = max(1, int(stack_seconds))
        self._refresh()

    def refresh_view(self) -> None:
        self._refresh()

    def is_active(self) -> bool:
        return self._remaining_seconds > 0.0

    def _refresh(self) -> None:
        remaining = max(0.0, self._remaining_seconds)
        if remaining <= 0.0:
            self.setVisible(False)
            return

        stacks = max(1, int(math.ceil(remaining / self._stack_seconds)))
        self._title.setText(self._title_text)
        self._time.setText(_format_duration(remaining))
        self._stacks.setText(f"x{stacks}" if stacks > 1 else "")
        self.setVisible(True)


class RewardsPlane(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("rewardsPlane")
        self.setProperty("tone", "dark")
        self.setFixedSize(240, 240)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        self.setLayout(layout)

        self._win = BuffStackTile(kind="win", title="Win Bonus (Idle EXP)")
        layout.addWidget(self._win)

        self._loss = BuffStackTile(kind="loss", title="Loss Penalty (Idle EXP)")
        layout.addWidget(self._loss)

        layout.addStretch(1)

        timer = QTimer(self)
        timer.setInterval(1000)
        timer.timeout.connect(self._tick)
        timer.start()
        self._timer = timer
        self._update_visibility()

    def set_idle_exp_timers(self, *, bonus_seconds: float, penalty_seconds: float) -> None:
        self._win.set_timer(remaining_seconds=bonus_seconds, stack_seconds=WIN_STACK_SECONDS)
        self._loss.set_timer(remaining_seconds=penalty_seconds, stack_seconds=LOSS_STACK_SECONDS)
        self._update_visibility()

    def _update_visibility(self) -> None:
        self.setVisible(True)

    def _tick(self) -> None:
        self._win.refresh_view()
        self._loss.refresh_view()
        self._update_visibility()
