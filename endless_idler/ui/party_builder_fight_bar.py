from __future__ import annotations

from PySide6.QtCore import QEasingCurve
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout


class FightBar(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("fightBar")
        self.setFixedSize(230, 44)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(0)
        self.setLayout(layout)

        label = QLabel("Fight")
        label.setObjectName("fightBarLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(1.0)
        self.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(1800)
        anim.setLoopCount(-1)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.setKeyValueAt(0.0, 0.55)
        anim.setKeyValueAt(0.5, 1.0)
        anim.setKeyValueAt(1.0, 0.55)
        anim.start()
        self._pulse_anim = anim
