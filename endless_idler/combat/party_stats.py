from __future__ import annotations

from endless_idler.combat.stats import Stats


STAT_SHARE_KEYS: tuple[str, ...] = (
    "max_hp",
    "atk",
    "defense",
    "regain",
    "crit_rate",
    "crit_damage",
    "effect_hit_rate",
    "mitigation",
    "dodge_odds",
    "effect_resistance",
    "vitality",
    "spd",
)


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
    spd: int,
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
        "crit_rate",
        "crit_damage",
        "effect_hit_rate",
        "mitigation",
        "dodge_odds",
        "effect_resistance",
        "vitality",
    ):
        if key in template:
            stats.set_base_stat(key, float(template[key]))
    stats.set_base_stat("spd", int(max(1, spd)))


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

    damage_type = getattr(plugin, "damage_type", None)
    if damage_type is not None:
        stats.damage_type = damage_type

    base_aggro = getattr(plugin, "base_aggro", None)
    if isinstance(base_aggro, (int, float)):
        stats.base_aggro = float(base_aggro)

    passes = getattr(plugin, "damage_reduction_passes", None)
    if isinstance(passes, int):
        stats.damage_reduction_passes = int(passes)


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


def build_scaled_character_stats(
    *,
    plugin: object | None,
    party_level: int,
    stars: int,
    stacks: int,
    progress: dict[str, float | int] | None,
    saved_base_stats: dict[str, float] | None,
    spd: int | None = None,
) -> Stats:
    stacks = max(1, int(stacks))
    stars = max(1, min(7, int(stars)))
    spd_value = int(spd if spd is not None else (2 + stars))

    stats = Stats()
    stats.passive_modifier = 1.5 ** max(0, stacks - 1)

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
        spd=spd_value,
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

    int_stats = {"max_hp", "atk", "defense", "regain", "spd"}
    for stats in party:
        for stat_name, amount in totals.items():
            if stat_name in int_stats:
                stats.modify_base_stat(stat_name, int(round(amount)))
            else:
                stats.modify_base_stat(stat_name, float(amount))
        stats.hp = stats.max_hp
