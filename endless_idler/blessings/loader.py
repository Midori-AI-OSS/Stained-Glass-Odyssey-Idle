"""Blessing module loader and validator."""

from __future__ import annotations

import importlib.util

from pathlib import Path

from endless_idler.blessings.plugin import BlessingPlugin


BLESSING_VARIABLE_NAME = "blessing"


def load_blessing_module(path: Path) -> BlessingPlugin | None:
    """Load and validate a blessing module from a Python file.

    The module must define a `blessing` variable that is a BlessingPlugin instance.

    Args:
        path: Path to the Python file containing the blessing definition

    Returns:
        The BlessingPlugin if found and valid, None otherwise
    """
    try:
        spec = importlib.util.spec_from_file_location(
            path.stem,
            path,
        )
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        blessing = getattr(module, BLESSING_VARIABLE_NAME, None)
        if isinstance(blessing, BlessingPlugin):
            return blessing

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
