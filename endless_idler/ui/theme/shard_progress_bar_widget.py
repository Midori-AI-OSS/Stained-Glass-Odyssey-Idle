from __future__ import annotations


# Element color constants (RGBA)
FIRE_RGBA = (255, 90, 40, 170)
ICE_RGBA = (80, 200, 255, 170)
LIGHTNING_RGBA = (255, 220, 0, 170)
WIND_RGBA = (80, 230, 170, 170)
DARK_RGBA = (75, 45, 100, 170)
LIGHT_RGBA = (255, 220, 120, 170)

# Generic/Multi-color cycling (used for generic damage types)
GENERIC_CYCLE_COLORS = [
    FIRE_RGBA,
    ICE_RGBA,
    LIGHTNING_RGBA,
    WIND_RGBA,
    DARK_RGBA,
    LIGHT_RGBA,
]

# Element color hex values for reference
FIRE_HEX = "#FF5A28"
ICE_HEX = "#50C8FF"
LIGHTNING_HEX = "#FFDC00"
WIND_HEX = "#50E6AA"
DARK_HEX = "#4B2D64"
LIGHT_HEX = "#FFDC78"

STYLESHEET = """
QWidget#shardProgressBarWidget {
    background-color: transparent;
    min-height: 18px;
}

QWidget#shardProgressBarWidget[elementId="fire"] {
    /* Fire element styling applied via AnimatedProgressBar color thresholds */
}

QWidget#shardProgressBarWidget[elementId="ice"] {
    /* Ice element styling applied via AnimatedProgressBar color thresholds */
}

QWidget#shardProgressBarWidget[elementId="lightning"] {
    /* Lightning element styling applied via AnimatedProgressBar color thresholds */
}

QWidget#shardProgressBarWidget[elementId="wind"] {
    /* Wind element styling applied via AnimatedProgressBar color thresholds */
}

QWidget#shardProgressBarWidget[elementId="dark"] {
    /* Dark element styling applied via AnimatedProgressBar color thresholds */
}

QWidget#shardProgressBarWidget[elementId="light"] {
    /* Light element styling applied via AnimatedProgressBar color thresholds */
}

QWidget#shardProgressBarWidget[elementId="generic"] {
    /* Generic/multi-element cycling applied dynamically */
}

QLabel#shardProgressBarLabel {
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    font-weight: 500;
}
""".strip()
