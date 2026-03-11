from __future__ import annotations

import time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.ui.components.progress_bar import AnimatedProgressBar
from endless_idler.ui.theme.shard_progress_bar_widget import (
    FIRE_RGBA,
    ICE_RGBA,
    LIGHTNING_RGBA,
    WIND_RGBA,
    DARK_RGBA,
    LIGHT_RGBA,
    GENERIC_CYCLE_COLORS,
)


# Element ID to color mapping
ELEMENT_COLORS: dict[str, tuple[int, int, int, int]] = {
    "fire": FIRE_RGBA,
    "ice": ICE_RGBA,
    "lightning": LIGHTNING_RGBA,
    "wind": WIND_RGBA,
    "dark": DARK_RGBA,
    "light": LIGHT_RGBA,
}

# Cycle duration in milliseconds for generic type color rotation
GENERIC_CYCLE_DURATION_MS = 3000


class ShardProgressBar(QWidget):
    """Progress bar widget showing shard progression toward 100-tick cycle.

    Displays:
    - Visual progress bar with element-themed colors
    - Current tick count (e.g., "67/100")
    - For generic damage types: cycles through all 6 element colors
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("shardProgressBarWidget")

        # State
        self._shard_bar_ticks = 0
        self._element_id = "generic"
        self._shard_types: tuple[str, ...] = ()
        self._cycle_index = 0
        self._cycle_start_time = 0.0

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Progress bar with text overlay
        self._progress_bar = AnimatedProgressBar()
        self._progress_bar.setFixedHeight(14)
        self._progress_bar._gradient_enabled = False
        self._progress_bar.setText("SHARD 0/100")
        layout.addWidget(self._progress_bar, 1)

        # Cycle timer for generic types
        self._cycle_timer = QTimer(self)
        self._cycle_timer.setInterval(33)  # ~30Hz update cadence for smooth transitions
        self._cycle_timer.timeout.connect(self._update_cycle_color)

        self._update_appearance()

    def set_shard_data(
        self,
        *,
        shard_bar_ticks: int,
        element_id: str,
        shard_types: tuple[str, ...],
    ) -> None:
        """Update the shard progress bar with new data.

        Args:
            shard_bar_ticks: Current tick count (0-100)
            element_id: Character's element ID (fire, ice, wind, lightning, light, dark, generic)
            shard_types: Tuple of shard reward types this character can earn
        """
        old_element = self._element_id
        self._shard_bar_ticks = max(0, min(100, int(shard_bar_ticks)))
        self._element_id = str(element_id or "generic").strip().lower()
        self._shard_types = tuple(str(t) for t in shard_types if t)

        # Update progress
        progress = self._shard_bar_ticks / 100.0
        self._progress_bar.set_value(progress)
        self._progress_bar.setText(f"SHARD {self._shard_bar_ticks}/100")

        # Handle element/color changes
        if self._element_id != old_element:
            self._update_appearance()

        # Manage cycle timer for generic types
        is_generic = self._is_generic_type()
        if is_generic and not self._cycle_timer.isActive():
            self._cycle_start_time = time.time()
            self._cycle_timer.start()
        elif not is_generic and self._cycle_timer.isActive():
            self._cycle_timer.stop()

    def _is_generic_type(self) -> bool:
        """Check if this character has generic/multiple element types."""
        if not self._shard_types:
            return False
        # Generic if we have all 6 element types
        element_count = sum(1 for t in self._shard_types if t in ELEMENT_COLORS)
        return element_count >= 6

    def _update_appearance(self) -> None:
        """Update widget appearance based on element type."""
        # Set element property for theme selector
        if self.property("elementId") != self._element_id:
            self.setProperty("elementId", self._element_id)
            style = self.style()
            if style is not None:
                style.unpolish(self)
                style.polish(self)
            self.update()

        # Set color based on element
        self._update_element_color()

    def _update_element_color(self) -> None:
        """Set progress bar color based on element type."""
        if self._is_generic_type():
            # Generic: start cycling colors
            self._update_cycle_color()
        else:
            # Specific element: use its color
            color = ELEMENT_COLORS.get(self._element_id, LIGHT_RGBA)
            self._progress_bar.set_color_thresholds(
                [
                    (0.0, color),
                    (0.5, color),
                    (1.0, color),
                ]
            )

    def _update_cycle_color(self) -> None:
        """Update color for generic type cycling effect."""
        if not self._is_generic_type():
            return

        elapsed_ms = (time.time() - self._cycle_start_time) * 1000
        cycle_progress = (
            elapsed_ms % GENERIC_CYCLE_DURATION_MS
        ) / GENERIC_CYCLE_DURATION_MS

        # Determine which two colors to blend between
        color_count = len(GENERIC_CYCLE_COLORS)
        raw_index = cycle_progress * color_count
        index = int(raw_index) % color_count
        next_index = (index + 1) % color_count
        blend_factor = raw_index - int(raw_index)

        # Blend between current and next color
        color1 = GENERIC_CYCLE_COLORS[index]
        color2 = GENERIC_CYCLE_COLORS[next_index]
        blended = self._blend_rgba(color1, color2, blend_factor)

        self._progress_bar.set_color_thresholds(
            [
                (0.0, blended),
                (0.5, blended),
                (1.0, blended),
            ]
        )

    def _blend_rgba(
        self,
        left: tuple[int, int, int, int],
        right: tuple[int, int, int, int],
        factor: float,
    ) -> tuple[int, int, int, int]:
        """Blend between two RGBA colors."""
        t = max(0.0, min(1.0, float(factor)))
        return (
            int(round(left[0] + ((right[0] - left[0]) * t))),
            int(round(left[1] + ((right[1] - left[1]) * t))),
            int(round(left[2] + ((right[2] - left[2]) * t))),
            int(round(left[3] + ((right[3] - left[3]) * t))),
        )

    def get_tick_count(self) -> int:
        """Return current tick count."""
        return self._shard_bar_ticks

    def get_element_id(self) -> str:
        """Return current element ID."""
        return self._element_id

    def get_shard_types(self) -> tuple[str, ...]:
        """Return current shard reward types."""
        return self._shard_types
