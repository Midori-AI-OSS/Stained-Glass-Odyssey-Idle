from __future__ import annotations

import math

from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QTabBar
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.blessings import discover_blessing_plugins
from endless_idler.blessings.lunar_blessing import get_lunar_progress_per_tick
from endless_idler.blessings.plugin import BlessingPlugin
from endless_idler.ui.components.blessing_panel import BlessingPanel

if TYPE_CHECKING:
    from endless_idler.save import RunSave


class SaveStoreLike(Protocol):
    current: "RunSave"


class HomePage(QWidget):
    """Decorative home shell inspired by Agents Runner dashboard chrome."""

    def __init__(
        self,
        save_store: SaveStoreLike,
        idle_runtime_snapshot_provider: Callable[[], dict[str, object]] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._save_store = save_store
        self._idle_runtime_snapshot_provider = idle_runtime_snapshot_provider
        self.setObjectName("HomePageRoot")

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
        self._update_timer.setInterval(33)
        self._update_timer.timeout.connect(self._update_blessing_display)
        self._update_timer.start()
        self._update_blessing_display()

    def _get_save(self) -> "RunSave":
        return self._save_store.current

    def _is_blessing_unlocked(self, plugin: BlessingPlugin) -> bool:
        """Check if a blessing is unlocked based on plugin and save state."""
        if not plugin.is_persistent:
            return plugin.is_unlocked

        save = self._get_save()
        blessing_data = save.blessings.get(plugin.blessing_id, {})
        if not isinstance(blessing_data, dict):
            return plugin.is_unlocked
        if "unlocked" in blessing_data:
            return bool(blessing_data.get("unlocked"))
        return plugin.is_unlocked

    def _is_session_based(self, plugin: BlessingPlugin) -> bool:
        """Check if a blessing is session-based (Odyssey's Blessing)."""
        return plugin.blessing_id == "odyssey_blessing"

    def _is_lunar_blessing(self, plugin: BlessingPlugin) -> bool:
        """Check if this is Lunar's Blessing (special dual display)."""
        return plugin.blessing_id == "lunar_blessing"

    def _runtime_snapshot(self) -> dict[str, object]:
        provider = self._idle_runtime_snapshot_provider
        if provider is None:
            return {}
        snapshot = provider()
        if not isinstance(snapshot, dict):
            return {}
        return snapshot

    def _runtime_blessing(self, blessing_id: str) -> dict[str, object]:
        snapshot = self._runtime_snapshot()
        runtime = snapshot.get("blessing_runtime")
        if not isinstance(runtime, dict):
            return {}
        blessing = runtime.get(blessing_id)
        if not isinstance(blessing, dict):
            return {}
        return blessing

    @staticmethod
    def _runtime_int(runtime: dict[str, object], key: str, default: int = 0) -> int:
        raw = runtime.get(key)
        if isinstance(raw, bool):
            return default
        if isinstance(raw, int):
            return raw
        if isinstance(raw, float):
            return int(raw)
        return default

    @staticmethod
    def _runtime_float(
        runtime: dict[str, object], key: str, default: float = 0.0
    ) -> float:
        raw = runtime.get(key)
        if isinstance(raw, bool):
            return default
        if isinstance(raw, int | float):
            return float(raw)
        return default

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
        runtime = self._runtime_blessing(plugin.blessing_id)
        if runtime:
            return max(0, self._runtime_int(runtime, "steps", 0))
        save = self._get_save()
        blessing_data = save.blessings.get(plugin.blessing_id, {})
        if not isinstance(blessing_data, dict):
            return 0
        raw_steps = blessing_data.get("steps", 0)
        if isinstance(raw_steps, bool):
            return 0
        if isinstance(raw_steps, int):
            return max(0, raw_steps)
        if isinstance(raw_steps, float):
            return max(0, int(raw_steps))
        return 0

    def _get_blessing_progress(self, plugin: BlessingPlugin) -> float:
        """Get the current progress for a blessing (0.0 to 1.0)."""
        runtime = self._runtime_blessing(plugin.blessing_id)
        if not runtime:
            return 0.0
        progress = self._runtime_float(runtime, "progress", 0.0)
        return max(0.0, min(1.0, progress))

    def _get_seconds_to_next_step(self, plugin: BlessingPlugin) -> float:
        runtime = self._runtime_blessing(plugin.blessing_id)
        if runtime:
            return max(
                0.0,
                self._runtime_float(runtime, "countdown_seconds", float(plugin.step_seconds)),
            )
        return float(plugin.step_seconds)

    def _build_tooltip(self, plugin: BlessingPlugin, steps: int) -> str:
        """Build tooltip HTML for a blessing using plugin's formatter."""
        progress = self._get_blessing_progress(plugin)
        seconds_to_next = self._get_seconds_to_next_step(plugin)
        context: dict[str, Any] = {
            "save": self._get_save(),
            "runtime": {
                "steps": max(0, int(steps)),
                "progress": max(0.0, min(1.0, float(progress))),
                "countdown_seconds": max(0, int(math.ceil(seconds_to_next))),
                "step_seconds": float(plugin.step_seconds),
            },
        }
        return plugin.format_tooltip(steps, context)

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
            seconds_to_next = self._get_seconds_to_next_step(plugin)
            shimmer = plugin.get_shimmer_intensity(seconds_to_next)
            panel.set_shimmer(shimmer)
            if self._is_lunar_blessing(plugin):
                progress_data = get_lunar_progress_per_tick(steps)
                panel.set_mod_value_dual(progress_data["display_pct"])
            elif self._is_session_based(plugin):
                panel.set_mod_value(f"x{multiplier:.4f}")
            else:
                bonus_pct = (steps * 0.0001) * 100
                panel.set_mod_value(f"+{bonus_pct:.2f}%")
            panel.set_tooltip_html(self._build_tooltip(plugin, steps))
