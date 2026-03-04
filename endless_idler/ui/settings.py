from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from PySide6.QtCore import QEasingCurve
from PySide6.QtCore import QParallelAnimationGroup
from PySide6.QtCore import QPoint
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtCore import QSignalBlocker
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QToolButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.settings import AppSettings
from endless_idler.settings import LOUDNESS_BOOST_DEFAULT
from endless_idler.settings import LOUDNESS_BOOST_MAX
from endless_idler.settings import LOUDNESS_BOOST_MIN
from endless_idler.settings import LOUDNESS_BOOST_STEP
from endless_idler.settings import clamp_volume
from endless_idler.settings import normalize_channel
from endless_idler.settings import normalize_loudness_boost_factor
from endless_idler.settings import normalize_quality
from endless_idler.ui.radio_control import RadioControlWidget


MAIN_LAYOUT_MARGINS = (20, 20, 20, 20)
MAIN_LAYOUT_SPACING = 14
HEADER_MARGINS = (12, 10, 12, 10)
HEADER_SPACING = 10
CARD_MARGINS = (14, 14, 14, 14)
CARD_SPACING = 12
GRID_HORIZONTAL_SPACING = 12
GRID_VERTICAL_SPACING = 10


@dataclass(frozen=True)
class _SettingsPaneSpec:
    key: str
    title: str
    subtitle: str
    section: str


class SettingsPage(QWidget):
    back_requested = Signal()
    settings_changed = Signal(dict)
    play_toggle_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SettingsPageRoot")

        self._suppress_autosave = False
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.setInterval(450)
        self._autosave_timer.timeout.connect(self._emit_saved)

        self._pane_animation: QParallelAnimationGroup | None = None
        self._pane_rest_pos: QPoint | None = None
        self._compact_mode = False
        self._active_pane_key = ""

        self._pane_specs = self._default_pane_specs()
        self._pane_index_by_key: dict[str, int] = {}
        self._nav_buttons: dict[str, QToolButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(*MAIN_LAYOUT_MARGINS)
        layout.setSpacing(MAIN_LAYOUT_SPACING)

        header = QWidget(self)
        header.setObjectName("SettingsHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(*HEADER_MARGINS)
        header_layout.setSpacing(HEADER_SPACING)

        title = QLabel("Settings")
        title.setObjectName("SettingsHeaderTitle")

        back = QToolButton()
        back.setObjectName("SettingsBackButton")
        back.setText("Back")
        back.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        back.clicked.connect(self._on_back)

        header_layout.addWidget(title)
        header_layout.addStretch(1)
        header_layout.addWidget(back, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(header)

        card = QWidget(self)
        card.setObjectName("SettingsCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(*CARD_MARGINS)
        card_layout.setSpacing(CARD_SPACING)

        self._compact_nav = QComboBox()
        self._compact_nav.setObjectName("SettingsCompactNav")
        self._compact_nav.setVisible(False)
        self._compact_nav.currentIndexChanged.connect(self._on_compact_nav_changed)
        card_layout.addWidget(self._compact_nav)

        panes_layout = QHBoxLayout()
        panes_layout.setContentsMargins(0, 0, 0, 0)
        panes_layout.setSpacing(14)

        self._nav_panel = QWidget()
        self._nav_panel.setObjectName("SettingsNavPanel")
        self._nav_panel.setMinimumWidth(250)
        self._nav_panel.setMaximumWidth(320)
        nav_layout = QVBoxLayout(self._nav_panel)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(6)

        self._right_panel = QWidget()
        self._right_panel.setObjectName("SettingsPaneHost")
        right_layout = QVBoxLayout(self._right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._page_stack = QStackedWidget()
        self._page_stack.setObjectName("SettingsPageStack")
        right_layout.addWidget(self._page_stack, 1)

        panes_layout.addWidget(self._nav_panel)
        panes_layout.addWidget(self._right_panel, 1)

        card_layout.addLayout(panes_layout, 1)
        layout.addWidget(card, 1)

        self._build_controls()
        self._build_pages()
        self._build_navigation(nav_layout)
        self._sync_nav_button_sizes()
        self._connect_autosave_signals()

        if self._pane_specs:
            first_key = self._pane_specs[0].key
            self._set_active_navigation(first_key)
            self._set_current_pane(first_key, animate=False)

        self._update_navigation_mode()
        QTimer.singleShot(0, self._sync_nav_button_sizes)

    def _default_pane_specs(self) -> list[_SettingsPaneSpec]:
        return [
            _SettingsPaneSpec(
                key="radio",
                title="Radio",
                subtitle="Midori AI Radio playback controls and defaults.",
                section="Runtime",
            )
        ]

    def _build_controls(self) -> None:
        self._radio_enabled = QCheckBox("Enable Midori AI Radio")
        self._radio_enabled.setToolTip(
            "Allows starting radio playback from the player controls."
        )

        self._radio_autostart = QCheckBox("Auto-start radio on app launch")
        self._radio_autostart.setToolTip(
            "Starts playback automatically at launch when radio is enabled."
        )
        self._radio_autostart.setEnabled(False)

        self._radio_channel_values: list[str] = []
        self._radio_channel_enabled = False
        self._radio_channel = QComboBox()
        self._radio_channel.setObjectName("SettingsRadioChannel")
        self._radio_channel.setToolTip(
            "Select a radio channel. All channels uses the server default behavior."
        )
        self._radio_channel.setEnabled(False)
        self.set_radio_channel_options([], selected="", enabled=False)

        self._radio_quality = QComboBox()
        self._radio_quality.setObjectName("SettingsRadioQuality")
        self._radio_quality.addItem("Low (96 kbps)", "low")
        self._radio_quality.addItem("Medium (160 kbps)", "medium")
        self._radio_quality.addItem("High (320 kbps)", "high")

        self._radio_volume = QSlider(Qt.Orientation.Horizontal)
        self._radio_volume.setObjectName("SettingsVolumeSlider")
        self._radio_volume.setRange(0, 100)
        self._radio_volume.setValue(70)
        self._radio_volume_value = QLabel("70%")
        self._radio_volume_value.setObjectName("SettingsPaneSubtitle")
        self._radio_volume.valueChanged.connect(self._on_radio_volume_value_changed)

        self._radio_loudness_boost_enabled = QCheckBox("Loudness Boost")
        self._radio_loudness_boost_enabled.setToolTip(
            "Applies a gain multiplier to radio volume mapping."
        )
        self._radio_loudness_boost_enabled.toggled.connect(
            self._on_radio_loudness_boost_toggled
        )

        self._radio_loudness_boost_factor = QDoubleSpinBox()
        self._radio_loudness_boost_factor.setObjectName("SettingsBoostSpinBox")
        self._radio_loudness_boost_factor.setRange(
            LOUDNESS_BOOST_MIN,
            LOUDNESS_BOOST_MAX,
        )
        self._radio_loudness_boost_factor.setSingleStep(LOUDNESS_BOOST_STEP)
        self._radio_loudness_boost_factor.setDecimals(2)
        self._radio_loudness_boost_factor.setValue(LOUDNESS_BOOST_DEFAULT)
        self._radio_loudness_boost_factor.setSuffix("x")
        self._radio_loudness_boost_factor.setEnabled(False)
        self._radio_loudness_boost_factor.setToolTip(
            "Boost multiplier for radio loudness. Effective output is capped by Qt "
            "audio output at 100%."
        )
        self._radio_loudness_boost_factor.valueChanged.connect(
            self._on_radio_loudness_boost_factor_changed
        )

        self._radio_control = RadioControlWidget()
        self._radio_control.setObjectName("SettingsRadioControl")
        self._radio_control.play_requested.connect(self.play_toggle_requested.emit)
        self._radio_control.volume_changed.connect(self._on_player_volume_changed)

        self._radio_play_button = QPushButton("Play / Stop Now")
        self._radio_play_button.setObjectName("SettingsRadioPlayButton")
        self._radio_play_button.clicked.connect(self.play_toggle_requested.emit)

        self._radio_status_value = QLabel("Radio unavailable.")
        self._radio_status_value.setObjectName("SettingsPaneSubtitle")
        self._radio_status_value.setWordWrap(True)

        self._radio_track_value = QLabel("No track")
        self._radio_track_value.setObjectName("SettingsPaneSubtitle")
        self._radio_track_value.setWordWrap(True)

        self._radio_enabled.toggled.connect(self._radio_autostart.setEnabled)

    def _build_pages(self) -> None:
        specs_by_key = {spec.key: spec for spec in self._pane_specs}
        radio_spec = specs_by_key["radio"]
        radio_page, radio_body = self._create_page(radio_spec)

        player_title = QLabel("Player")
        player_title.setObjectName("SettingsPaneLabel")
        radio_body.addWidget(player_title)

        player_row = QHBoxLayout()
        player_row.setSpacing(8)
        player_row.addWidget(self._radio_control)
        player_row.addWidget(self._radio_play_button)
        player_row.addStretch(1)
        radio_body.addLayout(player_row)

        status_title = QLabel("Status")
        status_title.setObjectName("SettingsPaneLabel")
        radio_body.addWidget(status_title)
        radio_body.addWidget(self._radio_status_value)

        track_title = QLabel("Current Track")
        track_title.setObjectName("SettingsPaneLabel")
        radio_body.addWidget(track_title)
        radio_body.addWidget(self._radio_track_value)

        radio_body.addWidget(self._radio_enabled)
        radio_body.addWidget(self._radio_autostart)

        radio_grid = QGridLayout()
        radio_grid.setHorizontalSpacing(GRID_HORIZONTAL_SPACING)
        radio_grid.setVerticalSpacing(GRID_VERTICAL_SPACING)
        radio_grid.setColumnStretch(1, 1)
        radio_grid.addWidget(QLabel("Channel"), 0, 0)
        radio_grid.addWidget(self._radio_channel, 0, 1)
        radio_grid.addWidget(QLabel("Stream quality"), 1, 0)
        radio_grid.addWidget(self._radio_quality, 1, 1)
        radio_grid.addWidget(QLabel("Volume"), 2, 0)
        volume_row = QHBoxLayout()
        volume_row.setSpacing(8)
        volume_row.addWidget(self._radio_volume, 1)
        volume_row.addWidget(self._radio_volume_value, 0, Qt.AlignmentFlag.AlignRight)
        radio_grid.addLayout(volume_row, 2, 1)
        radio_grid.addWidget(QLabel("Loudness"), 3, 0)

        boost_row = QHBoxLayout()
        boost_row.setSpacing(8)
        boost_row.addWidget(self._radio_loudness_boost_enabled)
        boost_row.addWidget(self._radio_loudness_boost_factor)
        boost_row.addStretch(1)
        radio_grid.addLayout(boost_row, 3, 1)

        radio_body.addLayout(radio_grid)
        radio_body.addStretch(1)
        self._register_page("radio", radio_page)

    def _build_navigation(self, nav_layout: QVBoxLayout) -> None:
        sections: dict[str, list[_SettingsPaneSpec]] = {}
        for spec in self._pane_specs:
            sections.setdefault(spec.section, []).append(spec)

        for section_title, specs in sections.items():
            section_label = QLabel(section_title)
            section_label.setObjectName("SettingsNavSection")
            nav_layout.addWidget(section_label)

            for spec in specs:
                button = QToolButton()
                button.setObjectName("SettingsNavButton")
                button.setText(spec.title)
                button.setToolTip(spec.subtitle)
                button.setCheckable(True)
                button.setAutoExclusive(True)
                button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
                button.setFixedHeight(40)
                button.setSizePolicy(
                    QSizePolicy.Policy.Fixed,
                    QSizePolicy.Policy.Fixed,
                )
                button.clicked.connect(
                    lambda checked=False, key=spec.key: self._on_nav_button_clicked(key)
                )
                nav_layout.addWidget(button)
                self._nav_buttons[spec.key] = button
                self._compact_nav.addItem(spec.title, spec.key)

        nav_layout.addStretch(1)

    def _create_page(self, spec: _SettingsPaneSpec) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(10)

        title = QLabel(spec.title)
        title.setObjectName("SettingsPaneTitle")

        subtitle = QLabel(spec.subtitle)
        subtitle.setObjectName("SettingsPaneSubtitle")
        subtitle.setWordWrap(True)

        body = QWidget(page)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(GRID_VERTICAL_SPACING)

        page_layout.addWidget(title)
        page_layout.addWidget(subtitle)
        page_layout.addWidget(body, 1)
        return page, body_layout

    def _register_page(self, key: str, widget: QWidget) -> None:
        index = self._page_stack.addWidget(widget)
        self._pane_index_by_key[key] = index

    def _connect_autosave_signals(self) -> None:
        self._radio_channel.currentIndexChanged.connect(self._trigger_immediate_autosave)
        self._radio_quality.currentIndexChanged.connect(self._trigger_immediate_autosave)

        self._radio_enabled.toggled.connect(self._trigger_immediate_autosave)
        self._radio_autostart.toggled.connect(self._trigger_immediate_autosave)
        self._radio_loudness_boost_enabled.toggled.connect(
            self._trigger_immediate_autosave
        )

        self._radio_volume.valueChanged.connect(self._queue_debounced_autosave)
        self._radio_loudness_boost_factor.valueChanged.connect(
            self._queue_debounced_autosave
        )

    def _on_back(self) -> None:
        self.try_autosave()
        self.back_requested.emit()

    def _on_nav_button_clicked(self, key: str) -> None:
        self._navigate_to_pane(key, user_initiated=True)

    def _on_compact_nav_changed(self, _index: int) -> None:
        key = str(self._compact_nav.currentData() or "").strip()
        if not key:
            return
        self._navigate_to_pane(key, user_initiated=True)

    def _navigate_to_pane(self, key: str, *, user_initiated: bool) -> None:
        key = str(key or "").strip()
        if not key or key not in self._pane_index_by_key:
            return
        if key == self._active_pane_key:
            self._set_active_navigation(key)
            return

        if user_initiated:
            self.try_autosave()

        self._set_current_pane(key, animate=True)
        self._set_active_navigation(key)

    def _set_active_navigation(self, key: str) -> None:
        self._active_pane_key = key
        for pane_key, button in self._nav_buttons.items():
            button.setChecked(pane_key == key)

        idx = self._compact_nav.findData(key)
        if idx >= 0:
            with QSignalBlocker(self._compact_nav):
                self._compact_nav.setCurrentIndex(idx)

    def _set_current_pane(self, key: str, *, animate: bool) -> None:
        target_index = self._pane_index_by_key.get(key)
        if target_index is None:
            return

        current_index = self._page_stack.currentIndex()
        if current_index == target_index:
            self._active_pane_key = key
            return

        if current_index < 0 or not animate:
            self._page_stack.setCurrentIndex(target_index)
            self._active_pane_key = key
            return

        forward = target_index > current_index
        self._page_stack.setCurrentIndex(target_index)
        self._animate_stack(forward=forward)
        self._active_pane_key = key

    def _animate_stack(self, *, forward: bool) -> None:
        if self._pane_animation is not None:
            self._pane_animation.stop()
            self._pane_animation = None

        if self._pane_rest_pos is not None:
            self._page_stack.move(self._pane_rest_pos)
        self._page_stack.setGraphicsEffect(None)  # pyright: ignore[reportArgumentType]

        base_pos = self._page_stack.pos()
        self._pane_rest_pos = QPoint(base_pos)

        offset = 16 if forward else -16
        start_pos = QPoint(base_pos.x() + offset, base_pos.y())

        effect = QGraphicsOpacityEffect(self._page_stack)
        effect.setOpacity(0.0)
        self._page_stack.setGraphicsEffect(effect)
        self._page_stack.move(start_pos)

        pos_anim = QPropertyAnimation(self._page_stack, b"pos", self)
        pos_anim.setDuration(210)
        pos_anim.setStartValue(start_pos)
        pos_anim.setEndValue(base_pos)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        opacity_anim = QPropertyAnimation(effect, b"opacity", self)
        opacity_anim.setDuration(210)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(pos_anim)
        group.addAnimation(opacity_anim)

        def _cleanup() -> None:
            if self._pane_rest_pos is not None:
                self._page_stack.move(self._pane_rest_pos)
            self._page_stack.setGraphicsEffect(None)  # pyright: ignore[reportArgumentType]
            self._pane_animation = None

        group.finished.connect(_cleanup)
        group.start()
        self._pane_animation = group

    def _queue_debounced_autosave(self, *_args: object) -> None:
        if self._suppress_autosave:
            return
        self._autosave_timer.start()

    def _trigger_immediate_autosave(self, *_args: object) -> None:
        if self._suppress_autosave:
            return
        if self._autosave_timer.isActive():
            self._autosave_timer.stop()
        self._emit_saved()

    def _emit_saved(self) -> None:
        if self._suppress_autosave:
            return
        self.settings_changed.emit(self.get_settings())

    def try_autosave(self) -> bool:
        if self._autosave_timer.isActive():
            self._autosave_timer.stop()
        self._emit_saved()
        return True

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_navigation_mode()
        self._sync_nav_button_sizes()

    def _update_navigation_mode(self) -> None:
        compact = self.width() < 1080
        if compact == self._compact_mode:
            return
        self._compact_mode = compact
        self._compact_nav.setVisible(compact)
        self._nav_panel.setVisible(not compact)
        if not compact:
            QTimer.singleShot(0, self._sync_nav_button_sizes)

    def _sync_nav_button_sizes(self) -> None:
        if self._compact_mode or not self._nav_buttons:
            return

        panel_width = self._nav_panel.width()
        if panel_width <= 0:
            return

        inner_width = panel_width
        nav_layout = self._nav_panel.layout()
        if nav_layout is not None:
            margins = nav_layout.contentsMargins()
            inner_width -= margins.left() + margins.right()

        target_width = max(1, inner_width - 2)
        for button in self._nav_buttons.values():
            button.setFixedWidth(target_width)

    def set_radio_channel_options(
        self,
        channels: list[str],
        *,
        selected: object,
        enabled: bool,
    ) -> None:
        normalized_selected = normalize_channel(selected)
        normalized_channels: list[str] = []
        for raw in channels:
            channel = normalize_channel(raw)
            if not channel or channel in normalized_channels:
                continue
            normalized_channels.append(channel)
        normalized_channels.sort()

        self._radio_channel_values = normalized_channels
        self._radio_channel_enabled = bool(enabled)

        with QSignalBlocker(self._radio_channel):
            self._radio_channel.clear()
            self._radio_channel.addItem("All channels", "")
            for channel in normalized_channels:
                self._radio_channel.addItem(channel, channel)
            if normalized_selected and normalized_selected not in normalized_channels:
                self._radio_channel.addItem(
                    f"Custom: {normalized_selected}",
                    normalized_selected,
                )
            self._set_combo_value(self._radio_channel, normalized_selected, fallback="")
        self._radio_channel.setEnabled(self._radio_channel_enabled)

    def set_settings(self, settings: Mapping[str, object] | AppSettings) -> None:
        if isinstance(settings, AppSettings):
            payload = settings.as_dict()
        else:
            payload = dict(settings)

        self._suppress_autosave = True
        try:
            radio_enabled = bool(payload.get("radio_enabled") or False)
            self._radio_enabled.setChecked(radio_enabled)
            self._radio_autostart.setChecked(bool(payload.get("radio_autostart") or False))
            self._radio_autostart.setEnabled(radio_enabled)

            radio_channel = normalize_channel(payload.get("radio_channel"))
            self.set_radio_channel_options(
                self._radio_channel_values,
                selected=radio_channel,
                enabled=self._radio_channel_enabled,
            )

            radio_quality = normalize_quality(payload.get("radio_quality"))
            self._set_combo_value(self._radio_quality, radio_quality, fallback="medium")

            radio_volume = clamp_volume(payload.get("radio_volume"))
            self._radio_volume.setValue(radio_volume)

            radio_loudness_boost_enabled = bool(
                payload.get("radio_loudness_boost_enabled") or False
            )
            self._radio_loudness_boost_enabled.setChecked(radio_loudness_boost_enabled)
            radio_loudness_boost_factor = normalize_loudness_boost_factor(
                payload.get("radio_loudness_boost_factor")
            )
            self._radio_loudness_boost_factor.setValue(radio_loudness_boost_factor)
            self._radio_loudness_boost_factor.setEnabled(radio_loudness_boost_enabled)
            self._refresh_radio_volume_label()
        finally:
            self._suppress_autosave = False

    def get_settings(self) -> dict[str, object]:
        return {
            "radio_enabled": bool(self._radio_enabled.isChecked()),
            "radio_autostart": bool(self._radio_autostart.isChecked()),
            "radio_channel": normalize_channel(str(self._radio_channel.currentData() or "")),
            "radio_quality": normalize_quality(str(self._radio_quality.currentData() or "medium")),
            "radio_volume": clamp_volume(self._radio_volume.value()),
            "radio_loudness_boost_enabled": bool(self._radio_loudness_boost_enabled.isChecked()),
            "radio_loudness_boost_factor": normalize_loudness_boost_factor(
                self._radio_loudness_boost_factor.value()
            ),
        }

    def apply_radio_state(self, state: Mapping[str, object] | None) -> None:
        state = state or {}
        qt_available = bool(state.get("qt_available") or False)
        service_available = bool(state.get("service_available") or False)
        is_playing = bool(state.get("is_playing") or False)
        enabled = bool(state.get("enabled") or False)
        volume = clamp_volume(state.get("volume"))
        status_text = str(state.get("status_text") or "Radio unavailable.")
        current_track = str(state.get("current_track") or "").strip() or "No track"
        connection_state = str(state.get("connection_state") or "")

        self._radio_control.setVisible(qt_available)
        self._radio_control.set_service_available(service_available)
        self._radio_control.set_playing(is_playing)
        self._radio_control.set_connection_state(connection_state)
        self._radio_control.set_radio_enabled(enabled)
        self._radio_control.set_volume(volume)
        self._radio_control.set_status_tooltip(status_text)

        self._radio_play_button.setEnabled(qt_available)
        self._radio_status_value.setText(status_text)
        self._radio_track_value.setText(current_track)

    def _on_radio_volume_value_changed(self, value: int) -> None:
        _ = value
        self._refresh_radio_volume_label()
        with QSignalBlocker(self._radio_control):
            self._radio_control.set_volume(self._radio_volume.value())

    def _on_player_volume_changed(self, value: int) -> None:
        clamped = clamp_volume(value)
        with QSignalBlocker(self._radio_volume):
            self._radio_volume.setValue(clamped)
        self._refresh_radio_volume_label()
        self._queue_debounced_autosave()

    def _on_radio_loudness_boost_toggled(self, enabled: bool) -> None:
        self._radio_loudness_boost_factor.setEnabled(bool(enabled))
        self._refresh_radio_volume_label()

    def _on_radio_loudness_boost_factor_changed(self, _value: float) -> None:
        self._refresh_radio_volume_label()

    def _refresh_radio_volume_label(self) -> None:
        raw = max(0, min(100, int(self._radio_volume.value())))
        effective = self._effective_radio_volume_percent(raw)
        self._radio_volume_value.setText(f"{effective}%")

    def _effective_radio_volume_percent(self, value: int) -> int:
        raw = max(0, min(100, int(value)))
        if not self._radio_loudness_boost_enabled.isChecked():
            return raw
        factor = normalize_loudness_boost_factor(
            self._radio_loudness_boost_factor.value()
        )
        return max(0, int(round(raw * factor)))

    @staticmethod
    def _set_combo_value(combo: QComboBox, value: str, fallback: str) -> None:
        idx = combo.findData(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
            return
        idx = combo.findData(fallback)
        if idx >= 0:
            combo.setCurrentIndex(idx)
