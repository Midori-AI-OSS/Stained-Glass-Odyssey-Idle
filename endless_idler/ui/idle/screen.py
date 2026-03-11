from __future__ import annotations

import math
import random
import threading

from collections.abc import Sequence

from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QFrame

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.combat.party_stats import apply_base_stat_multiplier
from endless_idler.combat.party_stats import apply_offsite_stat_share
from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.combat.stats import Stats
from endless_idler.progression import calculate_prestige_stat_gain_rate
from endless_idler.run_save_store import RunSaveStore
from endless_idler.run_rules import apply_idle_party_heal
from endless_idler.run_rules import start_idle_heal_timer
from endless_idler.tick_runtime import SharedTickRuntime
from endless_idler.tick_runtime import TickSnapshot
from endless_idler.ui.idle.widgets import IdleArena
from endless_idler.ui.idle.widgets import IdleOffsiteCard
from endless_idler.ui.idle.idle_state import IDLE_TICK_INTERVAL_SECONDS
from endless_idler.ui.idle.idle_state import IdleGameState
from endless_idler.ui.onsite import IdleOnsiteCharacterCard
from endless_idler.ui.onsite import compute_stat_maxima


def build_prestige_confirmation_html(
    *,
    display_name: str,
    exp_multiplier: float,
    prestige_count: int,
    stars: int,
) -> str:
    current_count = max(0, int(prestige_count))
    new_prestige_count = current_count + 1
    new_exp_mult = max(0.01, 0.5 * (0.5**current_count))
    current_stat_rate = calculate_prestige_stat_gain_rate(current_count, stars) * 100.0
    new_stat_rate = calculate_prestige_stat_gain_rate(new_prestige_count, stars) * 100.0

    message = f"<b>Prestige {display_name}?</b><br><br>"
    message += f"Current Prestige Level: {current_count}<br>"
    message += f"New Prestige Level: {new_prestige_count}<br><br>"
    message += "<b>Effects:</b><br>"
    message += f"• EXP Multiplier: {exp_multiplier:.2f} → {new_exp_mult:.2f}<br>"
    message += (
        "• Weighted Stat Gain Rate: "
        f"+{current_stat_rate:.2f}% → +{new_stat_rate:.2f}% per weighted stat upgrade<br>"
    )

    if new_exp_mult <= 0.01 and new_prestige_count >= 5:
        prestiges_past_floor = new_prestige_count - 4
        penalty_multiplier = 2.0**prestiges_past_floor
        message += f"<br><b>Warning:</b> EXP requirement penalty applied (x{penalty_multiplier:.1f})<br>"

    message += "<br>Your weighted stat gains per level will increase, while EXP gain rate will be reduced."
    return message


class IdleScreenWidget(QWidget):
    finished = Signal()

    @staticmethod
    def build_lineup_signature(
        save: object,
    ) -> tuple[tuple[str, ...], tuple[str, ...], tuple[tuple[str, int], ...], int]:
        onsite_raw = getattr(save, "onsite", [])
        offsite_raw = getattr(save, "offsite", [])
        stacks_raw = getattr(save, "stacks", {})
        party_level_raw = getattr(save, "party_level", 1)

        onsite = tuple(str(item) for item in onsite_raw if item)
        offsite = tuple(str(item) for item in offsite_raw if item)

        stack_pairs: list[tuple[str, int]] = []
        for char_id in [*onsite, *offsite]:
            raw = stacks_raw.get(char_id, 1) if isinstance(stacks_raw, dict) else 1
            stack_pairs.append((char_id, max(1, int(raw))))
        stack_pairs.sort()

        return (
            onsite,
            offsite,
            tuple(stack_pairs),
            max(1, int(party_level_raw)),
        )

    def __init__(
        self,
        *,
        save_store: RunSaveStore,
        tick_runtime: SharedTickRuntime | None = None,
        idle_state: IdleGameState | None = None,
        owns_tick_source: bool = True,
        plugins: Sequence[CharacterPlugin] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("idleScreen")

        self._rng = random.Random()
        self._save_store = save_store
        self._save = self._save_store.current
        self._lineup_signature = self.build_lineup_signature(self._save)
        # Placeholder references are initialized without parenting so they do not
        # render as stray widgets before panel builders assign the real controls.
        self._shared_exp_label = QLabel()
        self._shared_exp_slider = QSlider(Qt.Orientation.Horizontal)
        self._rr_label = QLabel()
        self._rr_slider = QSlider(Qt.Orientation.Horizontal)
        self._tick_runtime = tick_runtime or SharedTickRuntime(parent=self)
        self._tick_runtime_key = f"idle-screen-{id(self)}"
        self._owns_tick_source = bool(owns_tick_source)
        self._tick_cooldown_lock = threading.Lock()
        self._latest_tick_payload: dict[str, object] = {}
        start_idle_heal_timer(self._save)
        self._save_store.persist()

        onsite = [str(item) for item in self._save.onsite if item]
        offsite = [str(item) for item in self._save.offsite if item]
        stacks = dict(self._save.stacks)
        party_level = int(self._save.party_level)

        self._party_level = max(1, party_level)
        self._stacks = stacks
        self._onsite_ids = list(onsite)
        self._offsite_ids = list(offsite)
        self._tick_cooldown_seconds = float(
            max(0.0, float(getattr(self._save, "layout_tick_cooldown_seconds", 0.0)))
        )

        self._plugins = (
            list(plugins) if plugins is not None else discover_character_plugins()
        )
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}
        plugins_by_id: dict[str, object] = {
            key: value for key, value in self._plugin_by_id.items()
        }

        self._idle_state = idle_state or IdleGameState(
            char_ids=onsite,
            offsite_ids=offsite,
            party_level=self._party_level,
            stacks=self._stacks,
            plugins_by_id=plugins_by_id,
            rng=self._rng,
            progress_by_id=dict(self._save.character_progress),
            stats_by_id=dict(self._save.character_stats),
            initial_stats_by_id=dict(
                getattr(self._save, "character_initial_stats", {}) or {}
            ),
            inventory=self._save.inventory,
            exp_bonus_seconds=float(self._save.idle_exp_bonus_seconds),
            exp_penalty_seconds=float(self._save.idle_exp_penalty_seconds),
            shared_exp_percentage=int(
                getattr(self._save, "idle_shared_exp_percentage", 1)
            ),
            risk_reward_level=int(getattr(self._save, "idle_risk_reward_level", 0)),
            battle_start_time=float(getattr(self._save, "battle_start_time", 0.0)),
            blessings_data=dict(getattr(self._save, "blessings", {}) or {}),
        )

        self._onsite_cards: list[IdleOnsiteCharacterCard] = []
        self._offsite_cards: list[IdleOffsiteCard] = []
        self._allow_shutdown_persist = True

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        self.setLayout(root)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        root.addLayout(header)

        header.addStretch(1)
        self._tick_cooldown_label = QLabel("")
        self._tick_cooldown_label.setObjectName("idleTickCooldownLabel")
        self._tick_cooldown_label.setVisible(False)
        header.addWidget(
            self._tick_cooldown_label,
            0,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )

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
                on_prestige=self._prestige_character,
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
                on_prestige=self._prestige_character,
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

        right_column = QWidget()
        right_column_layout = QVBoxLayout()
        right_column_layout.setContentsMargins(0, 0, 0, 0)
        right_column_layout.setSpacing(10)
        right_column.setLayout(right_column_layout)
        right_column.setFixedWidth(220)

        mods_panel = self._make_mods_panel()
        right_column_layout.addWidget(mods_panel)
        right_column_layout.addStretch(1)

        arena_layout.addWidget(left_side, 0, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        arena_layout.addWidget(QWidget(), 0, 1, 1, 1)
        arena_layout.addWidget(right_column, 0, 2, 1, 1, Qt.AlignmentFlag.AlignTop)
        arena_layout.setColumnStretch(0, 0)
        arena_layout.setColumnStretch(1, 1)
        arena_layout.setColumnStretch(2, 0)

        self._update_mods_ui()

        if self._owns_tick_source:
            self._tick_runtime.configure_source(
                key=self._tick_runtime_key,
                source=self._produce_tick_payload,
            )
        self._tick_runtime.subscribe(
            key=self._tick_runtime_key,
            callback=self._on_tick_snapshot,
        )

        self._autosave_timer = QTimer(self)
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start(5000)  # Auto-save every 5 seconds
        self._update_tick_cooldown_label()

    @property
    def lineup_signature(
        self,
    ) -> tuple[tuple[str, ...], tuple[str, ...], tuple[tuple[str, int], ...], int]:
        return self._lineup_signature

    def _produce_tick_payload(
        self, tick_count: int, monotonic_seconds: float
    ) -> dict[str, object]:
        del tick_count
        del monotonic_seconds
        with self._tick_cooldown_lock:
            cooldown_seconds = self._tick_cooldown_seconds
            if cooldown_seconds > 0.0:
                cooldown_seconds = max(
                    0.0,
                    cooldown_seconds - IDLE_TICK_INTERVAL_SECONDS,
                )
                self._tick_cooldown_seconds = cooldown_seconds
        if cooldown_seconds > 0.0:
            return {
                "cooldown_seconds": cooldown_seconds,
                "idle_state": self._idle_state.export_runtime_snapshot(),
            }
        return {
            "cooldown_seconds": cooldown_seconds,
            "idle_state": self._idle_state.process_tick(),
        }

    def _update_tick_cooldown_label(self) -> None:
        with self._tick_cooldown_lock:
            cooldown_seconds = self._tick_cooldown_seconds
        remaining_seconds = int(math.ceil(cooldown_seconds))
        if remaining_seconds <= 0:
            self._tick_cooldown_label.setVisible(False)
            self._tick_cooldown_label.setText("")
            return
        self._tick_cooldown_label.setVisible(True)
        self._tick_cooldown_label.setText(f"Layout cooldown: {remaining_seconds}s")

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

        shared_exp_label = QLabel("Shared EXP: 1%")
        shared_exp_label.setObjectName("idleSharedExpLabel")
        shared_help_text = "Onsite chars lose X%, offsite gain that + 1% per onsite"
        shared_exp_label.setToolTip(shared_help_text)
        layout.addWidget(shared_exp_label)
        self._shared_exp_label = shared_exp_label

        self._shared_exp_slider = QSlider(Qt.Orientation.Horizontal)
        self._shared_exp_slider.setObjectName("idleSharedExpSlider")
        self._shared_exp_slider.setMinimum(1)
        self._shared_exp_slider.setMaximum(95)
        self._shared_exp_slider.setValue(1)
        self._shared_exp_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._shared_exp_slider.setTickInterval(10)
        self._shared_exp_slider.valueChanged.connect(self._on_shared_exp_changed)
        self._shared_exp_slider.setToolTip(shared_help_text)
        layout.addWidget(self._shared_exp_slider)

        layout.addSpacing(8)

        rr_label = QLabel("Risk & Reward: 0")
        rr_label.setObjectName("idleRRLabel")
        rr_help_text = (
            "Boost: (Lvl+1)x EXP\nDrain: (5.5x Lvl) HP\nSpeed scales with level"
        )
        rr_label.setToolTip(rr_help_text)
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
        self._rr_slider.setToolTip(rr_help_text)
        layout.addWidget(self._rr_slider)

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
        snapshots: list[
            tuple[IdleOnsiteCharacterCard, dict[str, object], Stats, float]
        ] = []
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
        for char_id in [
            str(item) for item in getattr(self, "_offsite_ids", []) if item
        ]:
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
                "exp_multiplier": float(
                    max(0.0, float(data.get("exp_multiplier", 1.0)))
                ),
                "max_hp_level_bonus_version": max(
                    0, int(data.get("max_hp_level_bonus_version", 0))
                ),
            }
            stats = build_scaled_character_stats(
                plugin=plugin,
                party_level=self._party_level,
                stars=stars,
                stacks=stacks,
                progress=progress,
                saved_base_stats=base_stats,
            )
            misplacement_getter = getattr(
                self._idle_state, "get_misplacement_stat_multiplier", None
            )
            if callable(misplacement_getter):
                raw_multiplier = misplacement_getter(char_id)
                if isinstance(raw_multiplier, int | float):
                    misplacement_multiplier = float(raw_multiplier)
                else:
                    misplacement_multiplier = 1.0
            else:
                misplacement_multiplier = 1.0
            apply_base_stat_multiplier(stats=stats, multiplier=misplacement_multiplier)
            reserves.append(stats)

        apply_offsite_stat_share(party=party_stats, reserves=reserves, share=0.10)

        for _card, _data, stats, ratio in snapshots:
            stats.hp = max(
                0, min(stats.max_hp, int(round(float(stats.max_hp) * ratio)))
            )

        maxima = compute_stat_maxima(party_stats)
        for card, data, stats, _ratio in snapshots:
            card.apply_snapshot(data, stats, maxima=maxima)

        for card in self._offsite_cards:
            card.update_display()

    def _on_tick_snapshot(self, snapshot: TickSnapshot) -> None:
        payload = dict(snapshot.payload)
        self._latest_tick_payload = payload
        with self._tick_cooldown_lock:
            current_cooldown = self._tick_cooldown_seconds
        cooldown_raw = payload.get("cooldown_seconds", current_cooldown)
        cooldown_seconds = self._coerce_float(cooldown_raw, 0.0)
        with self._tick_cooldown_lock:
            self._tick_cooldown_seconds = cooldown_seconds
        self._update_tick_cooldown_label()
        self._refresh_character_cards()
        healed = apply_idle_party_heal(self._save)
        if healed > 0:
            self._save_store.persist()

    def _rebirth_character(self, char_id: str) -> None:
        if not self._idle_state.rebirth_character(char_id):
            return

        self._apply_snapshot_to_save(self._idle_state.export_runtime_snapshot())
        self._save_store.persist(force=True)
        self._refresh_character_cards()

    def _prestige_character(self, char_id: str) -> None:
        """
        Apply prestige to a character with confirmation dialog.

        Shows the player what will happen before they commit to the prestige.
        """
        # Get current character data
        data = self._idle_state.get_char_data(char_id)
        if not data:
            return

        # Check if prestige is available
        exp_multiplier = float(data.get("exp_multiplier", 1.0))
        if exp_multiplier < 10.0:
            return

        # Get current prestige count
        prestige_count = max(0, int(data.get("prestige_count", 0)))

        # Show confirmation dialog
        plugin = self._plugin_by_id.get(char_id)
        if plugin is None:
            raise ValueError(
                f"Missing plugin metadata for prestige character {char_id!r}."
            )
        display_name = getattr(plugin, "display_name", char_id)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Prestige Confirmation")
        msg_box.setIcon(QMessageBox.Icon.Question)

        msg_box.setText(
            build_prestige_confirmation_html(
                display_name=display_name,
                exp_multiplier=exp_multiplier,
                prestige_count=prestige_count,
                stars=int(getattr(plugin, "stars", 0) or 0),
            )
        )
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        result = msg_box.exec()
        if result != QMessageBox.StandardButton.Yes:
            return

        # Apply prestige
        if not self._idle_state.prestige_character(char_id):
            return

        self._apply_snapshot_to_save(self._idle_state.export_runtime_snapshot())
        self._save_store.persist(force=True)
        self._refresh_character_cards()

    def _autosave(self, *, force: bool = False) -> None:
        idle_snapshot_raw = self._latest_tick_payload.get("idle_state")
        if not isinstance(idle_snapshot_raw, dict):
            idle_snapshot_raw = self._idle_state.export_runtime_snapshot()
        self._apply_snapshot_to_save(idle_snapshot_raw)
        self._save_store.persist(force=force)

    def _apply_snapshot_to_save(self, snapshot: dict[str, object]) -> None:
        save = self._save
        progress = snapshot.get("progress")
        if isinstance(progress, dict):
            save.character_progress = {
                str(char_id): dict(data)
                for char_id, data in progress.items()
                if isinstance(char_id, str) and isinstance(data, dict)
            }
        stats = snapshot.get("character_stats")
        if isinstance(stats, dict):
            save.character_stats = {
                str(char_id): dict(data)
                for char_id, data in stats.items()
                if isinstance(char_id, str) and isinstance(data, dict)
            }
        initial_stats = snapshot.get("initial_stats")
        if isinstance(initial_stats, dict):
            save.character_initial_stats = {
                str(char_id): dict(data)
                for char_id, data in initial_stats.items()
                if isinstance(char_id, str) and isinstance(data, dict)
            }
        blessings = snapshot.get("blessings")
        if isinstance(blessings, dict):
            save.blessings = {
                str(blessing_id): dict(data)
                for blessing_id, data in blessings.items()
                if isinstance(blessing_id, str) and isinstance(data, dict)
            }
        save.idle_exp_bonus_seconds = self._coerce_float(
            snapshot.get("exp_bonus_seconds", 0.0), 0.0
        )
        save.idle_exp_penalty_seconds = self._coerce_float(
            snapshot.get("exp_penalty_seconds", 0.0), 0.0
        )
        save.idle_shared_exp_percentage = max(
            1,
            min(95, self._coerce_int(snapshot.get("shared_exp_percentage", 1), 1)),
        )
        save.idle_risk_reward_level = max(
            0,
            min(150, self._coerce_int(snapshot.get("risk_reward_level", 0), 0)),
        )
        with self._tick_cooldown_lock:
            save.layout_tick_cooldown_seconds = float(self._tick_cooldown_seconds)

    @staticmethod
    def _coerce_float(value: object, default: float) -> float:
        if isinstance(value, bool):
            return default
        if isinstance(value, int | float):
            return max(0.0, float(value))
        if isinstance(value, str):
            try:
                return max(0.0, float(value))
            except ValueError:
                return default
        return default

    @staticmethod
    def _coerce_int(value: object, default: int) -> int:
        if isinstance(value, bool):
            return default
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return default
        return default

    def force_persist(self) -> None:
        self._allow_shutdown_persist = True
        self._autosave(force=True)

    def _finish(self) -> None:
        self.shutdown()
        self.finished.emit()

    def shutdown(self, *, persist: bool = True) -> None:
        self._tick_runtime.unsubscribe(self._tick_runtime_key)
        if self._owns_tick_source:
            self._tick_runtime.clear_source(self._tick_runtime_key)
        if self._autosave_timer:
            self._autosave_timer.stop()
        self._allow_shutdown_persist = self._allow_shutdown_persist and persist
        if persist and self._allow_shutdown_persist:
            self._autosave(force=True)
