from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtGui import QIcon

from endless_idler.ui.lucide_icons import lucide_icon


def radio_icon(*, size: int = 18, color: QColor | None = None) -> QIcon:
    return lucide_icon("audio-lines", size=size, color=color)
