"""Character plugin registry.

Each character lives as its own Python file in `endless_idler/characters/`.
This module discovers those character files without importing them (the copied
character modules come from another project and may have unmet dependencies).

Images are loaded from `endless_idler/assets/characters/<char_id>/` and a random
image is selected on each fresh app load.
"""

from __future__ import annotations

import random

from dataclasses import field
from dataclasses import dataclass
from pathlib import Path

from endless_idler.characters.metadata import DEFAULT_BASE_STATS
from endless_idler.characters.metadata import extract_character_metadata


_IMAGE_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
)

_CHARACTERS_DIR = Path(__file__).resolve().parent
_CHARACTER_ASSETS_DIR = _CHARACTERS_DIR.parent / "assets" / "characters"


@dataclass(frozen=True, slots=True)
class CharacterPlugin:
    char_id: str
    display_name: str
    stars: int = 1
    placement: str = "both"
    damage_type_id: str = "generic"
    damage_type_random: bool = False
    base_stats: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_BASE_STATS))
    base_aggro: float | None = None
    damage_reduction_passes: int | None = None
    passives: list[str] = field(default_factory=list)

    @property
    def image_dir(self) -> Path:
        return _CHARACTER_ASSETS_DIR / self.char_id

    def image_paths(self) -> list[Path]:
        if not self.image_dir.is_dir():
            return []

        images: list[Path] = []
        for path in self.image_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in _IMAGE_EXTENSIONS:
                continue
            images.append(path)

        images.sort()
        return images

    def random_image_path(self, rng: random.Random) -> Path | None:
        images = self.image_paths()
        if not images:
            return None
        return rng.choice(images)


def discover_character_plugins() -> list[CharacterPlugin]:
    """Discover character plugins from `endless_idler/characters/*.py` files."""

    plugins: list[CharacterPlugin] = []
    for path in sorted(_CHARACTERS_DIR.glob("*.py")):
        if path.name in {"__init__.py", "plugins.py", "foe_base.py", "player.py", "slime.py"}:
            continue

        (
            char_id,
            display_name,
            stars,
            placement,
            damage_type_id,
            damage_type_random,
            base_stats,
            base_aggro,
            damage_reduction_passes,
            passives,
        ) = extract_character_metadata(path)
        if not char_id:
            continue
        plugins.append(
            CharacterPlugin(
                char_id=char_id,
                display_name=display_name,
                stars=stars,
                placement=placement,
                damage_type_id=damage_type_id,
                damage_type_random=damage_type_random,
                base_stats=base_stats,
                base_aggro=base_aggro,
                damage_reduction_passes=damage_reduction_passes,
                passives=passives,
            )
        )

    return plugins
