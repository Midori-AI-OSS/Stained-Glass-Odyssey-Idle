from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtGui import QCloseEvent
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.settings import AppSettings
from endless_idler.settings import AppSettingsManager
from endless_idler.settings import normalize_channel
from endless_idler.ui.assets import asset_path
from endless_idler.ui.idle import IdleHubWidget
from endless_idler.ui.idle import IdleScreenWidget
from endless_idler.ui.radio import RadioController
from endless_idler.ui.settings import SettingsPage


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
        menu_layout.addWidget(self._make_button("Inventory", self.inventory_requested.emit))
        menu_layout.addWidget(self._make_button("Guidebook", self.guidebook_requested.emit))
        menu_layout.addWidget(self._make_button("Settings", self.settings_requested.emit))
        menu_layout.addWidget(self._make_button("Feedback", self.feedback_requested.emit))
        menu_layout.addStretch(1)

    def _make_button(self, label: str, on_click: Callable[[], None]) -> QPushButton:
        button = QPushButton(label)
        button.setObjectName(f"mainMenuButton_{label.lower().replace(' ', '_')}")
        button.setProperty("stainedMenu", True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(52)
        button.clicked.connect(on_click)
        return button


class MainMenuBackground(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._background = QPixmap(asset_path("backgrounds", "main_menu_cityscape.png"))

    def paintEvent(self, event: object) -> None:
        _ = event
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
        self._idle_hub: IdleHubWidget | None = None
        self._idle_screen: IdleScreenWidget | None = None
        self._menu_screen: QWidget | None = None
        self._settings_screen: SettingsPage | None = None

        self._settings_manager = AppSettingsManager()
        self._app_settings = self._settings_manager.load()
        self._radio_controller: RadioController | None = None
        self._radio_channel_options: list[str] = []

        self.setWindowTitle("Stained Glass Odyssey Idle")
        self.resize(1280, 820)

        menu = MainMenuWidget()
        menu.play_requested.connect(self._open_idle_hub)
        menu.settings_requested.connect(self._open_settings)
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

        if self._app_settings.radio_enabled and self._app_settings.radio_autostart:
            _ = self._ensure_radio_controller()
            self._sync_radio_controller_from_settings(user_initiated=False)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._radio_controller is not None:
            self._radio_controller.shutdown()
        super().closeEvent(event)

    def _open_idle_hub(self) -> None:
        if self._idle_hub is None:
            self._idle_hub = IdleHubWidget()
            self._idle_hub.back_requested.connect(self._open_main_menu)
            self._idle_hub.start_requested.connect(self._open_idle_screen)
            self._stack.addWidget(self._idle_hub)
        self._idle_hub.reload_save()
        self._stack.setCurrentWidget(self._idle_hub)

    def _open_settings(self) -> None:
        if self._settings_screen is None:
            self._settings_screen = SettingsPage()
            self._settings_screen.back_requested.connect(self._open_main_menu)
            self._settings_screen.settings_changed.connect(self._on_settings_changed)
            self._settings_screen.play_toggle_requested.connect(
                self._on_radio_control_play_requested
            )
            self._stack.addWidget(self._settings_screen)

        _ = self._ensure_radio_controller()
        self._sync_radio_controller_from_settings(user_initiated=False)
        self._refresh_radio_channel_options(disable_on_failure=True)
        self._settings_screen.set_settings(self._app_settings)
        self._settings_screen.apply_radio_state(self._radio_state_snapshot())
        self._stack.setCurrentWidget(self._settings_screen)

    def _open_main_menu(self) -> None:
        if self._menu_screen is not None:
            self._stack.setCurrentWidget(self._menu_screen)

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
        if self._idle_hub is not None:
            self._idle_hub.reload_save()
            self._stack.setCurrentWidget(self._idle_hub)
        if self._idle_screen is None:
            return
        self._cleanup_widget(self._idle_screen)
        self._idle_screen = None

    def _cleanup_widget(self, widget: QWidget) -> None:
        try:
            self._stack.removeWidget(widget)
        except Exception:
            pass
        try:
            widget.deleteLater()
        except Exception:
            pass

    def _ensure_radio_controller(self) -> RadioController | None:
        if self._radio_controller is not None:
            return self._radio_controller
        controller = RadioController(self)
        controller.state_changed.connect(self._on_radio_state_changed)
        self._radio_controller = controller
        return controller

    def _sync_radio_controller_from_settings(
        self,
        *,
        user_initiated: bool,
        previous_enabled: bool | None = None,
    ) -> None:
        controller = self._radio_controller
        if controller is None:
            if not self._app_settings.radio_enabled and self._settings_screen is None:
                return
            controller = self._ensure_radio_controller()
        if controller is None:
            return

        controller.set_channel(self._app_settings.radio_channel)
        controller.set_quality(self._app_settings.radio_quality)
        controller.set_loudness_boost(
            self._app_settings.radio_loudness_boost_enabled,
            self._app_settings.radio_loudness_boost_factor,
        )
        controller.set_volume(self._app_settings.radio_volume)

        start_when_enabled = bool(
            user_initiated
            and self._app_settings.radio_enabled
            and previous_enabled is False
        )
        controller.set_enabled(
            self._app_settings.radio_enabled,
            start_when_enabled=start_when_enabled,
        )

        if user_initiated:
            controller.cancel_start_when_service_ready()
        elif self._app_settings.radio_enabled and self._app_settings.radio_autostart:
            controller.request_start_when_service_ready()
        else:
            controller.cancel_start_when_service_ready()

    def _on_settings_changed(self, payload: dict[str, object]) -> None:
        previous_enabled = self._app_settings.radio_enabled
        self._app_settings = AppSettings.from_mapping(payload)
        self._settings_manager.save(self._app_settings)
        self._sync_radio_controller_from_settings(
            user_initiated=True,
            previous_enabled=previous_enabled,
        )

    def _on_radio_control_play_requested(self) -> None:
        controller = self._ensure_radio_controller()
        if controller is None:
            return

        if not self._app_settings.radio_enabled:
            self._app_settings = AppSettings.from_mapping(
                {
                    **self._app_settings.as_dict(),
                    "radio_enabled": True,
                }
            )
            self._settings_manager.save(self._app_settings)
            controller.set_enabled(True, start_when_enabled=False)
            if self._settings_screen is not None:
                self._settings_screen.set_settings(self._app_settings)

        controller.toggle_playback()

    def _on_radio_state_changed(self, state: object) -> None:
        if self._settings_screen is None:
            return
        if isinstance(state, dict):
            snapshot = state
        else:
            snapshot = self._radio_state_snapshot()
        self._settings_screen.apply_radio_state(snapshot)

    def _radio_state_snapshot(self) -> dict[str, object]:
        if self._radio_controller is None:
            return {
                "qt_available": False,
                "service_available": False,
                "service_known": False,
                "enabled": self._app_settings.radio_enabled,
                "quality": self._app_settings.radio_quality,
                "active_quality": self._app_settings.radio_quality,
                "pending_quality": None,
                "channel": self._app_settings.radio_channel,
                "active_channel": self._app_settings.radio_channel,
                "pending_channel": None,
                "resolved_channel": self._app_settings.radio_channel,
                "channel_label": self._app_settings.radio_channel or "all",
                "volume": self._app_settings.radio_volume,
                "loudness_boost_enabled": self._app_settings.radio_loudness_boost_enabled,
                "loudness_boost_factor": self._app_settings.radio_loudness_boost_factor,
                "effective_volume_percent": self._app_settings.radio_volume,
                "is_playing": False,
                "status_text": "Radio unavailable.",
                "current_track": "",
                "last_track": "",
                "degraded_from_playback": False,
                "desired_playing": False,
                "reconnect_attempts": 0,
                "last_reconnect_reason": "",
                "connection_state": "unavailable",
            }
        return self._radio_controller.state_snapshot()

    def _refresh_radio_channel_options(self, *, disable_on_failure: bool) -> None:
        if self._settings_screen is None:
            return

        selected_channel = normalize_channel(self._app_settings.radio_channel)
        controller = self._radio_controller
        if controller is None or not controller.qt_available:
            self._settings_screen.set_radio_channel_options(
                self._radio_channel_options,
                selected=selected_channel,
                enabled=False,
            )
            return

        def _handle_channels(channels: object, error_text: str) -> None:
            current_selected = normalize_channel(self._app_settings.radio_channel)
            if error_text or not isinstance(channels, list):
                if disable_on_failure and self._settings_screen is not None:
                    self._settings_screen.set_radio_channel_options(
                        self._radio_channel_options,
                        selected=current_selected,
                        enabled=False,
                    )
                return

            normalized: list[str] = []
            for raw in channels:
                channel = normalize_channel(raw)
                if not channel or channel in normalized:
                    continue
                normalized.append(channel)
            normalized.sort()
            self._radio_channel_options = normalized
            if self._settings_screen is not None:
                self._settings_screen.set_radio_channel_options(
                    normalized,
                    selected=current_selected,
                    enabled=True,
                )

        controller.fetch_channels(_handle_channels)

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
