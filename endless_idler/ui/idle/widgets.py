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

from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.ui.party_builder_common import build_character_stats_tooltip
from endless_idler.ui.tooltip import hide_stained_tooltip
from endless_idler.ui.tooltip import show_stained_tooltip


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
        self._char_id = char_id
        self._plugin = plugin
        self._idle_state = idle_state
        self._rng = rng
        self._stack_count = stack_count
        self._on_rebirth = on_rebirth
        self._on_prestige = on_prestige

        self.setFixedSize(220, 96)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.setLayout(layout)

        self._portrait = QLabel()
        self._portrait.setObjectName("idleOffsitePortrait")
        self._portrait.setFixedSize(48, 72)
        self._portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._portrait.setScaledContents(False)

        display_name = getattr(plugin, "display_name", char_id) if plugin else char_id
        portrait_path = plugin.random_image_path(rng) if plugin else None
        pixmap = QPixmap(str(portrait_path)) if portrait_path else QPixmap()
        if pixmap.isNull():
            self._portrait.setText(display_name[:2].upper())
        else:
            scaled = pixmap.scaled(
                48,
                72,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._portrait.setPixmap(scaled)
        layout.addWidget(self._portrait, 0, Qt.AlignmentFlag.AlignTop)

        body = QVBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(4)
        layout.addLayout(body, 1)

        self._name_label = QLabel(display_name)
        self._name_label.setObjectName("idleOffsiteName")
        name_row = QHBoxLayout()
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.setSpacing(6)
        body.addLayout(name_row)

        name_row.addWidget(self._name_label, 0, Qt.AlignmentFlag.AlignVCenter)
        plus = QLabel(f"+{max(0, stack_count - 1)}")
        plus.setObjectName("idleStackPlus")
        plus.setVisible(stack_count > 1)
        name_row.addWidget(plus, 0, Qt.AlignmentFlag.AlignVCenter)

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

        self._level_label = QLabel("Level: 1")
        self._level_label.setObjectName("idleOffsiteLevel")
        body.addWidget(self._level_label)

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

        body.addStretch(1)
        
        # Element tint will be applied on first update_display call
        for widget in (
            self._portrait,
            self._name_label,
            self._level_label,
            self._hp_bar,
            self._exp_bar,
        ):
            widget.installEventFilter(self)

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

        self._level_label.setText(f"Level: {level}")
        self._exp_bar.setRange(0, max(1, int(next_exp)))
        self._exp_bar.setValue(int(exp))
        if gain_per_second > 0:
            self._exp_bar.setFormat(f"EXP {max(0, int(exp))} / {max(1, int(next_exp))} +{gain_per_second:.2f}/s")
        else:
            self._exp_bar.setFormat(f"EXP {max(0, int(exp))} / {max(1, int(next_exp))}")

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

    def eventFilter(self, watched: object, event: object) -> bool:  # noqa: ANN001
        if hasattr(event, "type") and event.type() == QEvent.Type.Enter:
            self._show_tooltip()
        return super().eventFilter(watched, event)  # type: ignore[misc]

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
        
        from endless_idler.ui.battle.colors import color_for_damage_type_id
        element_id = getattr(stats, "element_id", "generic")
        color = color_for_damage_type_id(element_id)
        
        tint_color = f"rgba({color.red()}, {color.green()}, {color.blue()}, 60)"
        self.setStyleSheet(f"QFrame#idleOffsiteCard {{ background-color: {tint_color} !important; }}")

    def _request_rebirth(self) -> None:
        if self._on_rebirth is None:
            return
        self._on_rebirth(self._char_id)
    
    def _request_prestige(self) -> None:
        if self._on_prestige is None:
            return
        self._on_prestige(self._char_id)
