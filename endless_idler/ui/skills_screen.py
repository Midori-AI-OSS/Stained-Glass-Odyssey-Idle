from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.passives.registry import load_passive


class SkillsScreenWidget(QWidget):
    """Screen displaying all characters and their passive abilities."""
    
    back_requested = Signal()

    def __init__(self, *, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("skillsScreen")

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        self.setLayout(layout)

        # Header with back button
        header = QHBoxLayout()
        header.setSpacing(12)
        
        title = QLabel("Skills & Passive Abilities")
        title.setObjectName("skillsScreenTitle")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: rgba(255, 255, 255, 240);")
        header.addWidget(title)
        
        header.addStretch(1)
        
        back_button = QPushButton("← Back")
        back_button.setObjectName("skillsBackButton")
        back_button.setMinimumHeight(40)
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        back_button.clicked.connect(self.back_requested.emit)
        header.addWidget(back_button)
        
        layout.addLayout(header)

        # Content area with scroll
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setFrameShape(QFrame.Shape.NoFrame)
        content_scroll.setObjectName("skillsScrollArea")
        layout.addWidget(content_scroll)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        content_widget.setLayout(content_layout)
        content_scroll.setWidget(content_widget)

        # Discover and display all characters
        plugins = discover_character_plugins()
        
        # Sort by display name for better UX
        plugins.sort(key=lambda p: p.display_name.lower())

        for plugin in plugins:
            card = CharacterSkillCard(
                char_id=plugin.char_id,
                display_name=plugin.display_name,
                stars=plugin.stars,
                passive_ids=plugin.passives,
            )
            content_layout.addWidget(card)

        content_layout.addStretch(1)


class CharacterSkillCard(QFrame):
    """Card displaying a character and their passive abilities."""

    def __init__(
        self,
        *,
        char_id: str,
        display_name: str,
        stars: int,
        passive_ids: list[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("characterSkillCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Apply star-based styling
        star_colors = {
            1: "#708090",  # Grey
            2: "#90EE90",  # Light green
            3: "#87CEEB",  # Sky blue
            4: "#DDA0DD",  # Plum
            5: "#FFD700",  # Gold
        }
        star_color = star_colors.get(stars, "#708090")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self.setLayout(layout)

        # Character header
        header = QHBoxLayout()
        header.setSpacing(12)
        
        name_label = QLabel(display_name)
        name_label.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {star_color};"
        )
        header.addWidget(name_label)
        
        stars_label = QLabel("★" * stars)
        stars_label.setStyleSheet(f"font-size: 16px; color: {star_color};")
        header.addWidget(stars_label)
        
        header.addStretch(1)
        
        layout.addLayout(header)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {star_color}; max-height: 2px;")
        layout.addWidget(separator)

        # Passives section
        if not passive_ids:
            no_passives = QLabel("No passive abilities")
            no_passives.setStyleSheet("color: rgba(255, 255, 255, 120); font-style: italic;")
            layout.addWidget(no_passives)
        else:
            for passive_id in passive_ids:
                passive = load_passive(passive_id)
                if passive:
                    passive_widget = PassiveAbilityWidget(
                        display_name=passive.display_name,
                        description=passive.description,
                        triggers=[t.value for t in passive.triggers],
                    )
                    layout.addWidget(passive_widget)


class PassiveAbilityWidget(QFrame):
    """Widget displaying a single passive ability."""

    def __init__(
        self,
        *,
        display_name: str,
        description: str,
        triggers: list[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("passiveAbilityWidget")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            "QFrame#passiveAbilityWidget { "
            "background-color: rgba(255, 255, 255, 0.03); "
            "border: 1px solid rgba(255, 255, 255, 0.1); "
            "border-radius: 4px; "
            "}"
        )
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        self.setLayout(layout)

        # Passive name
        name_label = QLabel(display_name)
        name_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #FFD700;"
        )
        layout.addWidget(name_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            "font-size: 12px; color: rgba(255, 255, 255, 180); line-height: 1.4;"
        )
        layout.addWidget(desc_label)

        # Triggers
        if triggers:
            triggers_text = "Triggers: " + ", ".join(t.upper() for t in triggers)
            triggers_label = QLabel(triggers_text)
            triggers_label.setStyleSheet(
                "font-size: 11px; color: rgba(255, 200, 100, 150); font-style: italic; margin-top: 4px;"
            )
            layout.addWidget(triggers_label)
