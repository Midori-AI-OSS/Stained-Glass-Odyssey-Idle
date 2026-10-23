from __future__ import annotations

import random

from collections.abc import Sequence

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.save import OFFSITE_SLOTS
from endless_idler.save import ONSITE_SLOTS
from endless_idler.save import STANDBY_SLOTS
from endless_idler.save import RunSave


_ONSITE_PLACEMENTS = frozenset({"onsite", "both"})
_OFFSITE_PLACEMENTS = frozenset({"offsite", "both"})
_LADY_DARKNESS_ID = "lady_darkness"
_LADY_LIGHT_ID = "lady_light"
_PERSONA_LIGHT_AND_DARK_ID = "persona_light_and_dark"
_TRINITY_CHAR_IDS = (
    _LADY_DARKNESS_ID,
    _LADY_LIGHT_ID,
    _PERSONA_LIGHT_AND_DARK_ID,
)


def has_active_party(save: RunSave) -> bool:
    return any(bool(item) for item in save.onsite) or any(bool(item) for item in save.offsite)


def should_bootstrap_party(save: RunSave) -> bool:
    return not has_active_party(save)


def bootstrap_party(
    save: RunSave,
    *,
    plugins: Sequence[CharacterPlugin],
    rng: random.Random,
) -> None:
    onsite: list[str | None] = [None] * ONSITE_SLOTS
    offsite: list[str | None] = [None] * OFFSITE_SLOTS
    standby: list[str | None] = [None] * STANDBY_SLOTS

    plugin_by_id = {plugin.char_id: plugin for plugin in plugins}
    missing = [char_id for char_id in _TRINITY_CHAR_IDS if char_id not in plugin_by_id]
    if missing:
        raise ValueError(
            "Missing required trinity plugins: " + ", ".join(sorted(missing))
        )

    lady_darkness = plugin_by_id[_LADY_DARKNESS_ID]
    if lady_darkness.placement not in _ONSITE_PLACEMENTS:
        raise ValueError(
            f"Unsupported trinity placement for {_LADY_DARKNESS_ID}: {lady_darkness.placement!r}"
        )
    onsite[0] = _LADY_DARKNESS_ID

    lady_light = plugin_by_id[_LADY_LIGHT_ID]
    if lady_light.placement not in _OFFSITE_PLACEMENTS:
        raise ValueError(
            f"Unsupported trinity placement for {_LADY_LIGHT_ID}: {lady_light.placement!r}"
        )
    offsite[0] = _LADY_LIGHT_ID

    persona = plugin_by_id[_PERSONA_LIGHT_AND_DARK_ID]
    persona_lane_options: list[str] = []
    if persona.placement in _ONSITE_PLACEMENTS and any(slot is None for slot in onsite):
        persona_lane_options.append("onsite")
    if persona.placement in _OFFSITE_PLACEMENTS and any(slot is None for slot in offsite):
        persona_lane_options.append("offsite")
    if not persona_lane_options:
        raise ValueError(
            "Unsupported trinity placement for "
            + f"{_PERSONA_LIGHT_AND_DARK_ID}: {persona.placement!r}"
        )

    persona_lane = rng.choice(persona_lane_options)
    if persona_lane == "onsite":
        onsite[onsite.index(None)] = _PERSONA_LIGHT_AND_DARK_ID
    else:
        offsite[offsite.index(None)] = _PERSONA_LIGHT_AND_DARK_ID

    save.onsite = onsite
    save.offsite = offsite
    save.standby = standby
    save.stacks = {
        char_id: max(1, int(save.stacks.get(char_id, 1)))
        for char_id in _TRINITY_CHAR_IDS
    }
