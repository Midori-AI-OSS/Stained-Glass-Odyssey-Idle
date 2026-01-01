from __future__ import annotations

import random

from dataclasses import dataclass

from endless_idler.characters.plugins import CharacterPlugin
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


def build_party(
    *,
    onsite: list[str],
    party_level: int,
    stacks: dict[str, int],
    plugins_by_id: dict[str, CharacterPlugin],
    rng: random.Random,
) -> list[Combatant]:
    party: list[Combatant] = []
    for char_id in onsite[:4]:
        plugin = plugins_by_id.get(char_id)
        name = plugin.display_name if plugin else char_id
        stars = plugin.stars if plugin else 1
        stack_count = max(1, int(stacks.get(char_id, 1)))

        stats = Stats()
        scale = party_scaling(party_level=party_level, stars=stars, stacks=stack_count)
        apply_scaled_bases(stats, base_stats=getattr(plugin, "base_stats", None), scale=scale, spd=2 + stars)
        stats.damage_type = load_damage_type(resolve_damage_type_id(plugin, rng))
        if plugin:
            _apply_plugin_overrides(stats, plugin=plugin)
        stats.level = party_level
        stats.hp = stats.max_hp
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
        base = party_scaling(party_level=party_level, stars=stars, stacks=1)
        scale = base * rng.uniform(0.85, 1.1)
        apply_scaled_bases(stats, base_stats=getattr(plugin, "base_stats", None), scale=scale, spd=2 + max(0, stars - 1))
        stats.damage_type = load_damage_type(resolve_damage_type_id(plugin, rng))
        if plugin:
            _apply_plugin_overrides(stats, plugin=plugin)
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
) -> list[Combatant]:
    reserves: list[Combatant] = []
    party_level = max(1, int(party_level))
    limit = max(0, int(limit))
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

        stats = Stats()
        scale = party_scaling(party_level=party_level, stars=stars, stacks=stack_count)
        apply_scaled_bases(stats, base_stats=getattr(plugin, "base_stats", None), scale=scale, spd=2 + stars)
        stats.damage_type = load_damage_type(resolve_damage_type_id(plugin, rng))
        if plugin:
            _apply_plugin_overrides(stats, plugin=plugin)
        stats.level = party_level
        stats.hp = stats.max_hp
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


def party_scaling(*, party_level: int, stars: int, stacks: int) -> float:
    stars = max(1, min(6, int(stars)))
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


def _apply_plugin_overrides(stats: Stats, *, plugin: CharacterPlugin) -> None:
    base_aggro = getattr(plugin, "base_aggro", None)
    if isinstance(base_aggro, (int, float)):
        stats.base_aggro = float(base_aggro)
    passes = getattr(plugin, "damage_reduction_passes", None)
    if isinstance(passes, int):
        stats.damage_reduction_passes = int(passes)


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


def calculate_damage(
    attacker: Stats,
    target: Stats,
    rng: random.Random,
) -> tuple[int, bool, bool]:
    dodge_odds = float(max(0.0, min(1.0, target.dodge_odds)))
    if rng.random() < dodge_odds:
        return 0, False, True

    atk = attacker.atk
    defense = max(0, target.defense)
    multiplier = 100.0 / (100.0 + float(defense))
    base = float(atk) * multiplier

    base *= type_multiplier(attacker.element_id, target.element_id)
    base *= float(max(0.01, attacker.vitality))
    base /= float(max(0.01, target.vitality))
    base /= float(max(0.1, target.mitigation))

    crit_rate = float(max(0.0, min(1.0, attacker.crit_rate)))
    crit = rng.random() < crit_rate
    if crit:
        base *= float(max(1.0, attacker.crit_damage))

    base *= rng.uniform(0.9, 1.1)
    damage = max(1, int(base))
    return damage, crit, False
