from __future__ import annotations

from PySide6.QtWidgets import QApplication

from endless_idler.ui.theme.app_shell_widget import (
    STYLESHEET as APP_SHELL_WIDGET_STYLESHEET,
)
from endless_idler.ui.theme.blessing_panel_widget import (
    STYLESHEET as BLESSING_PANEL_WIDGET_STYLESHEET,
)
from endless_idler.ui.theme.home_widget import STYLESHEET as HOME_WIDGET_STYLESHEET
from endless_idler.ui.theme.layout_screen_widget import (
    STYLESHEET as LAYOUT_SCREEN_WIDGET_STYLESHEET,
)
from endless_idler.ui.theme.idle_blessing_meter_widget import (
    STYLESHEET as IDLE_BLESSING_METER_WIDGET_STYLESHEET,
)
from endless_idler.ui.theme.idle_offsite_card import (
    STYLESHEET as IDLE_OFFSITE_CARD_STYLESHEET,
)
from endless_idler.ui.theme.idle_screen_widget import (
    STYLESHEET as IDLE_SCREEN_WIDGET_STYLESHEET,
)
from endless_idler.ui.theme.onsite_character_card import (
    STYLESHEET as ONSITE_CHARACTER_CARD_STYLESHEET,
)
from endless_idler.ui.theme.party_hp_header import (
    STYLESHEET as PARTY_HP_HEADER_STYLESHEET,
)
from endless_idler.ui.theme.radio_control_widget import (
    STYLESHEET as RADIO_CONTROL_WIDGET_STYLESHEET,
)
from endless_idler.ui.theme.settings_widget import (
    STYLESHEET as SETTINGS_WIDGET_STYLESHEET,
)
from endless_idler.ui.theme.tooltip_widget import (
    STYLESHEET as TOOLTIP_WIDGET_STYLESHEET,
)
from endless_idler.ui.theme.progress_bar import STYLESHEET as PROGRESS_BAR_STYLESHEET
from endless_idler.ui.theme.shard_progress_bar_widget import (
    STYLESHEET as SHARD_PROGRESS_BAR_WIDGET_STYLESHEET,
)


def build_stained_glass_stylesheet() -> str:
    sections = (
        APP_SHELL_WIDGET_STYLESHEET,
        BLESSING_PANEL_WIDGET_STYLESHEET,
        HOME_WIDGET_STYLESHEET,
        LAYOUT_SCREEN_WIDGET_STYLESHEET,
        PARTY_HP_HEADER_STYLESHEET,
        IDLE_SCREEN_WIDGET_STYLESHEET,
        IDLE_BLESSING_METER_WIDGET_STYLESHEET,
        ONSITE_CHARACTER_CARD_STYLESHEET,
        IDLE_OFFSITE_CARD_STYLESHEET,
        RADIO_CONTROL_WIDGET_STYLESHEET,
        SETTINGS_WIDGET_STYLESHEET,
        TOOLTIP_WIDGET_STYLESHEET,
        PROGRESS_BAR_STYLESHEET,
        SHARD_PROGRESS_BAR_WIDGET_STYLESHEET,
    )
    return "\n\n".join(section for section in sections if section)


def apply_stained_glass_theme(app: QApplication) -> None:
    app.setStyleSheet(build_stained_glass_stylesheet())
