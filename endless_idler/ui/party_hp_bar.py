from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QSizePolicy


class PartyHpHeader(QFrame):
    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("partyHpHeader")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

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

    def set_hp(self, *, current: int, max_hp: int) -> None:
        max_hp = max(0, int(max_hp))
        current = max(0, int(current))
        current = min(current, max_hp) if max_hp else 0

        self._bar.setRange(0, max_hp if max_hp > 0 else 1)
        self._bar.setValue(current)
        self._bar.setTextVisible(max_hp > 0)
