from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout

from endless_idler.save import next_party_level_up_cost
from endless_idler.ui.resource_tooltips import build_party_level_tooltip
from endless_idler.ui.tooltip import hide_stained_tooltip, show_stained_tooltip


class StandbyPartyLevelTile(QFrame):
    level_requested = Signal()

    def __init__(self, *, level: int = 1, cost: int = 0) -> None:
        super().__init__()
        self.setObjectName("standbyPartyLevelTile")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(110, 130)
        
        # Store for tooltip
        self._current_level = level
        self._current_cost = cost

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
        
        # Enable hover events for tooltip
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def set_level(self, level: int) -> None:
        self._current_level = max(1, int(level))
        self._value.setText(f"Lv {self._current_level}")

    def set_cost(self, cost: int) -> None:
        self._current_cost = max(0, int(cost))
        self._cost.setText(f"Cost: {self._current_cost}" if self._current_cost else "")

    def mousePressEvent(self, event: object) -> None:
        try:
            button = event.button()
        except AttributeError:
            return
        if button != Qt.MouseButton.LeftButton:
            return
        self.level_requested.emit()
    
    def enterEvent(self, event: object) -> None:
        # Calculate next cost for preview
        next_cost = next_party_level_up_cost(
            new_level=self._current_level + 1,
            previous_cost=self._current_cost
        )
        
        html = build_party_level_tooltip(
            level=self._current_level,
            cost=self._current_cost,
            next_cost=next_cost,
        )
        show_stained_tooltip(self, html)
        try:
            super().enterEvent(event)  # type: ignore[misc]
        except Exception:
            pass
    
    def leaveEvent(self, event: object) -> None:
        hide_stained_tooltip()
        try:
            super().leaveEvent(event)  # type: ignore[misc]
        except Exception:
            pass
