from __future__ import annotations

from PySide6.QtCore import QEasingCurve
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsOpacityEffect


class PulsingPlane(QFrame):
    def __init__(self, *, object_name: str, tone: str) -> None:
        super().__init__()
        self.setObjectName(object_name)
        self.setProperty("tone", tone)
        self.setFixedSize(360, 360)

        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(1.0)
        self.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(2600)
        anim.setLoopCount(-1)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.setKeyValueAt(0.0, 0.78)
        anim.setKeyValueAt(0.5, 0.95)
        anim.setKeyValueAt(1.0, 0.78)
        anim.start()
        self._pulse_anim = anim
