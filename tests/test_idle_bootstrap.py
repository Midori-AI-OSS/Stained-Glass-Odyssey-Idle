from __future__ import annotations

import random

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.save import OFFSITE_SLOTS
from endless_idler.save import ONSITE_SLOTS
from endless_idler.save import RunSave
from endless_idler.ui.idle.bootstrap import bootstrap_party
from endless_idler.ui.idle.bootstrap import has_active_party
from endless_idler.ui.idle.bootstrap import should_bootstrap_party


def _plugin(char_id: str, placement: str) -> CharacterPlugin:
    return CharacterPlugin(char_id=char_id, display_name=char_id.title(), placement=placement)


def test_should_bootstrap_only_when_no_active_party() -> None:
    save = RunSave()
    assert should_bootstrap_party(save) is True
    assert has_active_party(save) is False

    save.onsite[0] = "ally"
    assert should_bootstrap_party(save) is False
    assert has_active_party(save) is True


def test_bootstrap_fills_without_duplicates_across_onsite_and_offsite() -> None:
    plugins = [
        _plugin("a", "onsite"),
        _plugin("b", "offsite"),
        _plugin("c", "both"),
        _plugin("d", "both"),
        _plugin("e", "both"),
        _plugin("f", "onsite"),
        _plugin("g", "offsite"),
    ]

    save = RunSave()
    bootstrap_party(save, plugins=plugins, rng=random.Random(7))

    onsite = [item for item in save.onsite if item]
    offsite = [item for item in save.offsite if item]
    combined = onsite + offsite

    assert len(combined) == len(set(combined))


def test_bootstrap_leaves_empty_slots_when_pool_exhausted() -> None:
    plugins = [
        _plugin("only_onsite", "onsite"),
        _plugin("only_offsite", "offsite"),
    ]

    save = RunSave()
    bootstrap_party(save, plugins=plugins, rng=random.Random(5))

    onsite = [item for item in save.onsite if item]
    offsite = [item for item in save.offsite if item]

    assert onsite == ["only_onsite"]
    assert offsite == ["only_offsite"]
    assert save.onsite.count(None) == ONSITE_SLOTS - 1
    assert save.offsite.count(None) == OFFSITE_SLOTS - 1
