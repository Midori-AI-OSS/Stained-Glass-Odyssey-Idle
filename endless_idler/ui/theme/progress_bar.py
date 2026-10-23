from __future__ import annotations

# Default colors (can be overridden by caller)
DEFAULT_BASE_RGBA = (52, 152, 219, 170)
DEFAULT_AURORA_START_RGBA = (78, 170, 230, 170)
DEFAULT_AURORA_MID_RGBA = (62, 178, 130, 170)
DEFAULT_AURORA_END_RGBA = (215, 188, 120, 176)
DEFAULT_SHIMMER_RGBA = (245, 250, 255, 128)
DEFAULT_TRACK_FILL_RGBA = (0, 0, 0, 42)
DEFAULT_TRACK_BORDER_RGBA = (255, 255, 255, 24)

STYLESHEET = """
QWidget#animatedProgressBar {
    background-color: transparent;
    min-height: 14px;
}
""".strip()
