from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout


class StandbyShopTile(QFrame):
    toggled = Signal(bool)

    def __init__(self, *, tokens: int = 0, open_: bool = True) -> None:
        super().__init__()
        self.setObjectName("standbyShopTile")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(110, 130)

        self._open = bool(open_)
        self.setProperty("open", self._open)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        self.setLayout(layout)

        layout.addStretch(1)

        self._token_label = QLabel()
        self._token_label.setObjectName("standbyShopTokens")
        self._token_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._token_label)

        self._label = QLabel("Shop")
        self._label.setObjectName("standbyShopLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        layout.addStretch(1)
        self.set_tokens(tokens)

    @property
    def token_label(self) -> QLabel:
        return self._token_label

    def set_tokens(self, tokens: int) -> None:
        self._token_label.setText(f"Coins: {max(0, int(tokens))}")

    def set_open(self, open_: bool) -> None:
        self._open = bool(open_)
        self.setProperty("open", self._open)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event: object) -> None:
        try:
            button = event.button()
        except AttributeError:
            return
        if button != Qt.MouseButton.LeftButton:
            return
        self.set_open(not self._open)
        self.toggled.emit(self._open)
