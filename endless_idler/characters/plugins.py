"""Character plugin registry.

Each character lives as its own Python file in `endless_idler/characters/`.
This module discovers those character files without importing them (the copied
character modules come from another project and may have unmet dependencies).

Images are loaded from `endless_idler/assets/characters/<char_id>/` and a random
image is selected on each fresh app load.
"""

from __future__ import annotations

import ast
import random

from dataclasses import dataclass
from pathlib import Path


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
        if path.name in {"__init__.py", "plugins.py", "foe_base.py"}:
            continue

        char_id, display_name = _extract_metadata(path)
        if not char_id:
            continue
        plugins.append(CharacterPlugin(char_id=char_id, display_name=display_name))

    return plugins


def _extract_metadata(path: Path) -> tuple[str, str]:
    char_id = path.stem
    display_name = _derive_display_name(char_id)

    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return char_id, display_name

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return char_id, display_name

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        found_id, found_name = _extract_from_classdef(node)
        if found_id:
            char_id = found_id
        if found_name:
            display_name = found_name
        if found_id or found_name:
            break

    if not display_name:
        display_name = _derive_display_name(char_id)

    return char_id, display_name


def _extract_from_classdef(node: ast.ClassDef) -> tuple[str | None, str | None]:
    char_id: str | None = None
    display_name: str | None = None

    for stmt in node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    if target.id == "id":
                        char_id = _const_str(stmt.value)
                    elif target.id == "name":
                        display_name = _const_str(stmt.value)
        elif isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name):
                if stmt.target.id == "id":
                    char_id = _const_str(stmt.value)
                elif stmt.target.id == "name":
                    display_name = _const_str(stmt.value)

        if char_id and display_name:
            break

    return char_id, display_name


def _const_str(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _derive_display_name(char_id: str) -> str:
    return " ".join(part.capitalize() for part in char_id.split("_"))

