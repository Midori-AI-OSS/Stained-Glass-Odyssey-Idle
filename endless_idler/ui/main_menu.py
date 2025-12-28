from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.ui.assets import asset_path
from endless_idler.ui.icons import lucide_icon
from endless_idler.ui.icons import lucide_service


class MainMenuWidget(QWidget):
    play_requested = Signal()
    settings_requested = Signal()
    warp_requested = Signal()
    guidebook_requested = Signal()
    feedback_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._buttons_by_icon: dict[str, list[QPushButton]] = {}

        root = QHBoxLayout()
        root.setContentsMargins(56, 56, 56, 56)
        root.setSpacing(24)
        self.setLayout(root)

        root.addStretch(1)

        menu_panel = QFrame()
        menu_panel.setObjectName("mainMenuPanel")
        menu_panel.setFrameShape(QFrame.Shape.NoFrame)
        menu_panel.setFixedWidth(320)
        root.addWidget(menu_panel, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        glow = QGraphicsDropShadowEffect(menu_panel)
        glow.setBlurRadius(44)
        glow.setOffset(0, 0)
        glow.setColor(QColor(255, 120, 80, 95))
        menu_panel.setGraphicsEffect(glow)

        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(18, 18, 18, 18)
        menu_layout.setSpacing(10)
        menu_panel.setLayout(menu_layout)

        title = QLabel("Stained Glass Odyssey Idle")
        title.setObjectName("mainMenuTitle")
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        menu_layout.addWidget(title)

        menu_layout.addSpacing(8)
        menu_layout.addWidget(self._make_button("Run", "play", self.play_requested.emit))
        menu_layout.addWidget(self._make_button("Warp", "package-open", self.warp_requested.emit))
        menu_layout.addWidget(self._make_button("Guidebook", "book", self.guidebook_requested.emit))
        menu_layout.addWidget(self._make_button("Settings", "settings", self.settings_requested.emit))
        menu_layout.addWidget(self._make_button("Feedback", "message-square", self.feedback_requested.emit))
        menu_layout.addStretch(1)

        service = lucide_service()
        service.svg_ready.connect(self._on_svg_ready)
        for icon_name in self._buttons_by_icon:
            service.ensure_svg(icon_name)

    def _make_button(self, label: str, icon_name: str, on_click: Callable[[], None]) -> QPushButton:
        button = QPushButton(label)
        button.setObjectName(f"mainMenuButton_{label.lower().replace(' ', '_')}")
        button.setProperty("stainedMenu", "true")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIcon(lucide_icon(icon_name, 20))
        button.setIconSize(QSize(20, 20))
        button.setMinimumHeight(52)
        button.clicked.connect(on_click)
        self._buttons_by_icon.setdefault(icon_name, []).append(button)
        return button

    def _on_svg_ready(self, name: str) -> None:
        buttons = self._buttons_by_icon.get(name)
        if not buttons:
            return
        icon = lucide_icon(name, 20)
        if icon.isNull():
            return
        for button in buttons:
            button.setIcon(icon)


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

        self.setWindowTitle("Stained Glass Odyssey Idle")
        self.resize(960, 540)

        menu = MainMenuWidget()
        menu.play_requested.connect(lambda: print("Play clicked"))
        menu.settings_requested.connect(lambda: print("Settings clicked"))
        menu.warp_requested.connect(lambda: print("Warp clicked"))
        menu.guidebook_requested.connect(lambda: print("Guidebook clicked"))
        menu.feedback_requested.connect(lambda: print("Feedback clicked"))

        background = MainMenuBackground()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        background.setLayout(layout)
        layout.addWidget(menu)
        self.setCentralWidget(background)
