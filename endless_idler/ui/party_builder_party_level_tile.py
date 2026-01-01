from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class StandbyPartyLevelTile(QFrame):
    level_requested = Signal()

    def __init__(self, *, level: int = 1, cost: int = 0) -> None:
        super().__init__()
        self.setObjectName("standbyPartyLevelTile")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(110, 130)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        self.setLayout(layout)

        layout.addStretch(1)

        self._title = QLabel("Party Level")
        self._title.setObjectName("standbyPartyLevelTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title)

        self._value = QLabel()
        self._value.setObjectName("standbyPartyLevelValue")
        self._value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._value)

        self._cost = QLabel()
        self._cost.setObjectName("standbyPartyLevelCost")
        self._cost.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._cost)

        layout.addStretch(1)
        self.set_level(level)
        self.set_cost(cost)

    def set_level(self, level: int) -> None:
        self._value.setText(f"Lv {max(1, int(level))}")

    def set_cost(self, cost: int) -> None:
        cost = max(0, int(cost))
        self._cost.setText(f"Cost: {cost}" if cost else "")

    def mousePressEvent(self, event: object) -> None:
        try:
            button = event.button()
        except AttributeError:
            return
        if button != Qt.MouseButton.LeftButton:
            return
        self.level_requested.emit()
