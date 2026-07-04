from __future__ import annotations

from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QWidget


class IdleArena(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("idleArena")
