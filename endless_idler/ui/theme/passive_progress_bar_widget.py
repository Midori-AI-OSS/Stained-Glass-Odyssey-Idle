from __future__ import annotations

from endless_idler.ui.theme.shard_progress_bar_widget import DARK_RGBA
from endless_idler.ui.theme.shard_progress_bar_widget import FIRE_RGBA
from endless_idler.ui.theme.shard_progress_bar_widget import ICE_RGBA
from endless_idler.ui.theme.shard_progress_bar_widget import LIGHTNING_RGBA
from endless_idler.ui.theme.shard_progress_bar_widget import LIGHT_RGBA
from endless_idler.ui.theme.shard_progress_bar_widget import WIND_RGBA


GENERIC_RGBA = LIGHT_RGBA
TRINITY_DARK_RGBA = DARK_RGBA
TRINITY_LIGHT_RGBA = LIGHT_RGBA

ELEMENT_COLORS: dict[str, tuple[int, int, int, int]] = {
    "fire": FIRE_RGBA,
    "ice": ICE_RGBA,
    "lightning": LIGHTNING_RGBA,
    "wind": WIND_RGBA,
    "dark": DARK_RGBA,
    "light": LIGHT_RGBA,
    "generic": GENERIC_RGBA,
}

STYLESHEET = """
QWidget#passiveProgressBarWidget {
    background-color: transparent;
    min-height: 18px;
}

QWidget#passiveProgressBarWidget[styleId="default"] {
}

QWidget#passiveProgressBarWidget[styleId="trinity"] {
}

QWidget#passiveProgressBarWidget[elementId="fire"] {
}

QWidget#passiveProgressBarWidget[elementId="ice"] {
}

QWidget#passiveProgressBarWidget[elementId="lightning"] {
}

QWidget#passiveProgressBarWidget[elementId="wind"] {
}

QWidget#passiveProgressBarWidget[elementId="dark"] {
}

QWidget#passiveProgressBarWidget[elementId="light"] {
}

QWidget#passiveProgressBarWidget[elementId="generic"] {
}

QWidget#passiveProgressBarWidget[dualElementIds="dark,light"] {
}
""".strip()
