from __future__ import annotations

import random

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.save import RunSave
from endless_idler.ui.idle.idle_state import IdleGameState


def test_runtime_snapshot_exports_full_canonical_passives_and_active_runtime() -> None:
    save = RunSave()
    state = IdleGameState(
        char_ids=["onsite"],
        party_level=1,
        stacks={"onsite": 1},
        plugins_by_id={
            "onsite": CharacterPlugin(
                char_id="onsite",
                display_name="Onsite",
                placement="onsite",
                passives=["lady_fire_infernal_momentum"],
            )
        },
        rng=random.Random(7),
        passives_data=save.passives,
    )

    snapshot = state.export_runtime_snapshot()

    passives = snapshot.get("passives")
    assert isinstance(passives, dict)
    assert passives == save.passives

    passive_runtime = snapshot.get("passive_runtime")
    assert isinstance(passive_runtime, dict)
    assert passive_runtime == {"lady_fire_infernal_momentum": {}}
    assert "ally_overload" not in passive_runtime


def test_process_tick_keeps_noop_passive_runtime_stable() -> None:
    state = IdleGameState(
        char_ids=["onsite"],
        party_level=1,
        stacks={"onsite": 1},
        plugins_by_id={
            "onsite": CharacterPlugin(
                char_id="onsite",
                display_name="Onsite",
                placement="onsite",
                passives=["lady_fire_infernal_momentum"],
            )
        },
        rng=random.Random(11),
        passives_data=RunSave().passives,
    )

    snapshot = state.process_tick()

    passive_runtime = snapshot.get("passive_runtime")
    assert isinstance(passive_runtime, dict)
    assert passive_runtime == {"lady_fire_infernal_momentum": {}}
