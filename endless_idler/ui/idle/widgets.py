from __future__ import annotations

import random

from collections.abc import Callable

from PySide6.QtCore import QEvent
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.combat.party_stats import apply_base_stat_multiplier
from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.ui.party_builder_common import build_character_stats_tooltip
from endless_idler.ui.party_builder_common import format_idle_exp_rate_suffix
from endless_idler.ui.tooltip import hide_stained_tooltip
from endless_idler.ui.tooltip import show_stained_tooltip


IDLE_OFFSITE_PORTRAIT_SIZE = 56
IDLE_OFFSITE_PORTRAIT_TARGET_SIZE = 72
IDLE_OFFSITE_PORTRAIT_MIN_SIZE = 56
IDLE_OFFSITE_PORTRAIT_MAX_SIZE = 72


class IdleArena(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("idleArena")

class IdleOffsiteCard(QFrame):
    def __init__(
        self,
        *,
        char_id: str,
        plugin: object,
        idle_state: object,
        rng: random.Random,
        stack_count: int,
        on_rebirth: Callable[[str], None] | None = None,
        on_prestige: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("idleOffsiteCard")
        self.setProperty("elementId", "generic")
        self._char_id = char_id
        self._plugin = plugin
        self._idle_state = idle_state
        self._rng = rng
        self._stack_count = stack_count
        self._on_rebirth = on_rebirth
        self._on_prestige = on_prestige
        self._portrait_placeholder = ""
        self._portrait_source_pixmap: QPixmap | None = None

        self.setFixedSize(280, 96)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.setLayout(layout)

        self._portrait = QLabel()
        self._portrait.setObjectName("idleOffsitePortrait")
        self._portrait.setFixedSize(IDLE_OFFSITE_PORTRAIT_SIZE, IDLE_OFFSITE_PORTRAIT_SIZE)
        self._portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._portrait.setScaledContents(False)

        display_name = getattr(plugin, "display_name", char_id) if plugin else char_id
        self._portrait_placeholder = str(display_name[:2].upper())
        portrait_path = plugin.random_image_path(rng) if plugin else None
        pixmap = QPixmap(str(portrait_path)) if portrait_path else QPixmap()
        if pixmap.isNull():
            self._portrait_source_pixmap = None
            self._portrait.setText(self._portrait_placeholder)
        else:
            self._portrait_source_pixmap = pixmap
            self._portrait.setText("")
        self._apply_portrait_size()
        layout.addWidget(self._portrait, 0, Qt.AlignmentFlag.AlignBottom)

        body = QVBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(4)
        layout.addLayout(body, 1)

        self._display_name = str(display_name)
        self._name_label = QLabel(f"{self._display_name} (1)")
        self._name_label.setObjectName("idleOffsiteName")
        name_row = QHBoxLayout()
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.setSpacing(6)
        body.addLayout(name_row)

        name_row.addWidget(self._name_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self._rebirth_button = QPushButton("Rebirth")
        self._rebirth_button.setObjectName("idleRebirthButton")
        self._rebirth_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._rebirth_button.setVisible(False)
        self._rebirth_button.clicked.connect(self._request_rebirth)
        name_row.addWidget(self._rebirth_button, 0, Qt.AlignmentFlag.AlignVCenter)
        
        self._prestige_button = QPushButton("Prestige")
        self._prestige_button.setObjectName("idlePrestigeButton")
        self._prestige_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._prestige_button.setVisible(False)
        self._prestige_button.clicked.connect(self._request_prestige)
        name_row.addWidget(self._prestige_button, 0, Qt.AlignmentFlag.AlignVCenter)
        
        name_row.addStretch(1)
        body.addStretch(1)

        self._hp_bar = QProgressBar()
        self._hp_bar.setObjectName("idleHpBar")
        self._hp_bar.setFixedHeight(12)
        self._hp_bar.setTextVisible(True)
        self._hp_bar.setRange(0, 1000)
        self._hp_bar.setValue(1000)
        self._hp_bar.setFormat("1000 / 1000")
        body.addWidget(self._hp_bar)

        self._exp_bar = QProgressBar()
        self._exp_bar.setObjectName("idleExpBar")
        self._exp_bar.setFixedHeight(12)
        self._exp_bar.setTextVisible(True)
        self._exp_bar.setRange(0, 30)
        self._exp_bar.setValue(0)
        self._exp_bar.setFormat("EXP 0 / 30")
        body.addWidget(self._exp_bar)
        
        # Element tint will be applied on first update_display call
        for widget in (
            self._portrait,
            self._name_label,
            self._hp_bar,
            self._exp_bar,
        ):
            widget.installEventFilter(self)

    def _compute_portrait_size(self) -> int:
        root_layout = self.layout()
        if isinstance(root_layout, QHBoxLayout):
            margins = root_layout.contentsMargins()
            available_height = max(12, self.height() - margins.top() - margins.bottom())
            available_width = max(12, self.width() - margins.left() - margins.right())
        else:
            available_height = max(12, self.height())
            available_width = max(12, self.width())

        width_cap = max(
            IDLE_OFFSITE_PORTRAIT_MIN_SIZE,
            int(round(float(available_width) * 0.40)),
        )
        upper_bound = min(IDLE_OFFSITE_PORTRAIT_MAX_SIZE, available_height, width_cap)
        lower_bound = min(IDLE_OFFSITE_PORTRAIT_MIN_SIZE, upper_bound)
        if upper_bound <= 0:
            return 12
        return max(lower_bound, min(IDLE_OFFSITE_PORTRAIT_TARGET_SIZE, upper_bound))

    def _apply_portrait_size(self) -> None:
        size = self._compute_portrait_size()
        self._portrait.setFixedSize(size, size)
        source = self._portrait_source_pixmap
        if source is None or source.isNull():
            self._portrait.setPixmap(QPixmap())
            self._portrait.setText(self._portrait_placeholder)
            return
        scaled = source.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._portrait.setText("")
        self._portrait.setPixmap(scaled)

    def resizeEvent(self, event: object) -> None:
        self._apply_portrait_size()
        try:
            super().resizeEvent(event)  # type: ignore[misc]
        except Exception:
            return

    def update_display(self) -> None:
        data = self._idle_state.get_char_data(self._char_id)
        if not data:
            return

        level = int(data.get("level", 1))
        exp = float(data.get("exp", 0))
        next_exp = float(data.get("next_exp", 30))
        hp = float(data.get("hp", 0))
        max_hp = float(data.get("max_hp", 1000))

        gain_per_second = 0.0
        getter = getattr(self._idle_state, "get_exp_gain_per_second", None)
        if callable(getter):
            try:
                gain_per_second = float(getter(self._char_id))
            except Exception:
                gain_per_second = 0.0

        self._name_label.setText(f"{self._display_name} ({max(1, level)})")
        self._exp_bar.setRange(0, max(1, int(next_exp)))
        self._exp_bar.setValue(int(exp))
        rate_suffix = format_idle_exp_rate_suffix(gain_per_second)
        self._exp_bar.setFormat(f"EXP {max(0, int(exp))} / {max(1, int(next_exp))}{rate_suffix}")

        self._hp_bar.setRange(0, max(1, int(max_hp)))
        self._hp_bar.setValue(int(hp))
        self._hp_bar.setFormat(f"{max(0, int(hp))} / {max(1, int(max_hp))}")

        # Show rebirth button when level >= 50
        self._rebirth_button.setVisible(level >= 50)
        
        # Show prestige button when exp_multiplier >= 10
        exp_multiplier = float(data.get("exp_multiplier", 1.0))
        self._prestige_button.setVisible(exp_multiplier >= 10.0)
        
        # Apply element tint on each update
        self._apply_element_tint(data)
        
        # Update tooltip if mouse is currently over the widget
        if self.underMouse():
            self._show_tooltip()

    def eventFilter(self, watched: object, event: object) -> bool:  # noqa: ANN001
        if hasattr(event, "type") and event.type() == QEvent.Type.Enter:
            self._show_tooltip()
        return super().eventFilter(watched, event)  # type: ignore[misc]

    def _misplacement_stat_multiplier(self) -> float:
        getter = getattr(self._idle_state, "get_misplacement_stat_multiplier", None)
        if not callable(getter):
            return 1.0
        return float(getter(self._char_id))

    def _misplacement_exp_multiplier(self) -> float:
        getter = getattr(self._idle_state, "get_misplacement_exp_multiplier", None)
        if not callable(getter):
            return 1.0
        return float(getter(self._char_id))

    def _show_tooltip(self) -> None:
        data = self._idle_state.get_char_data(self._char_id)
        if not (data and self._plugin):
            return

        base_stats = data.get("base_stats")
        saved_base_stats = dict(base_stats) if isinstance(base_stats, dict) else {}

        try:
            stack_count = max(1, int(data.get("stack", self._stack_count)))
        except (TypeError, ValueError):
            stack_count = max(1, int(self._stack_count))

        party_level = 1
        party_level_getter = getattr(self._idle_state, "get_party_level", None)
        if callable(party_level_getter):
            try:
                party_level = max(1, int(party_level_getter()))
            except Exception:
                party_level = 1

        progress: dict[str, float | int] = {
            "level": max(1, int(data.get("level", 1))),
            "exp": float(max(0.0, float(data.get("exp", 0.0)))),
            "exp_multiplier": float(max(0.0, float(data.get("exp_multiplier", 1.0)))),
            "max_hp_level_bonus_version": max(0, int(data.get("max_hp_level_bonus_version", 0))),
        }

        stars = max(1, int(getattr(self._plugin, "stars", 1) or 1))
        stats = build_scaled_character_stats(
            plugin=self._plugin,
            party_level=party_level,
            stars=stars,
            stacks=stack_count,
            progress=progress,
            saved_base_stats=saved_base_stats,
        )
        stat_multiplier = self._misplacement_stat_multiplier()
        exp_multiplier = self._misplacement_exp_multiplier()
        apply_base_stat_multiplier(
            stats=stats,
            multiplier=stat_multiplier,
        )
        try:
            stats.hp = max(0, int(float(data.get("hp", stats.hp))))
        except (TypeError, ValueError):
            pass

        name = getattr(self._plugin, "display_name", None) or self._char_id
        tooltip_html = build_character_stats_tooltip(
            name=str(name),
            stars=stars,
            stacks=stack_count if stack_count > 1 else None,
            stackable=stack_count > 1,
            stats=stats,
            mismatch=(stat_multiplier < 1.0 or exp_multiplier < 1.0),
            exp_multiplier_override=(stats.exp_multiplier * exp_multiplier),
        )
        if tooltip_html:
            show_stained_tooltip(self, tooltip_html, element_id=stats.element_id)

    def enterEvent(self, event: object) -> None:
        self._show_tooltip()

        try:
            super().enterEvent(event)  # type: ignore[misc]
        except Exception:
            return

    def leaveEvent(self, event: object) -> None:
        hide_stained_tooltip()
        try:
            super().leaveEvent(event)  # type: ignore[misc]
        except Exception:
            return
    
    def _apply_element_tint(self, data: dict) -> None:
        if not self._plugin:
            return
        
        if not data or not isinstance(data, dict):
            return
        
        base_stats = data.get("base_stats")
        saved_base_stats = dict(base_stats) if isinstance(base_stats, dict) else {}
        
        try:
            stack_count = max(1, int(data.get("stack", 1)))
        except (TypeError, ValueError):
            stack_count = 1
        
        stars = max(1, int(getattr(self._plugin, "stars", 1) or 1))
        
        progress: dict[str, float | int] = {
            "level": max(1, int(data.get("level", 1))),
            "exp": float(max(0.0, float(data.get("exp", 0.0)))),
            "exp_multiplier": float(max(0.0, float(data.get("exp_multiplier", 1.0)))),
            "max_hp_level_bonus_version": max(0, int(data.get("max_hp_level_bonus_version", 0))),
        }
        
        party_level = 1
        party_level_getter = getattr(self._idle_state, "get_party_level", None)
        if callable(party_level_getter):
            try:
                party_level = max(1, int(party_level_getter()))
            except Exception:
                party_level = 1
        
        stats = build_scaled_character_stats(
            plugin=self._plugin,
            party_level=party_level,
            stars=stars,
            stacks=stack_count,
            progress=progress,
            saved_base_stats=saved_base_stats,
        )
        apply_base_stat_multiplier(
            stats=stats,
            multiplier=self._misplacement_stat_multiplier(),
        )
        
        element_id = str(getattr(stats, "element_id", "generic") or "generic")
        element_id = element_id.strip().lower().replace(" ", "_").replace("-", "_")
        if self.property("elementId") == element_id:
            return
        self.setProperty("elementId", element_id)
        style = self.style()
        if style is not None:
            style.unpolish(self)
            style.polish(self)
        self.update()

    def _request_rebirth(self) -> None:
        if self._on_rebirth is None:
            return
        self._on_rebirth(self._char_id)
    
    def _request_prestige(self) -> None:
        if self._on_prestige is None:
            return
        self._on_prestige(self._char_id)
