"""Shape-based foe rendering widget with health fill visualization.

This module provides the ShapeFoeWidget class for rendering foes as geometric
shapes with color-coded damage types and health-based fill animations.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent
from PySide6.QtCore import QPointF
from PySide6.QtCore import QRectF
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColor
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPainterPath
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.foe_shape_selector import select_shape_for_foe
from endless_idler.ui.battle.colors import color_for_damage_type_id
from endless_idler.ui.battle.shape_palette import get_shape_template
from endless_idler.ui.battle.sim import Combatant


class ShapeRenderer(QWidget):
    """Widget that renders a shape with health-based fill."""

    def __init__(
        self,
        *,
        shape_id: str,
        fill_color: QColor,
        current_hp: int,
        max_hp: int,
        size: int = 60,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._shape_id = shape_id
        self._fill_color = fill_color
        self._current_hp = current_hp
        self._max_hp = max_hp
        self._size = size
        
        self.setFixedSize(size, size)

    def set_health(self, current_hp: int, max_hp: int) -> None:
        """Update health values and trigger repaint."""
        self._current_hp = current_hp
        self._max_hp = max_hp
        self.update()

    def paintEvent(self, event: object) -> None:
        """Render the shape with health-based fill."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        try:
            # Get shape template
            template = get_shape_template(self._shape_id)
            
            # Calculate health ratio
            health_ratio = self._current_hp / max(1, self._max_hp)
            health_ratio = max(0.0, min(1.0, health_ratio))
            
            # Create the full shape path
            scale_x = self._size / template.base_width
            scale_y = self._size / template.base_height
            full_path = template.geometry_fn(template.base_width, template.base_height)
            
            # Transform to fit widget size
            from PySide6.QtGui import QTransform
            transform = QTransform()
            transform.scale(scale_x, scale_y)
            full_path = transform.map(full_path)
            
            # Get bounding box for clipping
            bounds = full_path.boundingRect()
            
            # Create clipping path based on fill direction
            fill_direction = template.fill_direction
            clip_path = QPainterPath()
            
            if fill_direction == "bottom_up":
                # Fill from bottom to top
                fill_height = bounds.height() * health_ratio
                clip_rect = QRectF(
                    bounds.left(),
                    bounds.bottom() - fill_height,
                    bounds.width(),
                    fill_height,
                )
                clip_path.addRect(clip_rect)
            
            elif fill_direction == "left_right":
                # Fill from left to right
                fill_width = bounds.width() * health_ratio
                clip_rect = QRectF(
                    bounds.left(),
                    bounds.top(),
                    fill_width,
                    bounds.height(),
                )
                clip_path.addRect(clip_rect)
            
            elif fill_direction == "center_out":
                # Fill from center outward
                # Use scaling from center to simulate "center_out"
                center = bounds.center()
                transform = QTransform()
                transform.translate(center.x(), center.y())
                transform.scale(health_ratio, health_ratio)
                transform.translate(-center.x(), -center.y())
                clip_path = transform.map(full_path)
            
            else:
                # Default to bottom_up
                fill_height = bounds.height() * health_ratio
                clip_rect = QRectF(
                    bounds.left(),
                    bounds.bottom() - fill_height,
                    bounds.width(),
                    fill_height,
                )
                clip_path.addRect(clip_rect)
            
            # Draw the filled portion
            filled_path = full_path.intersected(clip_path)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(self._fill_color))
            painter.drawPath(filled_path)
            
            # Draw the outline
            outline_color = QColor(self._fill_color)
            outline_color = outline_color.darker(150)
            painter.setPen(QPen(outline_color, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(full_path)
            
        finally:
            painter.end()

    def pulse_anchor_global(self) -> QPointF:
        """Get the anchor point for combat animations."""
        rect = self.rect()
        center = rect.center()
        return QPointF(self.mapToGlobal(center))


class ShapeFoeWidget(QFrame):
    """Widget for rendering foes as shapes with health fill.
    
    Replaces the old CombatantCard for foe rendering.
    """

    def __init__(
        self,
        *,
        combatant: Combatant,
        team_side: str = "right",
        size: int = 60,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._combatant = combatant
        self._team_side = (team_side or "right").strip().lower()
        self._size = size

        self.setObjectName("shapeFoeWidget")
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        self.setLayout(layout)
        
        # Select shape based on foe stats
        shape_id = select_shape_for_foe(self._combatant.stats)
        
        # Get damage type color
        element_id = getattr(self._combatant.stats, "element_id", "generic")
        fill_color = color_for_damage_type_id(element_id)
        
        # Create shape renderer
        self._shape_renderer = ShapeRenderer(
            shape_id=shape_id,
            fill_color=fill_color,
            current_hp=int(self._combatant.stats.hp),
            max_hp=int(self._combatant.max_hp),
            size=size,
        )
        layout.addWidget(self._shape_renderer, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Create name label
        self._name_label = QLabel(self._combatant.name)
        self._name_label.setObjectName("shapeFoeName")
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_label.setWordWrap(True)
        self._name_label.setMaximumWidth(size + 20)
        layout.addWidget(self._name_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Apply subtle background tint
        self._apply_element_tint()
        
        # Install event filter for tooltips
        self._shape_renderer.installEventFilter(self)
        self._name_label.installEventFilter(self)

    def _apply_element_tint(self) -> None:
        """Apply a subtle background tint based on damage type."""
        element_id = getattr(self._combatant.stats, "element_id", "generic")
        color = color_for_damage_type_id(element_id)
        
        tint_color = f"rgba({color.red()}, {color.green()}, {color.blue()}, 10)"
        self.setStyleSheet(f"#shapeFoeWidget {{ background-color: {tint_color}; border-radius: 4px; }}")

    @property
    def combatant(self) -> Combatant:
        """Get the combatant this widget represents."""
        return self._combatant

    def refresh(self) -> None:
        """Refresh the widget to reflect current health."""
        current_hp = int(self._combatant.stats.hp)
        max_hp = int(self._combatant.max_hp)
        self._shape_renderer.set_health(current_hp, max_hp)
        self.update()

    def pulse_anchor_global(self) -> QPointF:
        """Get the anchor point for combat animations."""
        return self._shape_renderer.pulse_anchor_global()

    def eventFilter(self, watched: object, event: object) -> bool:
        """Handle events for tooltip display."""
        if hasattr(event, "type") and event.type() == QEvent.Type.Enter:
            # Show basic tooltip with foe name and health
            tooltip = f"<b>{self._combatant.name}</b><br>"
            tooltip += f"HP: {int(self._combatant.stats.hp)} / {int(self._combatant.max_hp)}<br>"
            element_id = getattr(self._combatant.stats, "element_id", "generic")
            tooltip += f"Type: {element_id.capitalize()}"
            self.setToolTip(tooltip)
        return super().eventFilter(watched, event)  # type: ignore[misc]
