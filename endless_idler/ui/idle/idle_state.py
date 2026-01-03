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
        shared_exp_percentage: int = 0,
        risk_reward_level: int = 0,
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

        self._tick_count = 0
        self._shared_exp_percentage = max(0, min(95, int(shared_exp_percentage)))
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
                "max_hp_level_bonus_version": max_hp_level_bonus_version,
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

        bonus = 0.25 * (1 + 0.01 * (old_level - 50))
        data["exp_multiplier"] = float(max(0.0, float(data.get("exp_multiplier", 1.0)))) + bonus
        data["req_multiplier"] = float(max(0.0, float(data.get("req_multiplier", 1.0)))) + 0.05
        data["rebirths"] = max(0, int(data.get("rebirths", 0))) + 1

        req_mult = float(data.get("req_multiplier", 1.0))
        data["next_exp"] = (1 * 30 * req_mult) * self._rng.uniform(0.95, 1.05)
        self._apply_offsite_stat_share_to_onsite_hp()
        return True

    def process_tick(self) -> None:
        self._tick_count += 1
        self.tick_update.emit(self._tick_count)

        shared_exp_pct = self._shared_exp_percentage / 100.0
        onsite_reduction = shared_exp_pct if shared_exp_pct > 0 else 0.0
        onsite_mult = 1.0 - onsite_reduction

        exp_multiplier = self._current_exp_multiplier()
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
            
            total_onsite_base_gain += base_gain
            onsite_gain = base_gain * onsite_mult
            data["exp"] += onsite_gain
            total_onsite_shared_gain += (base_gain - onsite_gain)

            regain = 0.1 if self._shared_exp_percentage == 0 else 0.5
            data["hp"] = min(data["max_hp"], data["hp"] + regain)

            if self._risk_reward_level > 0:
                char_level = max(1, int(data.get("level", 1)))
                speed_modifier = 0.5 * (1 - (0.00001 * (char_level * self._risk_reward_level)))
                speed_modifier = max(0.1, speed_modifier)
                ticks_per_drain = max(1, int(speed_modifier / IDLE_TICK_INTERVAL_SECONDS))
                
                if self._tick_count % ticks_per_drain == 0:
                    drain = 1.5 * self._risk_reward_level
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
                
                data["exp"] += total_gain * self._death_exp_debuff_multiplier(data)
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

        if char_id in self._char_ids:
            exp_mult = float(data.get("exp_multiplier", 1.0))
            gain = exp_mult
            if self._risk_reward_level > 0:
                gain *= (self._risk_reward_level + 1)
            gain *= exp_multiplier
            gain *= self._death_exp_debuff_multiplier(data)
            gain *= self._exp_gain_scale
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
                total_onsite_base_gain += onsite_gain
                shared_reduction = onsite_gain * onsite_reduction
                total_onsite_shared_gain += shared_reduction

            num_offsite = len(self._offsite_ids)
            if num_offsite > 0:
                offsite_gain_per_char = total_onsite_shared_gain / num_offsite
                normal_offsite_gain = total_onsite_base_gain * self._offsite_exp_share
                total_gain = offsite_gain_per_char + normal_offsite_gain
                return total_gain * self._death_exp_debuff_multiplier(data)

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
        tax = 1.5 ** ((level - 50) // 5) if level >= 50 else 1.0
        data["next_exp"] = (level * 30 * req_mult * tax) * self._rng.uniform(0.95, 1.05)
        self._apply_offsite_stat_share_to_onsite_hp()

    def _apply_weighted_stat_upgrades(self, *, char_id: str, base_stats: dict[str, float], level: int) -> None:
        points = 1 + (max(1, int(level)) // 10)
        stat_keys = (
            "atk",
            "defense",
            "crit_rate",
            "crit_damage",
            "dodge_odds",
            "regain",
        )

        weights: list[float] = []
        for key in stat_keys:
            value = float(base_stats.get(key, 0.1))
            if key in {"crit_rate", "dodge_odds", "mitigation"}:
                weight = value * 100.0
            elif key == "crit_damage":
                weight = value * 10.0
            else:
                weight = value

            if char_id == "luna" and key == "dodge_odds":
                weight *= 5.0

            weights.append(max(0.1, float(weight)))

        for stat_name in self._rng.choices(list(stat_keys), weights=weights, k=points):
            current = float(base_stats.get(stat_name, 1.0))
            base_stats[stat_name] = current * 1.001

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
        self._shared_exp_percentage = max(0, min(95, int(percentage)))

    def get_shared_exp_percentage(self) -> int:
        return self._shared_exp_percentage

    def set_risk_reward_level(self, level: int) -> None:
        self._risk_reward_level = max(0, min(150, int(level)))

    def get_risk_reward_level(self) -> int:
        return self._risk_reward_level
