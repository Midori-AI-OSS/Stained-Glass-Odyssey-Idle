from __future__ import annotations

import math
import time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QTabBar
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.blessings import get_default_blessing
from endless_idler.blessings.plugin import BlessingPlugin
from endless_idler.ui.components.blessing_panel import BlessingPanel


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
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.setSpacing(10)
        root.addWidget(panel, 1)

        tabs = QTabBar()
        tabs.setObjectName("HomeTabs")
        tabs.setDocumentMode(True)
        tabs.setExpanding(True)
        tabs.addTab("Overview")
        tabs.addTab("Upgrades")
        tabs.setCurrentIndex(0)
        panel_layout.addWidget(tabs)

        self._blessing_panel = BlessingPanel()
        self._blessing_panel.set_blessing_name("Odyssey's Blessing")
        self._blessing_panel.set_mod_value("x1.0000")
        self._blessing_panel.set_tooltip_html(self._build_blessing_tooltip())
        panel_layout.addWidget(self._blessing_panel)

        panel_layout.addStretch(1)

        self._update_timer = QTimer(self)
        self._update_timer.setInterval(1000)
        self._update_timer.timeout.connect(self._update_blessing_display)
        self._update_timer.start()
        self._update_blessing_display()

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

    def _build_blessing_tooltip(self) -> str:
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

        self._blessing_panel.set_current_progress(cycle_progress)
        self._blessing_panel.set_mod_value(f"x{multiplier:.4f}")
        self._blessing_panel.set_tooltip_html(self._build_blessing_tooltip())

        self._last_step_count = steps
