from __future__ import annotations

import math
import random

from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QTabBar
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.blessings import discover_blessing_plugins
from endless_idler.blessings.lunar_blessing import get_lunar_progress_per_tick
from endless_idler.blessings.plugin import BlessingPlugin
from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.ui.cards import IdleCharacterCard
from endless_idler.ui.components.blessing_panel import BlessingPanel
from endless_idler.ui.idle.idle_state import IdleGameState
from endless_idler.ui.idle.screen import IdleScreenWidget

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
        idle_state_provider: Callable[[], object] | None = None,
        idle_state_commit: Callable[[dict[str, object]], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._save_store = save_store
        self._idle_runtime_snapshot_provider = idle_runtime_snapshot_provider
        self._idle_state_provider = idle_state_provider
        self._idle_state_commit = idle_state_commit
        self._character_plugins = discover_character_plugins()
        self._character_plugins_by_id = {
            plugin.char_id: plugin for plugin in self._character_plugins
        }
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

        self._tabs = QTabBar()
        self._tabs.setObjectName("HomeTabs")
        self._tabs.setDocumentMode(True)
        self._tabs.setExpanding(True)
        self._tabs.addTab("Overview")
        self._tabs.addTab("Upgrades")
        self._tabs.setCurrentIndex(0)
        self._panel_layout.addWidget(self._tabs)

        self._content_stack = QStackedWidget(panel)
        self._content_stack.setObjectName("HomeContentStack")
        self._panel_layout.addWidget(self._content_stack, 1)

        self._overview_page = QWidget(self._content_stack)
        self._overview_layout = QVBoxLayout(self._overview_page)
        self._overview_layout.setContentsMargins(0, 0, 0, 0)
        self._overview_layout.setSpacing(10)
        self._content_stack.addWidget(self._overview_page)

        self._upgrade_page = QWidget(self._content_stack)
        self._upgrade_layout = QVBoxLayout(self._upgrade_page)
        self._upgrade_layout.setContentsMargins(0, 0, 0, 0)
        self._upgrade_layout.setSpacing(0)
        self._upgrade_scroll = QScrollArea(self._upgrade_page)
        self._upgrade_scroll.setObjectName("HomeUpgradeScroll")
        self._upgrade_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._upgrade_scroll.setWidgetResizable(True)
        self._upgrade_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._upgrade_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._upgrade_layout.addWidget(self._upgrade_scroll, 1)

        self._upgrade_host = QWidget(self._upgrade_scroll)
        self._upgrade_host.setObjectName("HomeUpgradeHost")
        self._upgrade_host_layout = QVBoxLayout(self._upgrade_host)
        self._upgrade_host_layout.setContentsMargins(0, 0, 0, 0)
        self._upgrade_host_layout.setSpacing(10)
        self._upgrade_host_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        self._upgrade_scroll.setWidget(self._upgrade_host)
        self._content_stack.addWidget(self._upgrade_page)

        self._tabs.currentChanged.connect(self._on_tab_changed)

        self._blessing_panels: dict[str, BlessingPanel] = {}
        self._create_blessing_panels()
        self._overview_layout.addStretch(1)
        self._upgrade_cards: list[IdleCharacterCard] = []
        self._upgrade_lineup_signature: (
            tuple[
                tuple[str, ...],
                tuple[str, ...],
                tuple[str, ...],
                tuple[tuple[str, int], ...],
                int,
            ]
            | None
        ) = None
        self._rebuild_upgrade_cards()

        self._update_timer = QTimer(self)
        self._update_timer.setInterval(33)
        self._update_timer.timeout.connect(self._update_home_display)
        self._update_timer.start()
        self._update_home_display()

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
            self._overview_layout.addWidget(panel)

    def _current_idle_state(self) -> object | None:
        provider = self._idle_state_provider
        if provider is None:
            return None
        state = provider()
        return state if state is not None else None

    def _build_idle_state(self) -> object | None:
        state = self._current_idle_state()
        if state is not None:
            return state

        save = self._get_save()
        plugins_by_id: dict[str, object] = {
            plugin.char_id: plugin for plugin in self._character_plugins
        }
        return IdleGameState(
            char_ids=[str(item) for item in getattr(save, "onsite", []) if item],
            offsite_ids=[str(item) for item in getattr(save, "offsite", []) if item],
            standby_ids=[str(item) for item in getattr(save, "standby", []) if item],
            party_level=max(1, int(getattr(save, "party_level", 1))),
            stacks=dict(getattr(save, "stacks", {})),
            plugins_by_id=plugins_by_id,
            rng=random.Random(),
            progress_by_id=dict(getattr(save, "character_progress", {})),
            stats_by_id=dict(getattr(save, "character_stats", {})),
            initial_stats_by_id=dict(
                getattr(save, "character_initial_stats", {}) or {}
            ),
            inventory=dict(getattr(save, "inventory", {})),
            exp_bonus_seconds=float(getattr(save, "idle_exp_bonus_seconds", 0.0)),
            exp_penalty_seconds=float(getattr(save, "idle_exp_penalty_seconds", 0.0)),
            shared_exp_percentage=int(getattr(save, "idle_shared_exp_percentage", 1)),
            risk_reward_level=int(getattr(save, "idle_risk_reward_level", 0)),
            battle_start_time=float(getattr(save, "battle_start_time", 0.0)),
            blessings_data=dict(getattr(save, "blessings", {}) or {}),
            passives_data=dict(getattr(save, "passives", {}) or {}),
        )

    def _commit_idle_state(self, state: object) -> None:
        commit = self._idle_state_commit
        exporter = getattr(state, "export_runtime_snapshot", None)
        if commit is None or not callable(exporter):
            return
        snapshot = exporter()
        if not isinstance(snapshot, dict):
            return
        commit(snapshot)
        persist = getattr(self._save_store, "persist", None)
        if callable(persist):
            persist(force=True)

    def _lineup_signature(
        self,
    ) -> tuple[
        tuple[str, ...],
        tuple[str, ...],
        tuple[str, ...],
        tuple[tuple[str, int], ...],
        int,
    ]:
        return IdleScreenWidget.build_lineup_signature(self._get_save())

    def _on_tab_changed(self, index: int) -> None:
        self._content_stack.setCurrentIndex(index)

    def _clear_upgrade_cards(self) -> None:
        while self._upgrade_host_layout.count() > 0:
            item = self._upgrade_host_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self._upgrade_cards.clear()

    def _rebuild_upgrade_cards(self) -> None:
        signature = self._lineup_signature()
        if signature == self._upgrade_lineup_signature:
            return
        self._upgrade_lineup_signature = signature
        self._clear_upgrade_cards()

        state = self._build_idle_state()
        if state is None:
            placeholder = QLabel("No characters available yet.", self._upgrade_host)
            placeholder.setObjectName("HomeUpgradeEmptyState")
            placeholder.setAlignment(
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
            )
            self._upgrade_host_layout.addWidget(placeholder)
            self._upgrade_host_layout.addStretch(1)
            return

        save = self._get_save()
        seen: set[str] = set()
        onsite_ids = [str(item) for item in getattr(save, "onsite", []) if item]
        offsite_ids = [str(item) for item in getattr(save, "offsite", []) if item]
        combined_ids = [*onsite_ids, *offsite_ids]
        for char_id in combined_ids:
            if char_id in seen:
                continue
            seen.add(char_id)
            context = "onsite" if char_id in onsite_ids else "offsite"
            plugin = self._character_plugins_by_id.get(char_id)
            card = IdleCharacterCard(
                context=context,
                char_id=char_id,
                plugin=plugin,
                idle_state=state,
                idle_state_provider=self._build_idle_state,
                rng=random.Random(),
                stack_count=max(1, int(getattr(save, "stacks", {}).get(char_id, 1))),
                on_rebirth=self._rebirth_character,
                on_prestige=self._prestige_character,
                compact_view=True,
                parent=self._upgrade_host,
            )
            self._upgrade_cards.append(card)
            self._upgrade_host_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter)

        self._upgrade_host_layout.addStretch(1)

    def _update_upgrade_cards(self) -> None:
        for card in self._upgrade_cards:
            card.update_display()

    def _rebirth_character(self, char_id: str) -> None:
        state = self._build_idle_state()
        rebirth = getattr(state, "rebirth_character", None)
        if not callable(rebirth) or not rebirth(char_id):
            return
        self._commit_idle_state(state)
        self._rebuild_upgrade_cards()
        self._update_upgrade_cards()

    def _prestige_character(self, char_id: str) -> None:
        state = self._build_idle_state()
        prestige = getattr(state, "prestige_character", None)
        if not callable(prestige) or not prestige(char_id):
            return
        self._commit_idle_state(state)
        self._rebuild_upgrade_cards()
        self._update_upgrade_cards()

    def _update_home_display(self) -> None:
        self._update_blessing_display()
        self._rebuild_upgrade_cards()
        self._update_upgrade_cards()

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
                self._runtime_float(
                    runtime, "countdown_seconds", float(plugin.step_seconds)
                ),
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
