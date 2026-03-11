from __future__ import annotations

import math
import random
import threading
import time

from typing import Any

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

from endless_idler.blessings import discover_blessing_plugins
from endless_idler.blessings import get_default_blessing
from endless_idler.blessings.lunar_blessing import get_lunar_progress_per_tick
from endless_idler.blessings.plugin import BlessingPlugin
from endless_idler.characters.placement_rules import MISPLACED_EXP_MULTIPLIER
from endless_idler.characters.placement_rules import MISPLACED_STAT_MULTIPLIER
from endless_idler.characters.placement_rules import plugin_lane_mismatch
from endless_idler.combat.damage_types import normalize_damage_type_id
from endless_idler.combat.party_stats import apply_base_stat_multiplier
from endless_idler.combat.party_stats import (
    apply_offsite_stat_share as apply_offsite_stat_share_to_stats,
)
from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.combat.party_stats import party_scaling
from endless_idler.combat.stats import Stats
from endless_idler.progression import calculate_prestige_stat_gain_rate
from endless_idler.progression import calculate_rebirth_exp_mult_gain
from endless_idler.progression import calculate_rebirth_exp_tax
from endless_idler.progression import calculate_rebirth_power


LOSS_EXP_MULTIPLIER = 0.5
WIN_EXP_MULTIPLIER = 4.0
OFFSITE_EXP_SHARE_PER_CHAR = 0.01
DEATH_EXP_DEBUFF_DURATION_SECONDS = 60 * 60
DEATH_EXP_DEBUFF_PER_STACK = 0.05
SHARED_EXP_ONSITE_MULTIPLIER = 0.75
SHARED_EXP_OFFSITE_MULTIPLIER = 1.5
IDLE_TICK_INTERVAL_SECONDS = 1.0 / 30.0
MIN_EXP_GAIN_PER_TICK = 0.0001
IDLE_BLESSING_STEP_MULTIPLIER = 1.025 ** (1.0 / 6.0)
SHARD_ROLL_INTERVAL_TICKS = 30
SHARD_BAR_CYCLE_TICKS = 300
SHARD_BASE_CHANCE_PERCENT = 0.0001
SHARD_EXP_SMOOTHING_SECONDS = 60.0
SHARD_DAMPENER_START_EXP_PER_SECOND = 1000.0
SHARD_DAMPENER_BUCKET_SIZE = 100.0
SHARD_DAMPENER_SCALE = 15000.0
SHARD_ALLOWED_TYPES = frozenset(
    {
        "fire",
        "ice",
        "wind",
        "lightning",
        "light",
        "dark",
    }
)
SHARD_ITEM_ID_BY_TYPE = {key: f"{key}_shard" for key in SHARD_ALLOWED_TYPES}
SHARD_EMA_ALPHA = 1.0 - math.exp(
    -IDLE_TICK_INTERVAL_SECONDS / SHARD_EXP_SMOOTHING_SECONDS
)


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
        inventory: dict[str, int] | None = None,
        exp_bonus_seconds: float = 0.0,
        exp_penalty_seconds: float = 0.0,
        exp_gain_scale: float = 1.0,
        advance_run_buffs: bool = True,
        shared_exp_percentage: int = 1,
        risk_reward_level: int = 0,
        battle_start_time: float = 0.0,
        blessings_data: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        super().__init__()
        self._char_ids = char_ids
        self._offsite_ids: list[str] = [
            str(item) for item in (offsite_ids or []) if item
        ]
        self._party_level = party_level
        self._stacks = stacks
        self._plugins_by_id = plugins_by_id
        self._misplaced_onsite_ids: set[str] = {
            char_id
            for char_id in self._char_ids
            if plugin_lane_mismatch(
                lane="onsite", plugin=self._plugins_by_id.get(char_id)
            )
        }
        self._misplaced_offsite_ids: set[str] = {
            char_id
            for char_id in self._offsite_ids
            if plugin_lane_mismatch(
                lane="offsite", plugin=self._plugins_by_id.get(char_id)
            )
        }
        self._rng = rng
        self._progress_by_id = progress_by_id or {}
        self._stats_by_id = stats_by_id or {}
        self._initial_stats_by_id = initial_stats_by_id or {}
        self._inventory = inventory if isinstance(inventory, dict) else {}
        self._exp_bonus_seconds = float(max(0.0, exp_bonus_seconds))
        self._exp_penalty_seconds = float(max(0.0, exp_penalty_seconds))
        self._exp_gain_scale = float(max(0.0, exp_gain_scale))
        self._advance_run_buffs = bool(advance_run_buffs)
        self._time = time.time
        self._offsite_exp_share = OFFSITE_EXP_SHARE_PER_CHAR
        self._battle_start_time = float(max(0.0, battle_start_time))
        self._elapsed_seconds = float(max(0.0, battle_start_time))
        self._blessings_data = blessings_data if blessings_data else {}
        self._damage_blessing_id_by_type = self._build_damage_blessing_id_by_type()
        self._lock = threading.RLock()

        self._tick_count = 0
        self._shared_exp_percentage = max(1, min(95, int(shared_exp_percentage)))
        self._risk_reward_level = max(0, min(150, int(risk_reward_level)))

        self._char_data: dict[str, dict[str, Any]] = {}
        for char_id in list(dict.fromkeys([*char_ids, *self._offsite_ids])):
            plugin = plugins_by_id.get(char_id)
            if not plugin:
                continue

            stack = max(1, int(stacks.get(char_id, 1)))
            stars = max(1, int(getattr(plugin, "stars", 1) or 1))
            plugin_base_stats = getattr(plugin, "base_stats", None)
            base_stats: dict[str, float] = (
                dict(plugin_base_stats) if isinstance(plugin_base_stats, dict) else {}
            )
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
            shard_bar_ticks = 0
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
                    death_exp_debuff_stacks = max(
                        0, int(saved.get("death_exp_debuff_stacks", 0))
                    )
                except (TypeError, ValueError):
                    death_exp_debuff_stacks = 0
                try:
                    death_exp_debuff_until = float(
                        max(0.0, float(saved.get("death_exp_debuff_until", 0.0)))
                    )
                except (TypeError, ValueError):
                    death_exp_debuff_until = 0.0
                try:
                    max_hp_level_bonus_version = max(
                        0, int(saved.get("max_hp_level_bonus_version", 0))
                    )
                except (TypeError, ValueError):
                    max_hp_level_bonus_version = 0
                try:
                    shard_bar_ticks = max(0, int(saved.get("shard_bar_ticks", 0)))
                except (TypeError, ValueError):
                    shard_bar_ticks = 0

            now = float(self._time())
            if death_exp_debuff_until and now >= death_exp_debuff_until:
                death_exp_debuff_stacks = 0
                death_exp_debuff_until = 0.0

            if max_hp_level_bonus_version < 1:
                intrinsic_hp = float(base_stats.get("max_hp", 1000.0))
                base_stats["max_hp"] = intrinsic_hp + max(0, level - 1) * 10.0
                max_hp_level_bonus_version = 1

            scale = party_scaling(
                party_level=self._party_level, stars=stars, stacks=stack
            )
            max_hp = max(1, int(float(base_stats.get("max_hp", 1000.0)) * scale))
            # Passive modifier formula: (stacks * 0.05) + 1.0
            # Provides 5% bonus per stack, starting at 1.05 with 1 stack
            passive_modifier = (stack * 0.05) + 1.0
            reward_types = self._reward_types_for_char(char_id)
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
                "damage_reduction_passes": getattr(
                    plugin, "damage_reduction_passes", None
                ),
                "exp_multiplier": exp_multiplier,
                "req_multiplier": req_multiplier,
                "rebirths": rebirths,
                "prestige_count": prestige_count,
                "rebirth_power": rebirth_power,
                "max_hp_level_bonus_version": max_hp_level_bonus_version,
                "passive_modifier": passive_modifier,
                "shard_bar_ticks": shard_bar_ticks % SHARD_BAR_CYCLE_TICKS,
                "shard_exp_s_ema": 0.0,
                "shard_reward_types": reward_types,
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

    def _progression_stars_for_char(self, char_id: str) -> int:
        plugin = self._plugins_by_id.get(char_id)
        if plugin is None:
            raise ValueError(f"Missing character plugin metadata for {char_id!r}.")
        return int(getattr(plugin, "stars", 0) or 0)

    def _reward_types_for_char(self, char_id: str) -> tuple[str, ...]:
        plugin = self._plugins_by_id.get(char_id)
        if plugin is None:
            return tuple()

        raw = normalize_damage_type_id(
            str(getattr(plugin, "damage_type_id", "generic") or "generic")
        )
        if not raw:
            return tuple()

        options: list[str] = []
        if "/" in raw:
            for part in raw.split("/"):
                normalized = normalize_damage_type_id(part)
                if normalized in SHARD_ALLOWED_TYPES and normalized not in options:
                    options.append(normalized)
        elif raw in SHARD_ALLOWED_TYPES:
            options.append(raw)
        elif raw == "generic":
            # Generic damage types can earn all 6 elemental shard types
            options.extend(sorted(SHARD_ALLOWED_TYPES))

        return tuple(options)

    def _shard_roll_percent(self, *, exp_s: float) -> float:
        base = float(SHARD_BASE_CHANCE_PERCENT)
        bucket = max(
            0,
            int(
                math.floor(
                    (float(exp_s) - SHARD_DAMPENER_START_EXP_PER_SECOND)
                    / SHARD_DAMPENER_BUCKET_SIZE
                )
            ),
        )
        denominator = 1.0 + (SHARD_DAMPENER_SCALE * bucket)
        if denominator <= 0.0:
            return base
        effective = base / denominator
        return max(0.0, min(base, effective))

    def _select_reward_shard_type(self, *, data: dict[str, Any]) -> str | None:
        raw_types = data.get("shard_reward_types")
        if not isinstance(raw_types, tuple):
            return None
        if len(raw_types) <= 0:
            return None
        if len(raw_types) == 1:
            return str(raw_types[0])
        selected = self._rng.choice(list(raw_types))
        return str(selected)

    def _award_shard(self, *, data: dict[str, Any]) -> None:
        reward_type = self._select_reward_shard_type(data=data)
        if not reward_type:
            return
        item_id = SHARD_ITEM_ID_BY_TYPE.get(reward_type)
        if not item_id:
            return
        current = max(0, int(self._inventory.get(item_id, 0)))
        self._inventory[item_id] = current + 1

    def _update_shard_progress(
        self,
        *,
        data: dict[str, Any],
        awarded_exp: float,
        roll_ready: bool,
    ) -> None:
        reward_types = data.get("shard_reward_types")
        if not isinstance(reward_types, tuple) or len(reward_types) <= 0:
            return

        awarded = max(0.0, float(awarded_exp))
        if IDLE_TICK_INTERVAL_SECONDS > 0.0:
            awarded_eps = awarded / IDLE_TICK_INTERVAL_SECONDS
        else:
            awarded_eps = 0.0

        try:
            previous_ema = max(0.0, float(data.get("shard_exp_s_ema", 0.0)))
        except (TypeError, ValueError):
            previous_ema = 0.0
        ema = previous_ema + (SHARD_EMA_ALPHA * (awarded_eps - previous_ema))
        data["shard_exp_s_ema"] = max(0.0, float(ema))

        if not roll_ready or awarded <= 0.0:
            return

        chance_percent = self._shard_roll_percent(exp_s=float(data["shard_exp_s_ema"]))
        if chance_percent <= 0.0:
            return
        if self._rng.random() >= (chance_percent / 100.0):
            return

        try:
            ticks = max(0, int(data.get("shard_bar_ticks", 0)))
        except (TypeError, ValueError):
            ticks = 0
        ticks += 1
        while ticks >= SHARD_BAR_CYCLE_TICKS:
            ticks -= SHARD_BAR_CYCLE_TICKS
            self._award_shard(data=data)
        data["shard_bar_ticks"] = ticks

    def _is_misplaced_character(self, char_id: str) -> bool:
        return (
            char_id in self._misplaced_onsite_ids
            or char_id in self._misplaced_offsite_ids
        )

    def _exp_multiplier_for_char(self, char_id: str) -> float:
        if self._is_misplaced_character(char_id):
            return MISPLACED_EXP_MULTIPLIER
        return 1.0

    def _stat_multiplier_for_char(self, char_id: str) -> float:
        if self._is_misplaced_character(char_id):
            return MISPLACED_STAT_MULTIPLIER
        return 1.0

    def _apply_offsite_stat_share_to_onsite_hp(self) -> None:
        if not self._char_ids and not self._offsite_ids:
            return

        reserves: list[Stats] = []
        reserve_snapshots: list[tuple[dict[str, Any], Stats]] = []
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
                "exp_multiplier": float(
                    max(0.0, float(data.get("exp_multiplier", 1.0)))
                ),
                "max_hp_level_bonus_version": max(
                    0, int(data.get("max_hp_level_bonus_version", 0))
                ),
                "rebirths": max(0, int(data.get("rebirths", 0))),
            }
            reserve_stats = build_scaled_character_stats(
                plugin=plugin,
                party_level=self._party_level,
                stars=stars,
                stacks=stack,
                progress=progress,
                saved_base_stats=base_stats,
            )
            apply_base_stat_multiplier(
                stats=reserve_stats,
                multiplier=self._stat_multiplier_for_char(char_id),
            )
            reserves.append(reserve_stats)
            reserve_snapshots.append((data, reserve_stats))

        party_stats: list[Stats] = []
        party_snapshots: list[tuple[dict[str, Any], Stats]] = []
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
                "exp_multiplier": float(
                    max(0.0, float(data.get("exp_multiplier", 1.0)))
                ),
                "max_hp_level_bonus_version": max(
                    0, int(data.get("max_hp_level_bonus_version", 0))
                ),
                "rebirths": max(0, int(data.get("rebirths", 0))),
            }
            party_stats_item = build_scaled_character_stats(
                plugin=plugin,
                party_level=self._party_level,
                stars=stars,
                stacks=stack,
                progress=progress,
                saved_base_stats=base_stats,
            )
            apply_base_stat_multiplier(
                stats=party_stats_item,
                multiplier=self._stat_multiplier_for_char(char_id),
            )
            party_stats.append(party_stats_item)
            party_snapshots.append((data, party_stats_item))

        if party_stats and reserves:
            apply_offsite_stat_share_to_stats(
                party=party_stats, reserves=reserves, share=0.10
            )

        for data, stats in [*party_snapshots, *reserve_snapshots]:
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
            data["hp"] = max(
                0.0, min(float(data["max_hp"]), ratio * float(data["max_hp"]))
            )

    def rebirth_character(self, char_id: str) -> bool:
        with self._lock:
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

            power = calculate_rebirth_power(old_level)
            data["rebirth_power"] = power

            exp_mult_gain = calculate_rebirth_exp_mult_gain(
                power=power,
                stars=self._progression_stars_for_char(char_id),
            )
            data["exp_multiplier"] = (
                float(max(0.0, float(data.get("exp_multiplier", 1.0)))) + exp_mult_gain
            )

            data["rebirths"] = max(0, int(data.get("rebirths", 0))) + 1

            req_mult = float(data.get("req_multiplier", 1.0))
            lunar_req_mult = self._lunar_exp_requirement_multiplier()
            data["next_exp"] = (
                1 * 30 * req_mult * lunar_req_mult
            ) * self._rng.uniform(0.95, 1.05)
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
        with self._lock:
            data = self._char_data.get(char_id)
            if not data:
                return False

            exp_multiplier = float(max(0.0, float(data.get("exp_multiplier", 1.0))))
            if exp_multiplier < 10.0:
                return False

            prestige_count = max(0, int(data.get("prestige_count", 0)))
            prestige_count += 1
            data["prestige_count"] = prestige_count

            new_exp_mult = 0.5 * (0.5 ** (prestige_count - 1))
            new_exp_mult = max(0.01, new_exp_mult)
            data["exp_multiplier"] = new_exp_mult

            if new_exp_mult <= 0.01 and prestige_count >= 5:
                prestiges_past_floor = prestige_count - 4
                penalty_multiplier = 2.0**prestiges_past_floor
                data["req_multiplier"] = (
                    float(max(0.0, float(data.get("req_multiplier", 1.0))))
                    * penalty_multiplier
                )

            return True

    def process_tick(self) -> dict[str, Any]:
        with self._lock:
            self._tick_count += 1
            tick_count = self._tick_count
            dt = float(max(0.0, IDLE_TICK_INTERVAL_SECONDS))
            self._elapsed_seconds += dt
            self._process_blessing_ticks(delta_seconds=dt)

            roll_ready = self._tick_count % SHARD_ROLL_INTERVAL_TICKS == 0

            exp_multiplier = self._current_exp_multiplier()
            idle_exp_mult = self._calculate_idle_exp_mult()
            (
                onsite_recipients,
                offsite_recipients,
                onsite_allocated_share,
                offsite_drip_share,
                offsite_baseline_bonus,
            ) = self._compute_exp_pool_distribution(
                exp_multiplier=exp_multiplier,
                idle_exp_mult=idle_exp_mult,
            )

            for char_id, data in onsite_recipients:
                recipient_modifier = self._recipient_exp_modifier_for_char(
                    char_id=char_id,
                    data=data,
                )
                awarded = onsite_allocated_share * recipient_modifier
                awarded_gain = self._apply_min_exp_gain_floor(awarded)
                data["exp"] += awarded_gain
                self._update_shard_progress(
                    data=data,
                    awarded_exp=awarded_gain,
                    roll_ready=roll_ready,
                )

                regain = 0.1 if self._shared_exp_percentage == 1 else 0.5
                data["hp"] = min(data["max_hp"], data["hp"] + regain)

                if self._risk_reward_level > 0:
                    char_level = max(1, int(data.get("level", 1)))
                    speed_modifier = 0.5 * (
                        1 - (0.00001 * (char_level * self._risk_reward_level))
                    )
                    speed_modifier = max(0.1, speed_modifier)
                    ticks_per_drain = max(
                        1, int(speed_modifier / IDLE_TICK_INTERVAL_SECONDS)
                    )

                    if self._tick_count % ticks_per_drain == 0:
                        drain = 5.5 * self._risk_reward_level
                        data["hp"] = max(0.0, data["hp"] - drain)

                if data["exp"] >= data["next_exp"]:
                    self._level_up(char_id)

            if offsite_recipients:
                offsite_allocated_share = offsite_drip_share + offsite_baseline_bonus
                for char_id, data in offsite_recipients:
                    recipient_modifier = self._recipient_exp_modifier_for_char(
                        char_id=char_id,
                        data=data,
                    )
                    awarded_gain = offsite_allocated_share * recipient_modifier
                    awarded_gain = self._apply_min_exp_gain_floor(awarded_gain)
                    data["exp"] += awarded_gain
                    self._update_shard_progress(
                        data=data,
                        awarded_exp=awarded_gain,
                        roll_ready=roll_ready,
                    )
                    data["hp"] = min(data["max_hp"], data["hp"] + 0.5)
                    if data["exp"] >= data["next_exp"]:
                        self._level_up(char_id)

            if self._advance_run_buffs and dt > 0.0:
                self._exp_bonus_seconds = max(0.0, self._exp_bonus_seconds - dt)
                self._exp_penalty_seconds = max(0.0, self._exp_penalty_seconds - dt)
            snapshot = self.export_runtime_snapshot()
        self.tick_update.emit(tick_count)
        return snapshot

    def get_exp_gain_per_second(self, char_id: str) -> float:
        per_tick = self.get_exp_gain_per_tick(char_id)
        if IDLE_TICK_INTERVAL_SECONDS <= 0:
            return 0.0
        return per_tick / IDLE_TICK_INTERVAL_SECONDS

    def get_exp_gain_per_tick(self, char_id: str) -> float:
        data = self._char_data.get(char_id)
        if not data:
            return 0.0

        exp_multiplier = self._current_exp_multiplier()
        idle_exp_mult = self._calculate_idle_exp_mult()
        (
            onsite_recipients,
            offsite_recipients,
            onsite_allocated_share,
            offsite_drip_share,
            offsite_baseline_bonus,
        ) = self._compute_exp_pool_distribution(
            exp_multiplier=exp_multiplier,
            idle_exp_mult=idle_exp_mult,
        )

        if char_id in self._char_ids:
            if not any(
                recipient_id == char_id for recipient_id, _ in onsite_recipients
            ):
                return 0.0
            recipient_modifier = self._recipient_exp_modifier_for_char(
                char_id=char_id,
                data=data,
            )
            gain = onsite_allocated_share * recipient_modifier
            return self._apply_min_exp_gain_floor(gain)

        if char_id in self._offsite_ids:
            if not any(
                recipient_id == char_id for recipient_id, _ in offsite_recipients
            ):
                return 0.0
            offsite_allocated_share = offsite_drip_share + offsite_baseline_bonus
            recipient_modifier = self._recipient_exp_modifier_for_char(
                char_id=char_id,
                data=data,
            )
            awarded_gain = offsite_allocated_share * recipient_modifier
            return self._apply_min_exp_gain_floor(awarded_gain)

        return 0.0

    def _death_exp_debuff_multiplier(self, data: dict[str, Any]) -> float:
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
        return self.get_idle_blessing_multiplier()

    def _shared_exp_fraction(self, *, offsite_recipient_count: int) -> float:
        if offsite_recipient_count <= 0:
            return 0.0
        shared_exp_pct = self._shared_exp_percentage / 100.0
        if shared_exp_pct <= 0.0:
            return 0.0
        return shared_exp_pct

    def _onsite_raw_pool_unit_gain(
        self,
        *,
        exp_multiplier: float,
        idle_exp_mult: float,
    ) -> float:
        gain = 1.0
        if self._risk_reward_level > 0:
            gain *= self._risk_reward_level + 1
        gain *= exp_multiplier
        gain *= self._exp_gain_scale
        gain *= idle_exp_mult
        return max(0.0, gain)

    def _recipient_exp_modifier_for_char(
        self,
        *,
        char_id: str,
        data: dict[str, Any],
    ) -> float:
        modifier = float(data.get("exp_multiplier", 1.0))
        modifier *= self._death_exp_debuff_multiplier(data)
        modifier *= float(data.get("passive_modifier", 1.0))
        modifier *= self._exp_multiplier_for_char(char_id)
        modifier *= self._damage_type_blessing_bonus(char_id)
        modifier *= self._lunar_exp_gain_bonus_multiplier()
        return max(0.0, modifier)

    def _lunar_exp_gain_bonus_multiplier(self) -> float:
        progress = self._lunar_progress_data()
        if progress is None:
            return 1.0
        gain_pct = max(0.0, float(progress.get("exp_gain_pct", 0.0)))
        return max(0.0, 1.0 + (gain_pct / 100.0))

    def _lunar_exp_requirement_multiplier(self) -> float:
        progress = self._lunar_progress_data()
        if progress is None:
            return 1.0
        reduction_pct = max(0.0, float(progress.get("exp_reduction_pct", 0.0)))
        return max(0.01, 1.0 - (reduction_pct / 100.0))

    def _lunar_progress_data(self) -> dict[str, float] | None:
        lunar_data = self._blessings_data.get("lunar_blessing", {})
        if not isinstance(lunar_data, dict):
            return None
        if not bool(lunar_data.get("unlocked", True)):
            return None
        try:
            steps = max(0, int(lunar_data.get("steps", 0)))
        except (TypeError, ValueError):
            return None
        return get_lunar_progress_per_tick(steps)

    def _damage_type_blessing_bonus(self, char_id: str) -> float:
        plugin = self._plugins_by_id.get(char_id)
        if plugin is None:
            return 1.0
        damage_type_id = normalize_damage_type_id(
            str(getattr(plugin, "damage_type_id", "generic") or "generic")
        )
        if not damage_type_id:
            return 1.0
        bonus = 1.0
        if damage_type_id == "generic":
            for blessing_id in self._damage_blessing_id_by_type.values():
                blessing_info = self._blessings_data.get(blessing_id, {})
                if not isinstance(blessing_info, dict):
                    continue
                if not blessing_info.get("unlocked", False):
                    continue
                steps = int(blessing_info.get("steps", 0))
                bonus += steps * 0.0001
        else:
            blessing_id = self._damage_blessing_id_by_type.get(damage_type_id)
            if not blessing_id:
                return bonus
            blessing_info = self._blessings_data.get(blessing_id, {})
            if isinstance(blessing_info, dict) and blessing_info.get("unlocked", False):
                steps = int(blessing_info.get("steps", 0))
                bonus += steps * 0.0001
        return bonus

    @staticmethod
    def _build_damage_blessing_id_by_type() -> dict[str, str]:
        mapping: dict[str, str] = {}
        for blessing in discover_blessing_plugins():
            target_damage_type = getattr(blessing, "target_damage_type", None)
            if not isinstance(target_damage_type, str):
                continue
            damage_type_id = normalize_damage_type_id(target_damage_type)
            blessing_id = str(getattr(blessing, "blessing_id", "") or "").strip()
            if not damage_type_id or not blessing_id:
                continue
            mapping[damage_type_id] = blessing_id
        return mapping

    def _exp_recipients(
        self,
    ) -> tuple[list[tuple[str, dict[str, Any]]], list[tuple[str, dict[str, Any]]]]:
        onsite_recipients: list[tuple[str, dict[str, Any]]] = []
        for char_id in self._char_ids:
            data = self._char_data.get(char_id)
            if data:
                onsite_recipients.append((char_id, data))

        offsite_recipients: list[tuple[str, dict[str, Any]]] = []
        for char_id in self._offsite_ids:
            data = self._char_data.get(char_id)
            if data:
                offsite_recipients.append((char_id, data))

        return onsite_recipients, offsite_recipients

    def _compute_exp_pool_distribution(
        self,
        *,
        exp_multiplier: float,
        idle_exp_mult: float,
    ) -> tuple[
        list[tuple[str, dict[str, Any]]],
        list[tuple[str, dict[str, Any]]],
        float,
        float,
        float,
    ]:
        onsite_recipients, offsite_recipients = self._exp_recipients()
        onsite_count = len(onsite_recipients)
        if onsite_count <= 0:
            return onsite_recipients, offsite_recipients, 0.0, 0.0, 0.0

        raw_unit_gain = self._onsite_raw_pool_unit_gain(
            exp_multiplier=exp_multiplier,
            idle_exp_mult=idle_exp_mult,
        )
        total_onsite_raw_pool = raw_unit_gain
        shared_exp_fraction = self._shared_exp_fraction(
            offsite_recipient_count=len(offsite_recipients),
        )

        drip_pool = total_onsite_raw_pool * shared_exp_fraction
        onsite_retained_pool = max(0.0, total_onsite_raw_pool - drip_pool)
        onsite_allocated_share = onsite_retained_pool / onsite_count

        if not offsite_recipients:
            return (
                onsite_recipients,
                offsite_recipients,
                onsite_allocated_share,
                0.0,
                0.0,
            )

        offsite_count = len(offsite_recipients)
        offsite_drip_share = drip_pool / offsite_count
        offsite_baseline_bonus = total_onsite_raw_pool * self._offsite_exp_share
        return (
            onsite_recipients,
            offsite_recipients,
            onsite_allocated_share,
            offsite_drip_share,
            offsite_baseline_bonus,
        )

    def _apply_min_exp_gain_floor(self, gain: float) -> float:
        if gain <= 0.0:
            return 0.0
        return max(MIN_EXP_GAIN_PER_TICK, float(gain))

    def _blessing(self) -> BlessingPlugin:
        return get_default_blessing()

    def _idle_blessing_elapsed_seconds(self) -> float:
        return max(0.0, self._elapsed_seconds)

    def get_idle_blessing_step_count(self) -> int:
        with self._lock:
            elapsed = self._idle_blessing_elapsed_seconds()
            blessing = self._blessing()
            return max(0, int(elapsed // blessing.step_seconds))

    def get_idle_blessing_multiplier(self) -> float:
        with self._lock:
            elapsed = self._idle_blessing_elapsed_seconds()
            blessing = self._blessing()
            steps = max(0, int(elapsed // blessing.step_seconds))
            return blessing.get_multiplier(steps)

    def get_idle_blessing_cycle_progress(self) -> float:
        with self._lock:
            elapsed = self._idle_blessing_elapsed_seconds()
            blessing = self._blessing()
            phase = elapsed % blessing.step_seconds
            return max(0.0, min(1.0, phase / blessing.step_seconds))

    def get_idle_blessing_seconds_to_next_step(self) -> int:
        with self._lock:
            elapsed = self._idle_blessing_elapsed_seconds()
            blessing = self._blessing()
            phase = elapsed % blessing.step_seconds
            remaining = blessing.step_seconds - phase
            if remaining <= 1e-9:
                remaining = blessing.step_seconds
            return max(0, int(math.ceil(remaining)))

    def export_run_buff_seconds(self) -> tuple[float, float]:
        with self._lock:
            return (
                float(max(0.0, self._exp_bonus_seconds)),
                float(max(0.0, self._exp_penalty_seconds)),
            )

    def _level_up(self, char_id: str) -> None:
        data = self._char_data.get(char_id)
        if not data:
            return

        data["level"] = max(1, int(data.get("level", 1))) + 1
        data["exp"] = 0.0

        base_stats = data.get("base_stats")
        if isinstance(base_stats, dict):
            self._apply_weighted_stat_upgrades(
                char_id=char_id, base_stats=base_stats, level=int(data["level"])
            )
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

        tax = calculate_rebirth_exp_tax(
            level=level,
            rebirth_power=float(data.get("rebirth_power", 1.0)),
            stars=self._progression_stars_for_char(char_id),
        )
        lunar_req_mult = self._lunar_exp_requirement_multiplier()
        data["next_exp"] = (
            level * 30 * req_mult * tax * lunar_req_mult
        ) * self._rng.uniform(0.95, 1.05)
        self._apply_offsite_stat_share_to_onsite_hp()

    def _apply_weighted_stat_upgrades(
        self, *, char_id: str, base_stats: dict[str, float], level: int
    ) -> None:
        data = self._char_data.get(char_id)
        prestige_count = 0
        if data:
            prestige_count = max(0, int(data.get("prestige_count", 0)))

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

        prestige_gain_rate = calculate_prestige_stat_gain_rate(
            prestige_count=prestige_count,
            stars=self._progression_stars_for_char(char_id),
        )
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

    def _apply_sparse_growth(
        self, *, char_id: str, base_stats: dict[str, float]
    ) -> None:
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

    def get_char_data(self, char_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._char_data.get(char_id)
            if not isinstance(data, dict):
                return None
            return dict(data)

    def get_party_level(self) -> int:
        with self._lock:
            return max(1, int(self._party_level))

    def export_progress(self) -> dict[str, dict[str, float | int]]:
        with self._lock:
            return self._export_progress_unlocked()

    def _export_progress_unlocked(self) -> dict[str, dict[str, float | int]]:
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
                death_exp_debuff_stacks = max(
                    0, int(data.get("death_exp_debuff_stacks", 0))
                )
            except (TypeError, ValueError):
                death_exp_debuff_stacks = 0
            try:
                death_exp_debuff_until = float(
                    max(0.0, float(data.get("death_exp_debuff_until", 0.0)))
                )
            except (TypeError, ValueError):
                death_exp_debuff_until = 0.0
            try:
                shard_bar_ticks = max(0, int(data.get("shard_bar_ticks", 0)))
            except (TypeError, ValueError):
                shard_bar_ticks = 0

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
                "next_vitality_gain_level": max(
                    0, int(data.get("next_vitality_gain_level", 0))
                ),
                "next_mitigation_gain_level": max(
                    0, int(data.get("next_mitigation_gain_level", 0))
                ),
                "max_hp_level_bonus_version": max(
                    0, int(data.get("max_hp_level_bonus_version", 0))
                ),
                "shard_bar_ticks": shard_bar_ticks % SHARD_BAR_CYCLE_TICKS,
            }
        return payload

    def export_character_stats(self) -> dict[str, dict[str, float]]:
        with self._lock:
            return self._export_character_stats_unlocked()

    def _export_character_stats_unlocked(self) -> dict[str, dict[str, float]]:
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
        with self._lock:
            return self._export_initial_stats_unlocked()

    def _export_initial_stats_unlocked(self) -> dict[str, dict[str, float]]:
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

    def export_blessings(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            return self._export_blessings_unlocked()

    def _export_blessings_unlocked(self) -> dict[str, dict[str, Any]]:
        payload: dict[str, dict[str, Any]] = {}
        persistent_plugins = {
            plugin.blessing_id: plugin
            for plugin in discover_blessing_plugins()
            if plugin.is_persistent
        }
        for blessing_id, raw in self._blessings_data.items():
            if not isinstance(blessing_id, str):
                continue
            clean_id = blessing_id.strip()
            if not clean_id or not isinstance(raw, dict):
                continue
            plugin = persistent_plugins.get(clean_id)
            if plugin is None:
                continue
            normalized: dict[str, Any] = {}
            for field_name, field_type in plugin.save_schema.items():
                if field_name in raw:
                    normalized[field_name] = raw[field_name]
                    continue
                if field_type is int:
                    normalized[field_name] = 0
                elif field_type is float:
                    normalized[field_name] = 0.0
                elif field_type is bool:
                    normalized[field_name] = (
                        plugin.is_unlocked if field_name == "unlocked" else False
                    )
            payload[clean_id] = normalized
        return payload

    def export_runtime_snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "tick_count": self._tick_count,
                "elapsed_seconds": float(self._elapsed_seconds),
                "party_level": max(1, int(self._party_level)),
                "shared_exp_percentage": int(self._shared_exp_percentage),
                "risk_reward_level": int(self._risk_reward_level),
                "char_data": {
                    char_id: dict(data)
                    for char_id, data in self._char_data.items()
                    if isinstance(char_id, str) and isinstance(data, dict)
                },
                "progress": self._export_progress_unlocked(),
                "character_stats": self._export_character_stats_unlocked(),
                "initial_stats": self._export_initial_stats_unlocked(),
                "blessings": self._export_blessings_unlocked(),
                "blessing_runtime": self._export_blessing_runtime_unlocked(),
                "exp_bonus_seconds": float(max(0.0, self._exp_bonus_seconds)),
                "exp_penalty_seconds": float(max(0.0, self._exp_penalty_seconds)),
                "inventory": {
                    str(item_id): max(0, int(count))
                    for item_id, count in self._inventory.items()
                },
            }

    def _export_blessing_runtime_unlocked(self) -> dict[str, dict[str, float | int | bool]]:
        runtime: dict[str, dict[str, float | int | bool]] = {}
        elapsed_total = max(0.0, float(self._elapsed_seconds))
        for plugin in discover_blessing_plugins():
            step_seconds = max(1e-9, float(plugin.step_seconds))
            blessing_id = plugin.blessing_id
            if plugin.is_persistent:
                blessing_data = self._blessings_data.get(blessing_id, {})
                if not isinstance(blessing_data, dict):
                    blessing_data = {}
                unlocked = bool(blessing_data.get("unlocked", plugin.is_unlocked))
                try:
                    steps = max(0, int(blessing_data.get("steps", 0)))
                except (TypeError, ValueError):
                    steps = 0
                if unlocked:
                    try:
                        elapsed = max(
                            0.0, float(blessing_data.get("tick_elapsed_seconds", 0.0))
                        )
                    except (TypeError, ValueError):
                        elapsed = 0.0
                else:
                    elapsed = 0.0
            else:
                unlocked = bool(plugin.is_unlocked)
                if unlocked:
                    steps = max(0, int(elapsed_total // step_seconds))
                    elapsed = elapsed_total % step_seconds
                else:
                    steps = 0
                    elapsed = 0.0

            progress = max(0.0, min(1.0, elapsed / step_seconds))
            remaining = step_seconds - elapsed
            if remaining <= 1e-9:
                remaining = step_seconds
            runtime[blessing_id] = {
                "unlocked": unlocked,
                "steps": steps,
                "elapsed_seconds": elapsed,
                "progress": progress,
                "countdown_seconds": max(0, int(math.ceil(remaining))),
            }
        return runtime

    def get_misplacement_stat_multiplier(self, char_id: str) -> float:
        clean_id = str(char_id or "").strip()
        if not clean_id:
            return 1.0
        with self._lock:
            return self._stat_multiplier_for_char(clean_id)

    def get_misplacement_exp_multiplier(self, char_id: str) -> float:
        clean_id = str(char_id or "").strip()
        if not clean_id:
            return 1.0
        with self._lock:
            return self._exp_multiplier_for_char(clean_id)

    def set_shared_exp_percentage(self, percentage: int) -> None:
        with self._lock:
            self._shared_exp_percentage = max(1, min(95, int(percentage)))

    def get_shared_exp_percentage(self) -> int:
        with self._lock:
            return self._shared_exp_percentage

    def set_risk_reward_level(self, level: int) -> None:
        with self._lock:
            self._risk_reward_level = max(0, min(150, int(level)))

    def get_risk_reward_level(self) -> int:
        with self._lock:
            return self._risk_reward_level

    def _process_blessing_ticks(self, *, delta_seconds: float) -> dict[str, dict[str, Any]]:
        updated_blessings: dict[str, dict[str, Any]] = dict(self._blessings_data)

        for plugin in discover_blessing_plugins():
            if not plugin.is_persistent:
                continue

            blessing_id = plugin.blessing_id
            blessing_data: dict[str, Any] = dict(updated_blessings.get(blessing_id, {}))

            if not bool(blessing_data.get("unlocked", plugin.is_unlocked)):
                blessing_data["tick_elapsed_seconds"] = 0.0
                updated_blessings[blessing_id] = blessing_data
                continue

            elapsed = max(0.0, float(blessing_data.get("tick_elapsed_seconds", 0.0)))
            elapsed += max(0.0, float(delta_seconds))
            steps = max(0, int(blessing_data.get("steps", 0)))
            while elapsed >= plugin.step_seconds:
                steps += 1
                elapsed -= plugin.step_seconds
            blessing_data["steps"] = steps
            blessing_data["tick_elapsed_seconds"] = elapsed
            updated_blessings[blessing_id] = blessing_data

        self._blessings_data = updated_blessings
        return updated_blessings
