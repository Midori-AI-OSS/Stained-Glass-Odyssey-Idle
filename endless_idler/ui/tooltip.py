from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPoint
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtGui import QGuiApplication
from PySide6.QtGui import QColor
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsBlurEffect
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.ui.assets import asset_path


_TOOLTIP: "StainedGlassTooltip | None" = None


def show_stained_tooltip(owner: QWidget, html: str) -> None:
    global _TOOLTIP  # noqa: PLW0603

    if not html:
        hide_stained_tooltip()
        return

    if _TOOLTIP is None:
        _TOOLTIP = StainedGlassTooltip()

    _TOOLTIP.set_html(html)
    _TOOLTIP.show_near_cursor(owner)


def hide_stained_tooltip() -> None:
    if _TOOLTIP is None:
        return
    _TOOLTIP.hide()


class StainedGlassTooltip(QFrame):
    def __init__(self) -> None:
        super().__init__(None)
        self.setObjectName("stainedTooltip")
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self._base_pixmap = self._load_background()

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self._bg = QLabel()
        self._bg.setObjectName("stainedTooltipBackground")
        self._bg.setScaledContents(True)
        blur = QGraphicsBlurEffect(self._bg)
        blur.setBlurRadius(14)
        self._bg.setGraphicsEffect(blur)
        layout.addWidget(self._bg, 0, 0, 1, 1)

        self._panel = QFrame()
        self._panel.setObjectName("stainedTooltipPanel")
        shadow = QGraphicsDropShadowEffect(self._panel)
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        self._panel.setGraphicsEffect(shadow)
        layout.addWidget(self._panel, 0, 0, 1, 1)

        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(0)
        self._panel.setLayout(panel_layout)

        self._content = QLabel()
        self._content.setObjectName("stainedTooltipContent")
        self._content.setTextFormat(Qt.TextFormat.RichText)
        self._content.setWordWrap(True)
        panel_layout.addWidget(self._content)

        self.hide()

    def set_html(self, html: str) -> None:
        self._content.setText(html)
        self._content.adjustSize()
        self._panel.adjustSize()
        self.adjustSize()
        self._refresh_background()

    def show_near_cursor(self, owner: QWidget) -> None:
        pos = QCursor.pos()
        screen = QGuiApplication.screenAt(pos)
        if screen is None and owner is not None:
            screen = QGuiApplication.screenAt(owner.mapToGlobal(QPoint(0, 0)))
        if screen is None:
            self.move(pos + QPoint(14, 18))
            self.show()
            return

        geo = screen.availableGeometry()
        size = self.sizeHint()
        x = pos.x() + 14
        y = pos.y() + 18
        if x + size.width() > geo.right():
            x = pos.x() - size.width() - 14
        if y + size.height() > geo.bottom():
            y = pos.y() - size.height() - 18
        x = max(geo.left(), min(x, geo.right() - size.width()))
        y = max(geo.top(), min(y, geo.bottom() - size.height()))

        self.move(QPoint(x, y))
        self.show()

    def _refresh_background(self) -> None:
        if self._base_pixmap.isNull():
            return
        size = self.size()
        if size.width() <= 0 or size.height() <= 0:
            return
        scaled = self._base_pixmap.scaled(
            size,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        scaled = self._apply_stained_glass_overlay(scaled)
        self._bg.setPixmap(scaled)

    def _load_background(self) -> QPixmap:
        path = Path(asset_path("backgrounds", "main_menu_cityscape.png"))
        pixmap = QPixmap(str(path))
        return pixmap if not pixmap.isNull() else QPixmap()

    def _apply_stained_glass_overlay(self, pixmap: QPixmap) -> QPixmap:
        tinted = QPixmap(pixmap)
        painter = QPainter(tinted)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        width = tinted.width()
        height = tinted.height()
        cell = 32

        for y in range(0, height, cell):
            for x in range(0, width, cell):
                seed = (x * 73856093) ^ (y * 19349663) ^ 0xA5A5A5
                r = 80 + (seed & 0x3F)
                g = 70 + ((seed >> 7) & 0x3F)
                b = 95 + ((seed >> 14) & 0x3F)
                painter.fillRect(x, y, cell, cell, QColor(r, g, b, 38))

        painter.setPen(QColor(0, 0, 0, 55))
        for x in range(0, width + 1, cell):
            painter.drawLine(x, 0, x, height)
        for y in range(0, height + 1, cell):
            painter.drawLine(0, y, width, y)

        painter.end()
        return tinted
