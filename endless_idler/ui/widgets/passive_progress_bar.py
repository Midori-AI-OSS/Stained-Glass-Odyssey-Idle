from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.ui.components.progress_bar import AnimatedProgressBar
from endless_idler.ui.theme.colors import normalize_element_id
from endless_idler.ui.theme.passive_progress_bar_widget import ELEMENT_COLORS
from endless_idler.ui.theme.passive_progress_bar_widget import TRINITY_DARK_RGBA
from endless_idler.ui.theme.passive_progress_bar_widget import TRINITY_LIGHT_RGBA


def _blend_rgba(
    left: tuple[int, int, int, int],
    right: tuple[int, int, int, int],
    factor: float,
) -> tuple[int, int, int, int]:
    t = max(0.0, min(1.0, float(factor)))
    return (
        int(round(left[0] + ((right[0] - left[0]) * t))),
        int(round(left[1] + ((right[1] - left[1]) * t))),
        int(round(left[2] + ((right[2] - left[2]) * t))),
        int(round(left[3] + ((right[3] - left[3]) * t))),
    )


class PassiveProgressBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("passiveProgressBarWidget")
        self._style_id = "default"
        self._element_id = "generic"
        self._dual_element_ids = ""

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self._progress_bar = AnimatedProgressBar()
        self._progress_bar.setFixedHeight(14)
        self._progress_bar._gradient_enabled = False
        self._progress_bar.setText("PASSIVE 0%")
        layout.addWidget(self._progress_bar, 1)

        self._apply_theme_properties()
        self._apply_element_appearance()

    def format(self) -> str:
        return self._progress_bar.format()

    def set_passive_data(
        self,
        *,
        label: str,
        progress: float,
        display_percent: float,
        shimmer: float,
        style_id: str,
        element_id: str,
        dual_element_ids: Sequence[str] = (),
    ) -> None:
        self._style_id = str(style_id or "default").strip().lower() or "default"
        self._element_id = normalize_element_id(element_id or "generic")
        self._dual_element_ids = ",".join(
            normalize_element_id(item)
            for item in dual_element_ids
            if str(item or "").strip()
        )
        self._apply_theme_properties()

        self._progress_bar.set_value(max(0.0, min(1.0, float(progress))))
        self._progress_bar.setText(
            f"{str(label or 'PASSIVE').strip().upper()} "
            + f"{max(0, int(round(float(display_percent))))}%"
        )
        self._progress_bar.set_shimmer(max(0.0, min(1.0, float(shimmer))))

        if self._style_id == "trinity":
            self._apply_trinity_appearance()
            return
        self._apply_element_appearance()

    def _apply_theme_properties(self) -> None:
        if self.property("styleId") != self._style_id:
            self.setProperty("styleId", self._style_id)
        if self.property("elementId") != self._element_id:
            self.setProperty("elementId", self._element_id)
        if self.property("dualElementIds") != self._dual_element_ids:
            self.setProperty("dualElementIds", self._dual_element_ids)
        style = self.style()
        if style is not None:
            style.unpolish(self)
            style.polish(self)
        self.update()

    def _apply_trinity_appearance(self) -> None:
        self._progress_bar._gradient_enabled = True
        self._progress_bar.set_color_thresholds([])
        self._progress_bar.set_base_color(TRINITY_DARK_RGBA)
        self._progress_bar.set_gradient_colors(
            start_color=TRINITY_DARK_RGBA,
            mid_color=_blend_rgba(TRINITY_DARK_RGBA, TRINITY_LIGHT_RGBA, 0.5),
            end_color=TRINITY_LIGHT_RGBA,
        )

    def _apply_element_appearance(self) -> None:
        color = ELEMENT_COLORS.get(self._element_id, ELEMENT_COLORS["generic"])
        self._progress_bar._gradient_enabled = False
        self._progress_bar.set_base_color(color)
        self._progress_bar.set_color_thresholds(
            [
                (0.0, color),
                (0.5, color),
                (1.0, color),
            ]
        )
