from __future__ import annotations

from PySide6.QtWidgets import QApplication

from endless_idler.ui.theme.idle_hub_widget import STYLESHEET as IDLE_HUB_WIDGET_STYLESHEET
from endless_idler.ui.theme.idle_offsite_card import STYLESHEET as IDLE_OFFSITE_CARD_STYLESHEET
from endless_idler.ui.theme.idle_screen_widget import STYLESHEET as IDLE_SCREEN_WIDGET_STYLESHEET
from endless_idler.ui.theme.main_menu_widget import STYLESHEET as MAIN_MENU_WIDGET_STYLESHEET
from endless_idler.ui.theme.onsite_character_card import STYLESHEET as ONSITE_CHARACTER_CARD_STYLESHEET
from endless_idler.ui.theme.party_hp_header import STYLESHEET as PARTY_HP_HEADER_STYLESHEET
from endless_idler.ui.theme.tooltip_widget import STYLESHEET as TOOLTIP_WIDGET_STYLESHEET


def build_stained_glass_stylesheet() -> str:
    sections = (
        MAIN_MENU_WIDGET_STYLESHEET,
        IDLE_HUB_WIDGET_STYLESHEET,
        PARTY_HP_HEADER_STYLESHEET,
        IDLE_SCREEN_WIDGET_STYLESHEET,
        ONSITE_CHARACTER_CARD_STYLESHEET,
        IDLE_OFFSITE_CARD_STYLESHEET,
        TOOLTIP_WIDGET_STYLESHEET,
    )
    return "\n\n".join(section for section in sections if section)


def apply_stained_glass_theme(app: QApplication) -> None:
    app.setStyleSheet(build_stained_glass_stylesheet())
