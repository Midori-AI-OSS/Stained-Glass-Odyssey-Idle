from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QTabBar
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.blessings import discover_blessing_plugins
from endless_idler.blessings import get_default_blessing
from endless_idler.blessings.plugin import BlessingPlugin
from endless_idler.ui.components.blessing_panel import BlessingPanel
from endless_idler.ui.stores import get_save_store

if TYPE_CHECKING:
    from endless_idler.save import RunSave


class HomePage(QWidget):
    """Decorative home shell inspired by Agents Runner dashboard chrome."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HomePageRoot")

        self._home_session_started_at = time.time()
        self._last_step_count = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        panel = QFrame(self)
        panel.setObjectName("HomePanel")
        self._panel_layout = QVBoxLayout(panel)
        self._panel_layout.setContentsMargins(12, 12, 12, 12)
        self._panel_layout.setSpacing(10)
        root.addWidget(panel, 1)

        tabs = QTabBar()
        tabs.setObjectName("HomeTabs")
        tabs.setDocumentMode(True)
        tabs.setExpanding(True)
        tabs.addTab("Overview")
        tabs.addTab("Upgrades")
        tabs.setCurrentIndex(0)
        self._panel_layout.addWidget(tabs)

        self._odyssey_panel = BlessingPanel()
        self._odyssey_panel.set_blessing_name("Odyssey's Blessing")
        self._odyssey_panel.set_mod_value("x1.0000")
        self._odyssey_panel.set_tooltip_html(self._build_odyssey_tooltip())
        self._panel_layout.addWidget(self._odyssey_panel)

        self._damage_blessings: list[BlessingPlugin] = []
        self._blessing_panels: dict[str, BlessingPanel] = {}
        self._create_damage_blessing_panels()

        self._panel_layout.addStretch(1)

        self._update_timer = QTimer(self)
        self._update_timer.setInterval(1000)
        self._update_timer.timeout.connect(self._update_blessing_display)
        self._update_timer.start()
        self._update_blessing_display()

    def _get_save(self) -> "RunSave":
        return get_save_store().current

    def _create_damage_blessing_panels(self) -> None:
        all_blessings = discover_blessing_plugins()
        damage_blessings = [
            b for b in all_blessings if b.target_damage_type is not None
        ]
        self._damage_blessings = damage_blessings
        save = self._get_save()
        for blessing in damage_blessings:
            blessing_id = blessing.blessing_id
            damage_type = blessing.target_damage_type
            if damage_type is None:
                continue
            blessing_data = save.blessings.get(damage_type, {})
            if not blessing_data.get("unlocked", False):
                continue
            panel = BlessingPanel()
            panel.set_blessing_name(blessing.display_name)
            panel.set_color_id(damage_type)
            self._blessing_panels[blessing_id] = panel
            self._panel_layout.addWidget(panel)

    def _update_damage_panels(self) -> None:
        save = self._get_save()
        for blessing in self._damage_blessings:
            blessing_id = blessing.blessing_id
            damage_type = blessing.target_damage_type
            if damage_type is None:
                continue
            panel = self._blessing_panels.get(blessing_id)
            if panel is None:
                continue
            blessing_data = save.blessings.get(damage_type, {})
            steps = blessing_data.get("steps", 0)
            max_steps = blessing.max_steps or 12
            progress = min(1.0, steps / max_steps) if max_steps > 0 else 0.0
            bonus_pct = (steps * 0.0001) * 100
            panel.set_current_progress(progress)
            panel.set_mod_value(f"+{bonus_pct:.2f}%")
            panel.set_tooltip_html(
                self._build_damage_tooltip(blessing, steps, bonus_pct, max_steps)
            )

    def _build_damage_tooltip(
        self,
        blessing: BlessingPlugin,
        steps: int,
        bonus_pct: float,
        max_steps: int,
    ) -> str:
        time_to_next = int(blessing.step_seconds)
        return (
            f"<b>{blessing.display_name}</b><br>"
            f"Steps: <b>{steps}</b> / {max_steps}<br>"
            f"Current Bonus: <b>+{bonus_pct:.2f}%</b><br>"
            f"Time to next step: <b>{self._format_seconds(time_to_next)}</b>"
        )

    def _blessing(self) -> BlessingPlugin:
        return get_default_blessing()

    def _elapsed_seconds(self) -> float:
        now = time.time()
        return max(0.0, now - self._home_session_started_at)

    def _get_step_count(self) -> int:
        elapsed = self._elapsed_seconds()
        blessing = self._blessing()
        return max(0, int(elapsed // blessing.step_seconds))

    def _get_multiplier(self) -> float:
        steps = self._get_step_count()
        blessing = self._blessing()
        return blessing.get_multiplier(steps)

    def _get_cycle_progress(self) -> float:
        elapsed = self._elapsed_seconds()
        blessing = self._blessing()
        phase = elapsed % blessing.step_seconds
        return max(0.0, min(1.0, phase / blessing.step_seconds))

    def _get_seconds_to_next_step(self) -> int:
        elapsed = self._elapsed_seconds()
        blessing = self._blessing()
        phase = elapsed % blessing.step_seconds
        remaining = blessing.step_seconds - phase
        if remaining <= 1e-9:
            remaining = blessing.step_seconds
        return max(0, int(math.ceil(remaining)))

    def _format_seconds(self, seconds: int) -> str:
        value = max(0, int(seconds))
        minutes = value // 60
        remainder = value % 60
        return f"{minutes:02d}:{remainder:02d}"

    def _build_odyssey_tooltip(self) -> str:
        multiplier = self._get_multiplier()
        steps = self._get_step_count()
        seconds_to_next = self._get_seconds_to_next_step()
        return (
            "<b>Odyssey's Blessing</b><br>"
            f"Current: <b>x{multiplier:.4f}</b><br>"
            f"Stacks gained: <b>{max(0, int(steps))}</b><br>"
            f"Next blessing in: <b>{self._format_seconds(seconds_to_next)}</b><br><br>"
            f"+{(1.025 ** (1.0 / 6.0) - 1.0) * 100.0:.3f}% every 5 minutes."
        )

    def _update_blessing_display(self) -> None:
        steps = self._get_step_count()
        cycle_progress = self._get_cycle_progress()
        multiplier = self._get_multiplier()

        self._odyssey_panel.set_current_progress(cycle_progress)
        self._odyssey_panel.set_mod_value(f"x{multiplier:.4f}")
        self._odyssey_panel.set_tooltip_html(self._build_odyssey_tooltip())

        self._update_damage_panels()

        self._last_step_count = steps
