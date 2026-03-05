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

        scrim = QFrame(self)
        scrim.setObjectName("HomeScrim")
        scrim_layout = QVBoxLayout(scrim)
        scrim_layout.setContentsMargins(12, 12, 12, 12)
        scrim_layout.setSpacing(10)
        root.addWidget(scrim, 1)

        title = QLabel("Stained Glass Odyssey")
        title.setObjectName("HomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        scrim_layout.addWidget(title)

        subtitle = QLabel("Home")
        subtitle.setObjectName("HomeSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        scrim_layout.addWidget(subtitle)

        tabs = QTabBar()
        tabs.setObjectName("HomeTabs")
        tabs.setDocumentMode(True)
        tabs.setExpanding(True)
        tabs.addTab("Overview")
        tabs.addTab("Legacy")
        tabs.setCurrentIndex(0)
        scrim_layout.addWidget(tabs)

        pane = QFrame(self)
        pane.setObjectName("HomePane")
        pane_layout = QVBoxLayout(pane)
        pane_layout.setContentsMargins(12, 12, 12, 12)
        pane_layout.setSpacing(8)
        scrim_layout.addWidget(pane, 1)

        headers = QWidget(pane)
        headers.setObjectName("HomeHeaders")
        headers_layout = QVBoxLayout(headers)
        headers_layout.setContentsMargins(0, 0, 0, 0)
        headers_layout.setSpacing(6)
        pane_layout.addWidget(headers)

        h1 = QLabel("Section")
        h1.setObjectName("HomeHeaderLabel")
        headers_layout.addWidget(h1)

        h2 = QLabel("Status")
        h2.setObjectName("HomeHeaderLabel")
        headers_layout.addWidget(h2)

        h3 = QLabel("Notes")
        h3.setObjectName("HomeHeaderLabel")
        headers_layout.addWidget(h3)

        for stain in ("slate", "cyan", "emerald"):
            row = QFrame(pane)
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

            pane_layout.addWidget(row)

        pane_layout.addStretch(1)
