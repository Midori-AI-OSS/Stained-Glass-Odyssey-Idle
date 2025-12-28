"""Character plugins.

Each character is defined as its own module (e.g. `endless_idler/characters/ally.py`).
The UI uses `discover_character_plugins()` to list available characters and load
their images from `endless_idler/assets/characters/<char_id>/`.
"""

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.characters.plugins import discover_character_plugins

__all__ = [
    "CharacterPlugin",
    "discover_character_plugins",
]
