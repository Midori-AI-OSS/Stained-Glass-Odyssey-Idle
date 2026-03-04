from __future__ import annotations

import random

from PySide6.QtCore import QPoint
from PySide6.QtCore import QRect
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from PySide6.QtGui import QCursor
from PySide6.QtGui import QGuiApplication
from PySide6.QtGui import QImage
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPen
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsBlurEffect
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.ui.theme.colors import color_for_damage_type_id

_TOOLTIP: "StainedGlassTooltip | None" = None


def show_stained_tooltip(owner: QWidget, html: str, *, element_id: str | None = None) -> None:
    global _TOOLTIP  # noqa: PLW0603

    if not html:
        hide_stained_tooltip()
        return

    if _TOOLTIP is None:
        _TOOLTIP = StainedGlassTooltip()

    _TOOLTIP.set_html(html, element_id=element_id)
    _TOOLTIP.show_near_cursor(owner)


def hide_stained_tooltip() -> None:
    if _TOOLTIP is None:
        return
    _TOOLTIP.hide()


class _TooltipBackdropFrame(QFrame):
    def __init__(self) -> None:
        super().__init__(None)
        self._pixmap = QPixmap()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self._pixmap = pixmap
        self.update()

    def paintEvent(self, event) -> None:  # noqa: ANN001
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        if not self._pixmap.isNull():
            painter.drawPixmap(self.rect(), self._pixmap)
        painter.end()


class StainedGlassTooltip(QFrame):
    def __init__(self) -> None:
        super().__init__(None)
        self.setObjectName("stainedTooltip")
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # Main layout for the tooltip
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Panel with drop shadow for depth
        self._panel = QFrame()
        self._panel.setObjectName("stainedTooltipPanel")
        self._panel.setProperty("elementId", "generic")
        shadow = QGraphicsDropShadowEffect(self._panel)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 200))
        self._panel.setGraphicsEffect(shadow)
        layout.addWidget(self._panel)

        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        self._panel.setLayout(panel_layout)

        self._backdrop = _TooltipBackdropFrame()
        self._backdrop.setObjectName("stainedTooltipBackdrop")
        panel_layout.addWidget(self._backdrop)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(12, 10, 12, 10)
        content_layout.setSpacing(0)
        self._backdrop.setLayout(content_layout)

        # Text content label
        self._content = QLabel()
        self._content.setObjectName("stainedTooltipContent")
        self._content.setTextFormat(Qt.TextFormat.RichText)
        self._content.setWordWrap(True)
        content_layout.addWidget(self._content)

        self._element_id: str | None = None
        self._tint_color = QColor(90, 110, 140)
        self.hide()

    def set_html(self, html: str, *, element_id: str | None = None) -> None:
        self._content.setText(html)
        self._element_id = element_id
        self._content.adjustSize()
        self._panel.adjustSize()
        self.adjustSize()
        if self._panel.layout() is not None:
            self._panel.layout().activate()
        if self.layout() is not None:
            self.layout().activate()
        self._apply_glass_style()

    def show_near_cursor(self, owner: QWidget) -> None:
        pos = QCursor.pos()
        screen = QGuiApplication.screenAt(pos)
        if screen is None and owner is not None:
            screen = QGuiApplication.screenAt(owner.mapToGlobal(QPoint(0, 0)))
        if screen is None:
            self.move(pos + QPoint(14, 18))
            self.show()
            QTimer.singleShot(0, lambda: self._refresh_backdrop(None))
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
        screen_to_use = screen
        QTimer.singleShot(0, lambda: self._refresh_backdrop(screen_to_use))

    def _apply_glass_style(self) -> None:
        """Apply true glass morphism style with element-based tinting and enhanced readability."""
        element_id = str(self._element_id or "generic").strip().lower().replace(" ", "_").replace("-", "_")
        if element_id == "generic":
            self._tint_color = QColor(90, 110, 140)
        else:
            # Element-tinted glass effect
            color = color_for_damage_type_id(element_id)

            self._tint_color = QColor(color.red(), color.green(), color.blue())

        if self._panel.property("elementId") != element_id:
            self._panel.setProperty("elementId", element_id)
            style = self._panel.style()
            if style is not None:
                style.unpolish(self._panel)
                style.polish(self._panel)
            self._panel.update()

    def _blur_pixmap(self, pixmap: QPixmap, *, radius: float) -> QPixmap:
        if pixmap.isNull():
            return pixmap

        margin = max(1, int(radius * 2))
        canvas = QImage(
            pixmap.width() + (margin * 2),
            pixmap.height() + (margin * 2),
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        canvas.fill(Qt.GlobalColor.transparent)

        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)
        item.setOffset(margin, margin)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(radius)
        item.setGraphicsEffect(blur)
        scene.addItem(item)
        scene.setSceneRect(0, 0, canvas.width(), canvas.height())

        painter = QPainter(canvas)
        scene.render(painter)
        painter.end()

        return QPixmap.fromImage(canvas.copy(QRect(margin, margin, pixmap.width(), pixmap.height())))

    def _make_frosted_fallback(self, width: int, height: int) -> QPixmap:
        image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.fillRect(
            image.rect(),
            QColor(self._tint_color.red(), self._tint_color.green(), self._tint_color.blue(), 155),
        )
        painter.fillRect(image.rect(), QColor(0, 0, 0, 90))

        pen = QPen(QColor(255, 255, 255, 18))
        pen.setWidth(1)
        painter.setPen(pen)
        step = 5
        for i in range(-height, width, step):
            painter.drawLine(i, 0, i + height, height)

        speckle = random.Random(hash((self._element_id, width, height)) & 0xFFFFFFFF)
        for _ in range(140):
            x = speckle.randrange(0, width)
            y = speckle.randrange(0, height)
            a = speckle.randrange(6, 18)
            painter.fillRect(x, y, 1, 1, QColor(255, 255, 255, a))

        painter.end()

        pixmap = self._blur_pixmap(QPixmap.fromImage(image), radius=2.8)

        tinted = pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
        painter2 = QPainter(tinted)
        painter2.fillRect(
            tinted.rect(),
            QColor(self._tint_color.red(), self._tint_color.green(), self._tint_color.blue(), 55),
        )
        painter2.fillRect(tinted.rect(), QColor(0, 0, 0, 70))
        painter2.end()

        return QPixmap.fromImage(tinted)

    def _refresh_backdrop(self, screen: QScreen | None) -> None:
        panel_w = self._panel.width() or self._panel.sizeHint().width()
        panel_h = self._panel.height() or self._panel.sizeHint().height()
        if panel_w <= 1 or panel_h <= 1:
            self._backdrop.set_pixmap(QPixmap())
            return

        grab: QPixmap | None = None
        if screen is not None:
            panel_global = self.mapToGlobal(self._panel.pos())
            screen_geo = screen.geometry()
            x = panel_global.x() - screen_geo.x()
            y = panel_global.y() - screen_geo.y()

            if x >= 0 and y >= 0:
                grab = screen.grabWindow(0, x, y, panel_w, panel_h)

        if grab is None or grab.isNull():
            self._backdrop.set_pixmap(self._make_frosted_fallback(panel_w, panel_h))
            return

        blurred = self._blur_pixmap(grab, radius=16.0)
        image = blurred.toImage().convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)

        painter = QPainter(image)
        painter.fillRect(image.rect(), QColor(self._tint_color.red(), self._tint_color.green(), self._tint_color.blue(), 90))
        painter.fillRect(image.rect(), QColor(0, 0, 0, 95))
        painter.end()

        self._backdrop.set_pixmap(QPixmap.fromImage(image))
