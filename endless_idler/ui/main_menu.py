from collections.abc import Callable

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from endless_idler.settings import SettingsManager
from endless_idler.ui.assets import asset_path
from endless_idler.ui.battle import BattleScreenWidget
from endless_idler.ui.idle import IdleScreenWidget
from endless_idler.ui.party_builder import PartyBuilderWidget
from endless_idler.ui.skills_screen import SkillsScreenWidget
from endless_idler.ui.tutorial_content import MAIN_TUTORIAL_STEPS
from endless_idler.ui.tutorial_overlay import TutorialOverlay


class MainMenuWidget(QWidget):
    play_requested = Signal()
    settings_requested = Signal()
    warp_requested = Signal()
    inventory_requested = Signal()
    guidebook_requested = Signal()
    feedback_requested = Signal()
    skills_requested = Signal()

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
        menu_layout.addWidget(self._make_button("Warp", self.warp_requested.emit))
        menu_layout.addWidget(self._make_button("Skills", self.skills_requested.emit))
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
        self._party_builder: PartyBuilderWidget | None = None
        self._battle_screen: BattleScreenWidget | None = None
        self._idle_screen: IdleScreenWidget | None = None
        self._skills_screen: SkillsScreenWidget | None = None
        self._menu_screen: QWidget | None = None

        self.setWindowTitle("Stained Glass Odyssey Idle")
        self.resize(1280, 820)

        menu = MainMenuWidget()
        self._main_menu_widget = menu
        menu.play_requested.connect(self._open_party_builder)
        menu.settings_requested.connect(self._stub_settings)
        menu.warp_requested.connect(self._stub_warp)
        menu.skills_requested.connect(self._open_skills_screen)
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

        # Initialize settings manager
        self._settings_manager = SettingsManager()
        self._settings = self._settings_manager.load()

        # Initialize tutorial overlay
        self._tutorial_overlay = TutorialOverlay(self)
        self._tutorial_overlay.finished.connect(self._on_tutorial_finished)
        self._tutorial_overlay.hide()

        # Check if tutorial should run (delayed to allow UI to fully render)
        if self._settings_manager.should_show_tutorial(self._settings):
            QTimer.singleShot(500, self._start_tutorial)

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
            self._cleanup_widget(self._battle_screen)
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
            self._cleanup_widget(self._idle_screen)
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

    def _open_skills_screen(self) -> None:
        if self._skills_screen is None:
            self._skills_screen = SkillsScreenWidget()
            self._skills_screen.back_requested.connect(self._open_main_menu)
            self._stack.addWidget(self._skills_screen)
        self._stack.setCurrentWidget(self._skills_screen)

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

    def keyPressEvent(self, event: object) -> None:
        """Handle keyboard shortcuts."""
        if hasattr(event, "key"):
            key = event.key()
            # K key to open Skills screen
            if key == Qt.Key.Key_K:
                # Only open if on main menu screen
                if self._stack.currentWidget() == self._menu_screen:
                    self._open_skills_screen()
                    return
        try:
            super().keyPressEvent(event)  # type: ignore[misc]
        except Exception:
            pass

    def _start_tutorial(self) -> None:
        """Start the tutorial sequence."""
        self._tutorial_overlay.start_tutorial(MAIN_TUTORIAL_STEPS)

    def _on_tutorial_finished(self, completed: bool) -> None:
        """Handle tutorial completion or skip."""
        if completed:
            self._settings = self._settings_manager.mark_tutorial_completed(self._settings)
        else:
            self._settings = self._settings_manager.mark_tutorial_skipped(self._settings)
        self._settings_manager.save(self._settings)

    def resizeEvent(self, event: object) -> None:
        """Keep tutorial overlay sized to window."""
        super().resizeEvent(event)  # type: ignore[misc]
        if hasattr(self, "_tutorial_overlay"):
            self._tutorial_overlay.resize(self.size())

    def _stub_settings(self) -> None:
        # TODO: Implement settings screen
        # When implemented, add "Reset Tutorial" button that calls self._start_tutorial()
        self._show_not_implemented("Settings")

    def _stub_warp(self) -> None:
        self._show_not_implemented("Warp")

    def _stub_inventory(self) -> None:
        self._show_not_implemented("Inventory")

    def _stub_guidebook(self) -> None:
        self._show_not_implemented("Guidebook")

    def _stub_feedback(self) -> None:
        self._show_not_implemented("Feedback")

    def _show_not_implemented(self, feature: str) -> None:
        feature = str(feature).strip() or "Feature"
        QMessageBox.information(self, feature, f"{feature} is not implemented yet.")
