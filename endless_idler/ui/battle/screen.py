from __future__ import annotations

import math
import time
import random

from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.passives.execution import apply_target_selection_passives
from endless_idler.passives.execution import trigger_turn_start_passives
from endless_idler.ui.battle.mechanics import apply_dark_sacrifice
from endless_idler.ui.battle.mechanics import apply_fire_self_bleed
from endless_idler.ui.battle.mechanics import dark_damage_multiplier_from_removed_hp
from endless_idler.ui.battle.mechanics import fire_damage_multiplier_from_removed_hp
from endless_idler.ui.battle.mechanics import resolve_light_heal
from endless_idler.run_rules import apply_battle_result
from endless_idler.run_rules import calculate_gold_bonus
from endless_idler.ui.battle.colors import color_for_damage_type_id
from endless_idler.ui.battle.sim import Combatant
from endless_idler.ui.battle.sim import apply_offsite_stat_share
from endless_idler.ui.battle.sim import build_reserves
from endless_idler.ui.battle.sim import build_foes
from endless_idler.ui.battle.sim import build_party
from endless_idler.ui.battle.sim import calculate_damage
from endless_idler.ui.battle.sim import choose_weighted_target_by_aggro
from endless_idler.ui.battle.widgets import Arena
from endless_idler.ui.battle.widgets import CombatantCard
from endless_idler.ui.onsite import BattleOnsiteCharacterCard
from endless_idler.ui.onsite import compute_stat_maxima
from endless_idler.ui.party_hp_bar import PartyHpHeader
from endless_idler.save import RunSave
from endless_idler.save import SaveManager
from endless_idler.save import new_run_save
from endless_idler.save import reset_character_progress_for_new_run
from endless_idler.progression import record_character_death


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
        self._onsite_ids = list(onsite)
        self._offsite_ids = list(offsite)
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
        
        # Reset idle exp multiplier and set battle start time for new battle
        self._save.idle_exp_mult = 1.0
        self._save.battle_start_time = time.time()
        self._save_manager.save(self._save)

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
            spawn_wave_mult=1.0,  # Initial wave uses base multiplier (wave_index=0)
        )

        self._party_cards: list[QWidget] = []
        self._reserve_cards: list[CombatantCard] = []
        self._foe_cards: list[CombatantCard] = []
        self._turn_side = "party"
        self._battle_over = False
        self._foe_kills = 0
        self._coins_earned = 0  # Track coins earned from foe kills
        
        # Tick-based action timing
        self._battle_tick: int = 0
        
        # Mark offsite combatants
        for reserve in self._reserves:
            reserve.is_offsite = True
        
        # Stalemate detection
        self._stalemate_hp_ratio: float | None = None
        self._stalemate_last_check_time: float = time.time()
        self._stalemate_stacks: int = 0
        self._stalemate_tick_counter: int = 0
        
        # Wave spawning system
        self._wave_number: int = 1
        self._wave_index: int = 0  # Wave index for difficulty scaling (starts at 0)
        self._last_wave_spawn_time: float = time.time()
        self._wave_spawn_interval: float = 30.0  # 30 seconds between waves

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
        back.clicked.connect(self._on_back_clicked)
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
        left_layout = QHBoxLayout()  # Changed from VBoxLayout to HBoxLayout for horizontal row
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

        party_stat_maxima = compute_stat_maxima([combatant.stats for combatant in self._party])
        for combatant in self._party:
            card = BattleOnsiteCharacterCard(
                combatant=combatant,
                plugin=self._plugin_by_id.get(combatant.char_id),
                rng=self._rng,
                team_side="left",
                stack_count=int(self._stacks.get(combatant.char_id, 1)),
                card_width=party_card_width,
                portrait_size=(party_portrait, party_portrait),
                maxima=party_stat_maxima,
            )
            self._party_cards.append(card)
            left_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignVCenter)

        left_layout.addStretch(1)
        reserves_panel = QWidget()
        reserves_layout = QHBoxLayout()  # Changed from VBoxLayout to HBoxLayout for horizontal row
        reserves_layout.setContentsMargins(0, 0, 0, 0)
        reserves_layout.setSpacing(10)
        reserves_panel.setLayout(reserves_layout)
        reserves_layout.addStretch(1)

        for combatant in self._reserves:
            card = CombatantCard(
                combatant=combatant,
                plugin=self._plugin_by_id.get(combatant.char_id),
                rng=self._rng,
                team_side="left",
                stack_count=int(self._stacks.get(combatant.char_id, 1)),
                portrait_size=48,
                card_width=220,
                variant="offsite",
            )
            self._reserve_cards.append(card)
            reserves_layout.addWidget(card)
        reserves_layout.addStretch(1)

        left_side = QWidget()
        left_side_layout = QVBoxLayout()  # Changed from HBoxLayout to VBoxLayout to stack rows vertically
        left_side_layout.setContentsMargins(0, 0, 0, 0)
        left_side_layout.setSpacing(12)
        left_side.setLayout(left_side_layout)
        left_side_layout.addStretch(1)  # Push content to bottom
        left_side_layout.addWidget(left, 0, Qt.AlignmentFlag.AlignHCenter)  # Onsite row (at bottom)
        if self._reserves:
            left_side_layout.addWidget(reserves_panel, 0, Qt.AlignmentFlag.AlignHCenter)  # Offsite row (below onsite)

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

    def _calculate_hp_ratio(self) -> float:
        """Calculate combined HP ratio: (party_max/party_current + reserves_max/reserves_current) vs (foes_max/foes_current)"""
        party_ratio = sum(
            c.max_hp / max(1, c.stats.hp) 
            for c in self._party 
            if c.stats.hp > 0
        )
        reserve_ratio = sum(
            c.max_hp / max(1, c.stats.hp) 
            for c in self._reserves 
            if c.stats.hp > 0
        )
        foe_ratio = sum(
            c.max_hp / max(1, c.stats.hp) 
            for c in self._foes 
            if c.stats.hp > 0
        )
        
        allies_total = party_ratio + reserve_ratio
        return allies_total / max(0.01, foe_ratio)
    
    def _check_stalemate(self) -> None:
        """Detect stalemate and apply bleed if HP ratios haven't changed significantly in 15 seconds"""
        current_time = time.time()
        current_ratio = self._calculate_hp_ratio()
        
        if self._stalemate_hp_ratio is None:
            self._stalemate_hp_ratio = current_ratio
            self._stalemate_last_check_time = current_time
            return
        
        time_elapsed = current_time - self._stalemate_last_check_time
        
        if time_elapsed >= 15.0:
            ratio_change = abs(current_ratio - self._stalemate_hp_ratio) / max(0.01, abs(self._stalemate_hp_ratio))
            
            if ratio_change < 0.10:
                self._stalemate_stacks += 1
                self._set_status(f"Stalemate! Bleed x{self._stalemate_stacks}")
            
            self._stalemate_hp_ratio = current_ratio
            self._stalemate_last_check_time = current_time
    
    def _apply_stalemate_bleed(self) -> None:
        """Apply 1% current HP true damage per stack to all combatants every 10 ticks"""
        if self._stalemate_stacks <= 0:
            return
        
        self._stalemate_tick_counter += 1
        
        if self._stalemate_tick_counter >= 10:
            self._stalemate_tick_counter = 0
            damage_percent = 0.01 * self._stalemate_stacks
            
            for combatant in self._party + self._reserves + self._foes:
                if combatant.stats.hp > 0:
                    damage = max(1, int(combatant.stats.hp * damage_percent))
                    combatant.stats.hp = max(0, combatant.stats.hp - damage)
            
            for card in self._party_cards + self._reserve_cards + self._foe_cards:
                if hasattr(card, 'refresh'):
                    card.refresh()

    def _check_wave_spawn(self) -> None:
        """Check if a new wave should spawn based on timer or zero foes"""
        current_time = time.time()
        time_since_last_wave = current_time - self._last_wave_spawn_time
        
        # Count alive foes
        foes_alive_count = sum(1 for foe in self._foes if foe.stats.hp > 0)
        
        # Check spawn conditions: 30 second timer OR zero foes alive
        should_spawn = (time_since_last_wave >= self._wave_spawn_interval) or (foes_alive_count == 0)
        
        if should_spawn:
            self._spawn_new_wave()
            self._last_wave_spawn_time = current_time
    
    def _spawn_new_wave(self) -> None:
        """Spawn a new wave of foes with 100 foe cap and overflow scaling.
        
        Implements a 100 foe cap by:
        1. Counting currently alive foes (hp > 0)
        2. Calculating available slots (100 - alive count)
        3. Spawning only what fits in available slots
        4. Applying wave-only multiplier (1.01^blocked_spawns) to compensate
        
        The wave-only multiplier is:
        - Applied only to foes spawned in the current wave
        - Reset for the next wave (doesn't carry over)
        - Calculated as: pow(1.01, blocked_spawns)
        
        Example: If 95 foes alive and wave requests 10:
        - Only 5 spawn (to hit cap of 100)
        - 5 blocked spawns
        - Wave-only mult = 1.01^5 ≈ 1.051 (5.1% stronger)
        """
        self._wave_number += 1
        
        # Calculate spawn wave multiplier based on wave index
        # spawn_wave_mult = 1.0005 ^ wave_index
        spawn_wave_mult = pow(1.0005, self._wave_index)
        
        # Use existing foe level calculation
        foe_level = max(1, int(self._party_level * float(self._fight_number) * 1.3))
        
        # FOE CAP LOGIC: Cap total foes at 100
        MAX_FOES = 100
        current_foe_count = sum(1 for foe in self._foes if foe.stats.hp > 0)
        available_slots = MAX_FOES - current_foe_count
        
        # TIME-BASED SPAWN COUNT SCALING
        # Calculate survival time since battle start
        survival_time = max(0.0, time.time() - self._save.battle_start_time)
        
        # Calculate time multiplier: time_mult = 1 + 0.15 * floor(t / 25) + 0.05 * floor(t / 30)
        time_mult = 1.0 + 0.15 * int(survival_time / 25) + 0.05 * int(survival_time / 30)
        
        # Baseline spawn count and apply time multiplier with ceiling
        base_spawn_count = 5
        requested_spawn_count = math.ceil(base_spawn_count * time_mult)
        
        # Calculate actual spawn count and blocked spawns
        actual_spawn_count = min(requested_spawn_count, max(0, available_slots))
        blocked_spawns = max(0, requested_spawn_count - actual_spawn_count)
        
        # Calculate wave-only multiplier for overflow compensation
        # Each blocked spawn increases multiplier by 1.01
        wave_only_mult = pow(1.01, blocked_spawns)
        
        # Combine base spawn wave multiplier with wave-only overflow multiplier
        combined_mult = spawn_wave_mult * wave_only_mult
        
        # Only spawn if we have available slots
        if actual_spawn_count > 0:
            # Build new foes with combined multiplier
            new_foes = build_foes(
                exclude_ids=set(self._onsite_ids + self._offsite_ids),
                party_level=foe_level,
                foe_count=actual_spawn_count,
                plugins=self._plugins,
                rng=self._rng,
                spawn_wave_mult=combined_mult,
            )
            
            # Add new foes to existing foes (don't replace)
            self._foes.extend(new_foes)
        else:
            new_foes = []
        
        # Increment wave index for next wave
        self._wave_index += 1
        
        # Update foe cards in the UI
        # Get layout for foe cards
        right_layout = self._arena.layout().itemAtPosition(0, 2).widget().layout()
        
        # Add new foe cards (only for newly spawned foes)
        for combatant in new_foes:
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
            right_layout.insertWidget(right_layout.count() - 1, card)  # Insert before stretch
        
        # Log wave spawn for debugging with cap info
        if blocked_spawns > 0:
            print(f"[Wave System] Wave {self._wave_number} spawned with {actual_spawn_count}/{requested_spawn_count} foes (CAPPED: {blocked_spawns} blocked, wave_only_mult={wave_only_mult:.4f}, wave_index={self._wave_index - 1}, total_mult={combined_mult:.4f}, time={survival_time:.1f}s, time_mult={time_mult:.2f})")
        else:
            print(f"[Wave System] Wave {self._wave_number} spawned with {actual_spawn_count} foes (wave_index={self._wave_index - 1}, mult={combined_mult:.4f}, time={survival_time:.1f}s, time_mult={time_mult:.2f})")
        
        status_msg = f"Wave {self._wave_number}!"
        if blocked_spawns > 0:
            status_msg += f" (Capped! +{blocked_spawns*1:.0f}% wave strength)"
        self._set_status(status_msg)

    def _calculate_action_interval(self, combatant: Combatant) -> int:
        """Calculate action interval in ticks based on atk_speed.
        
        Formula: action_interval_ticks = 500 / atk_speed
        Offsite characters act 10x slower (interval × 10)
        
        Args:
            combatant: The combatant to calculate interval for
            
        Returns:
            Number of ticks between actions
        """
        base_interval = 500.0 / max(1, combatant.stats.atk_speed)
        
        # Apply offsite multiplier
        if combatant.is_offsite:
            base_interval *= 10.0
        
        return int(base_interval)

    def _step_battle(self) -> None:
        if self._battle_over:
            return
        if self._is_over():
            self._on_battle_over()
            return
        
        # Increment tick counter
        self._battle_tick += 1
        
        # Check for stalemate and apply bleed
        self._check_stalemate()
        self._apply_stalemate_bleed()
        
        # Check wave spawn conditions
        self._check_wave_spawn()

        party_alive = [
            (c, w)
            for c, w in zip(self._party, self._party_cards, strict=False)
            if c.stats.hp > 0
        ]
        reserves_alive = [
            (c, w)
            for c, w in zip(self._reserves, self._reserve_cards, strict=False)
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

        # Trigger TURN_START passives for party (keep this per tick for now)
        party_stats = [c.stats for c in self._party if c.stats.hp > 0]
        reserve_stats = [c.stats for c in self._reserves if c.stats.hp > 0]
        all_party_stats = party_stats + reserve_stats
        foe_stats = [c.stats for c in self._foes if c.stats.hp > 0]
        
        turn_start_results = trigger_turn_start_passives(
            all_allies=all_party_stats,
            onsite_allies=party_stats,
            offsite_allies=reserve_stats,
            enemies=foe_stats,
        )
        
        # Process TURN_START passive results (e.g., healing from Lady Light)
        for result in turn_start_results:
            if "healing_done" in result:
                heals_by_target = result["healing_done"]
                for target_stats, heal_amount_val in heals_by_target.items():
                    # Find the combatant widget to refresh
                    for combatant in self._party + self._reserves:
                        if combatant.stats is target_stats:
                            # Find the widget
                            for card in self._party_cards + self._reserve_cards:
                                if hasattr(card, 'refresh'):
                                    card.refresh()
                            break
        
        if not party_alive or not foes_alive:
            self._on_battle_over()
            return

        # Determine which combatants should act this tick (tick-based timing)
        # Collect all alive combatants from all teams
        all_combatants_alive = party_alive + reserves_alive + foes_alive
        
        # Find combatants ready to act (next_action_tick <= current_tick)
        ready_to_act = [
            (c, w) for c, w in all_combatants_alive 
            if c.next_action_tick <= self._battle_tick
        ]
        
        # If no one is ready, continue to next tick
        if not ready_to_act:
            return
        
        # Pick one combatant to act this tick (weighted by atk_speed for fairness)
        # Higher atk_speed = more likely to be selected when multiple are ready
        weights = [c.stats.atk_speed for c, _ in ready_to_act]
        total_weight = sum(weights)
        if total_weight <= 0:
            return
        
        # Weighted random selection
        r = self._rng.random() * total_weight
        cumulative = 0.0
        attacker, attacker_widget = ready_to_act[0]
        for (c, w), weight in zip(ready_to_act, weights, strict=False):
            cumulative += weight
            if r <= cumulative:
                attacker, attacker_widget = c, w
                break
        
        # Schedule next action for this combatant
        action_interval = self._calculate_action_interval(attacker)
        attacker.next_action_tick = self._battle_tick + action_interval
        
        # Determine attacker side (party vs foes)
        if attacker in [c for c, _ in party_alive]:
            attacker_side = "party"
        elif attacker in [c for c, _ in reserves_alive]:
            attacker_side = "party"  # Reserves are on party side
        else:
            attacker_side = "foes"

        attacker.turns_taken += 1
        element_id = attacker.stats.element_id
        color = color_for_damage_type_id(element_id)

        party_onsite = [c for c, _ in party_alive]
        reserves_onsite = [c for c, _ in reserves_alive]
        foes_onsite = [c for c, _ in foes_alive]
        party_widgets = {c: w for c, w in party_alive}
        foe_widgets = {c: w for c, w in foes_alive}
        reserve_widgets = {c: w for c, w in reserves_alive}

        if attacker_side == "party":
            # Party or reserves attacking foes
            if attacker in party_onsite:
                allies_onsite = party_onsite
            else:
                # Attacker is from reserves
                allies_onsite = party_onsite  # Onsite allies are still the party
            allies_offsite = reserves_onsite
            enemies = foes_alive
        else:
            # Foes attacking party
            allies_onsite = foes_onsite
            allies_offsite = []
            # Foes can attack both party and reserves
            enemies = party_alive + reserves_alive

        if element_id == "ice":
            if not attacker.ice_charge_ready:
                attacker.ice_charge_ready = True
                self._set_status(f"{attacker.name} is charging…")
                return
            attacker.ice_charge_ready = False

        if element_id == "light":
            healed = resolve_light_heal(
                attacker=attacker,
                onsite_allies=allies_onsite,
                offsite_allies=allies_offsite,
            )
            if healed:
                self._set_status(f"{attacker.name} heals!")
                for target, _ in healed:
                    widget = party_widgets.get(target) or foe_widgets.get(target) or reserve_widgets.get(target)
                    if widget is not None:
                        widget.refresh()
                        
                        # Detect wrong-way healing scenario
                        # Healing might initially target wrong side if healer is wounded (below 50% HP)
                        wrong_widget = None
                        if attacker.stats.hp < (attacker.max_hp * 0.5):
                            # Healer is wounded - might misfire healing toward enemies initially
                            if attacker_side == "party" and enemies:
                                # Player healing allies but initially misfires toward enemy
                                potential_wrong_targets = [c for c, w in enemies if c.stats.hp > 0]
                                if potential_wrong_targets:
                                    wrong_target = self._rng.choice(potential_wrong_targets)
                                    wrong_widget = foe_widgets.get(wrong_target)
                            elif attacker_side == "foes" and enemies:
                                # Enemy healing allies but initially misfires toward player
                                potential_wrong_targets = [c for c, w in enemies if c.stats.hp > 0]
                                if potential_wrong_targets:
                                    wrong_target = self._rng.choice(potential_wrong_targets)
                                    wrong_widget = party_widgets.get(wrong_target)
                        
                        self._arena.add_pulse(
                            attacker_widget, 
                            widget, 
                            color, 
                            same_team=True,
                            wrong_target=wrong_widget
                        )
                return

        if element_id == "dark":
            removed = apply_dark_sacrifice(onsite_allies=allies_onsite, offsite_allies=allies_offsite)
            attacker.pending_damage_multiplier *= dark_damage_multiplier_from_removed_hp(removed)
            if removed:
                self._set_status(f"{attacker.name} sacrifices {removed} HP!")
                for target in allies_onsite:
                    widget = party_widgets.get(target) or foe_widgets.get(target)
                    if widget is not None:
                        widget.refresh()
                for target in allies_offsite:
                    widget = reserve_widgets.get(target)
                    if widget is not None:
                        widget.refresh()

        if element_id == "fire":
            removed = apply_fire_self_bleed(combatant=attacker, turns_taken=attacker.turns_taken)
            attacker.pending_damage_multiplier *= fire_damage_multiplier_from_removed_hp(removed)
            if removed:
                attacker_widget.refresh()

        damage_multiplier = float(max(0.0, attacker.pending_damage_multiplier))
        attacker.pending_damage_multiplier = 1.0

        if not enemies:
            return

        # Prepare passive context (convert Combatants to Stats)
        allies_onsite_stats = [c.stats for c in allies_onsite]
        allies_offsite_stats = [c.stats for c in allies_offsite]
        all_allies_stats = allies_onsite_stats + allies_offsite_stats
        enemies_stats = [c.stats for c, _ in enemies]

        if element_id == "wind":
            # Check if TARGET_SELECTION passives want to redirect
            # Use first enemy as "original_target" for wind attacks
            original_target_stats = enemies[0][0].stats if enemies else None
            
            if original_target_stats:
                final_target_stats = apply_target_selection_passives(
                    attacker=attacker.stats,
                    original_target=original_target_stats,
                    available_targets=enemies_stats,
                    all_allies=all_allies_stats,
                    onsite_allies=allies_onsite_stats,
                    offsite_allies=allies_offsite_stats,
                    enemies=enemies_stats,
                )
                
                # If redirected to a different target, attack only that target
                if final_target_stats is not original_target_stats:
                    # Find the combatant and widget for the redirected target
                    target, target_widget = next(
                        (c, w) for c, w in enemies if c.stats is final_target_stats
                    )
                    
                    # Single target attack due to redirection
                    damage, crit, dodged = calculate_damage(
                        attacker.stats,
                        target.stats,
                        self._rng,
                        damage_multiplier=damage_multiplier,
                        all_allies=all_allies_stats,
                        onsite_allies=allies_onsite_stats,
                        offsite_allies=allies_offsite_stats,
                        enemies=enemies_stats,
                    )
                    if not dodged and damage > 0:
                        previous_hp = int(target.stats.hp)
                        target.stats.hp = max(0, previous_hp - int(damage))
                        self._arena.add_pulse(attacker_widget, target_widget, color, crit=crit)
                        self._set_status(f"{attacker.name} gusts {target.name} for {damage}{' (CRIT)' if crit else ''} (redirected)")
                        target_widget.refresh()
                        if previous_hp > 0 and target.stats.hp <= 0:
                            self._handle_combatant_fell(target)
                    if self._is_over():
                        self._on_battle_over()
                    return
            
            # Normal wind attack - hit all enemies
            target_count = len(enemies)
            total_damage = 0
            any_crit = False
            for target, target_widget in enemies:
                damage, crit, dodged = calculate_damage(
                    attacker.stats,
                    target.stats,
                    self._rng,
                    damage_multiplier=damage_multiplier,
                    all_allies=all_allies_stats,
                    onsite_allies=allies_onsite_stats,
                    offsite_allies=allies_offsite_stats,
                    enemies=enemies_stats,
                )
                if dodged:
                    continue
                damage = int(damage // max(1, target_count))
                if damage <= 0:
                    continue
                previous_hp = int(target.stats.hp)
                target.stats.hp = max(0, previous_hp - int(damage))
                total_damage += damage
                any_crit = any_crit or crit
                self._arena.add_pulse(attacker_widget, target_widget, color, crit=crit)
                target_widget.refresh()
                if previous_hp > 0 and target.stats.hp <= 0:
                    self._handle_combatant_fell(target)
            if total_damage > 0:
                self._set_status(f"{attacker.name} gusts for {total_damage}{' (CRIT)' if any_crit else ''}")
            if self._is_over():
                self._on_battle_over()
            return

        if element_id == "lightning":
            # Initial target selection
            initial_target, initial_widget = (
                self._rng.choice(enemies)
                if attacker_side == "party"
                else choose_weighted_target_by_aggro(enemies, self._rng)
            )
            
            # Apply TARGET_SELECTION passives to allow redirection
            final_target_stats = apply_target_selection_passives(
                attacker=attacker.stats,
                original_target=initial_target.stats,
                available_targets=enemies_stats,
                all_allies=all_allies_stats,
                onsite_allies=allies_onsite_stats,
                offsite_allies=allies_offsite_stats,
                enemies=enemies_stats,
            )
            
            # Find the combatant and widget for the final target
            target, target_widget = next(
                (c, w) for c, w in enemies if c.stats is final_target_stats
            )
            total_damage = 0
            any_crit = False
            landed = 0
            for _ in range(5):
                if target.stats.hp <= 0:
                    break
                damage, crit, dodged = calculate_damage(
                    attacker.stats,
                    target.stats,
                    self._rng,
                    damage_multiplier=damage_multiplier,
                    all_allies=all_allies_stats,
                    onsite_allies=allies_onsite_stats,
                    offsite_allies=allies_offsite_stats,
                    enemies=enemies_stats,
                )
                if dodged:
                    continue
                if damage <= 0:
                    continue
                landed += 1
                any_crit = any_crit or crit
                previous_hp = int(target.stats.hp)
                target.stats.hp = max(0, previous_hp - int(damage))
                total_damage += damage
                self._arena.add_pulse(attacker_widget, target_widget, color, crit=crit)
                target_widget.refresh()
                if previous_hp > 0 and target.stats.hp <= 0:
                    self._handle_combatant_fell(target)
                    break
            if landed:
                self._set_status(f"{attacker.name} zaps {target.name} {landed}x for {total_damage}{' (CRIT)' if any_crit else ''}")
            if self._is_over():
                self._on_battle_over()
            return

        # Initial target selection for generic attack
        initial_target, initial_widget = (
            self._rng.choice(enemies)
            if attacker_side == "party"
            else choose_weighted_target_by_aggro(enemies, self._rng)
        )
        
        # Apply TARGET_SELECTION passives to allow redirection
        final_target_stats = apply_target_selection_passives(
            attacker=attacker.stats,
            original_target=initial_target.stats,
            available_targets=enemies_stats,
            all_allies=all_allies_stats,
            onsite_allies=allies_onsite_stats,
            offsite_allies=allies_offsite_stats,
            enemies=enemies_stats,
        )
        
        # Find the combatant and widget for the final target
        target, target_widget = next(
            (c, w) for c, w in enemies if c.stats is final_target_stats
        )

        damage, crit, dodged = calculate_damage(
            attacker.stats,
            target.stats,
            self._rng,
            damage_multiplier=damage_multiplier,
            all_allies=all_allies_stats,
            onsite_allies=allies_onsite_stats,
            offsite_allies=allies_offsite_stats,
            enemies=enemies_stats,
        )
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
        if previous_hp > 0 and target.stats.hp <= 0:
            self._handle_combatant_fell(target)

        if self._is_over():
            self._on_battle_over()

    def _handle_combatant_fell(self, target: Combatant) -> None:
        self._set_status(f"{target.name} fell!")
        if target in self._party:
            self._apply_death_exp_debuff(target.char_id)
        elif target in self._foes:
            self._foe_kills += 1
            # Award coins based on foe level: coins_gained = 1 * foe_level
            foe_level = max(1, int(getattr(target.stats, "level", 1)))
            coins = 1 * foe_level
            self._coins_earned += coins

    def _set_status(self, message: str) -> None:
        message = str(message or "").replace("\n", " ").strip()
        self._status.setToolTip(message)

        limit = max(0, int(self._status_char_limit))
        if limit and len(message) > limit:
            clipped = max(0, limit - 1)
            message = f"{message[:clipped]}…"
        self._status.setText(message)

    def _on_battle_over(self) -> None:
        if self._battle_over:
            return
        self._battle_over = True
        
        # Reset stalemate tracking
        self._stalemate_stacks = 0
        self._stalemate_hp_ratio = None
        self._stalemate_tick_counter = 0

        party_alive = any(c.stats.hp > 0 for c in self._party)
        foes_alive = any(c.stats.hp > 0 for c in self._foes)
        victory = bool(party_alive and not foes_alive)
        defeat = bool(foes_alive and not party_alive)
        if party_alive and not foes_alive:
            self._award_gold(self._coins_earned, victory=True)
            self._set_status("Victory")
            self._apply_idle_exp_bonus()
        elif foes_alive and not party_alive:
            self._award_gold(self._coins_earned, victory=False)
            self._set_status("Defeat")
            self._apply_idle_exp_penalty()
            # Show defeat popup and schedule auto-return to main menu
            self._show_defeat_popup()
        else:
            self._set_status("Over")

        try:
            save = self._save_manager.load() or self._save or RunSave()
            should_reset = False
            
            # Calculate survival time for defeat health loss calculation
            survival_seconds = 0.0
            if defeat and save.battle_start_time > 0.0:
                survival_seconds = max(0.0, time.time() - save.battle_start_time)
            
            if victory:
                should_reset = apply_battle_result(save, victory=True)
            elif defeat:
                should_reset = apply_battle_result(save, victory=False, survival_seconds=survival_seconds)
            if should_reset:
                for char_id in sorted(set(self._onsite_ids + self._offsite_ids)):
                    plugin = self._plugin_by_id.get(char_id)
                    record_character_death(
                        save,
                        char_id=char_id,
                        base_stats_template=getattr(plugin, "base_stats", None),
                    )

                preserved_progress = reset_character_progress_for_new_run(dict(save.character_progress))
                preserved_initial_stats = dict(getattr(save, "character_initial_stats", {}) or {})
                preserved_stats = dict(preserved_initial_stats)
                preserved_deaths = dict(getattr(save, "character_deaths", {}) or {})
                preserved_bonus = float(save.idle_exp_bonus_seconds)
                preserved_penalty = float(save.idle_exp_penalty_seconds)

                save = new_run_save(
                    available_char_ids=[plugin.char_id for plugin in self._plugins],
                    rng=self._rng,
                )
                save.character_progress = preserved_progress
                save.character_stats = preserved_stats
                save.character_initial_stats = preserved_initial_stats
                save.character_deaths = preserved_deaths
                save.idle_exp_bonus_seconds = preserved_bonus
                save.idle_exp_penalty_seconds = preserved_penalty

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
        self._extend_idle_exp_timer(key="idle_exp_bonus_seconds", seconds=5 * 60)

    def _apply_idle_exp_penalty(self) -> None:
        self._extend_idle_exp_timer(key="idle_exp_penalty_seconds", seconds=15 * 60)

    def _award_gold(self, coins: int, victory: bool = True) -> None:
        """Award gold based on coins earned from foe defeats.
        
        Args:
            coins: Base coins earned from defeating foes (level-based)
            victory: If True, award full gold. If False, award 50% of base coins only.
        """
        gold = max(0, int(coins))
        if gold <= 0:
            return

        try:
            manager = SaveManager()
            save = manager.load() or RunSave()
            
            tokens = max(0, int(save.tokens))
            winstreak = max(0, int(getattr(save, "winstreak", 0)))
            bonus = calculate_gold_bonus(tokens, winstreak)
            
            if victory:
                # Full rewards on victory: base coins + bonus
                total_gold = gold + bonus
            else:
                # Partial rewards on loss: 50% of base coins + full bonus
                # Bonus helps struggling players, reduced base maintains win incentive
                loss_gold = max(1, gold // 2)  # Minimum 1 gold for killing any foes
                total_gold = loss_gold + bonus
            
            save.tokens = tokens + total_gold
            manager.save(save)
        except Exception:
            return

    def _extend_idle_exp_timer(self, *, key: str, seconds: int) -> None:
        try:
            manager = SaveManager()
            save = manager.load() or RunSave()
            current = float(max(0.0, getattr(save, key, 0.0)))
            setattr(save, key, current + max(0, int(seconds)))
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

            plugin = getattr(self, "_plugin_by_id", {}).get(char_id)
            record_character_death(
                save,
                char_id=char_id,
                base_stats_template=getattr(plugin, "base_stats", None),
            )

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

    def _on_back_clicked(self) -> None:
        if self._battle_over:
            self._finish()
            return
        
        try:
            save = self._save_manager.load() or self._save or RunSave()
            
            # Calculate survival time for retreat health loss calculation
            survival_seconds = 0.0
            if save.battle_start_time > 0.0:
                survival_seconds = max(0.0, time.time() - save.battle_start_time)
            
            should_reset = apply_battle_result(save, victory=False, survival_seconds=survival_seconds)
            
            if should_reset:
                for char_id in sorted(set(self._onsite_ids + self._offsite_ids)):
                    plugin = self._plugin_by_id.get(char_id)
                    record_character_death(
                        save,
                        char_id=char_id,
                        base_stats_template=getattr(plugin, "base_stats", None),
                    )
                
                preserved_progress = reset_character_progress_for_new_run(dict(save.character_progress))
                preserved_initial_stats = dict(getattr(save, "character_initial_stats", {}) or {})
                preserved_stats = dict(preserved_initial_stats)
                preserved_deaths = dict(getattr(save, "character_deaths", {}) or {})
                preserved_bonus = float(save.idle_exp_bonus_seconds)
                preserved_penalty = float(save.idle_exp_penalty_seconds)
                
                save = new_run_save(
                    available_char_ids=[plugin.char_id for plugin in self._plugins],
                    rng=self._rng,
                )
                save.character_progress = preserved_progress
                save.character_stats = preserved_stats
                save.character_initial_stats = preserved_initial_stats
                save.character_deaths = preserved_deaths
                save.idle_exp_bonus_seconds = preserved_bonus
                save.idle_exp_penalty_seconds = preserved_penalty
            
            self._save_manager.save(save)
            self._save = save
            self._refresh_party_hp()
        except Exception:
            pass
        
        self._finish()

    def _show_defeat_popup(self) -> None:
        """Show defeat popup with run statistics and auto-return to main menu.
        
        Displays:
        - Clear indication that the run has ended
        - Fight number reached
        - Foes defeated in final battle
        - Auto-returns to main menu after dismissal
        """
        fight_num = self._fight_number
        foes_killed = self._foe_kills
        
        # Build the message with run statistics
        message_lines = [
            "Your party has been defeated!",
            "",
            f"Fight reached: {fight_num}",
            f"Foes defeated in final battle: {foes_killed}",
            "",
            "The run has ended and been reset.",
            "You will return to the main menu."
        ]
        message = "\n".join(message_lines)
        
        # Create and show the popup
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Run Lost")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Connect to auto-return after popup is closed
        msg_box.finished.connect(self._on_defeat_popup_closed)
        
        # Show the popup (non-blocking)
        msg_box.show()
    
    def _on_defeat_popup_closed(self) -> None:
        """Handle defeat popup closure by returning to main menu."""
        # Schedule a brief delay before returning to menu for smoother transition
        QTimer.singleShot(100, self._finish)

    def _finish(self) -> None:
        try:
            self._battle_timer.stop()
        except Exception:
            pass
        self.finished.emit()
