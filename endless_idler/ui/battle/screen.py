from __future__ import annotations

import time
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
from endless_idler.run_rules import apply_battle_result
from endless_idler.ui.battle.colors import color_for_damage_type_id
from endless_idler.ui.battle.sim import Combatant
from endless_idler.ui.battle.sim import apply_offsite_stat_share
from endless_idler.ui.battle.sim import build_reserves
from endless_idler.ui.battle.sim import build_foes
from endless_idler.ui.battle.sim import build_party
from endless_idler.ui.battle.sim import calculate_damage
from endless_idler.ui.battle.sim import choose_weighted_attacker
from endless_idler.ui.battle.stat_bars import CombatantStatBars
from endless_idler.ui.battle.stat_bars import compute_stat_maxima
from endless_idler.ui.battle.widgets import Arena
from endless_idler.ui.battle.widgets import CombatantCard
from endless_idler.ui.party_hp_bar import PartyHpHeader
from endless_idler.save import RunSave
from endless_idler.save import SaveManager
from endless_idler.save import new_run_save


DEATH_EXP_DEBUFF_DURATION_SECONDS = 60 * 60


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

        self._save_manager = SaveManager()
        self._save = self._save_manager.load() or RunSave()
        self._fight_number = max(1, int(getattr(self._save, "fight_number", 1)))

        self._party: list[Combatant] = build_party(
            onsite=onsite,
            party_level=self._party_level,
            stacks=self._stacks,
            plugins_by_id=self._plugin_by_id,
            rng=self._rng,
            progress_by_id=dict(self._save.character_progress),
            stats_by_id=dict(self._save.character_stats),
        )
        self._reserves: list[Combatant] = build_reserves(
            char_ids=offsite,
            party_level=self._party_level,
            stacks=self._stacks,
            plugins_by_id=self._plugin_by_id,
            rng=self._rng,
            limit=6,
            progress_by_id=dict(self._save.character_progress),
            stats_by_id=dict(self._save.character_stats),
        )
        apply_offsite_stat_share(party=self._party, reserves=self._reserves, share=0.10)

        foe_level = max(1, int(self._party_level * float(self._fight_number) * 1.3))
        self._foes: list[Combatant] = build_foes(
            exclude_ids=set(onsite + offsite),
            party_level=foe_level,
            foe_count=5,
            plugins=self._plugins,
            rng=self._rng,
        )

        self._party_cards: list[CombatantCard] = []
        self._foe_cards: list[CombatantCard] = []
        self._party_stat_bars: list[CombatantStatBars] = []
        self._stat_bars_by_card: dict[CombatantCard, CombatantStatBars] = {}
        self._turn_side = "party"
        self._battle_over = False
        self._foe_kills = 0

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

        party_hp = PartyHpHeader()
        party_hp.set_hp(
            current=int(getattr(self._save, "party_hp_current", 0)),
            max_hp=int(getattr(self._save, "party_hp_max", 0)),
        )
        header.addWidget(party_hp, 0, Qt.AlignmentFlag.AlignVCenter)
        self._party_hp_header = party_hp

        toggle_stats = QPushButton("👁")
        toggle_stats.setObjectName("battleToggleStatBars")
        toggle_stats.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_stats.setCheckable(True)
        toggle_stats.setChecked(True)
        toggle_stats.setToolTip("Toggle stat bars")
        toggle_stats.toggled.connect(self._set_stat_bars_visible)
        header.addWidget(toggle_stats, 0, Qt.AlignmentFlag.AlignRight)
        self._toggle_stat_bars_button = toggle_stats

        self._status = QLabel("")
        self._status.setObjectName("battleStatus")
        self._status_char_limit = 10
        self._status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._status.setFixedWidth(self._status.fontMetrics().horizontalAdvance("M" * 11) + 12)
        header.addWidget(self._status, 0, Qt.AlignmentFlag.AlignRight)

        arena = Arena()
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

        party_count = len(self._party)
        if party_count <= 1:
            party_portrait = 128
            party_card_width = 420
        elif party_count == 2:
            party_portrait = 116
            party_card_width = 390
        elif party_count == 3:
            party_portrait = 104
            party_card_width = 360
        else:
            party_portrait = 92
            party_card_width = 340

        party_stat_maxima = compute_stat_maxima(self._party)
        for combatant in self._party:
            card = CombatantCard(
                combatant=combatant,
                plugin=self._plugin_by_id.get(combatant.char_id),
                rng=self._rng,
                team_side="left",
                stack_count=int(self._stacks.get(combatant.char_id, 1)),
                portrait_size=party_portrait,
                card_width=party_card_width,
                variant="onsite",
            )
            self._party_cards.append(card)
            stat_bars = CombatantStatBars(combatant=combatant, maxima=party_stat_maxima)
            self._party_stat_bars.append(stat_bars)
            self._stat_bars_by_card[card] = stat_bars

            row = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)
            row.setLayout(row_layout)
            row_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignVCenter)
            row_layout.addWidget(stat_bars, 0, Qt.AlignmentFlag.AlignVCenter)
            row_layout.addStretch(1)
            left_layout.addWidget(row)

        left_layout.addStretch(1)
        reserves_panel = QWidget()
        reserves_layout = QVBoxLayout()
        reserves_layout.setContentsMargins(0, 0, 0, 0)
        reserves_layout.setSpacing(10)
        reserves_panel.setLayout(reserves_layout)
        reserves_layout.addStretch(1)

        for combatant in self._reserves:
            reserves_layout.addWidget(
                CombatantCard(
                    combatant=combatant,
                    plugin=self._plugin_by_id.get(combatant.char_id),
                    rng=self._rng,
                    team_side="left",
                    stack_count=int(self._stacks.get(combatant.char_id, 1)),
                    portrait_size=48,
                    card_width=220,
                    variant="offsite",
                )
            )
        reserves_layout.addStretch(1)

        left_side = QWidget()
        left_side_layout = QHBoxLayout()
        left_side_layout.setContentsMargins(0, 0, 0, 0)
        left_side_layout.setSpacing(12)
        left_side.setLayout(left_side_layout)
        if self._reserves:
            left_side_layout.addWidget(reserves_panel, 0, Qt.AlignmentFlag.AlignVCenter)
        left_side_layout.addWidget(left, 0, Qt.AlignmentFlag.AlignVCenter)

        right = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right.setLayout(right_layout)
        right_layout.addStretch(1)

        for combatant in self._foes:
            card = CombatantCard(
                combatant=combatant,
                plugin=self._plugin_by_id.get(combatant.char_id),
                rng=self._rng,
                compact=True,
                team_side="right",
                stack_count=1,
                variant="foe",
            )
            self._foe_cards.append(card)
            right_layout.addWidget(card)

        right_layout.addStretch(1)

        arena_layout.addWidget(left_side, 0, 0, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        arena_layout.addWidget(QWidget(), 0, 1, 1, 1)
        arena_layout.addWidget(right, 0, 2, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        arena_layout.setColumnStretch(0, 0)
        arena_layout.setColumnStretch(1, 1)
        arena_layout.setColumnStretch(2, 0)

        self._battle_timer = QTimer(self)
        self._battle_timer.setInterval(240)
        self._battle_timer.timeout.connect(self._step_battle)
        self._battle_timer.start()

    def _refresh_party_hp(self) -> None:
        if getattr(self, "_party_hp_header", None) is None:
            return
        try:
            save = self._save_manager.load() or self._save or RunSave()
        except Exception:
            save = self._save
        self._party_hp_header.set_hp(
            current=int(getattr(save, "party_hp_current", 0)),
            max_hp=int(getattr(save, "party_hp_max", 0)),
        )

    def _step_battle(self) -> None:
        if self._battle_over:
            return
        if self._is_over():
            self._on_battle_over()
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
            self._on_battle_over()
            return

        if self._turn_side == "party":
            attacker, attacker_widget = choose_weighted_attacker(party_alive, self._rng)
            target, target_widget = self._rng.choice(foes_alive)
            self._turn_side = "foes"
        else:
            attacker, attacker_widget = choose_weighted_attacker(foes_alive, self._rng)
            target, target_widget = self._rng.choice(party_alive)
            self._turn_side = "party"

        color = color_for_damage_type_id(attacker.stats.element_id)
        damage, crit, dodged = calculate_damage(attacker.stats, target.stats, self._rng)
        if dodged:
            self._set_status(f"{target.name} dodged!")
            self._arena.add_pulse(attacker_widget, target_widget, QColor(240, 240, 240))
            return

        if damage <= 0:
            return

        previous_hp = int(target.stats.hp)
        target.stats.hp = max(0, previous_hp - int(damage))
        self._arena.add_pulse(attacker_widget, target_widget, color, crit=crit)
        self._set_status(f"{attacker.name} hits {target.name} for {damage}{' (CRIT)' if crit else ''}")

        target_widget.refresh()
        stat_bars = self._stat_bars_by_card.get(target_widget)
        if stat_bars is not None:
            stat_bars.refresh()
        if previous_hp > 0 and target.stats.hp <= 0:
            self._set_status(f"{target.name} fell!")
            if target in self._party:
                self._apply_death_exp_debuff(target.char_id)
            elif target in self._foes:
                self._foe_kills += 1

        if self._is_over():
            self._on_battle_over()

    def _set_status(self, message: str) -> None:
        message = str(message or "").replace("\n", " ").strip()
        self._status.setToolTip(message)

        limit = max(0, int(self._status_char_limit))
        if limit and len(message) > limit:
            clipped = max(0, limit - 1)
            message = f"{message[:clipped]}…"
        self._status.setText(message)

    def _set_stat_bars_visible(self, visible: bool) -> None:
        for stat_bars in self._party_stat_bars:
            stat_bars.setVisible(bool(visible))

    def _on_battle_over(self) -> None:
        if self._battle_over:
            return
        self._battle_over = True

        party_alive = any(c.stats.hp > 0 for c in self._party)
        foes_alive = any(c.stats.hp > 0 for c in self._foes)
        victory = bool(party_alive and not foes_alive)
        defeat = bool(foes_alive and not party_alive)
        if party_alive and not foes_alive:
            self._award_gold(self._foe_kills)
            self._set_status("Victory")
            self._apply_idle_exp_bonus()
        elif foes_alive and not party_alive:
            self._set_status("Defeat")
            self._apply_idle_exp_penalty()
        else:
            self._set_status("Over")

        try:
            save = self._save_manager.load() or self._save or RunSave()
            should_reset = False
            if victory:
                should_reset = apply_battle_result(save, victory=True)
            elif defeat:
                should_reset = apply_battle_result(save, victory=False)
            if should_reset:
                preserved_progress = dict(save.character_progress)
                preserved_stats = dict(save.character_stats)
                preserved_bonus = float(save.idle_exp_bonus_until)
                preserved_penalty = float(save.idle_exp_penalty_until)

                save = new_run_save(
                    available_char_ids=[plugin.char_id for plugin in self._plugins],
                    rng=self._rng,
                )
                save.character_progress = preserved_progress
                save.character_stats = preserved_stats
                save.idle_exp_bonus_until = preserved_bonus
                save.idle_exp_penalty_until = preserved_penalty

            self._save_manager.save(save)
            self._save = save
            self._refresh_party_hp()
        except Exception:
            pass

        try:
            self._battle_timer.stop()
        except Exception:
            pass

    def _apply_idle_exp_bonus(self) -> None:
        self._extend_idle_exp_timer(key="idle_exp_bonus_until", seconds=5 * 60)

    def _apply_idle_exp_penalty(self) -> None:
        self._extend_idle_exp_timer(key="idle_exp_penalty_until", seconds=15 * 60)

    def _award_gold(self, kills: int) -> None:
        gold = max(0, int(kills))
        if gold <= 0:
            return

        try:
            manager = SaveManager()
            save = manager.load() or RunSave()
            save.tokens = max(0, int(save.tokens)) + gold
            manager.save(save)
        except Exception:
            return

    def _extend_idle_exp_timer(self, *, key: str, seconds: int) -> None:
        try:
            manager = SaveManager()
            save = manager.load() or RunSave()
            now = float(time.time())
            current = float(max(0.0, getattr(save, key, 0.0)))
            setattr(save, key, max(current, now) + max(0, int(seconds)))
            manager.save(save)
        except Exception:
            return

    def _apply_death_exp_debuff(self, char_id: str) -> None:
        char_id = str(char_id or "").strip()
        if not char_id:
            return

        try:
            manager = SaveManager()
            save = manager.load() or RunSave()
            progress = save.character_progress.get(char_id)
            if not isinstance(progress, dict):
                progress = {"level": 1, "exp": 0.0, "next_exp": 30.0}
                save.character_progress[char_id] = progress

            now = float(time.time())
            try:
                stacks = max(0, int(progress.get("death_exp_debuff_stacks", 0)))
            except (TypeError, ValueError):
                stacks = 0
            try:
                until = float(max(0.0, float(progress.get("death_exp_debuff_until", 0.0))))
            except (TypeError, ValueError):
                until = 0.0

            if until and now >= until:
                stacks = 0

            progress["death_exp_debuff_stacks"] = stacks + 1
            progress["death_exp_debuff_until"] = now + DEATH_EXP_DEBUFF_DURATION_SECONDS
            manager.save(save)
        except Exception:
            return

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
