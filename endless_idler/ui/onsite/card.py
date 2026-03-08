from __future__ import annotations

import random

from collections.abc import Callable

from PySide6.QtCore import QPoint
from PySide6.QtCore import QPointF
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
from endless_idler.ui.components.progress_bar import AnimatedProgressBar
from endless_idler.ui.onsite.stat_bars import StatBarsPanel
from endless_idler.ui.party_builder_common import build_character_stats_tooltip
from endless_idler.ui.party_builder_common import format_idle_exp_rate_suffix
from endless_idler.ui.tooltip import hide_stained_tooltip
from endless_idler.ui.tooltip import show_stained_tooltip
from endless_idler.utils import normalize_progress


IDLE_ONSITE_PORTRAIT_SIZE = 120


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


class OnsiteStatsPopup(QFrame):
    def __init__(
        self, *, on_close: Callable[[], None], parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._on_close = on_close
        self.setObjectName("onsiteStatPopup")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setWindowFlag(Qt.WindowType.Popup, True)

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        self._panel: StatBarsPanel | None = None

    def set_panel(self, panel: StatBarsPanel) -> None:
        if self._panel is not None:
            self.layout().removeWidget(self._panel)  # type: ignore[union-attr]
            self._panel.setParent(None)
        self._panel = panel
        self.layout().addWidget(panel)  # type: ignore[union-attr]

    def closeEvent(self, event: object) -> None:
        try:
            self._on_close()
        except Exception:
            pass
        try:
            super().closeEvent(event)  # type: ignore[misc]
        except Exception:
            return


class OnsiteCharacterCardBase(QFrame):
    def __init__(
        self,
        *,
        name: str,
        portrait_path: str | None,
        placeholder: str,
        stack_count: int,
        team_side: str,
        mode: str,
        portrait_size: tuple[int, int],
        card_width: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._team_side = (team_side or "left").strip().lower()
        self._stack_count = max(1, int(stack_count))
        self._base_name = str(name)
        self._tooltip_html = ""
        self._stats_panel: StatBarsPanel | None = None
        self._stats_popup: OnsiteStatsPopup | None = None
        self._action_button_handler: Callable[[], None] | None = None

        self.setObjectName("onsiteCharacterCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFixedWidth(max(220, int(card_width)))
        onsite_mode = (mode or "idle").strip().lower()
        self._is_idle_mode = onsite_mode == "idle"
        self.setProperty("onsiteMode", onsite_mode)
        self.setProperty("elementId", "generic")

        root = QHBoxLayout()
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)
        self.setLayout(root)

        self._portrait = PortraitLabel(size=portrait_size)
        self._portrait.setObjectName("onsitePortrait")
        self._portrait.set_portrait(portrait_path, placeholder=placeholder)
        root.addWidget(self._portrait, 0, Qt.AlignmentFlag.AlignVCenter)

        body = QVBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(6)
        root.addLayout(body, 1)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        body.addLayout(header)

        self._name_label = QLabel(self._base_name)
        self._name_label.setObjectName("onsiteCharName")
        header.addWidget(self._name_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self._stack_plus: QLabel | None = None
        if not self._is_idle_mode:
            stack_plus = QLabel(f"+{max(0, self._stack_count - 1)}")
            stack_plus.setObjectName("onsiteStackPlus")
            stack_plus.setVisible(self._stack_count > 1)
            header.addWidget(stack_plus, 0, Qt.AlignmentFlag.AlignVCenter)
            self._stack_plus = stack_plus

        header.addStretch(1)

        # Eye/stats popup is intentionally removed from Idle and Fight modes.
        self._stats_button: QPushButton | None = None
        if onsite_mode not in {"idle", "battle"}:
            stats_button = QPushButton("👁")
            stats_button.setObjectName("onsiteStatsButton")
            stats_button.setCursor(Qt.CursorShape.PointingHandCursor)
            stats_button.setCheckable(True)
            stats_button.setChecked(False)
            stats_button.setToolTip("Stats")
            stats_button.toggled.connect(self._toggle_stats_popup)
            header.addWidget(stats_button, 0, Qt.AlignmentFlag.AlignVCenter)
            self._stats_button = stats_button

        self._action_button = QPushButton("")
        self._action_button.setObjectName("onsiteActionButton")
        self._action_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._action_button.setVisible(False)
        header.addWidget(self._action_button, 0, Qt.AlignmentFlag.AlignVCenter)

        self._level_label: QLabel | None = None
        if not self._is_idle_mode:
            level_label = QLabel("Level: 1")
            level_label.setObjectName("onsiteCharLevel")
            body.addWidget(level_label)
            self._level_label = level_label

        self._stack_label: QLabel | None = None
        if not self._is_idle_mode:
            stack_label = QLabel(f"Stack: {self._stack_count}")
            stack_label.setObjectName("onsiteCharStack")
            body.addWidget(stack_label)
            self._stack_label = stack_label

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

        if self._is_idle_mode:
            body.addStretch(1)
        body.addWidget(self._hp_bar)

        self._exp_bar = AnimatedProgressBar()
        self._exp_bar.setObjectName("onsiteExpBar")
        self._exp_bar.setFixedHeight(12)
        self._exp_bar.set_value(0.0)
        self._exp_bar.setText("EXP 0 / 30")
        self._exp_bar._gradient_enabled = False
        self._exp_bar.set_gradient_colors(
            start_color=(52, 152, 219, 170),
            mid_color=(52, 152, 219, 170),
            end_color=(52, 152, 219, 170),
        )
        body.addWidget(self._exp_bar)

        if not self._is_idle_mode:
            body.addStretch(1)
        self.set_level(1)

    def set_stack_count(self, stack_count: int) -> None:
        self._stack_count = max(1, int(stack_count))
        if self._stack_plus is not None:
            self._stack_plus.setText(f"+{max(0, self._stack_count - 1)}")
            self._stack_plus.setVisible(self._stack_count > 1)
        if self._stack_label is not None:
            self._stack_label.setText(f"Stack: {self._stack_count}")

    def set_level(self, level: int) -> None:
        normalized = max(1, int(level))
        if self._is_idle_mode:
            self._name_label.setText(f"{self._base_name} ({normalized})")
            return
        if self._level_label is not None:
            self._level_label.setText(f"Level: {normalized}")

    def set_hp(self, *, current: float, max_hp: float) -> None:
        current_hp = max(0, int(current))
        max_hp_value = max(1, int(max_hp))
        self._hp_bar.set_value(normalize_progress(current_hp, max_hp_value))
        self._hp_bar.setText(f"HP {current_hp} / {max_hp_value}")

    def set_exp(self, *, current: float, max_exp: float, format_text: str) -> None:
        exp_value = max(0, int(current))
        exp_max = max(1, int(max_exp))
        self._exp_bar.set_value(min(exp_value, exp_max) / exp_max)
        self._exp_bar.setText(str(format_text))

    def set_action_button(
        self,
        *,
        label: str,
        visible: bool,
        on_click: Callable[[], None] | None = None,
    ) -> None:
        self._action_button.setText(str(label))
        self._action_button.setVisible(bool(visible))
        if self._action_button_handler is not None:
            try:
                self._action_button.clicked.disconnect(self._action_button_handler)
            except (RuntimeError, TypeError):
                pass
            self._action_button_handler = None
        if on_click is not None:
            self._action_button.clicked.connect(on_click)
            self._action_button_handler = on_click

    def set_stats(
        self,
        *,
        name: str,
        stars: int | None,
        stacks: int,
        stackable: bool,
        stats: Stats,
        maxima: dict[str, float],
        mismatch: bool = False,
        exp_multiplier_override: float | None = None,
    ) -> None:
        self._stats = stats
        self._tooltip_html = build_character_stats_tooltip(
            name=str(name),
            stars=stars,
            stacks=stacks,
            stackable=stackable,
            stats=stats,
            mismatch=mismatch,
            exp_multiplier_override=exp_multiplier_override,
        )

        if self._stats_panel is None:
            self._stats_panel = StatBarsPanel(stats=stats, maxima=maxima)
        else:
            self._stats_panel.set_stats(stats)
            self._stats_panel.set_maxima(maxima)

        if self._stats_popup is not None:
            self._stats_popup.set_panel(self._stats_panel)

        self._apply_element_tint(stats)

        if self.underMouse() and self._tooltip_html:
            element_id = getattr(getattr(self, "_stats", None), "element_id", None)
            show_stained_tooltip(self, self._tooltip_html, element_id=element_id)

    def _apply_element_tint(self, stats: Stats) -> None:
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

    def pulse_anchor_global(self) -> QPointF:
        rect = self.rect()
        if self._team_side == "right":
            point = rect.center()
            point.setX(rect.left())
            return QPointF(self.mapToGlobal(point))
        point = rect.center()
        point.setX(rect.right())
        return QPointF(self.mapToGlobal(point))

    def enterEvent(self, event: object) -> None:
        if self._tooltip_html:
            element_id = getattr(getattr(self, "_stats", None), "element_id", None)
            show_stained_tooltip(self, self._tooltip_html, element_id=element_id)
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

    def _toggle_stats_popup(self, checked: bool) -> None:
        if self._stats_button is None:
            return
        if not checked:
            if self._stats_popup is not None:
                self._stats_popup.close()
            return

        if self._stats_panel is None:
            self._stats_button.setChecked(False)
            return

        if self._stats_popup is None:
            self._stats_popup = OnsiteStatsPopup(
                on_close=self._on_popup_closed, parent=None
            )

        self._stats_popup.set_panel(self._stats_panel)
        pos = self._stats_button.mapToGlobal(QPoint(0, self._stats_button.height()))
        self._stats_popup.move(pos)
        self._stats_popup.show()
        self._stats_popup.raise_()
        self._stats_popup.activateWindow()

    def _on_popup_closed(self) -> None:
        if self._stats_button is None:
            return
        if self._stats_button.isChecked():
            self._stats_button.setChecked(False)


class BattleOnsiteCharacterCard(OnsiteCharacterCardBase):
    def __init__(
        self,
        *,
        combatant: object,
        plugin: object,
        rng: random.Random,
        team_side: str,
        stack_count: int,
        portrait_size: tuple[int, int],
        card_width: int,
        maxima: dict[str, float],
        parent: QWidget | None = None,
    ) -> None:
        self._combatant = combatant
        portrait_path = plugin.random_image_path(rng) if plugin else None
        name = getattr(combatant, "name", "")

        super().__init__(
            name=str(name),
            portrait_path=str(portrait_path) if portrait_path else None,
            placeholder=str(name),
            stack_count=stack_count,
            team_side=team_side,
            mode="battle",
            portrait_size=portrait_size,
            card_width=card_width,
            parent=parent,
        )

        stats = getattr(combatant, "stats", None)
        if isinstance(stats, Stats):
            self.set_stats(
                name=str(name),
                stars=getattr(plugin, "stars", None) if plugin else None,
                stacks=max(1, int(stack_count)),
                stackable=max(1, int(stack_count)) > 1,
                stats=stats,
                maxima=maxima,
            )
            self.set_level(int(getattr(stats, "level", 1)))
            self.set_stack_count(int(stack_count))

        self.refresh()

    def refresh(self) -> None:
        stats = getattr(self._combatant, "stats", None)
        max_hp = int(getattr(self._combatant, "max_hp", 1) or 1)
        hp = int(getattr(stats, "hp", max_hp) if stats is not None else max_hp)
        self.set_hp(current=hp, max_hp=max_hp)

        exp_value = int(getattr(stats, "exp", 0) if stats is not None else 0)
        level = int(getattr(stats, "level", 1) if stats is not None else 1)
        exp_max = max(1, 100 * max(1, level))
        self.set_exp(
            current=exp_value,
            max_exp=exp_max,
            format_text=f"EXP {max(0, exp_value)} / {exp_max}",
        )
        self.set_level(level)


class IdleOnsiteCharacterCard(OnsiteCharacterCardBase):
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
        parent: QWidget | None = None,
    ) -> None:
        self._char_id = str(char_id)
        self._plugin = plugin
        self._idle_state = idle_state
        self._rng = rng
        self._on_rebirth = on_rebirth
        self._on_prestige = on_prestige

        portrait_path = plugin.random_image_path(rng) if plugin else None
        display_name = getattr(plugin, "display_name", char_id) if plugin else char_id

        super().__init__(
            name=str(display_name),
            portrait_path=str(portrait_path) if portrait_path else None,
            placeholder=str(display_name),
            stack_count=stack_count,
            team_side="left",
            mode="idle",
            portrait_size=(IDLE_ONSITE_PORTRAIT_SIZE, IDLE_ONSITE_PORTRAIT_SIZE),
            card_width=420,
            parent=parent,
        )

    @property
    def char_id(self) -> str:
        return self._char_id

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
            except Exception:
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
        self.set_stack_count(stack_count)

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
            except Exception:
                gain_per_second = 0.0

        rate_suffix = format_idle_exp_rate_suffix(gain_per_second)
        exp_format = f"EXP {max(0, int(exp))} / {max(1, int(next_exp))}{rate_suffix}"

        self.set_level(level)
        self.set_hp(current=hp, max_hp=max_hp)
        self.set_exp(current=exp, max_exp=next_exp, format_text=exp_format)

        # Check prestige availability first (exp_multiplier >= 10)
        exp_multiplier = float(data.get("exp_multiplier", 1.0))
        show_prestige = exp_multiplier >= 10.0

        # Show rebirth button if level >= 50 and prestige is not available
        show_rebirth = max(1, int(level)) >= 50 and not show_prestige

        if show_prestige:

            def on_prestige_click() -> None:
                if self._on_prestige is not None:
                    self._on_prestige(self._char_id)

            self.set_action_button(
                label="Prestige", visible=True, on_click=on_prestige_click
            )
        elif show_rebirth:

            def on_rebirth_click() -> None:
                if self._on_rebirth is not None:
                    self._on_rebirth(self._char_id)

            self.set_action_button(
                label="Rebirth", visible=True, on_click=on_rebirth_click
            )
        else:
            self.set_action_button(label="", visible=False, on_click=None)

        stars = getattr(self._plugin, "stars", None) if self._plugin else None
        display_name = (
            getattr(self._plugin, "display_name", self._char_id)
            if self._plugin
            else self._char_id
        )
        stat_multiplier = self._misplacement_stat_multiplier()
        exp_multiplier = self._misplacement_exp_multiplier()
        self.set_stats(
            name=str(display_name),
            stars=stars,
            stacks=stack_count,
            stackable=stack_count > 1,
            stats=stats,
            maxima=maxima,
            mismatch=(stat_multiplier < 1.0 or exp_multiplier < 1.0),
            exp_multiplier_override=(stats.exp_multiplier * exp_multiplier),
        )
