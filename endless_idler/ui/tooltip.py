from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


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
        shadow = QGraphicsDropShadowEffect(self._panel)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 200))
        self._panel.setGraphicsEffect(shadow)
        layout.addWidget(self._panel)

        # Content layout inside panel
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(12, 10, 12, 10)
        panel_layout.setSpacing(0)
        self._panel.setLayout(panel_layout)

        # Text content label
        self._content = QLabel()
        self._content.setObjectName("stainedTooltipContent")
        self._content.setTextFormat(Qt.TextFormat.RichText)
        self._content.setWordWrap(True)
        panel_layout.addWidget(self._content)

        self._element_id: str | None = None
        self.hide()

    def set_html(self, html: str, *, element_id: str | None = None) -> None:
        self._content.setText(html)
        self._element_id = element_id
        self._content.adjustSize()
        self._panel.adjustSize()
        self.adjustSize()
        self._apply_glass_style()

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

    def _apply_glass_style(self) -> None:
        """Apply true glass morphism style with element-based tinting and enhanced readability."""
        if not self._element_id:
            # Default glass tint - subtle blue-gray with increased opacity for better readability
            background = "rgba(90, 110, 140, 180)"
            border_color = "rgba(255, 255, 255, 120)"
        else:
            # Element-tinted glass effect
            from endless_idler.ui.battle.colors import color_for_damage_type_id
            color = color_for_damage_type_id(self._element_id)
            
            # Use element color with increased opacity for better readability while maintaining glass effect
            background = f"rgba({color.red()}, {color.green()}, {color.blue()}, 160)"
            
            # Brighter border with slight element tint for enhanced glass appearance
            border_r = min(255, color.red() + 100)
            border_g = min(255, color.green() + 100)
            border_b = min(255, color.blue() + 100)
            border_color = f"rgba({border_r}, {border_g}, {border_b}, 120)"
        
        # Apply glass morphism stylesheet
        # - Increased opacity background for better text readability
        # - Square corners for stained glass aesthetic
        # - Bright border with subtle glow effect
        self._panel.setStyleSheet(
            f"QFrame#stainedTooltipPanel {{ "
            f"background-color: {background}; "
            f"border: 1px solid {border_color}; "
            f"border-radius: 0px; "
            f"}}"
        )
