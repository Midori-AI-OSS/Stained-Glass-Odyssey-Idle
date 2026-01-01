from __future__ import annotations

from PySide6.QtGui import QColor


_TYPE_COLORS: dict[str, tuple[int, int, int]] = {
    "fire": (255, 90, 40),
    "ice": (80, 200, 255),
    "lightning": (185, 90, 255),
    "wind": (80, 230, 170),
    "water": (60, 130, 255),
    "nature": (80, 200, 120),
    "arcane": (255, 80, 200),
    "dark": (150, 80, 220),
    "light": (255, 220, 120),
    "physical": (180, 180, 190),
    "generic": (235, 235, 240),
}


def color_for_damage_type_id(value: str) -> QColor:
    key = str(value or "generic").strip().lower().replace(" ", "_").replace("-", "_")
    rgb = _TYPE_COLORS.get(key, _TYPE_COLORS["generic"])
    return QColor(*rgb)
