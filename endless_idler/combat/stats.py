from __future__ import annotations

from typing import Any
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field

from endless_idler.combat.damage_types import DamageTypeBase
from endless_idler.combat.damage_types import Generic
from endless_idler.combat.stat_effect import StatEffect


ANIMATION_OFFSET: float = 2.8
DEFAULT_ANIMATION_DURATION: float = 0.045 * ANIMATION_OFFSET
DEFAULT_ANIMATION_PER_TARGET: float = 0.15 * ANIMATION_OFFSET

GAUGE_START: int = 10_000


@dataclass(slots=True)
class Stats:
    character_id: str = ""
    hp: int = 1000
    exp: int = 0
    level: int = 1
    exp_multiplier: float = 1.0
    actions_per_turn: int = 1
    actions_display: str = "pips"
    actions_pips_max: int = 5

    passive_modifier: float = 1.0

    _base_max_hp: int = field(default=1000, init=False)
    _base_atk: int = field(default=200, init=False)
    _base_defense: int = field(default=200, init=False)
    _base_crit_rate: float = field(default=0.05, init=False)
    _base_crit_damage: float = field(default=2.0, init=False)
    _base_effect_hit_rate: float = field(default=1.0, init=False)
    _base_mitigation: float = field(default=1.0, init=False)
    _base_regain: int = field(default=100, init=False)
    _base_dodge_odds: float = field(default=0.05, init=False)
    _base_effect_resistance: float = field(default=0.05, init=False)
    _base_vitality: float = field(default=1.0, init=False)
    _base_spd: int = field(default=2, init=False)
    damage_reduction_passes: int = 1

    damage_type: DamageTypeBase = field(default_factory=Generic)

    action_points: int = 0
    damage_taken: int = 0
    damage_dealt: int = 0
    kills: int = 0
    last_damage_taken: int = 0
    last_shield_absorbed: int = 0
    last_overkill: int = 0
    base_aggro: float = 0.1
    aggro_modifier: float = 0.0

    summon_slots_permanent: int = 0
    summon_slots_temporary: int = 0

    action_gauge: int = GAUGE_START
    action_value: float = 0.0
    base_action_value: float = field(default=0.0, init=False)

    animation_duration: float = DEFAULT_ANIMATION_DURATION
    animation_per_target: float = DEFAULT_ANIMATION_PER_TARGET

    ultimate_charge: int = 0
    ultimate_ready: bool = False
    ultimate_charge_capacity: int = 15

    overheal_enabled: bool = field(default=False, init=False)
    shields: int = field(default=0, init=False)

    passives: list[str] = field(default_factory=list)
    dots: list[str] = field(default_factory=list)
    hots: list[str] = field(default_factory=list)
    mods: list[str] = field(default_factory=list)
    _aggro_passives: list[str] = field(default_factory=list, init=False)
    login_theme_stat_bonuses: dict[str, float] = field(default_factory=dict, init=False)
    login_theme_damage_bonus: dict[str, float] = field(default_factory=dict, init=False)
    login_theme_damage_reduction: dict[str, float] = field(default_factory=dict, init=False)
    login_theme_drop_scope: str = field(default="matching", init=False)
    login_theme_identifier: str = field(default="", init=False)

    _active_effects: list[StatEffect] = field(default_factory=list, init=False)
    _passive_instances: list[Any] = field(default_factory=list, init=False)

    level_up_gains: dict[str, float] = field(
        default_factory=lambda: {"max_hp": 10.0, "atk": 5.0, "defense": 3.0}
    )

    @property
    def summon_slot_capacity(self) -> int:
        return max(0, int(self.summon_slots_permanent + self.summon_slots_temporary))

    @property
    def max_hp(self) -> int:
        return int(self._base_max_hp + self._calculate_stat_modifier("max_hp"))

    @max_hp.setter
    def max_hp(self, value: int) -> None:
        self._base_max_hp = int(value)
        if self.hp > self._base_max_hp:
            self.hp = self._base_max_hp

    @property
    def atk(self) -> int:
        return int(self._base_atk + self._calculate_stat_modifier("atk"))

    @atk.setter
    def atk(self, value: int) -> None:
        self._base_atk = int(value)

    @property
    def defense(self) -> int:
        return int(self._base_defense + self._calculate_stat_modifier("defense"))

    @defense.setter
    def defense(self, value: int) -> None:
        self._base_defense = int(value)

    @property
    def crit_rate(self) -> float:
        return max(0.0, self._base_crit_rate + self._calculate_stat_modifier("crit_rate"))

    @crit_rate.setter
    def crit_rate(self, value: float) -> None:
        self._base_crit_rate = float(value)

    @property
    def crit_damage(self) -> float:
        return max(1.0, self._base_crit_damage + self._calculate_stat_modifier("crit_damage"))

    @crit_damage.setter
    def crit_damage(self, value: float) -> None:
        self._base_crit_damage = float(value)

    @property
    def effect_hit_rate(self) -> float:
        return max(
            0.0,
            self._base_effect_hit_rate + self._calculate_stat_modifier("effect_hit_rate"),
        )

    @effect_hit_rate.setter
    def effect_hit_rate(self, value: float) -> None:
        self._base_effect_hit_rate = float(value)

    @property
    def mitigation(self) -> float:
        return max(0.1, self._base_mitigation + self._calculate_stat_modifier("mitigation"))

    @mitigation.setter
    def mitigation(self, value: float) -> None:
        self._base_mitigation = float(value)

    @property
    def regain(self) -> int:
        return int(max(0, self._base_regain + self._calculate_stat_modifier("regain")))

    @regain.setter
    def regain(self, value: int) -> None:
        self._base_regain = int(value)

    @property
    def dodge_odds(self) -> float:
        value = self._base_dodge_odds + self._calculate_stat_modifier("dodge_odds")
        return max(0.0, min(1.0, value))

    @dodge_odds.setter
    def dodge_odds(self, value: float) -> None:
        self._base_dodge_odds = float(value)

    @property
    def effect_resistance(self) -> float:
        return max(
            0.0,
            self._base_effect_resistance + self._calculate_stat_modifier("effect_resistance"),
        )

    @effect_resistance.setter
    def effect_resistance(self, value: float) -> None:
        self._base_effect_resistance = float(value)

    @property
    def vitality(self) -> float:
        return max(0.01, self._base_vitality + self._calculate_stat_modifier("vitality"))

    @vitality.setter
    def vitality(self, value: float) -> None:
        self._base_vitality = float(value)

    @property
    def spd(self) -> int:
        return int(max(1, self._base_spd + self._calculate_stat_modifier("spd")))

    @spd.setter
    def spd(self, value: int) -> None:
        self._base_spd = int(value)

    @property
    def aggro(self) -> float:
        defense_term = 0.0
        if self._base_defense > 0:
            defense_term = (self.defense - self._base_defense) / float(self._base_defense)
        modifier = self.aggro_modifier + self._calculate_stat_modifier("aggro_modifier")
        return self.base_aggro * (1 + modifier + defense_term)

    def _calculate_stat_modifier(self, stat_name: str) -> float:
        total = 0.0
        for effect in self._active_effects:
            value = effect.stat_modifiers.get(stat_name)
            if isinstance(value, (int, float)):
                total += float(value)
        return total

    def add_effect(self, effect: StatEffect) -> None:
        self.remove_effect_by_name(effect.name)
        self._active_effects.append(effect)

    def remove_effect_by_name(self, effect_name: str) -> bool:
        before = len(self._active_effects)
        self._active_effects = [e for e in self._active_effects if e.name != effect_name]
        return len(self._active_effects) < before

    def remove_effect_by_source(self, source: str) -> int:
        before = len(self._active_effects)
        self._active_effects = [e for e in self._active_effects if e.source != source]
        return before - len(self._active_effects)

    def tick_effects(self) -> None:
        expired: list[str] = []
        for effect in self._active_effects:
            effect.tick()
            if effect.is_expired():
                expired.append(effect.name)
        for name in expired:
            self.remove_effect_by_name(name)

    def get_active_effects(self) -> list[StatEffect]:
        return list(self._active_effects)

    def clear_all_effects(self) -> None:
        self._active_effects.clear()

    @property
    def element_id(self) -> str:
        dt = self.damage_type
        if isinstance(dt, str):
            return dt
        ident = getattr(dt, "id", None) or getattr(dt, "name", None)
        return str(ident or dt)

    @property
    def ultimate_charge_max(self) -> int:
        value = int(self.ultimate_charge_capacity)
        return max(1, value)

    def add_ultimate_charge(self, amount: int = 1) -> None:
        if self.ultimate_ready:
            return
        increment = max(0, int(amount))
        maximum = self.ultimate_charge_max
        self.ultimate_charge = min(maximum, self.ultimate_charge + increment)
        if self.ultimate_charge >= maximum:
            self.ultimate_ready = True

    def set_base_stat(self, stat_name: str, value: int | float) -> None:
        base_attr = f"_base_{stat_name}"
        if hasattr(self, base_attr):
            setattr(self, base_attr, value)

    def get_base_stat(self, stat_name: str) -> int | float:
        base_attr = f"_base_{stat_name}"
        if hasattr(self, base_attr):
            value = getattr(self, base_attr)
            if isinstance(value, (int, float)):
                return value
        return 0

    def modify_base_stat(self, stat_name: str, amount: int | float) -> None:
        self.set_base_stat(stat_name, self.get_base_stat(stat_name) + amount)


def collect_stat_modifier_keys(effects: Iterable[StatEffect]) -> set[str]:
    keys: set[str] = set()
    for effect in effects:
        keys.update(effect.stat_modifiers.keys())
    return keys
