from __future__ import annotations

import os
import random

from pathlib import Path
from dataclasses import dataclass


_IMAGE_EXTS = {
    ".bmp",
    ".jpeg",
    ".jpg",
    ".png",
    ".webp",
}


@dataclass(frozen=True, slots=True)
class CharacterPlugin:
    char_id: str
    display_name: str
    image_paths: tuple[Path, ...]

    def random_image_path(self, rng: random.Random) -> Path:
        return rng.choice(self.image_paths)


def default_character_roots() -> list[Path]:
    roots: list[Path] = []

    env = os.environ.get("ENDLESS_IDLER_CHAR_ROOTS")
    if env:
        for raw in env.split(os.pathsep):
            path = Path(raw).expanduser()
            if path.is_dir():
                roots.append(path)

    repo_root = _find_repo_root(Path(__file__).resolve())
    if repo_root is not None:
        assets_root = repo_root / "endless_idler" / "assets" / "characters"
        if assets_root.is_dir():
            roots.append(assets_root)

        codex_root = repo_root / ".codex" / "temp" / "char_photos"
        if codex_root.is_dir():
            for characters_dir in codex_root.glob(
                "*/Experimentation/Python-idle-game/idle_game/assets/characters"
            ):
                if characters_dir.is_dir():
                    roots.append(characters_dir)

    tmp_root = Path("/tmp")
    for characters_dir in tmp_root.glob(
        "stained-glass-odyssey-endless-*/Experimentation/Python-idle-game/idle_game/assets/characters"
    ):
        if characters_dir.is_dir():
            roots.append(characters_dir)

    return _dedupe_paths(roots)


def discover_character_plugins(*, roots: list[Path]) -> list[CharacterPlugin]:
    plugins: dict[str, list[Path]] = {}

    for root in roots:
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            char_id = child.name.strip()
            if not char_id:
                continue
            images = _collect_images(child)
            if not images:
                continue
            plugins.setdefault(char_id, []).extend(images)

    result: list[CharacterPlugin] = []
    for char_id in sorted(plugins):
        images = tuple(_dedupe_paths(plugins[char_id]))
        if not images:
            continue
        result.append(
            CharacterPlugin(
                char_id=char_id,
                display_name=_display_name(char_id),
                image_paths=images,
            )
        )
    return result


def _collect_images(folder: Path) -> list[Path]:
    images: list[Path] = []
    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in _IMAGE_EXTS:
            continue
        images.append(path)
    return images


def _display_name(char_id: str) -> str:
    return char_id.replace("_", " ").strip().title()


def _find_repo_root(start: Path) -> Path | None:
    for parent in (start, *start.parents):
        if (parent / "pyproject.toml").is_file() and (parent / "endless_idler").is_dir():
            return parent
    return None


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    deduped: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(resolved)
    return deduped
