from __future__ import annotations

import random

from dataclasses import dataclass

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.combat.stats import Stats


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
) -> list[Combatant]:
    party: list[Combatant] = []
    for char_id in onsite[:4]:
        plugin = plugins_by_id.get(char_id)
        name = plugin.display_name if plugin else char_id
        stars = plugin.stars if plugin else 1
        stack_count = max(1, int(stacks.get(char_id, 1)))

        stats = Stats()
        scale = party_scaling(party_level=party_level, stars=stars, stacks=stack_count)
        apply_scaled_bases(stats, scale=scale, spd=2 + stars)
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
    for index in range(1, foe_count + 1):
        char_id = rng.choice(pool)
        plugin = plugins_by_id.get(char_id)
        display = plugin.display_name if plugin else char_id
        name = f"{display} (Foe {index})"
        stars = plugin.stars if plugin else 1

        stats = Stats()
        base = party_scaling(party_level=party_level, stars=stars, stacks=1)
        scale = base * rng.uniform(0.85, 1.1)
        apply_scaled_bases(stats, scale=scale, spd=2 + max(0, stars - 1))
        stats.level = party_level
        stats.hp = stats.max_hp
        foes.append(Combatant(char_id=char_id, name=name, stats=stats, max_hp=stats.max_hp))
    return foes


def party_scaling(*, party_level: int, stars: int, stacks: int) -> float:
    stars = max(1, min(6, int(stars)))
    stacks = max(1, int(stacks))
    party_level = max(1, int(party_level))

    level_mult = 1.0 + 0.05 * max(0, party_level - 1)
    star_mult = 0.75 + 0.18 * stars
    stack_mult = 1.0 + 0.12 * max(0, stacks - 1)
    return level_mult * star_mult * stack_mult


def apply_scaled_bases(stats: Stats, *, scale: float, spd: int) -> None:
    stats.set_base_stat("max_hp", int(1000 * scale))
    stats.set_base_stat("atk", int(200 * scale))
    stats.set_base_stat("defense", int(150 * scale))
    stats.set_base_stat("regain", int(90 * scale))
    stats.set_base_stat("spd", int(max(1, spd)))


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

    base *= float(target.mitigation)
    base *= float(target.vitality)

    crit_rate = float(max(0.0, min(1.0, attacker.crit_rate)))
    crit = rng.random() < crit_rate
    if crit:
        base *= float(max(1.0, attacker.crit_damage))

    base *= rng.uniform(0.9, 1.1)
    damage = max(1, int(base))
    return damage, crit, False

