"""Helpers for static passive plugin definitions."""

from __future__ import annotations

from endless_idler.passives.plugin import PassivePlugin


def _display_name_for(passive_id: str) -> str:
    return " ".join(part.capitalize() for part in passive_id.split("_"))


def make_passive(passive_id: str) -> PassivePlugin:
    display_name = _display_name_for(passive_id)
    return PassivePlugin(
        passive_id=passive_id,
        display_name=display_name,
        description=f"{display_name} passive definition for the rebuilt idle passive framework.",
    )
