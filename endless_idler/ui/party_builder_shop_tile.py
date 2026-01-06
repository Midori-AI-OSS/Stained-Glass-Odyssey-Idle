from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout

from endless_idler.ui.resource_tooltips import build_tokens_tooltip
from endless_idler.ui.tooltip import hide_stained_tooltip, show_stained_tooltip


class StandbyShopTile(QFrame):
    toggled = Signal(bool)

    def __init__(self, *, tokens: int = 0, open_: bool = True) -> None:
        super().__init__()
        self.setObjectName("standbyShopTile")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(110, 130)

        self._open = bool(open_)
        self.setProperty("open", self._open)
        
        # Store for tooltip generation
        self._current_tokens = tokens
        self._bonus = 0
        self._winstreak = 0

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
        
        # Enable hover events for tooltip
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    @property
    def token_label(self) -> QLabel:
        return self._token_label

    def set_tokens(self, tokens: int, *, bonus: int = 0, winstreak: int = 0) -> None:
        self._current_tokens = max(0, int(tokens))
        self._bonus = max(0, int(bonus))
        self._winstreak = max(0, int(winstreak))
        self._token_label.setText(f"{self._current_tokens}")

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
    
    def enterEvent(self, event: object) -> None:
        html = build_tokens_tooltip(
            current=self._current_tokens,
            bonus=self._bonus,
            winstreak=self._winstreak,
        )
        show_stained_tooltip(self, html)
        try:
            super().enterEvent(event)  # type: ignore[misc]
        except Exception:
            pass
    
    def leaveEvent(self, event: object) -> None:
        hide_stained_tooltip()
        try:
            super().leaveEvent(event)  # type: ignore[misc]
        except Exception:
            pass
