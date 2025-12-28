from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtWidgets import QWidget


MIME_TYPE = "application/x-endless-idler-character"

STAR_COLORS: dict[int, str] = {
    1: "#808080",
    2: "#1E90FF",
    3: "#228B22",
    4: "#800080",
    5: "#FF3B30",
    6: "#FFD700",
}


def set_pixmap(
    label: QLabel,
    path: Path | None,
    *,
    size: int,
    placeholder: str | None = None,
) -> None:
    pixmap = QPixmap(str(path)) if path else QPixmap()
    if pixmap.isNull():
        if placeholder:
            label.setPixmap(_placeholder_pixmap(placeholder, size=size))
        else:
            label.clear()
        return
    label.setPixmap(
        pixmap.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    )


def derive_display_name(char_id: str) -> str:
    return " ".join(part.capitalize() for part in char_id.split("_"))


def sanitize_stars(stars: int) -> int:
    if stars <= 0:
        return 1
    if stars > 6:
        return 6
    return stars


def apply_star_rank_visuals(widget: QWidget, stars: int) -> None:
    stars = sanitize_stars(stars)
    widget.setProperty("starRank", stars)
    widget.setGraphicsEffect(_make_glow(widget, stars))
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def clear_star_rank_visuals(widget: QWidget) -> None:
    widget.setProperty("starRank", None)
    widget.setGraphicsEffect(None)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def _make_glow(widget: QWidget, stars: int) -> QGraphicsDropShadowEffect:
    glow = QGraphicsDropShadowEffect(widget)
    glow.setBlurRadius(20)
    glow.setOffset(0, 0)
    glow.setColor(QColor(STAR_COLORS.get(stars, "#708090")))
    return glow


def _placeholder_pixmap(text: str, *, size: int) -> QPixmap:
    initials = _initials(text)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.fillRect(pixmap.rect(), Qt.GlobalColor.darkGray)
    painter.setPen(Qt.GlobalColor.white)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, initials)
    painter.end()
    return pixmap


def _initials(text: str) -> str:
    parts = [part for part in text.replace("_", " ").split(" ") if part]
    if not parts:
        return "?"
    return "".join(part[0].upper() for part in parts[:2])
