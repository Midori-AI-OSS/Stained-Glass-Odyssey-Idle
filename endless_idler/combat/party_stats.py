from __future__ import annotations

import math

from endless_idler.combat.stats import Stats


STAT_SHARE_KEYS: tuple[str, ...] = (
    "max_hp",
    "atk",
    "defense",
    "regain",
    "crit_mod",
    "effect_hit_rate",
    "mitigation",
    "dodge_odds",
    "effect_resistance",
    "vitality",
    "atk_speed",
)
_INT_BASE_STATS = frozenset({"max_hp", "atk", "defense", "regain", "atk_speed"})
_POSITIVE_INT_BASE_STATS = frozenset({"max_hp", "atk", "defense", "atk_speed"})


def party_scaling(*, party_level: int, stars: int, stacks: int) -> float:
    stars = max(1, min(7, int(stars)))
    stacks = max(1, int(stacks))
    party_level = max(1, int(party_level))

    level_mult = 1.0 + 0.05 * max(0, party_level - 1)
    star_mult = 0.75 + 0.18 * stars
    stack_mult = 1.0 + 0.12 * max(0, stacks - 1)
    return level_mult * star_mult * stack_mult


def apply_scaled_bases(
    stats: Stats,
    *,
    base_stats: dict[str, float] | None,
    scale: float,
    atk_speed: int,
) -> None:
    template = base_stats if isinstance(base_stats, dict) else {}

    max_hp = float(template.get("max_hp", 1000.0))
    atk = float(template.get("atk", 200.0))
    defense = float(template.get("defense", 200.0))
    regain = float(template.get("regain", 100.0))

    stats.set_base_stat("max_hp", int(max_hp * scale))
    stats.set_base_stat("atk", int(atk * scale))
    stats.set_base_stat("defense", int(defense * scale))
    stats.set_base_stat("regain", int(regain * scale))

    for key in (
        "crit_mod",
        "effect_hit_rate",
        "mitigation",
        "dodge_odds",
        "effect_resistance",
        "vitality",
    ):
        if key in template:
            stats.set_base_stat(key, float(template[key]))
    stats.set_base_stat("atk_speed", int(max(1, atk_speed)))


def merged_base_stats(
    *,
    plugin_base_stats: dict[str, float] | None,
    saved_base_stats: dict[str, float] | None,
) -> dict[str, float]:
    base_stats: dict[str, float] = dict(plugin_base_stats) if isinstance(plugin_base_stats, dict) else {}
    if isinstance(saved_base_stats, dict):
        for key, raw in saved_base_stats.items():
            if not isinstance(key, str):
                continue
            name = key.strip()
            if not name:
                continue
            try:
                base_stats[name] = float(raw)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                continue
    return base_stats


def apply_plugin_overrides(stats: Stats, *, plugin: object | None) -> None:
    if plugin is None:
        return

    damage_type_id = getattr(plugin, "damage_type_id", None)
    if damage_type_id is not None:
        from endless_idler.combat.damage_types import load_damage_type
        stats.damage_type = load_damage_type(damage_type_id)

    base_aggro = getattr(plugin, "base_aggro", None)
    if isinstance(base_aggro, (int, float)):
        stats.base_aggro = float(base_aggro)

    passes = getattr(plugin, "damage_reduction_passes", None)
    if isinstance(passes, int):
        stats.damage_reduction_passes = int(passes)


def apply_soft_cap_to_level_bonus(level: int) -> float:
    """
    Apply soft cap to level bonus calculation.
    
    Linear up to 0.1 (level 100), then logarithmic diminishing returns.
    Rate slows by 2x for each 5% gain past threshold.
    
    Args:
        level: Character level
        
    Returns:
        Level bonus as a float with soft cap applied
    """
    THRESHOLD = 0.1
    STEP_SIZE = 0.005  # 5% of threshold
    
    # Calculate raw linear value
    raw_value = level * 0.001
    
    # If below threshold, no soft cap needed
    if raw_value <= THRESHOLD:
        return raw_value
    
    # Calculate excess over threshold
    excess = raw_value - THRESHOLD
    
    # Apply logarithmic diminishing returns
    # log2(1 + x) gives us the "doubling steps"
    soft_excess = STEP_SIZE * math.log2(1 + (excess / STEP_SIZE))
    
    return THRESHOLD + soft_excess


def apply_soft_cap_to_rebirth_bonus(rebirths: int) -> float:
    """
    Apply soft cap to rebirth bonus calculation.
    
    Linear up to 0.2 (rebirth 100), then logarithmic diminishing returns.
    Rate slows by 2x for each 5% gain past threshold.
    
    Args:
        rebirths: Number of rebirths
        
    Returns:
        Rebirth bonus as a float with soft cap applied
    """
    THRESHOLD = 0.2
    STEP_SIZE = 0.01  # 5% of threshold
    
    # Calculate raw linear value
    raw_value = rebirths * 0.002
    
    # If below threshold, no soft cap needed
    if raw_value <= THRESHOLD:
        return raw_value
    
    # Calculate excess over threshold
    excess = raw_value - THRESHOLD
    
    # Apply logarithmic diminishing returns
    soft_excess = STEP_SIZE * math.log2(1 + (excess / STEP_SIZE))
    
    return THRESHOLD + soft_excess


def calculate_atk_speed_bonus(level: int, rebirths: int) -> float:
    """
    Calculate atk_speed bonus from level and rebirth progression.
    
    Formula: bonus = apply_soft_cap_to_level_bonus(level) + apply_soft_cap_to_rebirth_bonus(rebirths)
    - Level bonus: +0.001 per level up to 0.1 (level 100), then soft cap with
      logarithmic diminishing returns (rate slows by 2x per 5% gain past 0.1)
    - Rebirth bonus: +0.002 per rebirth up to 0.2 (rebirth 100), then soft cap with
      logarithmic diminishing returns (rate slows by 2x per 5% gain past 0.2)
    
    Args:
        level: Character level
        rebirths: Number of rebirths
        
    Returns:
        Total atk_speed bonus as a float
    """
    level = max(0, int(level))
    rebirths = max(0, int(rebirths))
    
    level_bonus = apply_soft_cap_to_level_bonus(level)
    rebirth_bonus = apply_soft_cap_to_rebirth_bonus(rebirths)
    
    return level_bonus + rebirth_bonus


def apply_progress_meta(stats: Stats, *, progress: dict[str, float | int] | None) -> None:
    if not isinstance(progress, dict):
        return

    try:
        stats.level = max(1, int(progress.get("level", 1)))
    except (TypeError, ValueError):
        stats.level = 1

    try:
        stats.exp = max(0, int(float(progress.get("exp", 0.0))))
    except (TypeError, ValueError):
        stats.exp = 0

    try:
        stats.exp_multiplier = max(0.0, float(progress.get("exp_multiplier", 1.0)))
    except (TypeError, ValueError):
        stats.exp_multiplier = 1.0
    
    # Apply atk_speed bonuses from level and rebirth progression
    try:
        rebirths = max(0, int(progress.get("rebirths", 0)))
    except (TypeError, ValueError):
        rebirths = 0
    
    atk_speed_bonus = calculate_atk_speed_bonus(stats.level, rebirths)
    if atk_speed_bonus > 0:
        from endless_idler.combat.stat_effect import StatEffect
        effect = StatEffect(
            name="progression_atk_speed",
            stat_modifiers={"atk_speed": atk_speed_bonus},
            duration=-1,  # Permanent effect
            source="progression"
        )
        stats.add_effect(effect)


def build_scaled_character_stats(
    *,
    plugin: object | None,
    party_level: int,
    stars: int,
    stacks: int,
    progress: dict[str, float | int] | None,
    saved_base_stats: dict[str, float] | None,
    atk_speed: int | None = None,
) -> Stats:
    stacks = max(1, int(stacks))
    stars = max(1, min(7, int(stars)))
    atk_speed_value = int(atk_speed if atk_speed is not None else 1)

    stats = Stats()
    # Passive modifier formula: (stacks * 0.05) + 1
    # Provides 5% bonus per stack, starting at 1.0 (neutral) with 0 stacks
    stats.passive_modifier = (stacks * 0.05) + 1.0

    merged = merged_base_stats(
        plugin_base_stats=getattr(plugin, "base_stats", None) if plugin else None,
        saved_base_stats=saved_base_stats,
    )
    try:
        version = max(0, int(progress.get("max_hp_level_bonus_version", 0))) if isinstance(progress, dict) else 0
    except (TypeError, ValueError):
        version = 0
    if version < 1 and isinstance(progress, dict):
        try:
            level = max(1, int(progress.get("level", 1)))
        except (TypeError, ValueError):
            level = 1
        merged["max_hp"] = float(merged.get("max_hp", 1000.0)) + max(0, level - 1) * 10.0

    scale = party_scaling(party_level=party_level, stars=stars, stacks=stacks)
    apply_scaled_bases(
        stats,
        base_stats=merged,
        scale=scale,
        atk_speed=atk_speed_value,
    )
    apply_plugin_overrides(stats, plugin=plugin)
    apply_progress_meta(stats, progress=progress)
    stats.hp = stats.max_hp
    return stats


def apply_offsite_stat_share(
    *,
    party: list[Stats],
    reserves: list[Stats],
    share: float = 0.10,
) -> None:
    share = float(share)
    if share <= 0:
        return
    if not party or not reserves:
        return

    totals: dict[str, float] = {}
    for reserve in reserves:
        for stat_name in STAT_SHARE_KEYS:
            base = reserve.get_base_stat(stat_name)
            if isinstance(base, (int, float)):
                totals[stat_name] = totals.get(stat_name, 0.0) + float(base) * share

    if not totals:
        return

    int_stats = {"max_hp", "atk", "defense", "regain", "atk_speed"}
    for stats in party:
        for stat_name, amount in totals.items():
            if stat_name in int_stats:
                stats.modify_base_stat(stat_name, int(round(amount)))
            else:
                stats.modify_base_stat(stat_name, float(amount))
        stats.hp = stats.max_hp


def apply_base_stat_multiplier(*, stats: Stats, multiplier: float) -> None:
    scale = max(0.0, float(multiplier))
    if abs(scale - 1.0) <= 1e-9:
        return

    for stat_name in STAT_SHARE_KEYS:
        base = stats.get_base_stat(stat_name)
        if not isinstance(base, (int, float)):
            continue
        scaled = float(base) * scale
        if stat_name in _INT_BASE_STATS:
            floor = 1 if stat_name in _POSITIVE_INT_BASE_STATS else 0
            stats.set_base_stat(stat_name, max(floor, int(round(scaled))))
            continue
        stats.set_base_stat(stat_name, max(0.0, scaled))

    stats.hp = max(0, min(stats.hp, stats.max_hp))
