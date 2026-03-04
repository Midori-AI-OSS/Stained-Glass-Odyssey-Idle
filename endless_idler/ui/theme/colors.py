from __future__ import annotations

from PySide6.QtGui import QColor


_TYPE_COLORS: dict[str, tuple[int, int, int]] = {
    "fire": (255, 90, 40),
    "ice": (80, 200, 255),
    "lightning": (255, 220, 0),
    "wind": (80, 230, 170),
    "water": (60, 130, 255),
    "nature": (80, 200, 120),
    "arcane": (255, 80, 200),
    "dark": (75, 45, 100),
    "light": (255, 220, 120),
    "physical": (180, 180, 190),
    "generic": (235, 235, 240),
}


def normalize_element_id(value: str | None) -> str:
    key = str(value or "generic").strip().lower().replace(" ", "_").replace("-", "_")
    if key in _TYPE_COLORS:
        return key
    return "generic"


def color_for_damage_type_id(value: str | None) -> QColor:
    rgb = _TYPE_COLORS.get(normalize_element_id(value), _TYPE_COLORS["generic"])
    return QColor(*rgb)
