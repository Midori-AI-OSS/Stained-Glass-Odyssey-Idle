from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QSizePolicy

from endless_idler.ui.resource_tooltips import build_party_hp_tooltip
from endless_idler.ui.tooltip import hide_stained_tooltip, show_stained_tooltip


class PartyHpHeader(QFrame):
    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("partyHpHeader")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Store for tooltip
        self._current = 0
        self._max_hp = 0
        self._fight_number = 1

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)
        self.setLayout(layout)

        label = QLabel("Party HP")
        label.setObjectName("partyHpHeaderLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignVCenter)

        bar = QProgressBar()
        bar.setObjectName("partyHpHeaderBar")
        bar.setTextVisible(True)
        bar.setFormat("%v / %m")
        bar.setFixedWidth(220)
        layout.addWidget(bar, 0, Qt.AlignmentFlag.AlignVCenter)

        self._bar = bar
        
        # Enable hover events for tooltip
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def set_hp(self, *, current: int, max_hp: int, fight_number: int = 1) -> None:
        self._max_hp = max(0, int(max_hp))
        self._current = max(0, int(current))
        self._current = min(self._current, self._max_hp) if self._max_hp else 0
        self._fight_number = max(1, int(fight_number))

        self._bar.setRange(0, self._max_hp if self._max_hp > 0 else 1)
        self._bar.setValue(self._current)
        self._bar.setTextVisible(self._max_hp > 0)
    
    def enterEvent(self, event: object) -> None:
        html = build_party_hp_tooltip(
            current=self._current,
            max_hp=self._max_hp,
            fight_number=self._fight_number,
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
