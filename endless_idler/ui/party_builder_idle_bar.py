from __future__ import annotations

import random

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QLabel, QVBoxLayout


class IdleBar(QFrame):
    clicked = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("idleBar")
        self.setFixedSize(230, 44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(0)
        self.setLayout(layout)

        label = QLabel("Idle")
        label.setObjectName("idleBarLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(1.0)
        self.setGraphicsEffect(effect)
        self._opacity_effect = effect

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(3200)
        anim.setLoopCount(-1)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.setKeyValueAt(0.0, 0.65)
        anim.setKeyValueAt(0.5, 1.0)
        anim.setKeyValueAt(1.0, 0.65)
        anim.start()
        anim.setCurrentTime(random.randint(0, max(1, anim.duration() - 1)))
        self._pulse_anim = anim
        self.set_active(True)

    def set_active(self, active: bool) -> None:
        active = bool(active)
        self.setEnabled(active)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if active
            else Qt.CursorShape.ForbiddenCursor
        )

        if active:
            self.setToolTip("")
            self._opacity_effect.setOpacity(1.0)
            if self._pulse_anim.state() != QPropertyAnimation.State.Running:
                self._pulse_anim.start()
            return

        self.setToolTip("Add at least 1 OnSite character to idle.")
        try:
            self._pulse_anim.stop()
        except Exception:
            pass
        self._opacity_effect.setOpacity(0.35)

    def mousePressEvent(self, event: object) -> None:
        try:
            button = event.button()
        except AttributeError:
            return
        if button != Qt.MouseButton.LeftButton:
            return
        if not self.isEnabled():
            return
        self.clicked.emit()
