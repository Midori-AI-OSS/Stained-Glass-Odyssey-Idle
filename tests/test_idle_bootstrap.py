from __future__ import annotations

import random

import pytest

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.save import OFFSITE_SLOTS
from endless_idler.save import ONSITE_SLOTS
from endless_idler.save import STANDBY_SLOTS
from endless_idler.save import RunSave
from endless_idler.save_bootstrap import bootstrap_party
from endless_idler.save_bootstrap import has_active_party
from endless_idler.save_bootstrap import should_bootstrap_party


def _plugin(char_id: str, placement: str) -> CharacterPlugin:
    return CharacterPlugin(char_id=char_id, display_name=char_id.title(), placement=placement)


def test_should_bootstrap_only_when_no_active_party() -> None:
    save = RunSave()
    assert should_bootstrap_party(save) is True
    assert has_active_party(save) is False

    save.onsite[0] = "ally"
    assert should_bootstrap_party(save) is False
    assert has_active_party(save) is True


def test_bootstrap_assigns_exactly_one_starter_character() -> None:
    plugins = [
        _plugin("lady_darkness", "onsite"),
        _plugin("persona_light_and_dark", "both"),
        _plugin("other_onsite", "onsite"),
        _plugin("other_offsite", "offsite"),
    ]

    save = RunSave()
    bootstrap_party(save, plugins=plugins, rng=random.Random(7))

    assigned = [item for item in [*save.onsite, *save.offsite] if item]

    assert len(assigned) == 1
    assert assigned[0] in {"lady_darkness", "persona_light_and_dark"}
    assert save.stacks == {assigned[0]: 1}
    assert save.onsite.count(None) == ONSITE_SLOTS - 1
    assert save.offsite.count(None) == OFFSITE_SLOTS
    assert save.standby == [None] * STANDBY_SLOTS


def test_bootstrap_raises_when_starter_pool_missing() -> None:
    plugins = [
        _plugin("only_onsite", "onsite"),
        _plugin("only_offsite", "offsite"),
    ]

    save = RunSave()
    with pytest.raises(ValueError, match="Starter pool is empty"):
        bootstrap_party(save, plugins=plugins, rng=random.Random(5))
