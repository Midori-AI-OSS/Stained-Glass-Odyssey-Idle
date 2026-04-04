from __future__ import annotations

import random

from collections.abc import Callable
from typing import Literal

from PySide6.QtCore import QEvent
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.combat.party_stats import apply_base_stat_multiplier
from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.combat.stats import Stats
from endless_idler.progression import REBIRTH_LEVEL_THRESHOLD
from endless_idler.ui.components.progress_bar import AnimatedProgressBar
from endless_idler.ui.party_builder_common import build_character_stats_tooltip
from endless_idler.ui.party_builder_common import format_idle_exp_rate_suffix
from endless_idler.ui.theme.colors import normalize_element_id
from endless_idler.ui.tooltip import hide_stained_tooltip
from endless_idler.ui.tooltip import show_stained_tooltip
from endless_idler.ui.widgets.passive_progress_bar import PassiveProgressBar
from endless_idler.ui.widgets.shard_progress_bar import ShardProgressBar
from endless_idler.utils import normalize_progress


PORTRAIT_SIZE_ONSITE = 120
PORTRAIT_SIZE_OFFSITE_TARGET = 72
PORTRAIT_SIZE_OFFSITE_MIN = 56
PORTRAIT_SIZE_OFFSITE_MAX = 72

CARD_WIDTH_ONSITE = 420
CARD_WIDTH_OFFSITE = 280
CARD_HEIGHT_OFFSITE = 96


class PortraitLabel(QLabel):
    def __init__(self, *, size: tuple[int, int]) -> None:
        super().__init__()
        width, height = size
        self.setFixedSize(max(12, int(width)), max(12, int(height)))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)

    def set_portrait(self, path: str | None, *, placeholder: str) -> None:
        pixmap = QPixmap(path) if path else QPixmap()
        if pixmap.isNull():
            self.setText(placeholder[:2].upper())
            return
        self.setText("")
        self.setPixmap(
            pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )


class IdleCharacterCard(QFrame):
    def __init__(
        self,
        *,
        context: Literal["onsite", "offsite"],
        char_id: str,
        plugin: object,
        idle_state: object,
        rng: random.Random,
        stack_count: int,
        on_rebirth: Callable[[str], None] | None = None,
        on_prestige: Callable[[str], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._context = context
        self._char_id = str(char_id)
        self._plugin = plugin
        self._idle_state = idle_state
        self._rng = rng
        self._stack_count = max(1, int(stack_count))
        self._on_rebirth = on_rebirth
        self._on_prestige = on_prestige
        self._tooltip_html = ""
        self._portrait_placeholder = ""
        self._portrait_source_pixmap: QPixmap | None = None
        self._passive_bars: list[PassiveProgressBar] = []

        self.setObjectName("idleCharacterCard")
        self.setProperty("context", context)
        self.setProperty("elementId", "generic")
        self.setProperty("dualElementIds", "")

        display_name = getattr(plugin, "display_name", char_id) if plugin else char_id
        self._display_name = str(display_name)
        portrait_path = plugin.random_image_path(rng) if plugin else None

        if context == "onsite":
            self._setup_onsite_layout(
                portrait_path=portrait_path,
                display_name=self._display_name,
            )
        else:
            self._setup_offsite_layout(
                portrait_path=portrait_path,
                display_name=self._display_name,
            )

    @property
    def char_id(self) -> str:
        return self._char_id

    def _setup_onsite_layout(
        self, *, portrait_path: str | None, display_name: str
    ) -> None:
        self.setFixedWidth(CARD_WIDTH_ONSITE)

        root = QHBoxLayout()
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)
        self.setLayout(root)

        self._portrait = PortraitLabel(
            size=(PORTRAIT_SIZE_ONSITE, PORTRAIT_SIZE_ONSITE)
        )
        self._portrait.setObjectName("idlePortrait")
        self._portrait.set_portrait(
            str(portrait_path) if portrait_path else None,
            placeholder=display_name,
        )
        root.addWidget(self._portrait, 0, Qt.AlignmentFlag.AlignVCenter)

        self._body = QVBoxLayout()
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(6)
        root.addLayout(self._body, 1)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        self._body.addLayout(header)

        self._name_label = QLabel(f"{display_name} (1)")
        self._name_label.setObjectName("idleCharName")
        header.addWidget(self._name_label, 0, Qt.AlignmentFlag.AlignVCenter)

        header.addStretch(1)

        self._action_button = QPushButton("")
        self._action_button.setObjectName("idleActionButton")
        self._action_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._action_button.setVisible(False)
        header.addWidget(self._action_button, 0, Qt.AlignmentFlag.AlignVCenter)

        self._body.addStretch(1)

        self._setup_bars()

    def _setup_offsite_layout(
        self, *, portrait_path: str | None, display_name: str
    ) -> None:
        self.setFixedSize(CARD_WIDTH_OFFSITE, CARD_HEIGHT_OFFSITE)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        self.setLayout(layout)

        self._portrait = QLabel()
        self._portrait.setObjectName("idlePortrait")
        self._portrait.setFixedSize(
            PORTRAIT_SIZE_OFFSITE_TARGET, PORTRAIT_SIZE_OFFSITE_TARGET
        )
        self._portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._portrait.setScaledContents(False)

        self._portrait_placeholder = display_name[:2].upper()
        pixmap = QPixmap(str(portrait_path)) if portrait_path else QPixmap()
        if pixmap.isNull():
            self._portrait_source_pixmap = None
            self._portrait.setText(self._portrait_placeholder)
        else:
            self._portrait_source_pixmap = pixmap
            self._portrait.setText("")
        self._apply_offsite_portrait_size()
        layout.addWidget(self._portrait, 0, Qt.AlignmentFlag.AlignBottom)

        self._body = QVBoxLayout()
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(4)
        layout.addLayout(self._body, 1)

        self._name_label = QLabel(f"{display_name} (1)")
        self._name_label.setObjectName("idleCharName")
        name_row = QHBoxLayout()
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.setSpacing(6)
        self._body.addLayout(name_row)

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
        self._body.addStretch(1)

        self._setup_bars()

        for widget in (
            self._portrait,
            self._name_label,
            self._hp_bar,
            self._exp_bar,
        ):
            widget.installEventFilter(self)

    def _setup_bars(self) -> None:
        self._hp_bar = AnimatedProgressBar()
        self._hp_bar.setProperty("stat", "hp")
        self._hp_bar.set_value(1.0)
        self._hp_bar.setText("HP 0 / 1000")
        self._hp_bar._gradient_enabled = False
        self._hp_bar.set_color_thresholds(
            [
                (0.0, (231, 76, 60, 170)),
                (0.25, (243, 156, 18, 170)),
                (0.45, (241, 196, 15, 185)),
                (0.65, (46, 204, 113, 165)),
            ]
        )
        self._body.addWidget(self._hp_bar)

        self._exp_bar = AnimatedProgressBar()
        self._exp_bar.setObjectName("idleExpBar")
        self._exp_bar.setFixedHeight(12)
        self._exp_bar.set_value(0.0)
        self._exp_bar.setText("EXP 0 / 30")
        self._exp_bar._gradient_enabled = False
        self._exp_bar.set_gradient_colors(
            start_color=(52, 152, 219, 170),
            mid_color=(52, 152, 219, 170),
            end_color=(52, 152, 219, 170),
        )
        self._body.addWidget(self._exp_bar)

        self._shard_bar = ShardProgressBar()
        self._shard_bar.setVisible(False)
        self._body.addWidget(self._shard_bar)

    def _compute_offsite_portrait_size(self) -> int:
        root_layout = self.layout()
        if isinstance(root_layout, QHBoxLayout):
            margins = root_layout.contentsMargins()
            available_height = max(12, self.height() - margins.top() - margins.bottom())
            available_width = max(12, self.width() - margins.left() - margins.right())
        else:
            available_height = max(12, self.height())
            available_width = max(12, self.width())

        width_cap = max(
            PORTRAIT_SIZE_OFFSITE_MIN,
            int(round(float(available_width) * 0.40)),
        )
        upper_bound = min(PORTRAIT_SIZE_OFFSITE_MAX, available_height, width_cap)
        lower_bound = min(PORTRAIT_SIZE_OFFSITE_MIN, upper_bound)
        if upper_bound <= 0:
            return 12
        return max(lower_bound, min(PORTRAIT_SIZE_OFFSITE_TARGET, upper_bound))

    def _apply_offsite_portrait_size(self) -> None:
        size = self._compute_offsite_portrait_size()
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
        if self._context == "offsite":
            self._apply_offsite_portrait_size()
        try:
            super().resizeEvent(event)
        except (RuntimeError, TypeError):
            return

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

    def _dual_type_visual_data(self, data: dict) -> tuple[bool, tuple[str, str]]:
        plugin_is_dual = (
            getattr(self._plugin, "is_dual_type", False) if self._plugin else False
        )
        data_is_dual = data.get("is_dual_type")
        is_dual = data_is_dual if isinstance(data_is_dual, bool) else plugin_is_dual
        if not is_dual:
            return False, ("generic", "generic")

        plugin_types = (
            getattr(self._plugin, "dual_damage_types", ("", ""))
            if self._plugin
            else ("", "")
        )
        data_types = data.get("dual_damage_types", ("", ""))
        if (
            isinstance(data_types, list | tuple)
            and len(data_types) == 2
            and all(data_types)
        ):
            return True, (str(data_types[0]), str(data_types[1]))

        if (
            isinstance(plugin_types, tuple)
            and len(plugin_types) == 2
            and all(plugin_types)
        ):
            return True, (str(plugin_types[0]), str(plugin_types[1]))
        return False, ("generic", "generic")

    def snapshot(self) -> tuple[dict, Stats] | None:
        getter = getattr(self._idle_state, "get_char_data", None)
        if not callable(getter):
            return None
        data = getter(self._char_id)
        if not isinstance(data, dict) or not data:
            return None

        party_level = 1
        party_level_getter = getattr(self._idle_state, "get_party_level", None)
        if callable(party_level_getter):
            try:
                party_level = max(1, int(party_level_getter()))
            except (TypeError, ValueError):
                party_level = 1

        base_stats = data.get("base_stats")
        saved_base_stats = dict(base_stats) if isinstance(base_stats, dict) else {}

        try:
            stack_count = max(1, int(data.get("stack", 1)))
        except (TypeError, ValueError):
            stack_count = 1

        stars = (
            max(1, int(getattr(self._plugin, "stars", 1) or 1)) if self._plugin else 1
        )

        progress: dict[str, float | int] = {
            "level": max(1, int(data.get("level", 1))),
            "exp": float(max(0.0, float(data.get("exp", 0.0)))),
            "exp_multiplier": float(max(0.0, float(data.get("exp_multiplier", 1.0)))),
            "max_hp_level_bonus_version": max(
                0, int(data.get("max_hp_level_bonus_version", 0))
            ),
        }

        stats = build_scaled_character_stats(
            plugin=self._plugin,
            party_level=party_level,
            stars=stars,
            stacks=stack_count,
            progress=progress,
            saved_base_stats=saved_base_stats,
        )
        stat_multiplier = self._misplacement_stat_multiplier()
        apply_base_stat_multiplier(
            stats=stats,
            multiplier=stat_multiplier,
        )
        return data, stats

    def apply_snapshot(
        self, data: dict, stats: Stats, *, maxima: dict[str, float]
    ) -> None:
        stack_count = max(1, int(data.get("stack", 1)))
        self._stack_count = stack_count

        level = int(getattr(stats, "level", int(data.get("level", 1))))
        exp = float(data.get("exp", 0.0))
        next_exp = float(data.get("next_exp", 30.0))
        hp = float(getattr(stats, "hp", float(data.get("hp", 0.0))))
        max_hp = float(getattr(stats, "max_hp", float(data.get("max_hp", 1000.0))))

        gain_per_second = 0.0
        getter = getattr(self._idle_state, "get_exp_gain_per_second", None)
        if callable(getter):
            try:
                gain_per_second = float(getter(self._char_id))
            except (TypeError, ValueError):
                gain_per_second = 0.0

        rate_suffix = format_idle_exp_rate_suffix(gain_per_second)
        exp_format = f"EXP {max(0, int(exp))} / {max(1, int(next_exp))}{rate_suffix}"

        self._name_label.setText(f"{self._display_name} ({max(1, level)})")
        self._hp_bar.set_value(normalize_progress(hp, max_hp))
        self._hp_bar.setText(f"HP {int(hp)} / {int(max_hp)}")
        self._exp_bar.set_value(min(exp, next_exp) / max(1, next_exp))
        self._exp_bar.setText(exp_format)

        exp_multiplier = float(data.get("exp_multiplier", 1.0))
        show_prestige = exp_multiplier >= 10.0
        show_rebirth = (
            max(1, int(level)) >= REBIRTH_LEVEL_THRESHOLD and not show_prestige
        )

        if self._context == "onsite":
            self._update_onsite_buttons(
                show_rebirth=show_rebirth, show_prestige=show_prestige
            )
        else:
            self._update_offsite_buttons(
                show_rebirth=show_rebirth, show_prestige=show_prestige
            )

        self._update_shard_bar(data)
        self._update_passive_bars()

        stars = getattr(self._plugin, "stars", None) if self._plugin else None
        stat_multiplier = self._misplacement_stat_multiplier()
        exp_multiplier_adj = self._misplacement_exp_multiplier()
        self._tooltip_html = build_character_stats_tooltip(
            name=str(self._display_name),
            stars=stars,
            stacks=stack_count,
            stackable=stack_count > 1,
            stats=stats,
            mismatch=(stat_multiplier < 1.0 or exp_multiplier_adj < 1.0),
            exp_multiplier_override=(stats.exp_multiplier * exp_multiplier_adj),
        )

        self._apply_element_tint(data, stats)

        if self.underMouse() and self._tooltip_html:
            show_stained_tooltip(self, self._tooltip_html, element_id=stats.element_id)

    def update_display(self) -> None:
        data_getter = getattr(self._idle_state, "get_char_data", None)
        if not callable(data_getter):
            return
        data = data_getter(self._char_id)
        if not data:
            return

        snapshot_result = self.snapshot()
        if snapshot_result is None:
            return
        _, stats = snapshot_result
        self.apply_snapshot(data, stats, maxima={})

    def _update_onsite_buttons(
        self, *, show_rebirth: bool, show_prestige: bool
    ) -> None:
        if show_prestige:

            def on_prestige_click() -> None:
                if self._on_prestige is not None:
                    self._on_prestige(self._char_id)

            self._action_button.setText("Prestige")
            self._action_button.setVisible(True)
            try:
                self._action_button.clicked.disconnect()
            except (RuntimeError, TypeError):
                pass
            self._action_button.clicked.connect(on_prestige_click)
        elif show_rebirth:

            def on_rebirth_click() -> None:
                if self._on_rebirth is not None:
                    self._on_rebirth(self._char_id)

            self._action_button.setText("Rebirth")
            self._action_button.setVisible(True)
            try:
                self._action_button.clicked.disconnect()
            except (RuntimeError, TypeError):
                pass
            self._action_button.clicked.connect(on_rebirth_click)
        else:
            self._action_button.setVisible(False)

    def _update_offsite_buttons(
        self, *, show_rebirth: bool, show_prestige: bool
    ) -> None:
        self._rebirth_button.setVisible(show_rebirth)
        self._prestige_button.setVisible(show_prestige)

    def _update_shard_bar(self, data: dict) -> None:
        shard_reward_types = data.get("shard_reward_types")
        if isinstance(shard_reward_types, tuple) and len(shard_reward_types) > 0:
            shard_bar_ticks = int(data.get("shard_bar_ticks", 0))
            element_id = str(
                getattr(self._plugin, "damage_type_id", "generic") or "generic"
            )
            self._shard_bar.set_shard_data(
                shard_bar_ticks=shard_bar_ticks,
                element_id=element_id,
                shard_types=shard_reward_types,
            )
            self._shard_bar.setVisible(True)
        else:
            self._shard_bar.setVisible(False)

    def _update_passive_bars(self) -> None:
        getter = getattr(self._idle_state, "get_passive_bars_for_character", None)
        passive_bars = getter(self._char_id) if callable(getter) else []
        if not isinstance(passive_bars, list):
            passive_bars = []

        while len(self._passive_bars) < len(passive_bars):
            bar = PassiveProgressBar()
            bar.setVisible(False)
            self._passive_bars.append(bar)
            self._body.addWidget(bar)

        for index, passive_bar in enumerate(self._passive_bars):
            if index >= len(passive_bars):
                passive_bar.setVisible(False)
                continue

            bar_data = passive_bars[index]
            label = getattr(bar_data, "label", "PASSIVE")
            progress = float(getattr(bar_data, "progress", 0.0))
            display_percent = float(getattr(bar_data, "display_percent", 0.0))
            display_text = str(getattr(bar_data, "display_text", "") or "")
            shimmer = float(getattr(bar_data, "shimmer", 0.0))
            style_id = str(getattr(bar_data, "style_id", "default") or "default")
            element_id = str(getattr(bar_data, "element_id", "generic") or "generic")
            dual_element_ids = getattr(bar_data, "dual_element_ids", ())
            if not isinstance(dual_element_ids, tuple):
                dual_element_ids = tuple(dual_element_ids)

            passive_bar.set_passive_data(
                label=label,
                progress=progress,
                display_percent=display_percent,
                display_text=display_text,
                shimmer=shimmer,
                style_id=style_id,
                element_id=element_id,
                dual_element_ids=dual_element_ids,
            )
            passive_bar.setVisible(True)

    def _apply_element_tint(self, data: dict, stats: Stats) -> None:
        is_dual_type, dual_damage_types = self._dual_type_visual_data(data)
        if is_dual_type:
            dual_element_ids = ",".join(
                (
                    normalize_element_id(dual_damage_types[0]),
                    normalize_element_id(dual_damage_types[1]),
                )
            )
            self._set_card_theme_properties(
                element_id="", dual_element_ids=dual_element_ids
            )
            return

        self._set_card_theme_properties(
            element_id=normalize_element_id(getattr(stats, "element_id", "generic")),
            dual_element_ids="",
        )

    def _set_card_theme_properties(
        self, *, element_id: str, dual_element_ids: str
    ) -> None:
        normalized_element_id = (
            "" if not str(element_id or "") else normalize_element_id(element_id)
        )
        normalized_dual_ids = str(dual_element_ids or "")
        if (
            self.property("elementId") == normalized_element_id
            and self.property("dualElementIds") == normalized_dual_ids
        ):
            return
        self.setProperty("elementId", normalized_element_id)
        self.setProperty("dualElementIds", normalized_dual_ids)
        self._repolish_card()

    def _repolish_card(self) -> None:
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

    def eventFilter(self, watched: object, event: object) -> bool:
        if hasattr(event, "type") and event.type() == QEvent.Type.Enter:
            self._show_tooltip()
        return super().eventFilter(watched, event)

    def _show_tooltip(self) -> None:
        if not self._tooltip_html:
            return
        data_getter = getattr(self._idle_state, "get_char_data", None)
        if callable(data_getter):
            data = data_getter(self._char_id)
            if data:
                snapshot_result = self.snapshot()
                if snapshot_result:
                    _, stats = snapshot_result
                    show_stained_tooltip(
                        self, self._tooltip_html, element_id=stats.element_id
                    )
                    return
        show_stained_tooltip(self, self._tooltip_html, element_id=None)

    def enterEvent(self, event: object) -> None:
        self._show_tooltip()
        try:
            super().enterEvent(event)
        except (RuntimeError, TypeError):
            return

    def leaveEvent(self, event: object) -> None:
        hide_stained_tooltip()
        try:
            super().leaveEvent(event)
        except (RuntimeError, TypeError):
            return
