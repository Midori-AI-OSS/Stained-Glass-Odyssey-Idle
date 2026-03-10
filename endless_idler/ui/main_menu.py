from __future__ import annotations

import re

from collections.abc import Callable

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QToolButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.run_save_store import RunSaveStore
from endless_idler.settings import AppSettings
from endless_idler.settings import AppSettingsManager
from endless_idler.settings import clamp_volume
from endless_idler.settings import normalize_channel
from endless_idler.tick_runtime import SharedTickRuntime
from endless_idler.ui.home import HomePage
from endless_idler.ui.idle import IdleScreenWidget
from endless_idler.ui.idle.idle_state import IDLE_TICK_INTERVAL_SECONDS
from endless_idler.ui.layout import LayoutScreenWidget
from endless_idler.ui.lucide_icons import lucide_icon
from endless_idler.ui.radio import RadioController
from endless_idler.ui.radio_control import RadioControlWidget
from endless_idler.ui.settings import SettingsPage


class MainMenuWindow(QMainWindow):
    APP_TITLE = "Stained Glass Odyssey Idle"
    _PAGE_HOME = "home"
    _PAGE_IDLE = "idle"
    _PAGE_LAYOUT = "layout"
    _PAGE_SETTINGS = "settings"

    def __init__(self) -> None:
        super().__init__()
        self._settings_manager = AppSettingsManager()
        self._app_settings = self._settings_manager.load()
        self._radio_controller: RadioController | None = RadioController(self)
        self._radio_channel_options: list[str] = []
        self._plugins = discover_character_plugins()
        self._save_store = RunSaveStore(plugins=self._plugins)
        self._save_store.load_or_create()

        self._idle_screen: IdleScreenWidget | None = None
        self._tick_runtime = SharedTickRuntime(
            interval_seconds=IDLE_TICK_INTERVAL_SECONDS,
            parent=self,
        )
        self._nav_buttons: dict[str, QToolButton] = {}

        self.setWindowTitle(self.APP_TITLE)
        self.resize(1280, 820)

        shell = QWidget(self)
        shell.setObjectName("AppShellRoot")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(16, 16, 16, 16)
        shell_layout.setSpacing(12)
        self.setCentralWidget(shell)

        topbar = QFrame(shell)
        topbar.setObjectName("AppTopBar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(12, 10, 12, 10)
        topbar_layout.setSpacing(8)
        shell_layout.addWidget(topbar)

        topbar_layout.addWidget(
            self._make_nav_button(
                label="Home",
                icon_name="house",
                page_key=self._PAGE_HOME,
                on_click=self._show_home,
            )
        )
        topbar_layout.addWidget(
            self._make_nav_button(
                label="Idle",
                icon_name="group",
                page_key=self._PAGE_IDLE,
                on_click=self._show_idle,
            )
        )
        topbar_layout.addWidget(
            self._make_nav_button(
                label="Layout",
                icon_name="layout-list",
                page_key=self._PAGE_LAYOUT,
                on_click=self._show_layout,
            )
        )
        topbar_layout.addWidget(
            self._make_stub_button(
                label="Warp",
                icon_name="compass",
                on_click=self._stub_warp,
            )
        )
        topbar_layout.addWidget(
            self._make_stub_button(
                label="Inventory",
                icon_name="backpack",
                on_click=self._stub_inventory,
            )
        )
        topbar_layout.addWidget(
            self._make_stub_button(
                label="Guidebook",
                icon_name="book-open",
                on_click=self._stub_guidebook,
            )
        )
        topbar_layout.addWidget(
            self._make_nav_button(
                label="Settings",
                icon_name="settings",
                page_key=self._PAGE_SETTINGS,
                on_click=self._show_settings,
            )
        )
        topbar_layout.addWidget(
            self._make_stub_button(
                label="Feedback",
                icon_name="bug",
                on_click=self._stub_feedback,
            )
        )
        topbar_layout.addStretch(1)

        self._radio_control = RadioControlWidget(topbar)
        topbar_layout.addWidget(
            self._radio_control,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

        self._stack = QStackedWidget(shell)
        shell_layout.addWidget(self._stack, 1)

        self._home_screen = HomePage(save_store=self._save_store, parent=self)
        self._layout_screen = LayoutScreenWidget(
            save_store=self._save_store, parent=self
        )
        self._settings_screen = SettingsPage(self)
        self._settings_screen.settings_changed.connect(self._on_settings_changed)
        self._settings_screen.save_now_requested.connect(self._on_save_now_requested)
        self._settings_screen.save_backup_requested.connect(
            self._on_save_backup_requested
        )
        self._settings_screen.save_reset_requested.connect(
            self._on_save_reset_requested
        )
        self._idle_placeholder = self._build_idle_placeholder(self)

        self._stack.addWidget(self._home_screen)
        self._stack.addWidget(self._layout_screen)
        self._stack.addWidget(self._idle_placeholder)
        self._stack.addWidget(self._settings_screen)

        self._radio_control.play_requested.connect(
            self._on_radio_control_play_requested
        )
        self._radio_control.volume_changed.connect(
            self._on_radio_control_volume_changed
        )
        if self._radio_controller is not None:
            self._radio_controller.state_changed.connect(self._on_radio_state_changed)

        self._set_active_nav(self._PAGE_HOME)
        self._stack.setCurrentWidget(self._home_screen)
        self._sync_radio_controller_from_settings(user_initiated=False)
        self._on_radio_state_changed(self._radio_state_snapshot())
        self._settings_screen.set_save_path(str(self._save_store.path))

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._idle_screen is not None:
            self._idle_screen.shutdown()
        else:
            try:
                self._save_store.persist(force=True)
            except OSError:
                pass
        if self._radio_controller is not None:
            self._radio_controller.shutdown()
        super().closeEvent(event)

    def _make_nav_button(
        self,
        *,
        label: str,
        icon_name: str,
        page_key: str,
        on_click: Callable[[], None],
    ) -> QToolButton:
        button = QToolButton(self)
        button.setText(label)
        button.setIcon(lucide_icon(icon_name))
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.setProperty("appNav", True)
        button.clicked.connect(on_click)
        self._nav_buttons[page_key] = button
        return button

    def _make_stub_button(
        self,
        *,
        label: str,
        icon_name: str,
        on_click: Callable[[], None],
    ) -> QToolButton:
        button = QToolButton(self)
        button.setText(label)
        button.setIcon(lucide_icon(icon_name))
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        button.setProperty("appStub", True)
        button.clicked.connect(on_click)
        return button

    @staticmethod
    def _build_idle_placeholder(parent: QWidget | None = None) -> QWidget:
        holder = QWidget(parent)
        layout = QVBoxLayout(holder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch(1)
        label = QLabel("Preparing idle runtime...")
        label.setObjectName("AppIdleStartupLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        return holder

    def _set_active_nav(self, key: str) -> None:
        for page_key, button in self._nav_buttons.items():
            button.setChecked(page_key == key)

    def _show_home(self) -> None:
        self._stack.setCurrentWidget(self._home_screen)
        self._set_active_nav(self._PAGE_HOME)

    def _show_idle(self) -> None:
        self._layout_screen.persist_now()
        self._ensure_idle_runtime()
        if self._idle_screen is None:
            self._stack.setCurrentWidget(self._idle_placeholder)
        else:
            self._stack.setCurrentWidget(self._idle_screen)
        self._set_active_nav(self._PAGE_IDLE)

    def _show_layout(self) -> None:
        self._stack.setCurrentWidget(self._layout_screen)
        self._set_active_nav(self._PAGE_LAYOUT)

    def _show_settings(self) -> None:
        _ = self._ensure_radio_controller()
        self._sync_radio_controller_from_settings(user_initiated=False)
        self._refresh_radio_channel_options(disable_on_failure=True)
        self._settings_screen.set_settings(self._app_settings)
        self._settings_screen.apply_radio_state(self._radio_state_snapshot())
        self._settings_screen.set_save_path(str(self._save_store.path))
        self._stack.setCurrentWidget(self._settings_screen)
        self._set_active_nav(self._PAGE_SETTINGS)

    def _idle_lineup_signature(
        self,
    ) -> tuple[tuple[str, ...], tuple[str, ...], tuple[tuple[str, int], ...], int]:
        return IdleScreenWidget.build_lineup_signature(self._save_store.current)

    def _dispose_idle_runtime(self, *, persist: bool) -> None:
        if self._idle_screen is None:
            return
        idle = self._idle_screen
        self._idle_screen = None
        idle.shutdown(persist=persist)
        self._stack.removeWidget(idle)
        idle.deleteLater()

    def _ensure_idle_runtime(self) -> None:
        current_signature = self._idle_lineup_signature()
        if (
            self._idle_screen is not None
            and self._idle_screen.lineup_signature == current_signature
        ):
            return
        if self._idle_screen is not None:
            self._dispose_idle_runtime(persist=True)

        idle = IdleScreenWidget(
            save_store=self._save_store,
            tick_runtime=self._tick_runtime,
            plugins=self._plugins,
            parent=self,
        )
        idle.finished.connect(self._show_home)
        self._idle_screen = idle
        self._stack.addWidget(idle)

        if self._stack.currentWidget() is self._idle_placeholder:
            self._stack.setCurrentWidget(idle)

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
        controller = self._ensure_radio_controller()
        if controller is None:
            return

        if not controller.qt_available:
            self._on_radio_state_changed(self._radio_state_snapshot())
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
        self._on_radio_state_changed(self._radio_state_snapshot())

    def _on_save_now_requested(self) -> None:
        self._persist_shared_save()

    def _on_save_backup_requested(self) -> None:
        try:
            _ = self._save_store.backup_current()
        except OSError as exc:
            self._show_save_action_error("Backup failed", exc)
            return

    def _on_save_reset_requested(self) -> None:
        result = QMessageBox.question(
            self,
            "Reset Save",
            (
                "Create a backup of the current save, remove the active save, and close the game?\n\n"
                "Next launch will start a fresh run."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return

        self._layout_screen.cancel_pending_persist()
        if self._idle_screen is not None:
            self._idle_screen.shutdown(persist=False)
        try:
            self._save_store.backup_current()
            self._save_store.delete_active_save()
        except OSError as exc:
            self._show_save_action_error("Reset failed", exc)
            return
        QCoreApplication.quit()

    def _persist_shared_save(self) -> None:
        try:
            self._layout_screen.cancel_pending_persist()
            if self._idle_screen is not None:
                self._idle_screen.force_persist()
            else:
                self._save_store.persist(force=True)
        except OSError as exc:
            self._show_save_action_error("Save failed", exc)
            return

    def _show_save_action_error(self, title: str, exc: OSError) -> None:
        QMessageBox.warning(
            self,
            title,
            str(exc),
        )

    def _on_radio_control_play_requested(self) -> None:
        controller = self._ensure_radio_controller()
        if controller is None or not controller.qt_available:
            return

        snapshot = controller.state_snapshot()
        connection_state = str(snapshot.get("connection_state") or "").strip().lower()
        is_active = bool(snapshot.get("is_playing")) or bool(
            snapshot.get("desired_playing")
        )
        if connection_state == "reconnecting":
            is_active = True

        if is_active:
            self._app_settings.radio_enabled = False
            controller.set_enabled(False, start_when_enabled=False)
            self._settings_manager.save(self._app_settings)
            self._settings_screen.set_settings(self._app_settings)
            return

        if not self._app_settings.radio_enabled:
            self._app_settings.radio_enabled = True
            controller.set_enabled(True, start_when_enabled=False)
            self._settings_manager.save(self._app_settings)
            self._settings_screen.set_settings(self._app_settings)

        controller.start_playback()

    def _on_radio_control_volume_changed(self, value: int) -> None:
        clamped = clamp_volume(value)
        self._app_settings.radio_volume = clamped
        self._settings_manager.save(self._app_settings)

        controller = self._ensure_radio_controller()
        if controller is not None and controller.qt_available:
            controller.set_volume(clamped)
        self._settings_screen.set_settings(self._app_settings)
        self._on_radio_state_changed(self._radio_state_snapshot())

    def _on_radio_state_changed(self, state: object) -> None:
        if isinstance(state, dict):
            snapshot = state
        else:
            snapshot = self._radio_state_snapshot()

        self._settings_screen.apply_radio_state(snapshot)

        qt_available = bool(snapshot.get("qt_available") or False)
        service_available = bool(snapshot.get("service_available") or False)
        self._radio_control.setVisible(qt_available)
        self._radio_control.set_service_available(service_available)
        self._radio_control.set_playing(bool(snapshot.get("is_playing") or False))
        self._radio_control.set_radio_enabled(bool(snapshot.get("enabled") or False))
        self._radio_control.set_connection_state(
            str(snapshot.get("connection_state") or "idle")
        )
        self._radio_control.set_volume(clamp_volume(snapshot.get("volume")))
        self._radio_control.set_status_tooltip(str(snapshot.get("status_text") or ""))
        self._update_window_title_from_radio_state(snapshot)

    def _update_window_title_from_radio_state(self, state: dict[str, object]) -> None:
        if not bool(state.get("qt_available")):
            self.setWindowTitle(self.APP_TITLE)
            return

        if (not bool(state.get("enabled"))) and (not bool(state.get("is_playing"))):
            self.setWindowTitle(self.APP_TITLE)
            return

        channel_label = str(state.get("channel_label") or "all").strip() or "all"
        current_track = self._normalize_radio_window_track_title(
            state.get("current_track")
        )
        last_track = self._normalize_radio_window_track_title(state.get("last_track"))
        service_available = bool(state.get("service_available"))
        degraded_from_playback = bool(state.get("degraded_from_playback"))

        if degraded_from_playback and (not service_available) and last_track:
            self.setWindowTitle(f"{last_track} [{channel_label}] [Radio unavailable]")
            return

        if current_track:
            self.setWindowTitle(f"{current_track} [{channel_label}]")
            return

        self.setWindowTitle(f"{self.APP_TITLE} [{channel_label}]")

    @classmethod
    def _normalize_radio_window_track_title(cls, value: object) -> str:
        track = " ".join(str(value or "").split())
        if not track:
            return ""

        parts = [
            part.strip() for part in re.split(r"\s+[—–-]\s+", track) if part.strip()
        ]
        if not parts:
            return ""

        app_title = cls.APP_TITLE.casefold()
        while parts and parts[0].casefold() == app_title:
            parts.pop(0)
        while len(parts) >= 2 and parts[-1].casefold() == parts[-2].casefold():
            parts.pop()
        while len(parts) >= 2 and parts[0].casefold() == parts[-1].casefold():
            parts.pop()
        while parts and parts[-1].casefold() == app_title:
            parts.pop()

        if not parts:
            return ""
        return " - ".join(parts)

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
                if disable_on_failure:
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
