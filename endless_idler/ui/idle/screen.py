from __future__ import annotations

import random

from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSpinBox
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QFrame

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.ui.idle.widgets import IdleCharacterCard
from endless_idler.ui.idle.widgets import IdleArena
from endless_idler.ui.idle.idle_state import IdleGameState


class IdleScreenWidget(QWidget):
    finished = Signal()

    def __init__(self, *, payload: object, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("idleScreen")

        data = payload if isinstance(payload, dict) else {}
        party_level = int(data.get("party_level", 1) or 1)
        onsite_raw = data.get("onsite", [])
        stacks_raw = data.get("stacks", {})

        onsite = [str(item) for item in onsite_raw if item]
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

        self._plugins = discover_character_plugins()
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}

        self._idle_state = IdleGameState(
            char_ids=onsite,
            party_level=self._party_level,
            stacks=self._stacks,
            plugins_by_id=self._plugin_by_id,
            rng=self._rng,
        )

        self._character_cards: list[IdleCharacterCard] = []

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

        self._tick_label = QLabel("Tick: 0")
        self._tick_label.setObjectName("idleTickLabel")
        header.addWidget(self._tick_label, 0, Qt.AlignmentFlag.AlignRight)

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
            card = IdleCharacterCard(
                char_id=char_id,
                plugin=plugin,
                idle_state=self._idle_state,
                rng=self._rng,
                stack_count=stack_count,
            )
            self._character_cards.append(card)
            left_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignVCenter)

        left_layout.addStretch(1)

        right_panel = self._make_mods_panel()

        arena_layout.addWidget(left, 0, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        arena_layout.addWidget(QWidget(), 0, 1, 1, 1)
        arena_layout.addWidget(right_panel, 0, 2, 1, 1, Qt.AlignmentFlag.AlignTop)
        arena_layout.setColumnStretch(0, 0)
        arena_layout.setColumnStretch(1, 1)
        arena_layout.setColumnStretch(2, 0)

        self._update_mods_ui()

        self._idle_state.tick_update.connect(self._on_tick)
        self._idle_timer = QTimer(self)
        self._idle_timer.timeout.connect(self._idle_state.process_tick)
        self._idle_timer.start(100)

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

        self._shared_exp_btn = QPushButton("Shared EXP: OFF")
        self._shared_exp_btn.setObjectName("idleSharedExpButton")
        self._shared_exp_btn.setCheckable(True)
        self._shared_exp_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._shared_exp_btn.clicked.connect(self._toggle_shared_exp)
        layout.addWidget(self._shared_exp_btn)

        shared_help = QLabel("Gain: 1% Potential / viewed char")
        shared_help.setObjectName("idleModsHelp")
        shared_help.setWordWrap(True)
        layout.addWidget(shared_help)

        rr_title = QLabel("Risk & Reward")
        rr_title.setObjectName("idleRRTitle")
        layout.addWidget(rr_title)

        self._rr_toggle = QCheckBox("Enabled")
        self._rr_toggle.setObjectName("idleRRToggle")
        self._rr_toggle.clicked.connect(self._toggle_risk_reward)
        layout.addWidget(self._rr_toggle)

        level_row = QHBoxLayout()
        level_row.addWidget(QLabel("Lvl:"))
        self._rr_level = QSpinBox()
        self._rr_level.setObjectName("idleRRLevel")
        self._rr_level.setRange(1, 100)
        self._rr_level.valueChanged.connect(self._update_risk_reward_level)
        level_row.addWidget(self._rr_level)
        layout.addLayout(level_row)

        rr_help = QLabel("Boost: (Lvl+1)x EXP\nDrain: (1.5x Lvl) HP / 0.5s")
        rr_help.setObjectName("idleModsHelp")
        rr_help.setWordWrap(True)
        layout.addWidget(rr_help)

        layout.addStretch(1)

        return panel

    def _toggle_shared_exp(self, checked: bool) -> None:
        self._idle_state.set_shared_exp(checked)
        self._update_mods_ui()

    def _toggle_risk_reward(self, checked: bool) -> None:
        self._idle_state.set_risk_reward_enabled(checked)

    def _update_risk_reward_level(self, level: int) -> None:
        self._idle_state.set_risk_reward_level(level)

    def _update_mods_ui(self) -> None:
        shared = self._idle_state.is_shared_exp_enabled()
        self._shared_exp_btn.setChecked(shared)
        self._shared_exp_btn.setText(f"Shared EXP: {'ON' if shared else 'OFF'}")

        self._rr_toggle.setChecked(self._idle_state.is_risk_reward_enabled())
        self._rr_level.setValue(self._idle_state.get_risk_reward_level())

    def _on_tick(self, tick_count: int) -> None:
        self._tick_label.setText(f"Tick: {tick_count}")
        for card in self._character_cards:
            card.update_display()

    def _finish(self) -> None:
        if self._idle_timer:
            self._idle_timer.stop()
        self.finished.emit()
