from __future__ import annotations

from typing import override

from PySide6.QtCore import QEvent
from PySide6.QtCore import Qt
from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QWidget

from endless_idler.ui.components.progress_bar import AnimatedProgressBar
from endless_idler.ui.tooltip import hide_stained_tooltip
from endless_idler.ui.tooltip import show_stained_tooltip


class BlessingPanel(QFrame):
    """Reusable panel for displaying a blessing with progress bar and mod value.

    Layout: [Blessing Name] [AnimatedProgressBar] [Total Mod Value]

    Requires theme/blessing_panel.py tokens for visual consistency.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("blessingPanel")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._tooltip_html: str = ""
        self._color_id: str = "generic"

        # Main horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Blessing name label
        self._name_label = QLabel("Blessing")
        self._name_label.setObjectName("blessingPanelName")
        self._name_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self._name_label, 0)

        # Animated progress bar
        self._progress_bar = AnimatedProgressBar()
        self._progress_bar.setObjectName("blessingPanelProgressBar")
        self._progress_bar.setFixedHeight(18)
        self._progress_bar.set_value(0.0)
        layout.addWidget(self._progress_bar, 1)

        # Mod value label
        self._mod_label = QLabel("x1.0000")
        self._mod_label.setObjectName("blessingPanelModValue")
        self._mod_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self._mod_label, 0)

    def set_blessing_name(self, name: str) -> None:
        """Set the blessing name displayed in the panel.

        Args:
            name: The blessing name to display
        """
        self._name_label.setText(str(name))

    def set_current_progress(self, progress: float) -> None:
        """Set the current progress value (0.0 to 1.0).

        Args:
            progress: Progress value from 0.0 to 1.0
        """
        self._progress_bar.set_value(float(progress))

    def set_mod_value(self, value: str) -> None:
        """Set the mod value displayed (e.g., "x1.2500" or "+25%").

        Args:
            value: The mod value string to display
        """
        self._mod_label.setText(str(value))

    def set_tooltip_html(self, html: str | None) -> None:
        """Set the tooltip HTML content. If None or empty, no tooltip is shown.

        Args:
            html: HTML content for the tooltip, or None to disable
        """
        self._tooltip_html = str(html) if html else ""

    def set_color_id(self, color_id: str) -> None:
        """Set the element color ID for theming (e.g., "fire", "ice", "lightning").

        Args:
            color_id: Element identifier for color theming
        """
        new_id = (
            str(color_id or "generic")
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )
        if self._color_id == new_id:
            return
        self._color_id = new_id
        _ = self.setProperty("elementId", self._color_id)
        style = self.style()
        style.unpolish(self)
        style.polish(self)
        self.update()

    @override
    def enterEvent(self, event: QEnterEvent) -> None:
        if self._tooltip_html:
            show_stained_tooltip(self, self._tooltip_html, element_id=self._color_id)
        try:
            super().enterEvent(event)
        except Exception:
            return

    @override
    def leaveEvent(self, event: QEvent) -> None:
        hide_stained_tooltip()
        try:
            super().leaveEvent(event)
        except Exception:
            return
