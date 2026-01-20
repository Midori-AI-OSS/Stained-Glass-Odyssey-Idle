from __future__ import annotations

import time
import random

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

from endless_idler.combat.party_stats import apply_offsite_stat_share as apply_offsite_stat_share_to_stats
from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.combat.party_stats import party_scaling
from endless_idler.combat.stats import Stats


LOSS_EXP_MULTIPLIER = 0.5
WIN_EXP_MULTIPLIER = 4.0
OFFSITE_EXP_SHARE_PER_CHAR = 0.01
DEATH_EXP_DEBUFF_DURATION_SECONDS = 60 * 60
DEATH_EXP_DEBUFF_PER_STACK = 0.05
SHARED_EXP_ONSITE_MULTIPLIER = 0.75
SHARED_EXP_OFFSITE_MULTIPLIER = 1.5
IDLE_TICK_INTERVAL_SECONDS = 0.1


def calculate_rebirth_power(level: int) -> float:
    """
    Calculate the power value for rebirth mechanics.
    
    Formula: power = 1 + 0.15 * (L - 50)
    Where L is the current level at rebirth time (must be >= 50).
    
    This power value is used for:
    - EXP multiplier bonus calculation
    - Post-level-50 EXP scaling
    
    Args:
        level: Current character level at rebirth time (must be >= 50)
        
    Returns:
        The calculated power value as a float
    """
    level = max(50, int(level))
    return 1.0 + 0.15 * float(level - 50)


class IdleGameState(QObject):
    tick_update = Signal(int)

    def __init__(
        self,
        *,
        char_ids: list[str],
        offsite_ids: list[str] | None = None,
        party_level: int,
        stacks: dict[str, int],
        plugins_by_id: dict[str, object],
        rng: random.Random,
        progress_by_id: dict[str, dict[str, float | int]] | None = None,
        stats_by_id: dict[str, dict[str, float]] | None = None,
        initial_stats_by_id: dict[str, dict[str, float]] | None = None,
        exp_bonus_seconds: float = 0.0,
        exp_penalty_seconds: float = 0.0,
        exp_gain_scale: float = 1.0,
        advance_run_buffs: bool = True,
        shared_exp_percentage: int = 1,
        risk_reward_level: int = 0,
        battle_start_time: float = 0.0,
    ) -> None:
        super().__init__()
        self._char_ids = char_ids
        self._offsite_ids: list[str] = [str(item) for item in (offsite_ids or []) if item]
        self._party_level = party_level
        self._stacks = stacks
        self._plugins_by_id = plugins_by_id
        self._rng = rng
        self._progress_by_id = progress_by_id or {}
        self._stats_by_id = stats_by_id or {}
        self._initial_stats_by_id = initial_stats_by_id or {}
        self._exp_bonus_seconds = float(max(0.0, exp_bonus_seconds))
        self._exp_penalty_seconds = float(max(0.0, exp_penalty_seconds))
        self._exp_gain_scale = float(max(0.0, exp_gain_scale))
        self._advance_run_buffs = bool(advance_run_buffs)
        self._time = time.time
        self._offsite_exp_share = OFFSITE_EXP_SHARE_PER_CHAR
        self._battle_start_time = float(max(0.0, battle_start_time))

        self._tick_count = 0
        self._shared_exp_percentage = max(1, min(95, int(shared_exp_percentage)))
        self._risk_reward_level = max(0, min(150, int(risk_reward_level)))

        self._char_data: dict[str, dict] = {}
        for char_id in list(dict.fromkeys([*char_ids, *self._offsite_ids])):
            plugin = plugins_by_id.get(char_id)
            if not plugin:
                continue

            stack = max(1, int(stacks.get(char_id, 1)))
            stars = max(1, int(getattr(plugin, "stars", 1) or 1))
            plugin_base_stats = getattr(plugin, "base_stats", None)
            base_stats: dict[str, float] = dict(plugin_base_stats) if isinstance(plugin_base_stats, dict) else {}
            saved_stats = self._stats_by_id.get(char_id)
            if isinstance(saved_stats, dict):
                for key, raw in saved_stats.items():
                    if key in base_stats:
                        try:
                            base_stats[key] = float(raw)  # type: ignore[arg-type]
                        except (TypeError, ValueError):
                            continue

            initial_base_stats: dict[str, float]
            saved_initial = self._initial_stats_by_id.get(char_id)
            if isinstance(saved_initial, dict) and saved_initial:
                initial_base_stats = dict(saved_initial)
            else:
                initial_base_stats = dict(base_stats)

            saved = self._progress_by_id.get(char_id, {})
            level = 1
            exp = 0.0
            next_exp = 30.0
            exp_multiplier = 1.0
            req_multiplier = 1.0
            rebirths = 0
            prestige_count = 0
            rebirth_power = 1.0
            death_exp_debuff_stacks = 0
            death_exp_debuff_until = 0.0
            max_hp_level_bonus_version = 0
            if isinstance(saved, dict):
                try:
                    level = max(1, int(saved.get("level", 1)))
                except (TypeError, ValueError):
                    level = 1
                try:
                    exp = max(0.0, float(saved.get("exp", 0.0)))
                except (TypeError, ValueError):
                    exp = 0.0
                try:
                    next_exp = max(1.0, float(saved.get("next_exp", 30.0)))
                except (TypeError, ValueError):
                    next_exp = 30.0
                try:
                    exp_multiplier = max(0.0, float(saved.get("exp_multiplier", 1.0)))
                except (TypeError, ValueError):
                    exp_multiplier = 1.0
                try:
                    req_multiplier = max(0.0, float(saved.get("req_multiplier", 1.0)))
                except (TypeError, ValueError):
                    req_multiplier = 1.0
                try:
                    rebirths = max(0, int(saved.get("rebirths", 0)))
                except (TypeError, ValueError):
                    rebirths = 0
                try:
                    prestige_count = max(0, int(saved.get("prestige_count", 0)))
                except (TypeError, ValueError):
                    prestige_count = 0
                try:
                    rebirth_power = max(1.0, float(saved.get("rebirth_power", 1.0)))
                except (TypeError, ValueError):
                    rebirth_power = 1.0
                try:
                    death_exp_debuff_stacks = max(0, int(saved.get("death_exp_debuff_stacks", 0)))
                except (TypeError, ValueError):
                    death_exp_debuff_stacks = 0
                try:
                    death_exp_debuff_until = float(max(0.0, float(saved.get("death_exp_debuff_until", 0.0))))
                except (TypeError, ValueError):
                    death_exp_debuff_until = 0.0
                try:
                    max_hp_level_bonus_version = max(0, int(saved.get("max_hp_level_bonus_version", 0)))
                except (TypeError, ValueError):
                    max_hp_level_bonus_version = 0

            now = float(self._time())
            if death_exp_debuff_until and now >= death_exp_debuff_until:
                death_exp_debuff_stacks = 0
                death_exp_debuff_until = 0.0

            if max_hp_level_bonus_version < 1:
                intrinsic_hp = float(base_stats.get("max_hp", 1000.0))
                base_stats["max_hp"] = intrinsic_hp + max(0, level - 1) * 10.0
                max_hp_level_bonus_version = 1

            scale = party_scaling(party_level=self._party_level, stars=stars, stacks=stack)
            max_hp = max(1, int(float(base_stats.get("max_hp", 1000.0)) * scale))
            # Passive modifier formula: (stacks * 0.05) + 1.0
            # Provides 5% bonus per stack, starting at 1.05 with 1 stack
            passive_modifier = (stack * 0.05) + 1.0
            self._char_data[char_id] = {
                "level": level,
                "exp": exp,
                "next_exp": next_exp,
                "death_exp_debuff_stacks": death_exp_debuff_stacks,
                "death_exp_debuff_until": death_exp_debuff_until,
                "next_vitality_gain_level": 0,
                "next_mitigation_gain_level": 0,
                "hp": max_hp,
                "max_hp": max_hp,
                "combat_scale": scale,
                "base_stats": base_stats,
                "initial_base_stats": initial_base_stats,
                "stack": stack,
                "base_aggro": getattr(plugin, "base_aggro", None),
                "damage_reduction_passes": getattr(plugin, "damage_reduction_passes", None),
                "exp_multiplier": exp_multiplier,
                "req_multiplier": req_multiplier,
                "rebirths": rebirths,
                "prestige_count": prestige_count,
                "rebirth_power": rebirth_power,
                "max_hp_level_bonus_version": max_hp_level_bonus_version,
                "passive_modifier": passive_modifier,
            }

            if isinstance(saved, dict):
                try:
                    self._char_data[char_id]["next_vitality_gain_level"] = max(
                        0,
                        int(saved.get("next_vitality_gain_level", 0)),
                    )
                except (TypeError, ValueError):
                    self._char_data[char_id]["next_vitality_gain_level"] = 0
                try:
                    self._char_data[char_id]["next_mitigation_gain_level"] = max(
                        0,
                        int(saved.get("next_mitigation_gain_level", 0)),
                    )
                except (TypeError, ValueError):
                    self._char_data[char_id]["next_mitigation_gain_level"] = 0

            self._ensure_sparse_growth_schedule(char_id)

        self._apply_offsite_stat_share_to_onsite_hp()

    def _apply_offsite_stat_share_to_onsite_hp(self) -> None:
        if not self._char_ids:
            return
        if not self._offsite_ids:
            return

        reserves: list[Stats] = []
        for char_id in self._offsite_ids:
            data = self._char_data.get(char_id)
            plugin = self._plugins_by_id.get(char_id)
            if not data or plugin is None:
                continue
            base_stats = data.get("base_stats")
            if not isinstance(base_stats, dict):
                continue

            try:
                stack = max(1, int(data.get("stack", 1)))
            except (TypeError, ValueError):
                stack = 1
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
                    stacks=stack,
                    progress=progress,
                    saved_base_stats=base_stats,
                )
            )

        if not reserves:
            return

        party_stats: list[Stats] = []
        party_ids: list[str] = []
        for char_id in self._char_ids:
            data = self._char_data.get(char_id)
            plugin = self._plugins_by_id.get(char_id)
            if not data or plugin is None:
                continue
            base_stats = data.get("base_stats")
            if not isinstance(base_stats, dict):
                continue

            try:
                stack = max(1, int(data.get("stack", 1)))
            except (TypeError, ValueError):
                stack = 1
            stars = max(1, int(getattr(plugin, "stars", 1) or 1))
            progress = {
                "level": max(1, int(data.get("level", 1))),
                "exp": float(max(0.0, float(data.get("exp", 0.0)))),
                "exp_multiplier": float(max(0.0, float(data.get("exp_multiplier", 1.0)))),
                "max_hp_level_bonus_version": max(0, int(data.get("max_hp_level_bonus_version", 0))),
            }
            party_stats.append(
                build_scaled_character_stats(
                    plugin=plugin,
                    party_level=self._party_level,
                    stars=stars,
                    stacks=stack,
                    progress=progress,
                    saved_base_stats=base_stats,
                )
            )
            party_ids.append(char_id)

        if not party_stats:
            return

        apply_offsite_stat_share_to_stats(party=party_stats, reserves=reserves, share=0.10)

        for char_id, stats in zip(party_ids, party_stats, strict=False):
            data = self._char_data.get(char_id)
            if not data:
                continue
            try:
                old_max_hp = float(max(1.0, float(data.get("max_hp", 1.0))))
            except (TypeError, ValueError):
                old_max_hp = 1.0
            try:
                old_hp = float(max(0.0, float(data.get("hp", 0.0))))
            except (TypeError, ValueError):
                old_hp = 0.0

            ratio = old_hp / old_max_hp if old_max_hp > 0 else 1.0
            data["max_hp"] = max(1, int(stats.max_hp))
            data["hp"] = max(0.0, min(float(data["max_hp"]), ratio * float(data["max_hp"])))

    def rebirth_character(self, char_id: str) -> bool:
        data = self._char_data.get(char_id)
        if not data:
            return False

        level = max(1, int(data.get("level", 1)))
        if level < 50:
            return False

        old_level = level
        data["level"] = 1
        data["exp"] = 0.0
        data["next_vitality_gain_level"] = 0
        data["next_mitigation_gain_level"] = 0

        initial_base_stats = data.get("initial_base_stats")
        if isinstance(initial_base_stats, dict) and initial_base_stats:
            data["base_stats"] = dict(initial_base_stats)

        base_stats = data.get("base_stats")
        scale = float(max(0.0, float(data.get("combat_scale", 1.0))))
        intrinsic_hp = 1000.0
        if isinstance(base_stats, dict):
            intrinsic_hp = float(base_stats.get("max_hp", 1000.0))
        max_hp = max(1, int(intrinsic_hp * scale))
        data["max_hp"] = max_hp
        data["hp"] = max_hp
        self._ensure_sparse_growth_schedule(char_id)

        # Calculate power based on rebirth level
        # Formula: power = 1 + 0.15 * (L - 50)
        power = calculate_rebirth_power(old_level)
        data["rebirth_power"] = power
        
        # New EXP multiplier formula based on power
        # Formula: rebirth_exp_mult_gain = 0.01 + (power * 0.000005)
        exp_mult_gain = 0.01 + (power * 0.000005)
        data["exp_multiplier"] = float(max(0.0, float(data.get("exp_multiplier", 1.0)))) + exp_mult_gain
        
        data["rebirths"] = max(0, int(data.get("rebirths", 0))) + 1

        req_mult = float(data.get("req_multiplier", 1.0))
        data["next_exp"] = (1 * 30 * req_mult) * self._rng.uniform(0.95, 1.05)
        self._apply_offsite_stat_share_to_onsite_hp()
        return True

    def prestige_character(self, char_id: str) -> bool:
        """
        Apply prestige to a character, resetting their EXP multiplier and applying permanent stat gain bonuses.
        
        Requirements:
        - EXP multiplier must be >= 10
        
        Effects:
        1. EXP Multiplier Reset:
           new_exp_mult = max(0.01, 0.5 * (0.5 ** (prestige_count - 1)))
           - First prestige: 0.5
           - Second prestige: 0.25
           - Third prestige: 0.125
           - Fourth prestige: 0.0625
           - Fifth+ prestige: 0.01 (floor)
           
        2. Stat Gain Multiplier:
           Doubles stat gains per level-up (2 ** prestige_count)
           
        3. Post-Floor EXP Penalty:
           After EXP multiplier hits the floor (0.01),
           add 2x EXP required per level-up for each additional prestige
        
        Args:
            char_id: The character ID to prestige
            
        Returns:
            True if prestige was successful, False otherwise
        """
        data = self._char_data.get(char_id)
        if not data:
            return False
        
        # Check unlock condition: EXP multiplier >= 10
        exp_multiplier = float(max(0.0, float(data.get("exp_multiplier", 1.0))))
        if exp_multiplier < 10.0:
            return False
        
        # Increment prestige count
        prestige_count = max(0, int(data.get("prestige_count", 0)))
        prestige_count += 1
        data["prestige_count"] = prestige_count
        
        # Apply EXP multiplier reset formula
        # new_exp_mult = max(0.01, 0.5 * (0.5 ** (prestige_count - 1)))
        new_exp_mult = 0.5 * (0.5 ** (prestige_count - 1))
        new_exp_mult = max(0.01, new_exp_mult)
        data["exp_multiplier"] = new_exp_mult
        
        # Apply post-floor EXP penalty if needed
        # After floor (prestige_count >= 5), add 2x per additional prestige
        if new_exp_mult <= 0.01 and prestige_count >= 5:
            # Calculate how many prestiges past the floor
            prestiges_past_floor = prestige_count - 4  # First 4 prestiges get us to floor
            # Apply 2x EXP penalty for each prestige past floor
            penalty_multiplier = 2.0 ** prestiges_past_floor
            data["req_multiplier"] = float(max(0.0, float(data.get("req_multiplier", 1.0)))) * penalty_multiplier
        
        # Note: Stat gain multiplier (2^prestige_count) is applied during level-up
        # This is handled in the _apply_weighted_stat_upgrades method
        
        return True

    def process_tick(self) -> None:
        self._tick_count += 1
        self.tick_update.emit(self._tick_count)

        shared_exp_pct = self._shared_exp_percentage / 100.0
        onsite_reduction = shared_exp_pct if shared_exp_pct > 0 else 0.0
        onsite_mult = 1.0 - onsite_reduction

        exp_multiplier = self._current_exp_multiplier()
        idle_exp_mult = self._calculate_idle_exp_mult()
        total_onsite_base_gain = 0.0
        total_onsite_shared_gain = 0.0
        
        for char_id in self._char_ids:
            data = self._char_data.get(char_id)
            if not data:
                continue

            exp_mult = data["exp_multiplier"]
            base_gain = exp_mult

            if self._risk_reward_level > 0:
                base_gain *= (self._risk_reward_level + 1)

            base_gain *= exp_multiplier
            base_gain *= self._death_exp_debuff_multiplier(data)
            base_gain *= self._exp_gain_scale
            # Apply passive modifier from character stacks
            base_gain *= data.get("passive_modifier", 1.0)
            # Apply idle survival multiplier
            base_gain *= idle_exp_mult
            
            total_onsite_base_gain += base_gain
            onsite_gain = base_gain * onsite_mult
            data["exp"] += onsite_gain
            total_onsite_shared_gain += (base_gain - onsite_gain)

            # Since minimum shared_exp is now 1%, all players get 0.5 HP regain
            # Previously, 0% sharing gave 0.1 regain as a penalty
            regain = 0.1 if self._shared_exp_percentage == 1 else 0.5
            data["hp"] = min(data["max_hp"], data["hp"] + regain)

            if self._risk_reward_level > 0:
                char_level = max(1, int(data.get("level", 1)))
                speed_modifier = 0.5 * (1 - (0.00001 * (char_level * self._risk_reward_level)))
                speed_modifier = max(0.1, speed_modifier)
                ticks_per_drain = max(1, int(speed_modifier / IDLE_TICK_INTERVAL_SECONDS))
                
                if self._tick_count % ticks_per_drain == 0:
                    drain = 5.5 * self._risk_reward_level
                    data["hp"] = max(0.0, data["hp"] - drain)

            if data["exp"] >= data["next_exp"]:
                self._level_up(char_id)

        if self._offsite_ids and total_onsite_shared_gain > 0:
            num_offsite = len(self._offsite_ids)
            offsite_gain_per_char = total_onsite_shared_gain / num_offsite
            
            for char_id in self._offsite_ids:
                data = self._char_data.get(char_id)
                if not data:
                    continue
                
                normal_offsite_gain = total_onsite_base_gain * self._offsite_exp_share
                total_gain = offsite_gain_per_char + normal_offsite_gain
                
                # Apply offsite character modifiers exactly once per award.
                exp_mult = float(data.get("exp_multiplier", 1.0))
                passive_mod = data.get("passive_modifier", 1.0)
                data["exp"] += total_gain * exp_mult * self._death_exp_debuff_multiplier(data) * passive_mod
                data["hp"] = min(data["max_hp"], data["hp"] + 0.5)
                if data["exp"] >= data["next_exp"]:
                    self._level_up(char_id)

        if self._advance_run_buffs:
            dt = float(max(0.0, IDLE_TICK_INTERVAL_SECONDS))
            if dt > 0.0:
                self._exp_bonus_seconds = max(0.0, self._exp_bonus_seconds - dt)
                self._exp_penalty_seconds = max(0.0, self._exp_penalty_seconds - dt)

    def get_exp_gain_per_second(self, char_id: str) -> float:
        per_tick = self.get_exp_gain_per_tick(char_id)
        if IDLE_TICK_INTERVAL_SECONDS <= 0:
            return 0.0
        return per_tick / IDLE_TICK_INTERVAL_SECONDS

    def get_exp_gain_per_tick(self, char_id: str) -> float:
        data = self._char_data.get(char_id)
        if not data:
            return 0.0

        shared_exp_pct = self._shared_exp_percentage / 100.0
        onsite_reduction = shared_exp_pct if shared_exp_pct > 0 else 0.0
        onsite_mult = 1.0 - onsite_reduction
        
        exp_multiplier = self._current_exp_multiplier()
        idle_exp_mult = self._calculate_idle_exp_mult()

        if char_id in self._char_ids:
            exp_mult = float(data.get("exp_multiplier", 1.0))
            gain = exp_mult
            if self._risk_reward_level > 0:
                gain *= (self._risk_reward_level + 1)
            gain *= exp_multiplier
            gain *= self._death_exp_debuff_multiplier(data)
            gain *= self._exp_gain_scale
            # Apply passive modifier for display consistency
            gain *= data.get("passive_modifier", 1.0)
            # Apply idle survival multiplier
            gain *= idle_exp_mult
            return gain * onsite_mult

        if char_id in self._offsite_ids:
            total_onsite_base_gain = 0.0
            total_onsite_shared_gain = 0.0
            
            for onsite_id in self._char_ids:
                onsite_data = self._char_data.get(onsite_id)
                if not onsite_data:
                    continue
                onsite_mult_val = float(onsite_data.get("exp_multiplier", 1.0))
                onsite_gain = onsite_mult_val
                if self._risk_reward_level > 0:
                    onsite_gain *= (self._risk_reward_level + 1)
                onsite_gain *= exp_multiplier
                onsite_gain *= self._death_exp_debuff_multiplier(onsite_data)
                onsite_gain *= self._exp_gain_scale
                # Apply passive modifier from onsite character
                onsite_gain *= onsite_data.get("passive_modifier", 1.0)
                # Apply idle survival multiplier
                onsite_gain *= idle_exp_mult
                total_onsite_base_gain += onsite_gain
                shared_reduction = onsite_gain * onsite_reduction
                total_onsite_shared_gain += shared_reduction

            num_offsite = len(self._offsite_ids)
            if num_offsite > 0:
                offsite_gain_per_char = total_onsite_shared_gain / num_offsite
                normal_offsite_gain = total_onsite_base_gain * self._offsite_exp_share
                total_gain = offsite_gain_per_char + normal_offsite_gain
                # Apply offsite character modifiers exactly once per award.
                exp_mult = float(data.get("exp_multiplier", 1.0))
                passive_mod = data.get("passive_modifier", 1.0)
                return total_gain * exp_mult * self._death_exp_debuff_multiplier(data) * passive_mod

        return 0.0

    def _death_exp_debuff_multiplier(self, data: dict) -> float:
        now = float(self._time())
        try:
            until = float(max(0.0, float(data.get("death_exp_debuff_until", 0.0))))
        except (TypeError, ValueError):
            until = 0.0
        try:
            stacks = max(0, int(data.get("death_exp_debuff_stacks", 0)))
        except (TypeError, ValueError):
            stacks = 0

        if until and now >= until:
            data["death_exp_debuff_stacks"] = 0
            data["death_exp_debuff_until"] = 0.0
            return 1.0

        if not until or stacks <= 0:
            return 1.0

        penalty = DEATH_EXP_DEBUFF_PER_STACK * stacks
        return max(0.0, 1.0 - penalty)

    def _current_exp_multiplier(self) -> float:
        multiplier = 1.0
        if self._exp_bonus_seconds > 0.0:
            multiplier *= WIN_EXP_MULTIPLIER
        if self._exp_penalty_seconds > 0.0:
            multiplier *= LOSS_EXP_MULTIPLIER
        return multiplier
    
    def _calculate_idle_exp_mult(self) -> float:
        """
        Calculate idle exp multiplier based on survival time.
        Every 1 second the party is alive: idle_exp_mult *= 1.00001
        
        Returns:
            Current idle exp multiplier based on time survived
        """
        if self._battle_start_time <= 0.0:
            return 1.0
        
        current_time = float(self._time())
        seconds_survived = max(0.0, current_time - self._battle_start_time)
        
        # idle_exp_mult = 1.0 * (1.00001 ^ seconds_survived)
        # Using exponentiation for compounding effect
        return 1.00001 ** seconds_survived

    def export_run_buff_seconds(self) -> tuple[float, float]:
        return (float(max(0.0, self._exp_bonus_seconds)), float(max(0.0, self._exp_penalty_seconds)))

    def _level_up(self, char_id: str) -> None:
        data = self._char_data.get(char_id)
        if not data:
            return

        data["level"] = max(1, int(data.get("level", 1))) + 1
        data["exp"] = 0.0

        base_stats = data.get("base_stats")
        if isinstance(base_stats, dict):
            self._apply_weighted_stat_upgrades(char_id=char_id, base_stats=base_stats, level=int(data["level"]))
            self._apply_sparse_growth(char_id=char_id, base_stats=base_stats)
            base_stats["max_hp"] = float(base_stats.get("max_hp", 1000.0)) + 10.0

        scale = float(max(0.0, float(data.get("combat_scale", 1.0))))
        intrinsic_hp = 1000.0
        if isinstance(base_stats, dict):
            intrinsic_hp = float(base_stats.get("max_hp", 1000.0))
        data["max_hp"] = max(1, int(intrinsic_hp * scale))
        data["hp"] = data["max_hp"]

        level = data["level"]
        req_mult = data["req_multiplier"]
        
        # Post-level-50 EXP scaling using power-based formula
        # Every 5 levels after 50, multiply by: (1.25 + (0.05 * power))
        # The multiplier compounds at levels 55, 60, 65, 70, etc.
        if level >= 50:
            power = float(data.get("rebirth_power", 1.0))
            step_multiplier = 1.25 + (0.05 * power)
            steps = (level - 50) // 5
            tax = step_multiplier ** steps
        else:
            tax = 1.0
            
        data["next_exp"] = (level * 30 * req_mult * tax) * self._rng.uniform(0.95, 1.05)
        self._apply_offsite_stat_share_to_onsite_hp()

    def _apply_weighted_stat_upgrades(self, *, char_id: str, base_stats: dict[str, float], level: int) -> None:
        # Get prestige_count to apply stat gain multiplier
        data = self._char_data.get(char_id)
        prestige_count = 0
        if data:
            prestige_count = max(0, int(data.get("prestige_count", 0)))
        
        # Calculate prestige stat multiplier: 2^prestige_count
        prestige_multiplier = 2.0 ** prestige_count
        
        points = 1 + (max(1, int(level)) // 10)
        stat_keys = (
            "atk",
            "defense",
            "crit_mod",
            "dodge_odds",
            "regain",
        )

        weights: list[float] = []
        for key in stat_keys:
            value = float(base_stats.get(key, 0.1))
            if key == "crit_mod":
                weight = value / 10.0  # crit_mod values are higher (100+), scale down
            elif key in {"dodge_odds", "mitigation"}:
                weight = value * 100.0
            else:
                weight = value

            if char_id == "luna" and key == "dodge_odds":
                weight *= 5.0

            weights.append(max(0.1, float(weight)))

        # Base stat gain rate is 0.1% (1.001 multiplier)
        # Apply prestige multiplier to make each gain more impactful
        base_gain_rate = 0.001
        prestige_gain_rate = base_gain_rate * prestige_multiplier
        stat_multiplier = 1.0 + prestige_gain_rate
        
        for stat_name in self._rng.choices(list(stat_keys), weights=weights, k=points):
            current = float(base_stats.get(stat_name, 1.0))
            base_stats[stat_name] = current * stat_multiplier

    def _ensure_sparse_growth_schedule(self, char_id: str) -> None:
        data = self._char_data.get(char_id)
        if not data:
            return

        level = max(1, int(data.get("level", 1)))

        if max(0, int(data.get("next_vitality_gain_level", 0))) <= level:
            data["next_vitality_gain_level"] = level + self._rng.randint(10, 15)

        if max(0, int(data.get("next_mitigation_gain_level", 0))) <= level:
            data["next_mitigation_gain_level"] = level + self._rng.randint(10, 15)

    def _apply_sparse_growth(self, *, char_id: str, base_stats: dict[str, float]) -> None:
        data = self._char_data.get(char_id)
        if not data:
            return

        level = max(1, int(data.get("level", 1)))
        self._ensure_sparse_growth_schedule(char_id)

        for stat_key, schedule_key in (
            ("vitality", "next_vitality_gain_level"),
            ("mitigation", "next_mitigation_gain_level"),
        ):
            try:
                next_gain_level = max(0, int(data.get(schedule_key, 0)))
            except (TypeError, ValueError):
                next_gain_level = 0

            if next_gain_level <= 0:
                next_gain_level = level + self._rng.randint(10, 15)

            while level >= next_gain_level:
                current = float(base_stats.get(stat_key, 1.0))
                base_stats[stat_key] = current + 0.001 * self._rng.uniform(0.5, 1.5)
                next_gain_level += self._rng.randint(10, 15)

            data[schedule_key] = int(next_gain_level)

    def get_char_data(self, char_id: str) -> dict | None:
        return self._char_data.get(char_id)

    def get_party_level(self) -> int:
        return max(1, int(self._party_level))

    def export_progress(self) -> dict[str, dict[str, float | int]]:
        payload: dict[str, dict[str, float | int]] = {}
        for char_id, data in self._char_data.items():
            try:
                level = max(1, int(data.get("level", 1)))
            except (TypeError, ValueError):
                level = 1
            try:
                exp = max(0.0, float(data.get("exp", 0.0)))
            except (TypeError, ValueError):
                exp = 0.0
            try:
                next_exp = max(1.0, float(data.get("next_exp", 30.0)))
            except (TypeError, ValueError):
                next_exp = 30.0
            try:
                exp_multiplier = max(0.0, float(data.get("exp_multiplier", 1.0)))
            except (TypeError, ValueError):
                exp_multiplier = 1.0
            try:
                req_multiplier = max(0.0, float(data.get("req_multiplier", 1.0)))
            except (TypeError, ValueError):
                req_multiplier = 1.0
            try:
                rebirths = max(0, int(data.get("rebirths", 0)))
            except (TypeError, ValueError):
                rebirths = 0
            try:
                rebirth_power = max(1.0, float(data.get("rebirth_power", 1.0)))
            except (TypeError, ValueError):
                rebirth_power = 1.0
            try:
                prestige_count = max(0, int(data.get("prestige_count", 0)))
            except (TypeError, ValueError):
                prestige_count = 0
            try:
                death_exp_debuff_stacks = max(0, int(data.get("death_exp_debuff_stacks", 0)))
            except (TypeError, ValueError):
                death_exp_debuff_stacks = 0
            try:
                death_exp_debuff_until = float(max(0.0, float(data.get("death_exp_debuff_until", 0.0))))
            except (TypeError, ValueError):
                death_exp_debuff_until = 0.0

            payload[char_id] = {
                "level": level,
                "exp": exp,
                "next_exp": next_exp,
                "exp_multiplier": exp_multiplier,
                "req_multiplier": req_multiplier,
                "rebirths": rebirths,
                "rebirth_power": rebirth_power,
                "prestige_count": prestige_count,
                "death_exp_debuff_stacks": death_exp_debuff_stacks,
                "death_exp_debuff_until": death_exp_debuff_until,
                "next_vitality_gain_level": max(0, int(data.get("next_vitality_gain_level", 0))),
                "next_mitigation_gain_level": max(0, int(data.get("next_mitigation_gain_level", 0))),
                "max_hp_level_bonus_version": max(0, int(data.get("max_hp_level_bonus_version", 0))),
            }
        return payload

    def export_character_stats(self) -> dict[str, dict[str, float]]:
        payload: dict[str, dict[str, float]] = {}
        for char_id, data in self._char_data.items():
            stats = data.get("base_stats")
            if not isinstance(stats, dict):
                continue
            sanitized: dict[str, float] = {}
            for key, raw in stats.items():
                if not isinstance(key, str):
                    continue
                name = key.strip()
                if not name:
                    continue
                try:
                    sanitized[name] = float(raw)
                except (TypeError, ValueError):
                    continue
            payload[char_id] = sanitized
        return payload

    def export_initial_stats(self) -> dict[str, dict[str, float]]:
        payload: dict[str, dict[str, float]] = {}
        for char_id, data in self._char_data.items():
            stats = data.get("initial_base_stats")
            if not isinstance(stats, dict):
                continue
            sanitized: dict[str, float] = {}
            for key, raw in stats.items():
                if not isinstance(key, str):
                    continue
                name = key.strip()
                if not name:
                    continue
                try:
                    sanitized[name] = float(raw)
                except (TypeError, ValueError):
                    continue
            payload[char_id] = sanitized
        return payload

    def set_shared_exp_percentage(self, percentage: int) -> None:
        self._shared_exp_percentage = max(1, min(95, int(percentage)))

    def get_shared_exp_percentage(self) -> int:
        return self._shared_exp_percentage

    def set_risk_reward_level(self, level: int) -> None:
        self._risk_reward_level = max(0, min(150, int(level)))

    def get_risk_reward_level(self) -> int:
        return self._risk_reward_level
