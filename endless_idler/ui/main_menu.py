from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.ui.assets import asset_path
from endless_idler.ui.party_builder import PartyBuilderWindow


class MainMenuWidget(QWidget):
    play_requested = Signal()
    party_requested = Signal()
    settings_requested = Signal()
    warp_requested = Signal()
    inventory_requested = Signal()
    guidebook_requested = Signal()
    feedback_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        root = QHBoxLayout()
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(24)
        self.setLayout(root)

        root.addStretch(1)

        menu_panel = QFrame()
        menu_panel.setObjectName("mainMenuPanel")
        menu_panel.setFrameShape(QFrame.Shape.NoFrame)
        menu_panel.setFixedWidth(220)
        root.addWidget(menu_panel, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        glow = QGraphicsDropShadowEffect(menu_panel)
        glow.setBlurRadius(44)
        glow.setOffset(0, 0)
        glow.setColor(QColor(255, 120, 80, 95))
        menu_panel.setGraphicsEffect(glow)

        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(10, 10, 10, 10)
        menu_layout.setSpacing(10)
        menu_panel.setLayout(menu_layout)

        menu_layout.addWidget(self._make_button("Run", self.play_requested.emit))
        menu_layout.addWidget(self._make_button("Party", self.party_requested.emit))
        menu_layout.addWidget(self._make_button("Warp", self.warp_requested.emit))
        menu_layout.addWidget(self._make_button("Inventory", self.inventory_requested.emit))
        menu_layout.addWidget(self._make_button("Guidebook", self.guidebook_requested.emit))
        menu_layout.addWidget(self._make_button("Settings", self.settings_requested.emit))
        menu_layout.addWidget(self._make_button("Feedback", self.feedback_requested.emit))
        menu_layout.addStretch(1)

    def _make_button(self, label: str, on_click: Callable[[], None]) -> QPushButton:
        button = QPushButton(label)
        button.setObjectName(f"mainMenuButton_{label.lower().replace(' ', '_')}")
        button.setProperty("stainedMenu", "true")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(52)
        button.clicked.connect(on_click)
        return button


class MainMenuBackground(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._background = QPixmap(asset_path("backgrounds", "main_menu_cityscape.png"))

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        if not self._background.isNull():
            scaled = self._background.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            painter.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())

        painter.fillRect(self.rect(), QColor(0, 0, 0, 110))
        painter.end()


class MainMenuWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._party_window: PartyBuilderWindow | None = None

        self.setWindowTitle("Stained Glass Odyssey Idle")
        self.resize(960, 540)

        menu = MainMenuWidget()
        menu.play_requested.connect(lambda: print("Play clicked"))
        menu.party_requested.connect(self._open_party_builder)
        menu.settings_requested.connect(lambda: print("Settings clicked"))
        menu.warp_requested.connect(lambda: print("Warp clicked"))
        menu.inventory_requested.connect(lambda: print("Inventory clicked"))
        menu.guidebook_requested.connect(lambda: print("Guidebook clicked"))
        menu.feedback_requested.connect(lambda: print("Feedback clicked"))

        background = MainMenuBackground()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        background.setLayout(layout)
        layout.addWidget(menu)
        self.setCentralWidget(background)

    def _open_party_builder(self) -> None:
        if self._party_window is None:
            self._party_window = PartyBuilderWindow()
        self._party_window.show()
        self._party_window.raise_()
        self._party_window.activateWindow()
