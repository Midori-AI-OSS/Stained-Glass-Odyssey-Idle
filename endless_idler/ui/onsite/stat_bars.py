from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.combat.stats import Stats


@dataclass(frozen=True, slots=True)
class StatBarSpec:
    key: str
    label: str


STAT_BARS: tuple[StatBarSpec, ...] = (
    StatBarSpec(key="atk", label="Attack"),
    StatBarSpec(key="defense", label="Defense"),
    StatBarSpec(key="spd", label="Speed"),
    StatBarSpec(key="crit_rate", label="Crit Rate"),
    StatBarSpec(key="dodge_odds", label="Dodge"),
    StatBarSpec(key="regain", label="Regain"),
    StatBarSpec(key="mitigation", label="Mitigation"),
)


def compute_stat_maxima(stats_list: list[Stats]) -> dict[str, float]:
    maxima: dict[str, float] = {spec.key: 0.0 for spec in STAT_BARS}
    for stats in stats_list:
        maxima["atk"] = max(maxima["atk"], float(stats.atk))
        maxima["defense"] = max(maxima["defense"], float(stats.defense))
        maxima["spd"] = max(maxima["spd"], float(stats.spd))
        maxima["crit_rate"] = max(maxima["crit_rate"], float(stats.crit_rate))
        maxima["dodge_odds"] = max(maxima["dodge_odds"], float(stats.dodge_odds))
        maxima["regain"] = max(maxima["regain"], float(stats.regain))
        maxima["mitigation"] = max(maxima["mitigation"], float(stats.mitigation))

    for key, value in list(maxima.items()):
        if value <= 0:
            maxima[key] = 1.0
    return maxima


class StatBarsPanel(QFrame):
    def __init__(
        self,
        *,
        stats: Stats,
        maxima: dict[str, float],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._stats = stats
        self._maxima = dict(maxima)
        self._bars: dict[str, QProgressBar] = {}

        self.setObjectName("onsiteStatBars")
        self.setFrameShape(QFrame.Shape.NoFrame)

        root = QVBoxLayout()
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)
        self.setLayout(root)

        for spec in STAT_BARS:
            row = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)
            row.setLayout(row_layout)

            label = QLabel(spec.label)
            label.setObjectName("onsiteStatLabel")
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            label.setFixedWidth(82)
            row_layout.addWidget(label, 0)

            bar = QProgressBar()
            bar.setObjectName("onsiteStatBar")
            bar.setProperty("statKey", spec.key)
            bar.setRange(0, 100)
            bar.setTextVisible(False)
            bar.setFixedWidth(150)
            bar.setFixedHeight(10)
            row_layout.addWidget(bar, 1)

            self._bars[spec.key] = bar
            root.addWidget(row)

        self.refresh()

    def set_stats(self, stats: Stats) -> None:
        self._stats = stats
        self.refresh()

    def set_maxima(self, maxima: dict[str, float]) -> None:
        self._maxima = dict(maxima)
        self.refresh()

    def refresh(self) -> None:
        stats = self._stats
        values: dict[str, tuple[float, str]] = {
            "atk": (float(stats.atk), f"Attack {stats.atk}"),
            "defense": (float(stats.defense), f"Defense {stats.defense}"),
            "spd": (float(stats.spd), f"Speed {stats.spd}"),
            "crit_rate": (float(stats.crit_rate), f"Crit Rate {stats.crit_rate * 100:.1f}%"),
            "dodge_odds": (float(stats.dodge_odds), f"Dodge {stats.dodge_odds * 100:.1f}%"),
            "regain": (float(stats.regain), f"Regain {stats.regain}"),
            "mitigation": (float(stats.mitigation), f"Mitigation {stats.mitigation:.2f}"),
        }

        for key, bar in self._bars.items():
            value, tooltip = values.get(key, (0.0, ""))
            maximum = float(self._maxima.get(key, 1.0))
            if maximum <= 0:
                maximum = 1.0
            percent = int(round(100.0 * value / maximum))
            percent = max(0, min(100, percent))
            bar.setValue(percent)
            if tooltip:
                bar.setToolTip(tooltip)

