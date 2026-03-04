from __future__ import annotations

import math

from PySide6.QtCore import QEasingCurve
from PySide6.QtCore import QPoint
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtCore import QRect
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPen
from PySide6.QtGui import QPolygon
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QWidget


class MergeArrow(QFrame):
    def __init__(self, *, start: QPoint, end: QPoint, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._start = QPoint(start)
        self._end = QPoint(end)

    def set_points(self, *, start: QPoint, end: QPoint) -> None:
        self._start = QPoint(start)
        self._end = QPoint(end)
        self.update()

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        start = self._start
        end = self._end
        if start == end:
            return

        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.GlobalColor.white)
        painter.setPen(pen)
        painter.drawLine(start, end)

        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.hypot(dx, dy)
        if length <= 0.0:
            return

        ux = dx / length
        uy = dy / length
        px = -uy
        py = ux

        head_len = 12.0
        head_w = 7.0
        tip = end
        base_x = end.x() - int(round(ux * head_len))
        base_y = end.y() - int(round(uy * head_len))
        left = QPoint(
            base_x + int(round(px * head_w)),
            base_y + int(round(py * head_w)),
        )
        right = QPoint(
            base_x - int(round(px * head_w)),
            base_y - int(round(py * head_w)),
        )
        painter.setBrush(Qt.GlobalColor.white)
        painter.drawPolygon(QPolygon([tip, left, right]))


class MergeFxOverlay(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def play_merge(self, *, sources: list[QWidget], destination: QWidget) -> None:
        if not sources:
            return
        if destination is None:
            return
        if not self.isVisible():
            self.show()

        end = self._widget_center(destination)
        for source in sources:
            if source is None:
                continue
            start = self._widget_center(source)
            self._spawn_arrow(start=start, end=end)
            self._spawn_dissolve(source, start_center=start)

    def _widget_center(self, widget: QWidget) -> QPoint:
        global_center = widget.mapToGlobal(widget.rect().center())
        return self.mapFromGlobal(global_center)

    def _spawn_arrow(self, *, start: QPoint, end: QPoint) -> None:
        arrow = MergeArrow(start=start, end=end, parent=self)
        arrow.setGeometry(self.rect())
        effect = QGraphicsOpacityEffect(arrow)
        effect.setOpacity(0.0)
        arrow.setGraphicsEffect(effect)
        arrow.show()

        anim = QPropertyAnimation(effect, b"opacity", arrow)
        anim.setDuration(520)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.setKeyValueAt(0.0, 0.0)
        anim.setKeyValueAt(0.2, 0.85)
        anim.setKeyValueAt(1.0, 0.0)
        anim.finished.connect(arrow.deleteLater)
        anim.start()

    def _spawn_dissolve(self, source: QWidget, *, start_center: QPoint) -> None:
        pixmap = source.grab()
        if pixmap.isNull():
            return

        sprite = QLabel(self)
        sprite.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        sprite.setPixmap(pixmap)
        sprite.adjustSize()
        sprite_rect = QRect(
            start_center.x() - sprite.width() // 2,
            start_center.y() - sprite.height() // 2,
            sprite.width(),
            sprite.height(),
        )
        sprite.setGeometry(sprite_rect)

        effect = QGraphicsOpacityEffect(sprite)
        effect.setOpacity(1.0)
        sprite.setGraphicsEffect(effect)
        sprite.show()

        fade = QPropertyAnimation(effect, b"opacity", sprite)
        fade.setDuration(520)
        fade.setEasingCurve(QEasingCurve.Type.InOutSine)
        fade.setKeyValueAt(0.0, 1.0)
        fade.setKeyValueAt(1.0, 0.0)
        fade.finished.connect(sprite.deleteLater)
        fade.start()

        shrink = QPropertyAnimation(sprite, b"geometry", sprite)
        shrink.setDuration(520)
        shrink.setEasingCurve(QEasingCurve.Type.InOutSine)
        shrink.setStartValue(sprite_rect)
        shrink.setEndValue(
            QRect(
                start_center.x() - max(6, sprite.width() // 8),
                start_center.y() - max(6, sprite.height() // 8),
                max(12, sprite.width() // 4),
                max(12, sprite.height() // 4),
            )
        )
        shrink.start()

        QTimer.singleShot(900, sprite.deleteLater)

