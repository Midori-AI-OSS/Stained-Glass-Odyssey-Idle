from __future__ import annotations

import random

from dataclasses import dataclass

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.combat.party_stats import apply_offsite_stat_share as apply_offsite_stat_share_to_stats
from endless_idler.combat.party_stats import apply_scaled_bases
from endless_idler.combat.party_stats import apply_plugin_overrides
from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.combat.party_stats import party_scaling
from endless_idler.combat.damage_types import load_damage_type
from endless_idler.combat.damage_types import normalize_damage_type_id
from endless_idler.combat.damage_types import resolve_damage_type_for_battle
from endless_idler.combat.damage_types import type_multiplier
from endless_idler.combat.stats import Stats


KNOWN_DAMAGE_TYPE_IDS = (
    "fire",
    "ice",
    "lightning",
    "dark",
    "light",
    "wind",
    "generic",
)

RANDOM_DAMAGE_TYPE_IDS = tuple(item for item in KNOWN_DAMAGE_TYPE_IDS if item != "generic")


@dataclass(slots=True)
class Combatant:
    char_id: str
    name: str
    stats: Stats
    max_hp: int
    turns_taken: int = 0
    pending_damage_multiplier: float = 1.0
    ice_charge_ready: bool = False


def apply_offsite_stat_share(
    *,
    party: list[Combatant],
    reserves: list[Combatant],
    share: float = 0.10,
) -> None:
    apply_offsite_stat_share_to_stats(
        party=[combatant.stats for combatant in party],
        reserves=[combatant.stats for combatant in reserves],
        share=share,
    )
    for combatant in party:
        combatant.max_hp = combatant.stats.max_hp


def build_party(
    *,
    onsite: list[str],
    party_level: int,
    stacks: dict[str, int],
    plugins_by_id: dict[str, CharacterPlugin],
    rng: random.Random,
    progress_by_id: dict[str, dict[str, float | int]] | None = None,
    stats_by_id: dict[str, dict[str, float]] | None = None,
) -> list[Combatant]:
    party: list[Combatant] = []
    progress_by_id = progress_by_id or {}
    stats_by_id = stats_by_id or {}
    for char_id in onsite[:4]:
        plugin = plugins_by_id.get(char_id)
        name = plugin.display_name if plugin else char_id
        stars = plugin.stars if plugin else 1
        stack_count = max(1, int(stacks.get(char_id, 1)))

        stats = build_scaled_character_stats(
            plugin=plugin,
            party_level=party_level,
            stars=stars,
            stacks=stack_count,
            progress=progress_by_id.get(char_id),
            saved_base_stats=stats_by_id.get(char_id),
        )
        stats.damage_type = load_damage_type(resolve_damage_type_id(plugin, rng))
        apply_plugin_overrides(stats, plugin=plugin)
        if stats.element_id == "ice" and (plugin is None or plugin.damage_reduction_passes is None):
            stats.damage_reduction_passes = max(2, int(stats.damage_reduction_passes))
        party.append(Combatant(char_id=char_id, name=name, stats=stats, max_hp=stats.max_hp))
    return party


def build_foes(
    *,
    exclude_ids: set[str],
    party_level: int,
    foe_count: int,
    plugins: list[CharacterPlugin],
    rng: random.Random,
) -> list[Combatant]:
    plugins_by_id = {plugin.char_id: plugin for plugin in plugins}
    pool = [plugin.char_id for plugin in plugins if plugin.char_id not in exclude_ids]
    if not pool:
        pool = [plugin.char_id for plugin in plugins]

    foes: list[Combatant] = []
    foe_count = max(1, int(foe_count))
    unique_count = min(len(pool), foe_count)
    if unique_count <= 0:
        return foes

    for index, char_id in enumerate(rng.sample(pool, k=unique_count), start=1):
        plugin = plugins_by_id.get(char_id)
        display = plugin.display_name if plugin else char_id
        name = f"{display} (Foe {index})"
        stars = plugin.stars if plugin else 1

        stats = Stats()
        stats.passive_modifier = 1.0
        base = party_scaling(party_level=party_level, stars=stars, stacks=1)
        scale = base * rng.uniform(0.85, 1.1)
        apply_scaled_bases(
            stats,
            base_stats=getattr(plugin, "base_stats", None),
            scale=scale,
            spd=2 + max(0, stars - 1),
        )
        stats.damage_type = load_damage_type(resolve_damage_type_id(plugin, rng))
        apply_plugin_overrides(stats, plugin=plugin)
        if stats.element_id == "ice" and (plugin is None or plugin.damage_reduction_passes is None):
            stats.damage_reduction_passes = max(2, int(stats.damage_reduction_passes))
        stats.level = party_level
        stats.hp = stats.max_hp
        foes.append(Combatant(char_id=char_id, name=name, stats=stats, max_hp=stats.max_hp))
    return foes


def build_reserves(
    *,
    char_ids: list[str],
    party_level: int,
    stacks: dict[str, int],
    plugins_by_id: dict[str, CharacterPlugin],
    rng: random.Random,
    limit: int = 6,
    progress_by_id: dict[str, dict[str, float | int]] | None = None,
    stats_by_id: dict[str, dict[str, float]] | None = None,
) -> list[Combatant]:
    reserves: list[Combatant] = []
    party_level = max(1, int(party_level))
    limit = max(0, int(limit))
    progress_by_id = progress_by_id or {}
    stats_by_id = stats_by_id or {}
    seen: set[str] = set()
    for char_id in [str(item) for item in char_ids if item]:
        if limit and len(reserves) >= limit:
            break
        if char_id in seen:
            continue
        seen.add(char_id)

        plugin = plugins_by_id.get(char_id)
        name = plugin.display_name if plugin else char_id
        stars = plugin.stars if plugin else 1
        stack_count = max(1, int(stacks.get(char_id, 1)))

        stats = build_scaled_character_stats(
            plugin=plugin,
            party_level=party_level,
            stars=stars,
            stacks=stack_count,
            progress=progress_by_id.get(char_id),
            saved_base_stats=stats_by_id.get(char_id),
        )
        stats.damage_type = load_damage_type(resolve_damage_type_id(plugin, rng))
        apply_plugin_overrides(stats, plugin=plugin)
        if stats.element_id == "ice" and (plugin is None or plugin.damage_reduction_passes is None):
            stats.damage_reduction_passes = max(2, int(stats.damage_reduction_passes))
        reserves.append(Combatant(char_id=char_id, name=name, stats=stats, max_hp=stats.max_hp))
    return reserves


def resolve_damage_type_id(plugin: CharacterPlugin | None, rng: random.Random) -> str:
    if plugin and plugin.damage_type_random:
        return rng.choice(RANDOM_DAMAGE_TYPE_IDS)

    if not plugin:
        return "generic"

    raw = normalize_damage_type_id(plugin.damage_type_id)
    resolved = resolve_damage_type_for_battle(
        char_id=plugin.char_id,
        raw_damage_type_id=raw,
        rng=rng,
    )
    if resolved in KNOWN_DAMAGE_TYPE_IDS:
        return resolved
    return "generic"


def choose_weighted_attacker(
    alive: list[tuple[Combatant, object]],
    rng: random.Random,
) -> tuple[Combatant, object]:
    weights = [max(1.0, float(item[0].stats.spd)) for item in alive]
    total = sum(weights)
    roll = rng.random() * total
    running = 0.0
    for (combatant, widget), weight in zip(alive, weights, strict=False):
        running += weight
        if running >= roll:
            return combatant, widget
    return alive[-1]


def choose_weighted_target_by_aggro(
    alive: list[tuple[Combatant, object]],
    rng: random.Random,
) -> tuple[Combatant, object]:
    weights = [max(0.0, float(item[0].stats.aggro)) for item in alive]
    total = sum(weights)
    if total <= 0:
        return rng.choice(alive)

    roll = rng.random() * total
    running = 0.0
    for (combatant, widget), weight in zip(alive, weights, strict=False):
        running += weight
        if running >= roll:
            return combatant, widget
    return alive[-1]


def calculate_damage(
    attacker: Stats,
    target: Stats,
    rng: random.Random,
    *,
    damage_multiplier: float = 1.0,
) -> tuple[int, bool, bool]:
    dodge_odds = float(max(0.0, min(1.0, target.dodge_odds)))
    if rng.random() < dodge_odds:
        return 0, False, True

    atk = attacker.atk
    defense = max(0, target.defense)
    mitigation_passes = max(1, int(getattr(target, "damage_reduction_passes", 1) or 1))
    mitigation_multiplier = 100.0 / (100.0 + float(defense))
    mitigation_multiplier **= float(mitigation_passes)
    base = float(atk) * mitigation_multiplier

    base *= type_multiplier(attacker.element_id, target.element_id)
    base *= float(max(0.01, attacker.vitality))
    base /= float(max(0.01, target.vitality))
    base /= float(max(0.1, target.mitigation))
    base *= float(max(0.0, damage_multiplier))

    crit_rate = float(max(0.0, min(1.0, attacker.crit_rate)))
    crit = rng.random() < crit_rate
    if crit:
        base *= float(max(1.0, attacker.crit_damage))

    base *= rng.uniform(0.9, 1.1)
    damage = max(1, int(base))
    return damage, crit, False
