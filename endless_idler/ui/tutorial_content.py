"""Tutorial content and step definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TutorialPosition(Enum):
    """Where to position tutorial card relative to target."""

    RIGHT = "right"
    BOTTOM = "bottom"
    LEFT = "left"
    TOP = "top"
    CENTER = "center"


@dataclass
class TutorialStep:
    """Definition of a single tutorial step."""

    # Identification
    step_id: str  # e.g., "skills_button"
    title: str  # e.g., "Finding Your Skills"

    # Content
    message: str  # Main text (can use HTML)

    # Target highlighting
    target_widget_name: str | None  # Object name to highlight (None = no highlight)
    target_screen: str | None  # Which screen to show ("main_menu", "party_builder")
    card_position: TutorialPosition  # Where to put the tutorial card

    # Optional
    hotkey_hint: str | None = None  # e.g., "Press [K]"
    requires_action: bool = False  # Wait for user to perform action?
    auto_advance_seconds: float | None = None  # Auto-next after N seconds


# Pre-defined tutorial sequence
MAIN_TUTORIAL_STEPS = [
    TutorialStep(
        step_id="welcome",
        title="Welcome to Stained Glass Odyssey!",
        message=(
            "This quick tutorial will show you the essential features.<br><br>"
            "You can skip at any time or use the <b>Previous</b> button to go back."
        ),
        target_widget_name=None,
        target_screen="main_menu",
        card_position=TutorialPosition.CENTER,
    ),
    TutorialStep(
        step_id="skills_button",
        title="Skills & Passive Abilities",
        message=(
            "Your characters have <b>passive abilities</b> that make them unique!<br><br>"
            "Click the <b>Skills</b> button to view all character abilities.<br>"
            "Hotkey: Press <b>[K]</b> anytime to open this screen."
        ),
        target_widget_name="mainMenuButton_skills",
        target_screen="main_menu",
        card_position=TutorialPosition.RIGHT,
        hotkey_hint="Press [K]",
    ),
    TutorialStep(
        step_id="run_button",
        title="Starting Your Run",
        message=(
            "Click <b>Run</b> to enter the Party Builder.<br><br>"
            "This is where you'll assemble your team and prepare for battles."
        ),
        target_widget_name="mainMenuButton_run",
        target_screen="main_menu",
        card_position=TutorialPosition.RIGHT,
    ),
    TutorialStep(
        step_id="resources",
        title="Your Resources",
        message=(
            "These indicators show your <b>tokens</b> (for buying characters) "
            "and <b>party HP</b> (your team's health).<br><br>"
            "Hover over them for detailed tooltips."
        ),
        target_widget_name="partyHpHeader",
        target_screen="party_builder",
        card_position=TutorialPosition.BOTTOM,
    ),
    TutorialStep(
        step_id="party_zones",
        title="Party Management",
        message=(
            "Your team has three areas:<br>"
            "• <b>Bar</b> (top): Available characters to buy<br>"
            "• <b>Onsite</b> (middle): Active fighters<br>"
            "• <b>Offsite</b> (middle): Reserve support<br><br>"
            "Drag and drop characters to move them between zones!"
        ),
        target_widget_name=None,
        target_screen="party_builder",
        card_position=TutorialPosition.CENTER,
    ),
    TutorialStep(
        step_id="fight_idle",
        title="Into Battle!",
        message=(
            "When you're ready, click <b>Fight</b> to test your party in combat!<br><br>"
            "You can also use <b>Idle</b> mode to earn experience passively while you're away."
        ),
        target_widget_name=None,
        target_screen="party_builder",
        card_position=TutorialPosition.CENTER,
    ),
    TutorialStep(
        step_id="complete",
        title="You're Ready!",
        message=(
            "That covers the basics!<br><br>"
            "• Press <b>[K]</b> to view Skills anytime<br>"
            "• Press <b>[ESC]</b> to return to the main menu<br>"
            "• Check the <b>Guidebook</b> for more help (coming soon)<br><br>"
            "Good luck on your journey! ✨"
        ),
        target_widget_name=None,
        target_screen="main_menu",
        card_position=TutorialPosition.CENTER,
    ),
]
