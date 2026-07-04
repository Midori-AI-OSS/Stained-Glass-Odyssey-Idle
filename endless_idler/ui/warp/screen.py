from __future__ import annotations

import random

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QTabBar
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.run_save_store import RunSaveStore
from endless_idler.warp.banners import BannerDefinition
from endless_idler.warp.banners import generate_banners
from endless_idler.warp.constants import BANNER_IDS
from endless_idler.warp.constants import BANNER_SHARD_MAP
from endless_idler.warp.engine import WarpEngine
from endless_idler.warp.engine import WarpOutcome


def _repolish(widget: QWidget) -> None:
    style = widget.style()
    if style is None:
        return
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


class WarpScreen(QWidget):
    """Warp (gacha pull) screen with banner tabs, detail panel, and pull button."""

    _BANNER_LABELS: dict[str, str] = {
        "fire": "Fire",
        "ice": "Ice",
        "wind": "Wind",
        "lightning": "Lightning",
        "light": "Light",
        "dark": "Dark",
        "yolo": "YOLO",
    }

    def __init__(
        self,
        *,
        save_store: RunSaveStore,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._save_store: RunSaveStore = save_store
        self.setObjectName("WarpScreenRoot")
        self._plugins: list[CharacterPlugin] = discover_character_plugins()
        self._banners: dict[str, BannerDefinition] = generate_banners(self._plugins)
        self._selected_banner_id: str = ""
        self._last_outcome: WarpOutcome | None = None
        self._last_outcome_banner_id: str = ""
        self._last_error: str = ""
        self._rng: random.Random = random.Random()

        self._tab_bar: QTabBar
        self._banner_name_label: QLabel
        self._pool_label: QLabel
        self._cost_label: QLabel
        self._balance_label: QLabel
        self._pity_label: QLabel
        self._pull_total_label: QLabel
        self._last_rarity_label: QLabel
        self._pull_button: QPushButton
        self._result_label: QLabel
        self._history_label: QLabel
        self._yolo_prefs_panel: QFrame
        self._yolo_pref_buttons: dict[str, QPushButton] = {}

        self._build_ui()

    def refresh_display(self) -> None:
        """Refresh screen labels from the current save state."""
        self._refresh_display()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self._tab_bar = QTabBar(self)
        self._tab_bar.setDocumentMode(True)
        self._tab_bar.setExpanding(True)
        for banner_id in BANNER_IDS:
            _ = self._tab_bar.addTab(
                self._BANNER_LABELS.get(banner_id, banner_id.title())
            )
        root.addWidget(self._tab_bar, 0)

        root.addWidget(self._build_banner_panel(), 0)

        root.addWidget(self._build_pull_section(), 0)

        root.addWidget(self._build_result_panel(), 1)

        self._yolo_prefs_panel = self._build_yolo_prefs_panel()
        self._yolo_prefs_panel.setVisible(False)
        root.addWidget(self._yolo_prefs_panel, 0)

        _ = self._tab_bar.currentChanged.connect(self._on_banner_selected)
        self._refresh_tab_enabled_states()
        initial_index = self._initial_banner_index()
        self._tab_bar.setCurrentIndex(initial_index)
        self._on_banner_selected(initial_index)

    def _build_banner_panel(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("WarpBannerPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self._banner_name_label = QLabel("Warp Banner", panel)
        self._banner_name_label.setWordWrap(True)
        layout.addWidget(self._banner_name_label, 0)

        self._pool_label = QLabel("Pool: (empty)", panel)
        self._pool_label.setWordWrap(True)
        layout.addWidget(self._pool_label, 0)

        self._pity_label = QLabel("Pity: 0", panel)
        layout.addWidget(self._pity_label, 0)

        self._pull_total_label = QLabel("Total Pulls: 0", panel)
        layout.addWidget(self._pull_total_label, 0)

        self._last_rarity_label = QLabel("Last: —", panel)
        layout.addWidget(self._last_rarity_label, 0)

        return panel

    def _build_pull_section(self) -> QFrame:
        section = QFrame(self)
        section.setObjectName("WarpPullSection")

        layout = QVBoxLayout(section)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self._cost_label = QLabel("Cost: 160 Shards", section)
        self._cost_label.setObjectName("WarpCostLabel")
        self._cost_label.setWordWrap(True)
        layout.addWidget(self._cost_label, 0)

        self._balance_label = QLabel("Your balance: 0", section)
        self._balance_label.setObjectName("WarpBalanceLabel")
        self._balance_label.setWordWrap(True)
        layout.addWidget(self._balance_label, 0)

        self._pull_button = QPushButton("Pull — 160 Shards", section)
        self._pull_button.setObjectName("WarpPullButton")
        _ = self._pull_button.clicked.connect(self._on_pull)
        layout.addWidget(self._pull_button, 0)

        return section

    def _build_result_panel(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("WarpResultPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self._result_label = QLabel("No pulls yet", panel)
        self._result_label.setWordWrap(True)
        self._result_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        layout.addWidget(self._result_label, 0)

        self._history_label = QLabel("Recent: No characters obtained yet", panel)
        self._history_label.setWordWrap(True)
        self._history_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        layout.addWidget(self._history_label, 0)
        layout.addStretch(1)

        return panel

    def _build_yolo_prefs_panel(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("WarpYoloPrefsPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("YOLO Shard Preferences", panel)
        header.setObjectName("WarpYoloPrefsHeader")
        layout.addWidget(header)

        hint = QLabel(
            "Select up to 3 preferred shard types for YOLO pulls. "
            + "Preferred types are deducted first.",
            panel,
        )
        hint.setObjectName("WarpYoloPrefsHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)
        layout.addLayout(buttons_row)

        self._yolo_pref_buttons = {}
        damage_types = ["fire", "ice", "wind", "lightning", "light", "dark"]

        for dt in damage_types:
            btn = QPushButton(dt.capitalize(), panel)
            btn.setObjectName("WarpYoloPrefButton")
            btn.setCheckable(True)
            _ = btn.setProperty("damageType", dt)
            _ = btn.clicked.connect(
                lambda checked, t=dt: self._on_yolo_pref_toggled(t, checked)
            )
            buttons_row.addWidget(btn)
            self._yolo_pref_buttons[dt] = btn

        buttons_row.addStretch(1)
        layout.addStretch(1)
        return panel

    def _on_yolo_pref_toggled(self, damage_type: str, checked: bool) -> None:
        save = self._save_store.current
        prefs = list(save.warp_yolo_preferences or [])

        if checked:
            if damage_type not in prefs:
                prefs.append(damage_type)
        else:
            if damage_type in prefs:
                prefs.remove(damage_type)

        # Enforce max 3: if user selects a 4th, deselect the first selected
        if len(prefs) > 3:
            removed = prefs.pop(0)
            btn = self._yolo_pref_buttons.get(removed)
            if btn is not None:
                _ = btn.blockSignals(True)
                btn.setChecked(False)
                _ = btn.blockSignals(False)

        save.warp_yolo_preferences = prefs
        self._save_store.persist()

    def _on_banner_selected(self, index: int) -> None:
        if index < 0 or index >= len(BANNER_IDS):
            return
        banner_id = BANNER_IDS[index]
        self._selected_banner_id = banner_id

        # Show YOLO prefs panel only when YOLO tab is selected
        is_yolo = banner_id == "yolo"
        self._yolo_prefs_panel.setVisible(is_yolo)
        if is_yolo:
            self._restore_yolo_pref_buttons()

        self._refresh_tab_enabled_states()
        self._refresh_display()

    def _restore_yolo_pref_buttons(self) -> None:
        """Read save.warp_yolo_preferences and update toggle button states."""
        save = self._save_store.current
        prefs = set(save.warp_yolo_preferences or [])
        for dt, btn in self._yolo_pref_buttons.items():
            _ = btn.blockSignals(True)
            btn.setChecked(dt in prefs)
            _ = btn.blockSignals(False)

    def _on_pull(self) -> None:
        if not self._selected_banner_id:
            return

        banner_id = self._selected_banner_id
        engine = self._build_engine()
        self._last_error = ""
        try:
            outcome = engine.pull()
        except ValueError as exc:
            self._last_outcome = None
            self._last_outcome_banner_id = banner_id
            self._last_error = str(exc)
            self._refresh_display()
            return

        self._last_outcome = outcome
        self._last_outcome_banner_id = banner_id
        self._save_store.persist(force=True)
        self._refresh_display()

    def _build_engine(self) -> WarpEngine:
        save = self._save_store.current
        banner = self._banners[self._selected_banner_id]
        return WarpEngine(save, self._selected_banner_id, banner, rng=self._rng)

    def _refresh_display(self) -> None:
        if not self._selected_banner_id:
            return

        banner_id = self._selected_banner_id
        banner = self._banners[banner_id]
        save = self._save_store.current
        has_pool = self._banner_has_pool(banner)
        shard_label = self._shard_label_for_banner(banner_id)
        cost = WarpEngine.get_cost()
        engine = self._build_engine()
        affordable = engine.can_afford()
        balance = self._shard_balance_for_banner(banner_id)

        banner_label = self._BANNER_LABELS.get(banner_id, banner_id.title())
        self._banner_name_label.setText(f"{banner_label} Banner")
        self._pool_label.setText(self._pool_summary_for_banner(banner))

        # Cost label — prominent, with YOLO suffix
        if banner_id == "yolo":
            self._cost_label.setText(f"Cost: {cost} Shards (your choice)")
        else:
            self._cost_label.setText(f"Cost: {cost} {shard_label}")

        # Balance label — YOLO shows count only
        if banner_id == "yolo":
            self._balance_label.setText(f"Your balance: {balance}")
        else:
            self._balance_label.setText(f"Your balance: {balance} {shard_label}")

        self._pity_label.setText(f"Pity: {save.warp_pity.get(banner_id, 0)}")
        self._pull_total_label.setText(
            f"Total Pulls: {save.warp_pull_total.get(banner_id, 0)}"
        )
        last_rarity = self._format_rarity(save.warp_last_rarity.get(banner_id))
        self._last_rarity_label.setText(f"Last: {last_rarity}")

        # Pull button
        if affordable and has_pool:
            pull_label = self._shard_label_for_banner(banner_id)
            self._pull_button.setText(f"Pull — {cost} {pull_label}")
            self._pull_button.setEnabled(True)
        else:
            self._pull_button.setText("Not enough shards")
            self._pull_button.setEnabled(False)

        # Dynamic affordability styling
        affordability = "affordable" if affordable else "insufficient"
        self._cost_label.setProperty("affordability", affordability)
        self._balance_label.setProperty("affordability", affordability)
        _repolish(self._cost_label)
        _repolish(self._balance_label)

        self._refresh_result_panel(banner_id)

    def _refresh_result_panel(self, banner_id: str) -> None:
        save = self._save_store.current
        recent = save.warp_character_obtained.get(banner_id, [])[-5:]

        if self._last_error and self._last_outcome_banner_id == banner_id:
            self._result_label.setText(f"Pull failed: {self._last_error}")
        elif self._last_outcome_banner_id == banner_id and self._last_outcome:
            self._result_label.setText(self._format_outcome(self._last_outcome))
        elif recent:
            rarity = self._format_rarity(save.warp_last_rarity.get(banner_id))
            self._result_label.setText(f"Last obtained: {recent[-1]} — {rarity}")
        else:
            self._result_label.setText("No pulls yet")

        if recent:
            self._history_label.setText(f"Recent: {', '.join(recent)}")
        else:
            self._history_label.setText("Recent: No characters obtained yet")

    def _refresh_tab_enabled_states(self) -> None:
        for index, banner_id in enumerate(BANNER_IDS):
            banner = self._banners[banner_id]
            has_pool = self._banner_has_pool(banner)
            self._tab_bar.setTabEnabled(index, has_pool)
            if has_pool:
                self._tab_bar.setTabToolTip(index, "")
            else:
                self._tab_bar.setTabToolTip(index, "This banner has no characters yet.")

    def _initial_banner_index(self) -> int:
        for index, banner_id in enumerate(BANNER_IDS):
            if self._banner_has_pool(self._banners[banner_id]):
                return index
        return 0

    def _shard_label_for_banner(self, banner_id: str) -> str:
        if banner_id == "yolo":
            return "Any Shards"

        shard_id = BANNER_SHARD_MAP.get(banner_id)
        if shard_id is None:
            return "Shards"
        damage_type_id = shard_id.removesuffix("_shard")
        label = self._BANNER_LABELS.get(damage_type_id, damage_type_id.title())
        return f"{label} Shards"

    def _shard_balance_for_banner(self, banner_id: str) -> int:
        inventory = self._save_store.current.inventory
        if banner_id == "yolo":
            return sum(inventory.get(shard_id, 0) for shard_id in BANNER_SHARD_MAP.values())

        shard_id = BANNER_SHARD_MAP.get(banner_id)
        if shard_id is None:
            return 0
        return inventory.get(shard_id, 0)

    @staticmethod
    def _banner_has_pool(banner: BannerDefinition) -> bool:
        return bool(banner.five_star_pool or banner.six_star_pool)

    @staticmethod
    def _pool_summary_for_banner(banner: BannerDefinition) -> str:
        five_count = len(banner.five_star_pool)
        six_count = len(banner.six_star_pool)
        if five_count <= 0 and six_count <= 0:
            return "Pool: (empty)"
        return f"5★: {five_count} characters, 6★: {six_count} characters"

    @staticmethod
    def _format_rarity(rarity: int | None) -> str:
        if rarity is None:
            return "—"
        return f"★{rarity}"

    @classmethod
    def _format_outcome(cls, outcome: WarpOutcome) -> str:
        rarity = cls._format_rarity(outcome.rarity)
        if outcome.character_id is None:
            return f"No character obtained — {rarity}"
        return f"{outcome.character_id} — {rarity}"
