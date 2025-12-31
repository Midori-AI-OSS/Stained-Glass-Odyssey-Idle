from __future__ import annotations

import time
import random

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal


LOSS_EXP_MULTIPLIER = 0.5
WIN_EXP_MULTIPLIER = 4.0
OFFSITE_EXP_SHARE_PER_CHAR = 0.01


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
            base_hp = 1000 + (stack - 1) * 100
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

        data["level"] += 1
        data["exp"] = 0
        data["max_hp"] += 10
        data["hp"] = data["max_hp"]

        level = data["level"]
        req_mult = data["req_multiplier"]
        tax = 1.5 ** ((level - 50) // 5) if level >= 50 else 1.0
        data["next_exp"] = (level * 30 * req_mult * tax) * self._rng.uniform(0.95, 1.05)

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
