from __future__ import annotations

import random

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.save import OFFSITE_SLOTS
from endless_idler.save import ONSITE_SLOTS
from endless_idler.save import RunSave


_ONSITE_PLACEMENTS = frozenset({"onsite", "both"})
_OFFSITE_PLACEMENTS = frozenset({"offsite", "both"})


def has_active_party(save: RunSave) -> bool:
    return any(bool(item) for item in save.onsite) or any(bool(item) for item in save.offsite)


def should_bootstrap_party(save: RunSave) -> bool:
    return not has_active_party(save)


def bootstrap_party(
    save: RunSave,
    *,
    plugins: list[CharacterPlugin],
    rng: random.Random,
) -> None:
    onsite_pool = [plugin.char_id for plugin in plugins if plugin.placement in _ONSITE_PLACEMENTS]
    offsite_pool = [plugin.char_id for plugin in plugins if plugin.placement in _OFFSITE_PLACEMENTS]

    rng.shuffle(onsite_pool)
    rng.shuffle(offsite_pool)

    used: set[str] = set()
    onsite: list[str | None] = [None] * ONSITE_SLOTS
    offsite: list[str | None] = [None] * OFFSITE_SLOTS

    onsite_index = 0
    for char_id in onsite_pool:
        if onsite_index >= ONSITE_SLOTS:
            break
        if char_id in used:
            continue
        onsite[onsite_index] = char_id
        onsite_index += 1
        used.add(char_id)

    offsite_index = 0
    for char_id in offsite_pool:
        if offsite_index >= OFFSITE_SLOTS:
            break
        if char_id in used:
            continue
        offsite[offsite_index] = char_id
        offsite_index += 1
        used.add(char_id)

    save.onsite = onsite
    save.offsite = offsite

    active_ids = {char_id for char_id in onsite + offsite if char_id}
    stacks: dict[str, int] = {}
    for char_id in active_ids:
        stacks[char_id] = max(1, int(save.stacks.get(char_id, 1)))
    save.stacks = stacks
