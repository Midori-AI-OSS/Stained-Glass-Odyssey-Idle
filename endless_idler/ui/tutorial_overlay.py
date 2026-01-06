"""Tutorial overlay widget with spotlight effect."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QPropertyAnimation, QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygon
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from endless_idler.ui.tutorial_content import TutorialPosition, TutorialStep


class TutorialCard(QFrame):
    """Tutorial content card with stained glass aesthetic."""

    next_requested = Signal()
    previous_requested = Signal()
    skip_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("tutorialCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(420)
        self.setMinimumHeight(200)

        # Drop shadow for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 200))
        self.setGraphicsEffect(shadow)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        self.setLayout(layout)

        # Progress indicator
        self._progress_label = QLabel()
        self._progress_label.setObjectName("tutorialProgress")
        self._progress_label.setStyleSheet("color: rgba(200, 200, 200, 180); font-size: 12px;")
        layout.addWidget(self._progress_label)

        # Title
        self._title_label = QLabel()
        self._title_label.setObjectName("tutorialTitle")
        self._title_label.setStyleSheet("color: rgba(255, 255, 255, 235); font-size: 20px; font-weight: bold;")
        self._title_label.setWordWrap(True)
        layout.addWidget(self._title_label)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 28); border: none; height: 1px;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        # Message content
        self._message_label = QLabel()
        self._message_label.setObjectName("tutorialMessage")
        self._message_label.setTextFormat(Qt.TextFormat.RichText)
        self._message_label.setWordWrap(True)
        self._message_label.setStyleSheet("color: rgba(255, 255, 255, 220); font-size: 14px; line-height: 1.5;")
        layout.addWidget(self._message_label)

        # Hotkey hint (optional)
        self._hotkey_label = QLabel()
        self._hotkey_label.setObjectName("tutorialHotkey")
        self._hotkey_label.setStyleSheet(
            "color: rgba(120, 180, 255, 255); font-size: 13px; font-weight: bold; padding: 8px;"
        )
        self._hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hotkey_label.hide()
        layout.addWidget(self._hotkey_label)

        layout.addStretch(1)

        # Button row
        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        layout.addLayout(button_row)

        # Previous button
        self._prev_button = QPushButton("← Previous")
        self._prev_button.setObjectName("tutorialPrevButton")
        self._prev_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._prev_button.setMinimumHeight(36)
        self._prev_button.clicked.connect(self.previous_requested.emit)
        button_row.addWidget(self._prev_button)

        button_row.addStretch(1)

        # Skip button
        skip_button = QPushButton("Skip Tutorial")
        skip_button.setObjectName("tutorialSkipButton")
        skip_button.setCursor(Qt.CursorShape.PointingHandCursor)
        skip_button.setMinimumHeight(36)
        skip_button.clicked.connect(self.skip_requested.emit)
        button_row.addWidget(skip_button)

        # Next button
        self._next_button = QPushButton("Next →")
        self._next_button.setObjectName("tutorialNextButton")
        self._next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next_button.setMinimumHeight(36)
        self._next_button.clicked.connect(self.next_requested.emit)
        button_row.addWidget(self._next_button)

        # Apply stained glass styling
        self.setStyleSheet(
            """
            #tutorialCard {
                background-color: rgba(20, 30, 60, 220);
                border: 1px solid rgba(255, 255, 255, 28);
                border-radius: 8px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 26);
                border: 1px solid rgba(255, 255, 255, 56);
                border-radius: 4px;
                color: rgba(255, 255, 255, 235);
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(120, 180, 255, 56);
                border: 1px solid rgba(120, 180, 255, 130);
            }
            QPushButton:pressed {
                background-color: rgba(80, 140, 215, 90);
            }
            QPushButton:disabled {
                background-color: rgba(100, 100, 100, 26);
                border: 1px solid rgba(100, 100, 100, 56);
                color: rgba(150, 150, 150, 180);
            }
            """
        )

    def set_content(
        self,
        *,
        title: str,
        message: str,
        hotkey_hint: str | None,
        step_number: int,
        total_steps: int,
    ) -> None:
        """Update the card content."""
        self._title_label.setText(title)
        self._message_label.setText(message)
        self._progress_label.setText(f"Step {step_number} of {total_steps}")

        if hotkey_hint:
            self._hotkey_label.setText(hotkey_hint)
            self._hotkey_label.show()
        else:
            self._hotkey_label.hide()

        # Update button states
        self._prev_button.setEnabled(step_number > 1)
        if step_number == total_steps:
            self._next_button.setText("Finish")
        else:
            self._next_button.setText("Next →")


class TutorialArrow(QWidget):
    """Arrow pointing from tutorial card to target widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._start = QPoint(0, 0)
        self._end = QPoint(0, 0)

    def set_points(self, start: QPoint, end: QPoint) -> None:
        """Set arrow start and end points."""
        self._start = start
        self._end = end
        self.update()

    def paintEvent(self, event: object) -> None:
        """Draw arrow from start to end."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        start = self._start
        end = self._end

        if start == end:
            return

        # Draw line
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(120, 180, 255, 255))
        painter.setPen(pen)
        painter.drawLine(start, end)

        # Draw arrowhead
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.hypot(dx, dy)

        if length <= 0.0:
            return

        # Unit vectors
        ux = dx / length
        uy = dy / length
        px = -uy
        py = ux

        # Arrowhead dimensions
        head_len = 14.0
        head_w = 8.0
        tip = end
        base_x = end.x() - int(round(ux * head_len))
        base_y = end.y() - int(round(uy * head_len))
        left = QPoint(
            base_x + int(round(px * head_w)),
            base_y + int(round(py * head_w)),
        )
        right = QPoint(
            base_x - int(round(px * head_w)),
            base_y - int(round(py * head_w)),
        )

        painter.setBrush(QColor(120, 180, 255, 255))
        painter.drawPolygon(QPolygon([tip, left, right]))


class TutorialOverlay(QWidget):
    """Full-screen overlay for tutorial steps with spotlight effect."""

    finished = Signal(bool)  # True if completed, False if skipped

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("tutorialOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Tutorial state
        self._steps: list[TutorialStep] = []
        self._current_step_index = 0
        self._spotlight_rect: QRect | None = None

        # Create tutorial card
        self._card = TutorialCard(self)
        self._card.next_requested.connect(self._on_next)
        self._card.previous_requested.connect(self._on_previous)
        self._card.skip_requested.connect(self._on_skip)

        # Create arrow
        self._arrow = TutorialArrow(self)
        self._arrow.hide()

        # Opacity animation
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0.0)

        self.hide()

    def start_tutorial(self, steps: list[TutorialStep]) -> None:
        """Begin tutorial sequence."""
        if not steps:
            return

        self._steps = steps
        self._current_step_index = 0

        # Show overlay
        self.show()
        self.raise_()

        # Fade in animation
        fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.start()

        # Show first step
        self._show_current_step()

    def _show_current_step(self) -> None:
        """Display the current tutorial step."""
        if not self._steps or self._current_step_index >= len(self._steps):
            return

        step = self._steps[self._current_step_index]

        # Switch to target screen if needed
        self._switch_to_screen(step.target_screen)

        # Find target widget for spotlight
        target_widget = None
        if step.target_widget_name:
            target_widget = self._find_widget(step.target_widget_name)

        # Update spotlight
        if target_widget and target_widget.isVisible():
            # Get target geometry in overlay coordinates
            global_rect = target_widget.rect()
            global_rect.moveTopLeft(target_widget.mapToGlobal(QPoint(0, 0)))
            self._spotlight_rect = QRect(
                self.mapFromGlobal(global_rect.topLeft()),
                global_rect.size(),
            )
            # Add padding to spotlight
            self._spotlight_rect.adjust(-12, -12, 12, 12)
        else:
            self._spotlight_rect = None

        # Update card content
        self._card.set_content(
            title=step.title,
            message=step.message,
            hotkey_hint=step.hotkey_hint,
            step_number=self._current_step_index + 1,
            total_steps=len(self._steps),
        )

        # Position card
        self._position_card(step.card_position, target_widget)

        # Update arrow
        if target_widget and target_widget.isVisible() and self._spotlight_rect:
            self._update_arrow(step.card_position)
            self._arrow.show()
        else:
            self._arrow.hide()

        # Trigger repaint for spotlight
        self.update()

    def _position_card(self, position: TutorialPosition, target_widget: QWidget | None) -> None:
        """Position the tutorial card based on the requested position."""
        from endless_idler.ui.tutorial_content import TutorialPosition

        card_width = self._card.width()
        card_height = self._card.height()
        overlay_width = self.width()
        overlay_height = self.height()

        if position == TutorialPosition.CENTER or not target_widget or not target_widget.isVisible():
            # Center on screen
            x = (overlay_width - card_width) // 2
            y = (overlay_height - card_height) // 2
        elif position == TutorialPosition.RIGHT:
            # Position to the right of target
            if self._spotlight_rect:
                x = self._spotlight_rect.right() + 40
                y = self._spotlight_rect.center().y() - card_height // 2
                # Keep on screen
                if x + card_width > overlay_width - 20:
                    x = self._spotlight_rect.left() - card_width - 40
            else:
                x = (overlay_width - card_width) // 2
                y = (overlay_height - card_height) // 2
        elif position == TutorialPosition.LEFT:
            # Position to the left of target
            if self._spotlight_rect:
                x = self._spotlight_rect.left() - card_width - 40
                y = self._spotlight_rect.center().y() - card_height // 2
                # Keep on screen
                if x < 20:
                    x = self._spotlight_rect.right() + 40
            else:
                x = (overlay_width - card_width) // 2
                y = (overlay_height - card_height) // 2
        elif position == TutorialPosition.BOTTOM:
            # Position below target
            if self._spotlight_rect:
                x = self._spotlight_rect.center().x() - card_width // 2
                y = self._spotlight_rect.bottom() + 40
                # Keep on screen
                if y + card_height > overlay_height - 20:
                    y = self._spotlight_rect.top() - card_height - 40
            else:
                x = (overlay_width - card_width) // 2
                y = (overlay_height - card_height) // 2
        elif position == TutorialPosition.TOP:
            # Position above target
            if self._spotlight_rect:
                x = self._spotlight_rect.center().x() - card_width // 2
                y = self._spotlight_rect.top() - card_height - 40
                # Keep on screen
                if y < 20:
                    y = self._spotlight_rect.bottom() + 40
            else:
                x = (overlay_width - card_width) // 2
                y = (overlay_height - card_height) // 2
        else:
            x = (overlay_width - card_width) // 2
            y = (overlay_height - card_height) // 2

        # Clamp to screen bounds
        x = max(20, min(x, overlay_width - card_width - 20))
        y = max(20, min(y, overlay_height - card_height - 20))

        self._card.move(x, y)

    def _update_arrow(self, position: TutorialPosition) -> None:
        """Update arrow to point from card to spotlight."""
        from endless_idler.ui.tutorial_content import TutorialPosition

        if not self._spotlight_rect:
            self._arrow.hide()
            return

        card_rect = self._card.geometry()
        card_center = card_rect.center()
        spotlight_center = self._spotlight_rect.center()

        # Determine arrow start point (edge of card closest to target)
        if position == TutorialPosition.RIGHT:
            start = QPoint(card_rect.left(), card_center.y())
        elif position == TutorialPosition.LEFT:
            start = QPoint(card_rect.right(), card_center.y())
        elif position == TutorialPosition.BOTTOM:
            start = QPoint(card_center.x(), card_rect.top())
        elif position == TutorialPosition.TOP:
            start = QPoint(card_center.x(), card_rect.bottom())
        else:
            # Center position, no arrow
            self._arrow.hide()
            return

        # Arrow end point (edge of spotlight closest to card)
        end = spotlight_center

        self._arrow.set_points(start, end)
        self._arrow.show()

    def _switch_to_screen(self, screen_name: str | None) -> None:
        """Switch to the specified screen."""
        if not screen_name:
            return

        # Find the parent MainMenuWindow
        parent_window = self.parent()
        if not parent_window:
            return

        # Access the stacked widget (this is a bit hacky, but works)
        # The MainMenuWindow has a _stack attribute we can use
        if hasattr(parent_window, "_stack"):
            stack = parent_window._stack
            if screen_name == "main_menu" and hasattr(parent_window, "_main_menu_widget"):
                stack.setCurrentWidget(parent_window._main_menu_widget)
            elif screen_name == "party_builder" and hasattr(parent_window, "_party_builder"):
                stack.setCurrentWidget(parent_window._party_builder)
            elif screen_name == "skills" and hasattr(parent_window, "_skills_screen"):
                stack.setCurrentWidget(parent_window._skills_screen)

    def _find_widget(self, object_name: str) -> QWidget | None:
        """Find a widget by its object name."""
        parent_window = self.parent()
        if not parent_window:
            return None

        # Search recursively for widget with matching object name
        return parent_window.findChild(QWidget, object_name)

    def _on_next(self) -> None:
        """Handle next button click."""
        if self._current_step_index < len(self._steps) - 1:
            self._current_step_index += 1
            self._show_current_step()
        else:
            # Tutorial complete
            self._complete_tutorial()

    def _on_previous(self) -> None:
        """Handle previous button click."""
        if self._current_step_index > 0:
            self._current_step_index -= 1
            self._show_current_step()

    def _on_skip(self) -> None:
        """Handle skip button click."""
        self.finished.emit(False)
        self._fade_out()

    def _complete_tutorial(self) -> None:
        """Handle tutorial completion."""
        self.finished.emit(True)
        self._fade_out()

    def _fade_out(self) -> None:
        """Fade out and hide the overlay."""
        fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.finished.connect(self.hide)
        fade_out.start()

    def paintEvent(self, event: object) -> None:
        """Draw dark overlay with spotlight cutout."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Fill entire widget with semi-transparent dark
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

        # Cut out spotlight region (clear area over target widget)
        if self._spotlight_rect:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            # Draw rounded rect for spotlight
            path = QPainterPath()
            path.addRoundedRect(
                self._spotlight_rect.x(),
                self._spotlight_rect.y(),
                self._spotlight_rect.width(),
                self._spotlight_rect.height(),
                8,
                8,
            )
            painter.fillPath(path, QColor(0, 0, 0, 0))

    def resizeEvent(self, event: object) -> None:
        """Handle window resize."""
        super().resizeEvent(event)
        # Reposition card and arrow when overlay resizes
        if self._steps and self._current_step_index < len(self._steps):
            self._show_current_step()
