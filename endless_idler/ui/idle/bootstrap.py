from __future__ import annotations

import random

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.save import OFFSITE_SLOTS
from endless_idler.save import ONSITE_SLOTS
from endless_idler.save import STANDBY_SLOTS
from endless_idler.save import RunSave


_ONSITE_PLACEMENTS = frozenset({"onsite", "both"})
_OFFSITE_PLACEMENTS = frozenset({"offsite", "both"})
_STARTER_CHAR_IDS = ("lady_darkness", "persona_light_and_dark")


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
    onsite: list[str | None] = [None] * ONSITE_SLOTS
    offsite: list[str | None] = [None] * OFFSITE_SLOTS
    standby: list[str | None] = [None] * STANDBY_SLOTS

    starter_pool = [plugin for plugin in plugins if plugin.char_id in _STARTER_CHAR_IDS]
    if not starter_pool:
        raise ValueError("Starter pool is empty; expected at least one starter plugin.")

    starter = rng.choice(starter_pool)
    starter_id = starter.char_id

    if starter.placement in _ONSITE_PLACEMENTS:
        onsite[0] = starter_id
    elif starter.placement in _OFFSITE_PLACEMENTS:
        offsite[0] = starter_id
    else:
        raise ValueError(f"Unsupported starter placement for {starter_id}: {starter.placement!r}")

    save.onsite = onsite
    save.offsite = offsite
    save.standby = standby

    save.stacks = {starter_id: max(1, int(save.stacks.get(starter_id, 1)))}
