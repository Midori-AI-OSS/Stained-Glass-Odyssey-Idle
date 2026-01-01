from collections.abc import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from endless_idler.ui.assets import asset_path
from endless_idler.ui.battle import BattleScreenWidget
from endless_idler.ui.idle import IdleScreenWidget
from endless_idler.ui.party_builder import PartyBuilderWidget


class MainMenuWidget(QWidget):
    play_requested = Signal()
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
        root.addWidget(
            menu_panel, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
        )

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
        menu_layout.addWidget(self._make_button("Warp", self.warp_requested.emit))
        menu_layout.addWidget(
            self._make_button("Inventory", self.inventory_requested.emit)
        )
        menu_layout.addWidget(
            self._make_button("Guidebook", self.guidebook_requested.emit)
        )
        menu_layout.addWidget(
            self._make_button("Settings", self.settings_requested.emit)
        )
        menu_layout.addWidget(
            self._make_button("Feedback", self.feedback_requested.emit)
        )
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
        self._party_builder: PartyBuilderWidget | None = None
        self._battle_screen: BattleScreenWidget | None = None
        self._idle_screen: IdleScreenWidget | None = None
        self._menu_screen: QWidget | None = None

        self.setWindowTitle("Stained Glass Odyssey Idle")
        self.resize(1280, 820)

        menu = MainMenuWidget()
        menu.play_requested.connect(self._open_party_builder)
        menu.settings_requested.connect(self._stub_settings)
        menu.warp_requested.connect(self._stub_warp)
        menu.inventory_requested.connect(self._stub_inventory)
        menu.guidebook_requested.connect(self._stub_guidebook)
        menu.feedback_requested.connect(self._stub_feedback)

        background = MainMenuBackground()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        background.setLayout(layout)
        layout.addWidget(menu)

        self._stack = QStackedWidget()
        self._menu_screen = background
        self._stack.addWidget(self._menu_screen)
        self.setCentralWidget(self._stack)

    def _open_party_builder(self) -> None:
        if self._party_builder is None:
            self._party_builder = PartyBuilderWidget()
            self._party_builder.back_requested.connect(self._open_main_menu)
            self._party_builder.fight_requested.connect(self._open_battle_screen)
            self._party_builder.idle_requested.connect(self._open_idle_screen)
            self._stack.addWidget(self._party_builder)
        self._stack.setCurrentWidget(self._party_builder)

    def _open_main_menu(self) -> None:
        if self._menu_screen is not None:
            self._stack.setCurrentWidget(self._menu_screen)

    def _open_battle_screen(self, payload: object) -> None:
        if self._battle_screen is not None:
            try:
                self._battle_screen.deleteLater()
            except Exception:
                pass
            self._battle_screen = None

        battle = BattleScreenWidget(payload=payload)
        battle.finished.connect(self._close_battle_screen)
        self._battle_screen = battle
        self._stack.addWidget(battle)
        self._stack.setCurrentWidget(battle)

    def _close_battle_screen(self) -> None:
        if self._party_builder is not None:
            self._stack.setCurrentWidget(self._party_builder)
            self._party_builder.reload_save()
        if self._battle_screen is None:
            return
        self._cleanup_widget(self._battle_screen)
        self._battle_screen = None

    def _open_idle_screen(self, payload: object) -> None:
        if self._idle_screen is not None:
            try:
                self._idle_screen.deleteLater()
            except Exception:
                pass
            self._idle_screen = None

        idle = IdleScreenWidget(payload=payload)
        idle.finished.connect(self._close_idle_screen)
        self._idle_screen = idle
        self._stack.addWidget(idle)
        self._stack.setCurrentWidget(idle)

    def _close_idle_screen(self) -> None:
        if self._party_builder is not None:
            self._stack.setCurrentWidget(self._party_builder)
            self._party_builder.reload_save()
        if self._idle_screen is None:
            return
        self._cleanup_widget(self._idle_screen)
        self._idle_screen = None

    def _cleanup_widget(self, widget: QWidget) -> None:
        """Safely remove and delete a widget from the stack."""
        try:
            self._stack.removeWidget(widget)
        except Exception:
            pass
        try:
            widget.deleteLater()
        except Exception:
            pass

    def _stub_settings(self) -> None:
        """Placeholder for Settings feature."""
        pass

    def _stub_warp(self) -> None:
        """Placeholder for Warp feature."""
        pass

    def _stub_inventory(self) -> None:
        """Placeholder for Inventory feature."""
        pass

    def _stub_guidebook(self) -> None:
        """Placeholder for Guidebook feature."""
        pass

    def _stub_feedback(self) -> None:
        """Placeholder for Feedback feature."""
        pass
