from __future__ import annotations

import random

from dataclasses import dataclass

from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPen
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.ui.battle.sim import Combatant


@dataclass(slots=True)
class LinePulse:
    source: QWidget
    target: QWidget
    color: QColor
    remaining_ms: int = 220
    width: int = 3


class PortraitLabel(QLabel):
    def __init__(self, *, size: int) -> None:
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_portrait(self, path: str | None, *, placeholder: str) -> None:
        pixmap = QPixmap(path) if path else QPixmap()
        if pixmap.isNull():
            self.setText(placeholder[:2].upper())
            return
        self.setText("")
        self.setPixmap(
            pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )


class CombatantCard(QFrame):
    def __init__(
        self,
        *,
        combatant: Combatant,
        plugin: CharacterPlugin | None,
        rng: random.Random,
        compact: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._combatant = combatant
        self._compact = bool(compact)

        self.setObjectName("battleCombatantCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFixedWidth(260 if not compact else 180)

        root = QHBoxLayout()
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)
        self.setLayout(root)

        portrait_size = 56 if compact else 72
        self._portrait = PortraitLabel(size=portrait_size)
        root.addWidget(self._portrait, 0, Qt.AlignmentFlag.AlignTop)

        portrait_path = plugin.random_image_path(rng) if plugin else None
        self._portrait.set_portrait(
            str(portrait_path) if portrait_path else None,
            placeholder=combatant.name,
        )

        body = QVBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(6)
        root.addLayout(body, 1)

        self._name = QLabel(combatant.name)
        self._name.setObjectName("battleCombatantName")
        body.addWidget(self._name)

        self._hp = QProgressBar()
        self._hp.setObjectName("battleHpBar")
        self._hp.setTextVisible(True)
        self._hp.setRange(0, max(1, int(combatant.max_hp)))
        self._hp.setValue(int(combatant.stats.hp))
        self._hp.setFormat(self._hp_format())
        body.addWidget(self._hp)

        if not compact:
            details = QLabel(self._details_text())
            details.setObjectName("battleCombatantDetails")
            details.setWordWrap(True)
            body.addWidget(details)

    @property
    def combatant(self) -> Combatant:
        return self._combatant

    def refresh(self) -> None:
        self._hp.setValue(int(self._combatant.stats.hp))
        self._hp.setFormat(self._hp_format())
        self._hp.update()
        self.update()

    def _hp_format(self) -> str:
        return f"{max(0, int(self._combatant.stats.hp))} / {max(1, int(self._combatant.max_hp))}"

    def _details_text(self) -> str:
        stats = self._combatant.stats
        return f"ATK {stats.atk}  DEF {stats.defense}  SPD {stats.spd}"


class OffsiteStrip(QFrame):
    def __init__(
        self,
        *,
        char_ids: list[str],
        plugins_by_id: dict[str, CharacterPlugin],
        rng: random.Random,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("battleOffsiteStrip")
        self.setFrameShape(QFrame.Shape.NoFrame)

        root = QVBoxLayout()
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        self.setLayout(root)

        title = QLabel("Offsite")
        title.setObjectName("battleOffsiteTitle")
        root.addWidget(title)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        root.addLayout(row)

        for char_id in char_ids:
            plugin = plugins_by_id.get(char_id)
            label = PortraitLabel(size=40)
            portrait_path = plugin.random_image_path(rng) if plugin else None
            display = plugin.display_name if plugin else char_id
            label.set_portrait(str(portrait_path) if portrait_path else None, placeholder=display)
            label.setToolTip(display)
            row.addWidget(label)

        row.addStretch(1)


class LineOverlay(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("battleLineOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self._pulses: list[LinePulse] = []

    def add_pulse(self, source: QWidget, target: QWidget, color: QColor) -> None:
        self._pulses.append(LinePulse(source=source, target=target, color=color))
        self.update()

    def tick(self, delta_ms: int) -> None:
        if not self._pulses:
            return
        changed = False
        for pulse in self._pulses:
            pulse.remaining_ms -= delta_ms
            if pulse.remaining_ms <= 0:
                changed = True
        if changed:
            self._pulses = [pulse for pulse in self._pulses if pulse.remaining_ms > 0]
        self.update()

    def paintEvent(self, event: object) -> None:
        if not self._pulses:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        for pulse in list(self._pulses):
            if pulse.remaining_ms <= 0:
                continue
            if not pulse.source.isVisible() or not pulse.target.isVisible():
                continue

            start = pulse.source.mapTo(self, pulse.source.rect().center())
            end = pulse.target.mapTo(self, pulse.target.rect().center())

            alpha = max(0, min(255, int(255 * (pulse.remaining_ms / 220.0))))
            color = QColor(pulse.color)
            color.setAlpha(alpha)
            pen = QPen(color)
            pen.setWidth(max(1, int(pulse.width)))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(start, end)

        painter.end()


class Arena(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("battleArena")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._overlay = LineOverlay(self)
        self._overlay.raise_()

        timer = QTimer(self)
        timer.setInterval(30)
        timer.timeout.connect(self._tick)
        timer.start()
        self._timer = timer

    def add_pulse(self, source: QWidget, target: QWidget, color: QColor) -> None:
        self._overlay.add_pulse(source, target, color)
        self._overlay.raise_()

    def resizeEvent(self, event: object) -> None:
        try:
            super().resizeEvent(event)  # type: ignore[misc]
        except Exception:
            pass
        self._overlay.setGeometry(self.rect())
        self._overlay.raise_()

    def _tick(self) -> None:
        self._overlay.tick(30)

