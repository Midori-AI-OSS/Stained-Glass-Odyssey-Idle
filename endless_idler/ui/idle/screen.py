from __future__ import annotations

import random

from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QFrame

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.combat.party_stats import apply_offsite_stat_share
from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.combat.stats import Stats
from endless_idler.run_rules import apply_idle_party_heal
from endless_idler.run_rules import start_idle_heal_timer
from endless_idler.save import OFFSITE_SLOTS
from endless_idler.save import ONSITE_SLOTS
from endless_idler.save import RunSave
from endless_idler.save import SaveManager
from endless_idler.ui.idle.widgets import IdleArena
from endless_idler.ui.idle.widgets import IdleOffsiteCard
from endless_idler.ui.idle.idle_state import IDLE_TICK_INTERVAL_SECONDS
from endless_idler.ui.idle.idle_state import IdleGameState
from endless_idler.ui.onsite import IdleOnsiteCharacterCard
from endless_idler.ui.onsite import compute_stat_maxima
from endless_idler.ui.party_hp_bar import PartyHpHeader


class IdleScreenWidget(QWidget):
    finished = Signal()

    def __init__(self, *, payload: object, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("idleScreen")

        data = payload if isinstance(payload, dict) else {}
        party_level = int(data.get("party_level", 1) or 1)
        onsite_raw = data.get("onsite", [])
        offsite_raw = data.get("offsite", [])
        stacks_raw = data.get("stacks", {})

        onsite = [str(item) for item in onsite_raw if item]
        offsite = [str(item) for item in offsite_raw if item]
        stacks: dict[str, int] = {}
        if isinstance(stacks_raw, dict):
            for key, value in stacks_raw.items():
                if not isinstance(key, str):
                    continue
                try:
                    stacks[key] = max(1, int(value))
                except (TypeError, ValueError):
                    continue

        self._rng = random.Random()
        self._party_level = max(1, party_level)
        self._stacks = stacks
        self._onsite_ids = list(onsite)
        self._offsite_ids = list(offsite)
        self._save_manager = SaveManager()
        self._save = self._save_manager.load()
        if self._save is None:
            self._save = RunSave(
                party_level=self._party_level,
                onsite=[str(item) if item else None for item in list(onsite_raw)[:ONSITE_SLOTS]],
                offsite=[str(item) if item else None for item in list(offsite_raw)[:OFFSITE_SLOTS]],
                stacks=dict(self._stacks),
            )
            start_idle_heal_timer(self._save)
            self._save_manager.save(self._save)
        else:
            start_idle_heal_timer(self._save)
            self._save_manager.save(self._save)

        self._plugins = discover_character_plugins()
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}

        self._idle_state = IdleGameState(
            char_ids=onsite,
            offsite_ids=offsite,
            party_level=self._party_level,
            stacks=self._stacks,
            plugins_by_id=self._plugin_by_id,
            rng=self._rng,
            progress_by_id=dict(self._save.character_progress),
            stats_by_id=dict(self._save.character_stats),
            initial_stats_by_id=dict(getattr(self._save, "character_initial_stats", {}) or {}),
            exp_bonus_seconds=float(self._save.idle_exp_bonus_seconds),
            exp_penalty_seconds=float(self._save.idle_exp_penalty_seconds),
            shared_exp_percentage=int(getattr(self._save, "idle_shared_exp_percentage", 0)),
            risk_reward_level=int(getattr(self._save, "idle_risk_reward_level", 0)),
        )

        self._onsite_cards: list[IdleOnsiteCharacterCard] = []
        self._offsite_cards: list[IdleOffsiteCard] = []

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        self.setLayout(root)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        root.addLayout(header)

        back = QPushButton("Back")
        back.setObjectName("battleBackButton")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(self._finish)
        header.addWidget(back, 0, Qt.AlignmentFlag.AlignLeft)

        header.addStretch(1)
        title = QLabel("Idle Mode")
        title.setObjectName("battleTitle")
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        header.addStretch(1)

        party_hp = PartyHpHeader()
        party_hp.set_hp(
            current=int(getattr(self._save, "party_hp_current", 0)),
            max_hp=int(getattr(self._save, "party_hp_max", 0)),
        )
        header.addWidget(party_hp, 0, Qt.AlignmentFlag.AlignVCenter)
        self._party_hp_header = party_hp

        arena = IdleArena()
        self._arena = arena

        arena_layout = QGridLayout()
        arena_layout.setContentsMargins(12, 12, 12, 12)
        arena_layout.setHorizontalSpacing(14)
        arena_layout.setVerticalSpacing(10)
        arena.setLayout(arena_layout)
        root.addWidget(arena, 1)

        left = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        left.setLayout(left_layout)
        left_layout.addStretch(1)

        for char_id in onsite:
            plugin = self._plugin_by_id.get(char_id)
            if not plugin:
                continue

            stack_count = int(self._stacks.get(char_id, 1))
            card = IdleOnsiteCharacterCard(
                char_id=char_id,
                plugin=plugin,
                idle_state=self._idle_state,
                rng=self._rng,
                stack_count=stack_count,
                on_rebirth=self._rebirth_character,
            )
            self._onsite_cards.append(card)
            left_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignVCenter)

        left_layout.addStretch(1)

        reserves_panel = QWidget()
        reserves_layout = QVBoxLayout()
        reserves_layout.setContentsMargins(0, 0, 0, 0)
        reserves_layout.setSpacing(10)
        reserves_panel.setLayout(reserves_layout)
        reserves_layout.addStretch(1)

        for char_id in offsite:
            plugin = self._plugin_by_id.get(char_id)
            if not plugin:
                continue

            stack_count = int(self._stacks.get(char_id, 1))
            card = IdleOffsiteCard(
                char_id=char_id,
                plugin=plugin,
                idle_state=self._idle_state,
                rng=self._rng,
                stack_count=stack_count,
                on_rebirth=self._rebirth_character,
            )
            self._offsite_cards.append(card)
            reserves_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignVCenter)
        reserves_layout.addStretch(1)

        left_side = QWidget()
        left_side_layout = QHBoxLayout()
        left_side_layout.setContentsMargins(0, 0, 0, 0)
        left_side_layout.setSpacing(12)
        left_side.setLayout(left_side_layout)
        if offsite:
            left_side_layout.addWidget(reserves_panel, 0, Qt.AlignmentFlag.AlignVCenter)
        left_side_layout.addWidget(left, 0, Qt.AlignmentFlag.AlignVCenter)

        right_panel = self._make_mods_panel()

        arena_layout.addWidget(left_side, 0, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        arena_layout.addWidget(QWidget(), 0, 1, 1, 1)
        arena_layout.addWidget(right_panel, 0, 2, 1, 1, Qt.AlignmentFlag.AlignTop)
        arena_layout.setColumnStretch(0, 0)
        arena_layout.setColumnStretch(1, 1)
        arena_layout.setColumnStretch(2, 0)

        self._update_mods_ui()

        self._idle_state.tick_update.connect(self._on_tick)
        self._idle_timer = QTimer(self)
        self._idle_timer.timeout.connect(self._idle_state.process_tick)
        self._idle_timer.start(int(max(1, IDLE_TICK_INTERVAL_SECONDS * 1000)))

        self._autosave_timer = QTimer(self)
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start(5000)  # Auto-save every 5 seconds

    def _refresh_party_hp(self) -> None:
        if getattr(self, "_party_hp_header", None) is None:
            return
        self._party_hp_header.set_hp(
            current=int(getattr(self._save, "party_hp_current", 0)),
            max_hp=int(getattr(self._save, "party_hp_max", 0)),
        )

    def _make_mods_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("idleModsPanel")
        panel.setFixedWidth(220)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        panel.setLayout(layout)

        mods_title = QLabel("MODS")
        mods_title.setObjectName("idleModsTitle")
        layout.addWidget(mods_title)

        shared_exp_label = QLabel("Shared EXP: 0%")
        shared_exp_label.setObjectName("idleSharedExpLabel")
        layout.addWidget(shared_exp_label)
        self._shared_exp_label = shared_exp_label

        self._shared_exp_slider = QSlider(Qt.Orientation.Horizontal)
        self._shared_exp_slider.setObjectName("idleSharedExpSlider")
        self._shared_exp_slider.setMinimum(0)
        self._shared_exp_slider.setMaximum(95)
        self._shared_exp_slider.setValue(0)
        self._shared_exp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._shared_exp_slider.setTickInterval(10)
        self._shared_exp_slider.valueChanged.connect(self._on_shared_exp_changed)
        layout.addWidget(self._shared_exp_slider)

        shared_help = QLabel("Onsite chars lose X%, offsite gain that + 1% per onsite")
        shared_help.setObjectName("idleModsHelp")
        shared_help.setWordWrap(True)
        layout.addWidget(shared_help)

        layout.addSpacing(8)

        rr_label = QLabel("Risk & Reward: 0")
        rr_label.setObjectName("idleRRLabel")
        layout.addWidget(rr_label)
        self._rr_label = rr_label

        self._rr_slider = QSlider(Qt.Orientation.Horizontal)
        self._rr_slider.setObjectName("idleRRSlider")
        self._rr_slider.setMinimum(0)
        self._rr_slider.setMaximum(150)
        self._rr_slider.setValue(0)
        self._rr_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._rr_slider.setTickInterval(25)
        self._rr_slider.valueChanged.connect(self._on_risk_reward_changed)
        layout.addWidget(self._rr_slider)

        rr_help = QLabel("Boost: (Lvl+1)x EXP\nDrain: (5.5x Lvl) HP\nSpeed scales with level")
        rr_help.setObjectName("idleModsHelp")
        rr_help.setWordWrap(True)
        layout.addWidget(rr_help)

        layout.addStretch(1)

        return panel

    def _on_shared_exp_changed(self, value: int) -> None:
        self._idle_state.set_shared_exp_percentage(value)
        self._update_mods_ui()

    def _on_risk_reward_changed(self, value: int) -> None:
        self._idle_state.set_risk_reward_level(value)
        self._update_mods_ui()

    def _update_mods_ui(self) -> None:
        shared_pct = self._idle_state.get_shared_exp_percentage()
        self._shared_exp_label.setText(f"Shared EXP: {shared_pct}%")
        self._shared_exp_slider.setValue(shared_pct)

        rr_level = self._idle_state.get_risk_reward_level()
        self._rr_label.setText(f"Risk & Reward: {rr_level}")
        self._rr_slider.setValue(rr_level)

    def _refresh_character_cards(self) -> None:
        snapshots: list[tuple[IdleOnsiteCharacterCard, dict, Stats, float]] = []
        party_stats: list[Stats] = []
        for card in self._onsite_cards:
            snapshot = card.snapshot()
            if snapshot is None:
                continue
            data, stats = snapshot
            try:
                max_hp = float(max(1.0, float(data.get("max_hp", 1.0))))
            except (TypeError, ValueError):
                max_hp = 1.0
            try:
                hp = float(max(0.0, float(data.get("hp", 0.0))))
            except (TypeError, ValueError):
                hp = 0.0
            ratio = min(1.0, hp / max_hp) if max_hp > 0 else 1.0
            snapshots.append((card, data, stats, ratio))
            party_stats.append(stats)

        reserves: list[Stats] = []
        seen: set[str] = set()
        for char_id in [str(item) for item in getattr(self, "_offsite_ids", []) if item]:
            if len(reserves) >= 6:
                break
            if char_id in seen:
                continue
            seen.add(char_id)

            plugin = self._plugin_by_id.get(char_id)
            data = self._idle_state.get_char_data(char_id)
            if plugin is None or not isinstance(data, dict):
                continue
            base_stats = data.get("base_stats")
            if not isinstance(base_stats, dict):
                continue
            stacks = max(1, int(data.get("stack", 1)))
            stars = max(1, int(getattr(plugin, "stars", 1) or 1))
            progress: dict[str, float | int] = {
                "level": max(1, int(data.get("level", 1))),
                "exp": float(max(0.0, float(data.get("exp", 0.0)))),
                "exp_multiplier": float(max(0.0, float(data.get("exp_multiplier", 1.0)))),
                "max_hp_level_bonus_version": max(0, int(data.get("max_hp_level_bonus_version", 0))),
            }
            reserves.append(
                build_scaled_character_stats(
                    plugin=plugin,
                    party_level=self._party_level,
                    stars=stars,
                    stacks=stacks,
                    progress=progress,
                    saved_base_stats=base_stats,
                )
            )

        apply_offsite_stat_share(party=party_stats, reserves=reserves, share=0.10)

        for (_card, _data, stats, ratio) in snapshots:
            stats.hp = max(0, min(stats.max_hp, int(round(float(stats.max_hp) * ratio))))

        maxima = compute_stat_maxima(party_stats)
        for card, data, stats, _ratio in snapshots:
            card.apply_snapshot(data, stats, maxima=maxima)

        for card in self._offsite_cards:
            card.update_display()

    def _on_tick(self, tick_count: int) -> None:
        self._refresh_character_cards()
        healed = 0
        try:
            healed = apply_idle_party_heal(self._save)
        except Exception:
            healed = 0
        if healed > 0:
            self._save_manager.save(self._save)
            self._refresh_party_hp()

    def _rebirth_character(self, char_id: str) -> None:
        if not self._idle_state.rebirth_character(char_id):
            return

        try:
            save = self._save
            progress = dict(save.character_progress)
            progress.update(self._idle_state.export_progress())
            save.character_progress = progress
            stats = dict(save.character_stats)
            stats.update(self._idle_state.export_character_stats())
            save.character_stats = stats
            initial_stats = dict(getattr(save, "character_initial_stats", {}) or {})
            initial_stats.update(self._idle_state.export_initial_stats())
            save.character_initial_stats = initial_stats
            bonus_seconds, penalty_seconds = self._idle_state.export_run_buff_seconds()
            save.idle_exp_bonus_seconds = bonus_seconds
            save.idle_exp_penalty_seconds = penalty_seconds
            save.idle_shared_exp_percentage = self._idle_state.get_shared_exp_percentage()
            save.idle_risk_reward_level = self._idle_state.get_risk_reward_level()
            self._save_manager.save(save)
        except Exception:
            return

        self._refresh_character_cards()

    def _autosave(self) -> None:
        try:
            save = self._save
            progress = dict(save.character_progress)
            progress.update(self._idle_state.export_progress())
            save.character_progress = progress
            stats = dict(save.character_stats)
            stats.update(self._idle_state.export_character_stats())
            save.character_stats = stats
            initial_stats = dict(getattr(save, "character_initial_stats", {}) or {})
            initial_stats.update(self._idle_state.export_initial_stats())
            save.character_initial_stats = initial_stats
            bonus_seconds, penalty_seconds = self._idle_state.export_run_buff_seconds()
            save.idle_exp_bonus_seconds = bonus_seconds
            save.idle_exp_penalty_seconds = penalty_seconds
            save.idle_shared_exp_percentage = self._idle_state.get_shared_exp_percentage()
            save.idle_risk_reward_level = self._idle_state.get_risk_reward_level()
            self._save_manager.save(save)
        except Exception:
            pass

    def _finish(self) -> None:
        if self._idle_timer:
            self._idle_timer.stop()
        if self._autosave_timer:
            self._autosave_timer.stop()
        try:
            save = self._save
            progress = dict(save.character_progress)
            progress.update(self._idle_state.export_progress())
            save.character_progress = progress
            stats = dict(save.character_stats)
            stats.update(self._idle_state.export_character_stats())
            save.character_stats = stats
            initial_stats = dict(getattr(save, "character_initial_stats", {}) or {})
            initial_stats.update(self._idle_state.export_initial_stats())
            save.character_initial_stats = initial_stats
            bonus_seconds, penalty_seconds = self._idle_state.export_run_buff_seconds()
            save.idle_exp_bonus_seconds = bonus_seconds
            save.idle_exp_penalty_seconds = penalty_seconds
            save.idle_shared_exp_percentage = self._idle_state.get_shared_exp_percentage()
            save.idle_risk_reward_level = self._idle_state.get_risk_reward_level()
            self._save_manager.save(save)
        except Exception:
            pass
        self.finished.emit()
