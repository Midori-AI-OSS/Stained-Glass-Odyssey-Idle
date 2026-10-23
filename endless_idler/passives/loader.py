"""Passive module loader and validator."""

from __future__ import annotations

import importlib.util

from pathlib import Path

from endless_idler.passives.plugin import PassivePlugin


PASSIVE_VARIABLE_NAME = "passive"


def load_passive_module(path: Path) -> PassivePlugin | None:
    """Load and validate a passive module from a Python file."""
    try:
        spec = importlib.util.spec_from_file_location(
            f"endless_idler.passives.{path.stem}",
            path,
        )
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        passive = getattr(module, PASSIVE_VARIABLE_NAME, None)
        if isinstance(passive, PassivePlugin):
            return passive

    except (
        AttributeError,
        FileNotFoundError,
        ImportError,
        OSError,
        SyntaxError,
        ValueError,
    ):
        return None

    return None
