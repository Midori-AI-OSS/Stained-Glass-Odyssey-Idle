from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSizePolicy


class NextFightInfo(QFrame):
    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("nextFightInfo")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)
        self.setLayout(layout)

        label = QLabel("Next Fight")
        label.setObjectName("nextFightLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignVCenter)

        self._level_label = QLabel("Level: 1")
        self._level_label.setObjectName("nextFightLevelLabel")
        self._level_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._level_label, 0, Qt.AlignmentFlag.AlignVCenter)

    def set_level(self, level: int) -> None:
        level = max(1, int(level))
        self._level_label.setText(f"Level: {level}")
