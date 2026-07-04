"""PassivePlugin dataclass definition."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from types import GenericAlias
from typing import Any


def _build_default_runtime_state(_saved_state: dict[str, Any]) -> dict[str, Any]:
    return {}


def _noop_tick(_context: Any) -> None:
    return None


PassiveRuntimeStateFactory = Callable[[dict[str, Any]], dict[str, Any]]
PassiveTickHook = Callable[[Any], None]
PassiveSaveFieldType = type | GenericAlias


@dataclass(frozen=True, slots=True)
class PassivePlugin:
    """Metadata describing a passive plugin.

    Passives are discovered from module-level `passive` objects and remain owned
    by character metadata through `CharacterPlugin.passives`.
    """

    passive_id: str
    display_name: str
    description: str
    save_schema: dict[str, PassiveSaveFieldType] = field(default_factory=dict)
    tick_order: int = 0
    build_runtime_state: PassiveRuntimeStateFactory = _build_default_runtime_state
    tick: PassiveTickHook = _noop_tick
