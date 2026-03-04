from __future__ import annotations

import json

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout

from endless_idler.ui.party_builder_common import MIME_TYPE


class SellZone(QFrame):
    def __init__(self, *, on_sell: Callable[[str], None]) -> None:
        super().__init__()
        self.setObjectName("sellZone")
        self.setFixedSize(110, 130)

        self._on_sell = on_sell
        self._active = False
        self.setAcceptDrops(False)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)
        self.setLayout(layout)

        self._label = QLabel("Sell")
        self._label.setObjectName("sellZoneLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)
        self._label.hide()

        self.set_active(False)

    def set_active(self, active: bool) -> None:
        self._active = active
        self.setProperty("active", active)
        self.setAcceptDrops(active)
        self._label.setVisible(active)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def dragEnterEvent(self, event: object) -> None:
        if not self._active:
            return
        if not hasattr(event, "mimeData"):
            return
        mime = event.mimeData()
        if not mime.hasFormat(MIME_TYPE):
            return
        event.acceptProposedAction()

    def dropEvent(self, event: object) -> None:
        if not self._active:
            return
        if not hasattr(event, "mimeData"):
            return
        mime = event.mimeData()
        if not mime.hasFormat(MIME_TYPE):
            return

        raw = bytes(mime.data(MIME_TYPE))
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return

        char_id = str(data.get("char_id", "")).strip()
        if not char_id:
            return

        self._on_sell(char_id)
        if hasattr(event, "setDropAction"):
            event.setDropAction(Qt.DropAction.MoveAction)
        if hasattr(event, "accept"):
            event.accept()
