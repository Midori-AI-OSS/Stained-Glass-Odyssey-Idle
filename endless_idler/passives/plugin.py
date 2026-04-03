"""PassivePlugin dataclass definition."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True, slots=True)
class PassivePlugin:
    """Metadata describing a passive plugin.

    Passives are discovered from module-level `passive` objects and remain owned
    by character metadata through `CharacterPlugin.passives`.
    """

    passive_id: str
    display_name: str
    description: str
    save_schema: dict[str, type] = field(default_factory=dict)
