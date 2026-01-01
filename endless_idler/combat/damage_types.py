"""Damage type helpers.

Matches the Endless Autofighter plugin damage types and includes the prototype's
type-effectiveness chart (weakness/resistance multipliers).
"""

from __future__ import annotations

import random


def normalize_damage_type_id(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "generic"

    if "/" in raw:
        parts = [part.strip() for part in raw.split("/") if part.strip()]
        normalized_parts = [normalize_damage_type_id(part) for part in parts]
        normalized_parts = [part for part in normalized_parts if part]
        if len(normalized_parts) >= 2:
            return " / ".join(normalized_parts)
        if normalized_parts:
            return normalized_parts[0]

    return raw.lower().replace("-", "_").replace(" ", "_")


def resolve_damage_type_for_battle(
    *,
    char_id: str,
    raw_damage_type_id: str,
    rng: random.Random,
) -> str:
    resolved = normalize_damage_type_id(raw_damage_type_id)
    if resolved == "load_damage_type":
        resolved = "generic"
    if " / " in resolved:
        options = [part.strip() for part in resolved.split("/") if part.strip()]
        normalized = [normalize_damage_type_id(option) for option in options]
        normalized = [option for option in normalized if option and option != "generic"]
        if normalized:
            return rng.choice(normalized)
    return resolved


_PROTOTYPE_TYPE_CHART: dict[str, dict[str, str]] = {
    "fire": {"weakness": "ice", "resistance": "fire"},
    "ice": {"weakness": "fire", "resistance": "ice"},
    "wind": {"weakness": "lightning", "resistance": "wind"},
    "lightning": {"weakness": "wind", "resistance": "lightning"},
    "light": {"weakness": "dark", "resistance": "light"},
    "dark": {"weakness": "light", "resistance": "dark"},
    "generic": {"weakness": "none", "resistance": "all"},
}


def type_multiplier(attacker_type_id: str, defender_type_id: str) -> float:
    attacker = normalize_damage_type_id(attacker_type_id)
    defender = normalize_damage_type_id(defender_type_id)
    defender_info = _PROTOTYPE_TYPE_CHART.get(defender, _PROTOTYPE_TYPE_CHART["generic"])

    if defender_info["weakness"] == attacker:
        return 1.25
    if defender_info["resistance"] == "all" or defender_info["resistance"] == attacker:
        return 0.75
    return 1.0


class DamageTypeBase:
    id: str = "generic"
    name: str = "Generic"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r})"


class Fire(DamageTypeBase):
    id = "fire"
    name = "Fire"


class Ice(DamageTypeBase):
    id = "ice"
    name = "Ice"


class Wind(DamageTypeBase):
    id = "wind"
    name = "Wind"


class Lightning(DamageTypeBase):
    id = "lightning"
    name = "Lightning"


class Light(DamageTypeBase):
    id = "light"
    name = "Light"


class Dark(DamageTypeBase):
    id = "dark"
    name = "Dark"


class Generic(DamageTypeBase):
    id = "generic"
    name = "Generic"


_DAMAGE_TYPES_BY_ID: dict[str, type[DamageTypeBase]] = {
    cls.id: cls
    for cls in (
        Fire,
        Ice,
        Wind,
        Lightning,
        Light,
        Dark,
        Generic,
    )
}


def load_damage_type(value: str | DamageTypeBase | None) -> DamageTypeBase:
    if isinstance(value, DamageTypeBase):
        return value

    normalized = normalize_damage_type_id(str(value or "generic"))
    normalized = normalized.split("/", 1)[0].strip()
    return _DAMAGE_TYPES_BY_ID.get(normalized, Generic)()
