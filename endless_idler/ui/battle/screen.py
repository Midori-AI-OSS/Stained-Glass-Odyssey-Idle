from __future__ import annotations

import random

from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.ui.battle.sim import Combatant
from endless_idler.ui.battle.sim import build_foes
from endless_idler.ui.battle.sim import build_party
from endless_idler.ui.battle.sim import calculate_damage
from endless_idler.ui.battle.sim import choose_weighted_attacker
from endless_idler.ui.battle.widgets import Arena
from endless_idler.ui.battle.widgets import CombatantCard
from endless_idler.ui.battle.widgets import OffsiteStrip


class BattleScreenWidget(QWidget):
    finished = Signal()

    def __init__(self, *, payload: object, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("battleScreen")

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

        self._plugins = discover_character_plugins()
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}

        self._party: list[Combatant] = build_party(
            onsite=onsite,
            party_level=self._party_level,
            stacks=self._stacks,
            plugins_by_id=self._plugin_by_id,
        )
        self._foes: list[Combatant] = build_foes(
            exclude_ids=set(onsite + offsite),
            party_level=self._party_level,
            foe_count=5,
            plugins=self._plugins,
            rng=self._rng,
        )

        self._party_cards: list[CombatantCard] = []
        self._foe_cards: list[CombatantCard] = []
        self._turn_side = "party"

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
        title = QLabel("Battle")
        title.setObjectName("battleTitle")
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        header.addStretch(1)

        self._status = QLabel("")
        self._status.setObjectName("battleStatus")
        header.addWidget(self._status, 0, Qt.AlignmentFlag.AlignRight)

        arena = Arena()
        self._arena = arena

        arena_layout = QGridLayout()
        arena_layout.setContentsMargins(0, 0, 0, 0)
        arena_layout.setHorizontalSpacing(14)
        arena_layout.setVerticalSpacing(0)
        arena.setLayout(arena_layout)
        root.addWidget(arena, 1)

        left = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        left.setLayout(left_layout)

        for combatant in self._party:
            card = CombatantCard(
                combatant=combatant,
                plugin=self._plugin_by_id.get(combatant.char_id),
                rng=self._rng,
            )
            self._party_cards.append(card)
            left_layout.addWidget(card)

        left_layout.addStretch(1)
        if offsite:
            left_layout.addWidget(
                OffsiteStrip(
                    char_ids=offsite,
                    plugins_by_id=self._plugin_by_id,
                    rng=self._rng,
                )
            )

        right = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right.setLayout(right_layout)

        for combatant in self._foes:
            card = CombatantCard(
                combatant=combatant,
                plugin=self._plugin_by_id.get(combatant.char_id),
                rng=self._rng,
                compact=True,
            )
            self._foe_cards.append(card)
            right_layout.addWidget(card)

        right_layout.addStretch(1)

        arena_layout.addWidget(left, 0, 0, 1, 1)
        arena_layout.addWidget(QWidget(), 0, 1, 1, 1)
        arena_layout.addWidget(right, 0, 2, 1, 1)
        arena_layout.setColumnStretch(0, 0)
        arena_layout.setColumnStretch(1, 1)
        arena_layout.setColumnStretch(2, 0)

        self._battle_timer = QTimer(self)
        self._battle_timer.setInterval(240)
        self._battle_timer.timeout.connect(self._step_battle)
        self._battle_timer.start()

    def _step_battle(self) -> None:
        if self._is_over():
            return

        party_alive = [
            (c, w)
            for c, w in zip(self._party, self._party_cards, strict=False)
            if c.stats.hp > 0
        ]
        foes_alive = [
            (c, w)
            for c, w in zip(self._foes, self._foe_cards, strict=False)
            if c.stats.hp > 0
        ]
        if not party_alive or not foes_alive:
            self._finish()
            return

        if self._turn_side == "party":
            attacker, attacker_widget = choose_weighted_attacker(party_alive, self._rng)
            target, target_widget = self._rng.choice(foes_alive)
            color = QColor(80, 170, 255)
            self._turn_side = "foes"
        else:
            attacker, attacker_widget = choose_weighted_attacker(foes_alive, self._rng)
            target, target_widget = self._rng.choice(party_alive)
            color = QColor(255, 95, 95)
            self._turn_side = "party"

        damage, crit, dodged = calculate_damage(attacker.stats, target.stats, self._rng)
        if dodged:
            self._status.setText(f"{target.name} dodged!")
            self._arena.add_pulse(attacker_widget, target_widget, QColor(255, 255, 255))
            return

        if damage <= 0:
            return

        target.stats.hp = max(0, int(target.stats.hp) - int(damage))
        if crit:
            color = QColor(255, 215, 0)
        self._arena.add_pulse(attacker_widget, target_widget, color)
        self._status.setText(f"{attacker.name} hits {target.name} for {damage}{' (CRIT)' if crit else ''}")

        target_widget.refresh()
        if target.stats.hp <= 0:
            self._status.setText(f"{target.name} fell!")

        if self._is_over():
            self._finish()

    def _is_over(self) -> bool:
        party_alive = any(c.stats.hp > 0 for c in self._party)
        foes_alive = any(c.stats.hp > 0 for c in self._foes)
        return not party_alive or not foes_alive

    def _finish(self) -> None:
        try:
            self._battle_timer.stop()
        except Exception:
            pass
        self.finished.emit()

