from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSizePolicy

from endless_idler.ui.components.progress_bar import AnimatedProgressBar


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

        bar = AnimatedProgressBar()
        bar.setObjectName("partyHpHeaderBar")
        bar.setFixedHeight(12)
        bar.set_value(0.0)
        bar.setText("0 / 0")
        bar._gradient_enabled = False
        bar.set_color_thresholds(
            [
                (0.0, (231, 76, 60, 170)),
                (0.25, (243, 156, 18, 170)),
                (0.45, (241, 196, 15, 185)),
                (0.65, (46, 204, 113, 165)),
            ]
        )
        layout.addWidget(bar, 0, Qt.AlignmentFlag.AlignVCenter)

        self._bar = bar

    def set_hp(self, *, current: int, max_hp: int) -> None:
        max_hp = max(0, int(max_hp))
        current = max(0, int(current))
        current = min(current, max_hp) if max_hp else 0

        if max_hp > 0:
            self._bar.set_value(current / max_hp)
            self._bar.setText(f"{current} / {max_hp}")
        else:
            self._bar.set_value(0.0)
            self._bar.setText("0 / 0")
