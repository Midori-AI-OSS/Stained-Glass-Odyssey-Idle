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
from endless_idler.blessings.lunar_blessing import get_lunar_progress_per_tick
from endless_idler.blessings.lunar_blessing import LUNAR_STEP_SECONDS
from endless_idler.blessings.lunar_blessing import LUNAR_WEEK_SECONDS
from endless_idler.blessings.plugin import BlessingPlugin
from endless_idler.run_save_store import RunSaveStore
from endless_idler.ui.components.blessing_panel import BlessingPanel

if TYPE_CHECKING:
    from endless_idler.save import RunSave


class HomePage(QWidget):
    """Decorative home shell inspired by Agents Runner dashboard chrome."""

    def __init__(self, save_store: RunSaveStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._save_store = save_store
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

        self._blessing_panels: dict[str, BlessingPanel] = {}
        self._create_blessing_panels()

        self._panel_layout.addStretch(1)

        self._update_timer = QTimer(self)
        self._update_timer.setInterval(1000)
        self._update_timer.timeout.connect(self._update_blessing_display)
        self._update_timer.start()
        self._update_blessing_display()

    def _get_save(self) -> "RunSave":
        return self._save_store.current

    def _is_blessing_unlocked(self, plugin: BlessingPlugin) -> bool:
        """Check if a blessing is unlocked based on plugin and save state."""
        if not plugin.is_unlocked:
            return False
        save = self._get_save()
        if plugin.target_damage_type is not None:
            blessing_data = save.blessings.get(plugin.target_damage_type, {})
            return blessing_data.get("unlocked", False)
        return True

    def _is_session_based(self, plugin: BlessingPlugin) -> bool:
        """Check if a blessing is session-based (Odyssey's Blessing)."""
        return plugin.blessing_id == "odyssey_blessing"

    def _is_lunar_blessing(self, plugin: BlessingPlugin) -> bool:
        """Check if this is Lunar's Blessing (special dual display)."""
        return plugin.blessing_id == "lunar_blessing"

    def _create_blessing_panels(self) -> None:
        """Create blessing panels dynamically from discovered plugins."""
        all_blessings = discover_blessing_plugins()
        for plugin in all_blessings:
            if not self._is_blessing_unlocked(plugin):
                continue
            panel = BlessingPanel()
            panel.set_blessing_name(plugin.display_name)
            panel.set_tooltip_html(plugin.description)
            if plugin.target_damage_type is not None:
                panel.set_color_id(plugin.target_damage_type)
            elif self._is_lunar_blessing(plugin):
                panel.set_color_id("lunar")
            self._blessing_panels[plugin.blessing_id] = panel
            self._panel_layout.addWidget(panel)

    def _get_blessing_steps(self, plugin: BlessingPlugin) -> int:
        """Get the current step count for a blessing."""
        if self._is_session_based(plugin):
            elapsed = self._elapsed_seconds()
            return max(0, int(elapsed // plugin.step_seconds))
        else:
            save = self._get_save()
            if plugin.target_damage_type is not None:
                blessing_data = save.blessings.get(plugin.blessing_id, {})
            else:
                blessing_data = save.blessings.get(plugin.blessing_id, {})
            return blessing_data.get("steps", 0)

    def _get_blessing_progress(self, plugin: BlessingPlugin) -> float:
        """Get the current progress for a blessing (0.0 to 1.0)."""
        if self._is_session_based(plugin):
            elapsed = self._elapsed_seconds()
            phase = elapsed % plugin.step_seconds
            return max(0.0, min(1.0, phase / plugin.step_seconds))
        else:
            save = self._get_save()
            blessing_data = save.blessings.get(plugin.blessing_id, {})
            step_start_time = blessing_data.get("step_start_time", 0.0)
            current_time = time.time()
            elapsed_in_step = current_time - step_start_time
            progress = elapsed_in_step / plugin.step_seconds
            return max(0.0, min(1.0, progress))

    def _build_tooltip(self, plugin: BlessingPlugin, steps: int) -> str:
        """Build tooltip HTML for a blessing."""
        if self._is_session_based(plugin):
            return self._build_odyssey_tooltip()
        elif self._is_lunar_blessing(plugin):
            progress_data = get_lunar_progress_per_tick(steps)
            return self._build_lunar_tooltip(steps, progress_data)
        else:
            return self._build_damage_tooltip(plugin, steps)

    def _build_damage_tooltip(self, plugin: BlessingPlugin, steps: int) -> str:
        """Build tooltip for damage-type blessings."""
        bonus_pct = (steps * 0.0001) * 100
        time_to_next = int(plugin.step_seconds)
        return (
            f"<b>{plugin.display_name}</b><br>"
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
        seconds_to_next = self._get_seconds_to_next_step()
        return (
            "<b>Odyssey's Blessing</b><br>"
            f"Current: <b>x{multiplier:.4f}</b><br>"
            f"Next blessing in: <b>{self._format_seconds(seconds_to_next)}</b><br><br>"
            f"+{(1.025 ** (1.0 / 6.0) - 1.0) * 100.0:.3f}% every 5 minutes."
        )

    def _build_lunar_tooltip(self, steps: int, progress_data: dict[str, float]) -> str:
        exp_gain = progress_data["exp_gain_pct"]
        exp_reduction = progress_data["exp_reduction_pct"]
        weeks = progress_data["progress_weeks"]
        minutes_to_next = LUNAR_STEP_SECONDS / 60.0
        total_minutes = steps * minutes_to_next
        minutes_into_week = total_minutes % (LUNAR_WEEK_SECONDS / 60.0)
        minutes_remaining = (LUNAR_WEEK_SECONDS / 60.0) - minutes_into_week
        return (
            "<b>Lunar's Blessing</b><br>"
            f"<b>+{exp_gain:.1f}%</b> experience gained<br>"
            f"<b>-{exp_reduction:.1f}%</b> experience needed per level<br><br>"
            f"Progress: <b>{weeks:.2f}</b> weeks<br>"
            f"Next step in: <b>{self._format_seconds(int(minutes_remaining * 60))}</b><br><br>"
            f"Each week grants +1% exp gain and -1% exp needed. "
            f"After 50%, diminishing returns apply (each 10% requires 2x time)."
        )

    def _update_blessing_display(self) -> None:
        """Update all blessing panels with current state."""
        all_blessings = discover_blessing_plugins()
        for plugin in all_blessings:
            if not self._is_blessing_unlocked(plugin):
                continue
            panel = self._blessing_panels.get(plugin.blessing_id)
            if panel is None:
                continue
            steps = self._get_blessing_steps(plugin)
            progress = self._get_blessing_progress(plugin)
            multiplier = plugin.get_multiplier(steps)
            panel.set_current_progress(progress)
            if self._is_lunar_blessing(plugin):
                progress_data = get_lunar_progress_per_tick(steps)
                panel.set_mod_value_dual(progress_data["display_pct"])
            elif self._is_session_based(plugin):
                panel.set_mod_value(f"x{multiplier:.4f}")
            else:
                bonus_pct = (steps * 0.0001) * 100
                panel.set_mod_value(f"+{bonus_pct:.2f}%")
            panel.set_tooltip_html(self._build_tooltip(plugin, steps))
        self._last_step_count = self._get_step_count()
