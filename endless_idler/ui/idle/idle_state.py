from __future__ import annotations

import time
import random

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal


LOSS_EXP_MULTIPLIER = 0.5
WIN_EXP_MULTIPLIER = 4.0
OFFSITE_EXP_SHARE_PER_CHAR = 0.01
STACK_HP_BONUS = 100


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
        exp_bonus_until: float = 0.0,
        exp_penalty_until: float = 0.0,
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
        self._exp_bonus_until = float(max(0.0, exp_bonus_until))
        self._exp_penalty_until = float(max(0.0, exp_penalty_until))
        self._time = time.time
        self._offsite_exp_share = OFFSITE_EXP_SHARE_PER_CHAR

        self._tick_count = 0
        self._shared_exp = False
        self._risk_reward_enabled = False
        self._risk_reward_level = 1

        self._char_data: dict[str, dict] = {}
        for char_id in list(dict.fromkeys([*char_ids, *self._offsite_ids])):
            plugin = plugins_by_id.get(char_id)
            if not plugin:
                continue

            stack = max(1, int(stacks.get(char_id, 1)))
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

            base_hp = int(base_stats.get("max_hp", 1000.0)) + (stack - 1) * STACK_HP_BONUS
            saved = self._progress_by_id.get(char_id, {})
            level = 1
            exp = 0.0
            next_exp = 30.0
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

            max_hp = base_hp + max(0, level - 1) * 10
            self._char_data[char_id] = {
                "level": level,
                "exp": exp,
                "next_exp": next_exp,
                "hp": max_hp,
                "max_hp": max_hp,
                "base_stats": base_stats,
                "stack": stack,
                "base_aggro": getattr(plugin, "base_aggro", None),
                "damage_reduction_passes": getattr(plugin, "damage_reduction_passes", None),
                "exp_multiplier": 1.0,
                "req_multiplier": 1.0,
                "rebirths": 0,
            }

    def process_tick(self) -> None:
        self._tick_count += 1
        self.tick_update.emit(self._tick_count)

        shared_bonus = 0.0
        if self._shared_exp:
            for char_id in self._char_ids:
                data = self._char_data.get(char_id)
                if not data:
                    continue
                shared_bonus += data["exp_multiplier"] * 0.01

        exp_multiplier = self._current_exp_multiplier()
        total_onsite_gain = 0.0
        for char_id in self._char_ids:
            data = self._char_data.get(char_id)
            if not data:
                continue

            exp_mult = data["exp_multiplier"]
            gain = exp_mult + shared_bonus

            if self._risk_reward_enabled:
                gain *= (self._risk_reward_level + 1)

            gain *= exp_multiplier
            total_onsite_gain += gain
            data["exp"] += gain

            regain = 0.1 if not self._shared_exp else 0.5
            data["hp"] = min(data["max_hp"], data["hp"] + regain)

            if self._risk_reward_enabled and self._tick_count % 5 == 0:
                drain = 1.5 * self._risk_reward_level
                data["hp"] = max(0.0, data["hp"] - drain)

            if data["exp"] >= data["next_exp"]:
                self._level_up(char_id)

        if self._offsite_ids and total_onsite_gain > 0:
            offsite_gain = float(total_onsite_gain) * float(self._offsite_exp_share)
            for char_id in self._offsite_ids:
                data = self._char_data.get(char_id)
                if not data:
                    continue
                data["exp"] += offsite_gain
                data["hp"] = min(data["max_hp"], data["hp"] + 0.5)
                if data["exp"] >= data["next_exp"]:
                    self._level_up(char_id)

    def _current_exp_multiplier(self) -> float:
        now = float(self._time())
        multiplier = 1.0
        if now < self._exp_bonus_until:
            multiplier *= WIN_EXP_MULTIPLIER
        if now < self._exp_penalty_until:
            multiplier *= LOSS_EXP_MULTIPLIER
        return multiplier

    def _level_up(self, char_id: str) -> None:
        data = self._char_data.get(char_id)
        if not data:
            return

        data["level"] = max(1, int(data.get("level", 1))) + 1
        data["exp"] = 0.0

        base_stats = data.get("base_stats")
        if isinstance(base_stats, dict):
            self._apply_weighted_stat_upgrades(char_id=char_id, base_stats=base_stats, level=int(data["level"]))

        stack = max(1, int(data.get("stack", 1)))
        if isinstance(base_stats, dict):
            intrinsic_hp = int(float(base_stats.get("max_hp", 1000.0)))
        else:
            intrinsic_hp = 1000
        base_hp = intrinsic_hp + (stack - 1) * STACK_HP_BONUS
        data["max_hp"] = base_hp + max(0, int(data["level"]) - 1) * 10
        data["hp"] = data["max_hp"]

        level = data["level"]
        req_mult = data["req_multiplier"]
        tax = 1.5 ** ((level - 50) // 5) if level >= 50 else 1.0
        data["next_exp"] = (level * 30 * req_mult * tax) * self._rng.uniform(0.95, 1.05)

    def _apply_weighted_stat_upgrades(self, *, char_id: str, base_stats: dict[str, float], level: int) -> None:
        points = 1 + (max(1, int(level)) // 10)
        stat_keys = (
            "atk",
            "defense",
            "mitigation",
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

    def get_char_data(self, char_id: str) -> dict | None:
        return self._char_data.get(char_id)

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

            payload[char_id] = {"level": level, "exp": exp, "next_exp": next_exp}
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

    def set_shared_exp(self, enabled: bool) -> None:
        self._shared_exp = bool(enabled)

    def is_shared_exp_enabled(self) -> bool:
        return self._shared_exp

    def set_risk_reward_enabled(self, enabled: bool) -> None:
        self._risk_reward_enabled = bool(enabled)

    def is_risk_reward_enabled(self) -> bool:
        return self._risk_reward_enabled

    def set_risk_reward_level(self, level: int) -> None:
        self._risk_reward_level = max(1, int(level))

    def get_risk_reward_level(self) -> int:
        return self._risk_reward_level
