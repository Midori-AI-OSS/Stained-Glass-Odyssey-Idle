from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QTabBar
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


class HomePage(QWidget):
    """Decorative home shell inspired by Agents Runner dashboard chrome."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HomePageRoot")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        panel = QFrame(self)
        panel.setObjectName("HomePanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.setSpacing(10)
        root.addWidget(panel, 1)

        title = QLabel("Stained Glass Odyssey")
        title.setObjectName("HomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        panel_layout.addWidget(title)

        tabs = QTabBar()
        tabs.setObjectName("HomeTabs")
        tabs.setDocumentMode(True)
        tabs.setExpanding(True)
        tabs.addTab("Overview")
        tabs.addTab("Upgrades")
        tabs.setCurrentIndex(0)
        panel_layout.addWidget(tabs)

        for stain in ("slate", "cyan", "emerald"):
            row = QFrame(panel)
            row.setObjectName("HomeDecorRow")
            row.setProperty("stain", stain)
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(10, 10, 10, 10)
            row_layout.setSpacing(2)

            row_title = QLabel("Decorative panel")
            row_title.setObjectName("HomeRowTitle")
            row_layout.addWidget(row_title)

            row_note = QLabel("Navigation and runtime controls live in the top bar.")
            row_note.setObjectName("HomeRowNote")
            row_note.setWordWrap(True)
            row_layout.addWidget(row_note)

            panel_layout.addWidget(row)

        panel_layout.addStretch(1)
