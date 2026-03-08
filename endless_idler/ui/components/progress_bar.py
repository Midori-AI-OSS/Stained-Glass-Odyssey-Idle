from __future__ import annotations

import math
import time

from PySide6.QtCore import QRect
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from PySide6.QtGui import QLinearGradient
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QWidget

from endless_idler.ui.theme.progress_bar import DEFAULT_BASE_RGBA
from endless_idler.ui.theme.progress_bar import DEFAULT_SHIMMER_RGBA
from endless_idler.ui.theme.progress_bar import DEFAULT_AURORA_MID_RGBA
from endless_idler.ui.theme.progress_bar import DEFAULT_AURORA_END_RGBA
from endless_idler.ui.theme.progress_bar import DEFAULT_TRACK_FILL_RGBA
from endless_idler.ui.theme.progress_bar import DEFAULT_AURORA_START_RGBA
from endless_idler.ui.theme.progress_bar import DEFAULT_TRACK_BORDER_RGBA


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _blend_rgba(
    left: tuple[int, int, int, int], right: tuple[int, int, int, int], factor: float
) -> tuple[int, int, int, int]:
    t = _clamp01(factor)
    return (
        int(round(left[0] + ((right[0] - left[0]) * t))),
        int(round(left[1] + ((right[1] - left[1]) * t))),
        int(round(left[2] + ((right[2] - left[2]) * t))),
        int(round(left[3] + ((right[3] - left[3]) * t))),
    )


def _blend_factor_for_progress(progress: float) -> float:
    phase = _clamp01(progress)
    if phase <= 0.50:
        return 0.0
    if phase >= 0.65:
        return 1.0
    return (phase - 0.50) / 0.15


class AnimatedProgressBar(QWidget):
    """Reusable progress bar with smooth animations and visual effects.

    Requires theme/progress_bar.py tokens for visual consistency.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("animatedProgressBar")

        # Configuration
        self._target_progress = 0.0
        self._target_shimmer = 0.0
        self._display_progress = 0.0
        self._display_shimmer = 0.0
        self._reset_active = False
        self._shimmer_phase = 0.0
        self._last_frame_at = 0.0

        # Color transition configuration
        self._color_thresholds: list[tuple[float, tuple[int, int, int, int]]] = []
        self._gradient_enabled = True

        # Animation parameters
        self._smoothing_rate = 22.0
        self._shimmer_speed = 0.20
        self._shimmer_amplifier = 0.48

        # Timer for 60 FPS animation
        self._frame_timer = QTimer(self)
        self._frame_timer.setInterval(16)
        self._frame_timer.timeout.connect(self._on_animation_frame)

    def set_value(self, progress: float) -> None:
        """Set the progress value with smooth animation.

        Args:
            progress: Progress value from 0.0 to 1.0
        """
        self._target_progress = _clamp01(progress)
        if not self._should_animate():
            self._display_progress = self._target_progress
            if self._frame_timer.isActive():
                self._frame_timer.stop()
        elif not self._frame_timer.isActive():
            self._last_frame_at = time.perf_counter()
            self._frame_timer.start()
        self.update()

    def set_shimmer(self, intensity: float) -> None:
        """Set the shimmer effect intensity.

        Args:
            intensity: Shimmer intensity from 0.0 (off) to 1.0 (max)
        """
        self._target_shimmer = _clamp01(intensity)
        if not self._should_animate():
            self._display_shimmer = self._target_shimmer
            if self._frame_timer.isActive():
                self._frame_timer.stop()
        elif not self._frame_timer.isActive():
            self._last_frame_at = time.perf_counter()
            self._frame_timer.start()
        self.update()

    def set_reset_mode(self, active: bool) -> None:
        """Set reset mode which slows animation for visual feedback.

        Args:
            active: True to enable reset mode, False to disable
        """
        self._reset_active = bool(active)
        self.update()

    def set_color_thresholds(
        self, thresholds: list[tuple[float, tuple[int, int, int, int]]]
    ) -> None:
        """Set color thresholds for progress-based color changes.

        Args:
            thresholds: List of (progress_value, rgba_color) tuples
                       Progress value is 0.0-1.0, color is (r,g,b,a)
        """
        self._color_thresholds = sorted(thresholds, key=lambda x: x[0])
        self.update()

    def set_gradient_colors(
        self,
        start_color: tuple[int, int, int, int],
        mid_color: tuple[int, int, int, int],
        end_color: tuple[int, int, int, int],
    ) -> None:
        """Set the gradient colors for the aurora effect.

        Args:
            start_color: RGBA tuple for gradient start
            mid_color: RGBA tuple for gradient middle
            end_color: RGBA tuple for gradient end
        """
        self._start_color = start_color
        self._mid_color = mid_color
        self._end_color = end_color
        self.update()

    def _should_animate(self) -> bool:
        """Check if animation should be running."""
        if self._reset_active:
            return True
        if self._target_shimmer > 0.001 or self._display_shimmer > 0.001:
            return True
        if abs(self._target_progress - self._display_progress) > 0.001:
            return True
        if abs(self._target_shimmer - self._display_shimmer) > 0.001:
            return True
        return False

    def _approach(
        self, *, current: float, target: float, rate: float, dt: float
    ) -> float:
        """Exponential smoothing for natural animation."""
        if dt <= 0.0:
            return current
        blend = 1.0 - math.exp(-max(0.0, rate) * dt)
        return current + ((target - current) * blend)

    def _on_animation_frame(self) -> None:
        """Handle animation frame updates."""
        now = time.perf_counter()
        if self._last_frame_at <= 0.0:
            dt = 1.0 / 60.0
        else:
            dt = max(0.001, min(0.1, now - self._last_frame_at))
        self._last_frame_at = now

        self._display_progress = _clamp01(
            self._approach(
                current=self._display_progress,
                target=self._target_progress,
                rate=self._smoothing_rate,
                dt=dt,
            )
        )
        self._display_shimmer = _clamp01(
            self._approach(
                current=self._display_shimmer,
                target=self._target_shimmer,
                rate=16.0,
                dt=dt,
            )
        )

        phase_speed = self._shimmer_speed + (
            self._shimmer_amplifier * self._display_shimmer
        )
        if self._reset_active:
            phase_speed *= 0.72
        self._shimmer_phase = (self._shimmer_phase + (phase_speed * dt)) % 1.0

        if not self._should_animate():
            self._display_progress = self._target_progress
            self._display_shimmer = self._target_shimmer
            self._frame_timer.stop()

        self.update()

    def paintEvent(self, event) -> None:  # noqa: ANN001
        """Render the progress bar with all visual effects."""
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        track = self.rect().adjusted(0, 0, -1, -1)
        if track.width() <= 2 or track.height() <= 2:
            painter.end()
            return

        # Draw track
        painter.setPen(QPen(QColor(*DEFAULT_TRACK_BORDER_RGBA), 1.0))
        painter.setBrush(QColor(*DEFAULT_TRACK_FILL_RGBA))
        painter.drawRect(track)

        inner = track.adjusted(1, 1, -1, -1)
        fill_width = int(round(max(0.0, float(inner.width()) * self._display_progress)))
        if fill_width > 0:
            fill_rect = QRect(
                inner.left(), inner.top(), fill_width, max(1, inner.height())
            )

            # Determine fill color based on thresholds or gradient
            fill_color = QColor(*DEFAULT_BASE_RGBA)  # Default blue

            # Check color thresholds first
            if self._color_thresholds:
                # Find the color for current progress
                color = None
                for threshold, rgba in reversed(self._color_thresholds):
                    if self._display_progress >= threshold:
                        color = rgba
                        break
                if color:
                    fill_color = QColor(*color)

            # Use gradient if enabled and no threshold color
            elif self._gradient_enabled:
                aurora_mix = _blend_factor_for_progress(self._display_progress)
                start_rgba = _blend_rgba(
                    DEFAULT_BASE_RGBA, DEFAULT_AURORA_START_RGBA, aurora_mix
                )
                mid_rgba = _blend_rgba(
                    DEFAULT_BASE_RGBA, DEFAULT_AURORA_MID_RGBA, aurora_mix
                )
                end_rgba = _blend_rgba(
                    DEFAULT_BASE_RGBA, DEFAULT_AURORA_END_RGBA, aurora_mix
                )

                fill_gradient = QLinearGradient(
                    fill_rect.left(),
                    fill_rect.top(),
                    fill_rect.right(),
                    fill_rect.top(),
                )
                fill_gradient.setColorAt(0.0, QColor(*start_rgba))
                fill_gradient.setColorAt(0.5, QColor(*mid_rgba))
                fill_gradient.setColorAt(1.0, QColor(*end_rgba))
                painter.setPen(QPen(QColor(255, 255, 255, 22), 1.0))
                painter.setBrush(fill_gradient)
            else:
                painter.setPen(QPen(QColor(255, 255, 255, 22), 1.0))
                painter.setBrush(fill_color)

            painter.drawRect(fill_rect)

            # Draw shimmer effect
            if self._display_shimmer > 0.0:
                center_x = int(
                    round(
                        fill_rect.left()
                        + (float(fill_rect.width()) * self._shimmer_phase)
                    )
                )
                half_width = max(8, int(round(float(fill_rect.width()) * 0.14)))
                shimmer_rect = QRect(
                    center_x - half_width,
                    fill_rect.top(),
                    half_width * 2,
                    fill_rect.height(),
                )
                shimmer_alpha = int(
                    max(
                        0.0, min(255.0, DEFAULT_SHIMMER_RGBA[3] * self._display_shimmer)
                    )
                )
                shimmer_gradient = QLinearGradient(
                    shimmer_rect.left(),
                    shimmer_rect.top(),
                    shimmer_rect.right(),
                    shimmer_rect.top(),
                )
                shimmer_gradient.setColorAt(0.0, QColor(*DEFAULT_SHIMMER_RGBA[:3], 0))
                shimmer_gradient.setColorAt(
                    0.5, QColor(*DEFAULT_SHIMMER_RGBA[:3], shimmer_alpha)
                )
                shimmer_gradient.setColorAt(1.0, QColor(*DEFAULT_SHIMMER_RGBA[:3], 0))
                painter.setPen(QPen(QColor(255, 255, 255, 0), 0.0))
                painter.setBrush(shimmer_gradient)
                painter.save()
                painter.setClipRect(fill_rect)
                painter.drawRect(shimmer_rect)
                painter.restore()

        painter.end()
