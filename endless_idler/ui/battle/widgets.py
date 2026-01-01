from __future__ import annotations

import random

from dataclasses import dataclass

from PySide6.QtCore import QPointF
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtGui import QPolygonF
from PySide6.QtGui import QBrush
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
from endless_idler.ui.party_builder_common import build_character_stats_tooltip
from endless_idler.ui.tooltip import hide_stained_tooltip
from endless_idler.ui.tooltip import show_stained_tooltip


@dataclass(slots=True)
class LinePulse:
    source: QWidget
    target: QWidget
    color: QColor
    remaining_ms: int = 220
    width: int = 3
    crit: bool = False


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
        team_side: str = "left",
        stack_count: int = 1,
        portrait_size: int | None = None,
        card_width: int | None = None,
        compact: bool = False,
        variant: str = "onsite",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._combatant = combatant
        self._compact = bool(compact)
        self._team_side = (team_side or "left").strip().lower()
        self._stack_count = max(1, int(stack_count))
        self._variant = (variant or "onsite").strip().lower()
        self._exp: QProgressBar | None = None
        self._tooltip_html = ""
        self._stars: int | None = plugin.stars if plugin else None

        self.setObjectName("battleCombatantCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setProperty("battleVariant", self._variant)
        default_width = 260 if not compact else 180
        self.setFixedWidth(max(120, int(card_width or default_width)))

        root = QHBoxLayout()
        if self._variant == "offsite":
            root.setContentsMargins(8, 8, 8, 8)
            root.setSpacing(8)
        elif self._variant == "onsite":
            root.setContentsMargins(12, 12, 12, 12)
            root.setSpacing(10)
        else:
            root.setContentsMargins(10, 10, 10, 10)
            root.setSpacing(10)
        self.setLayout(root)

        default_portrait = 56 if compact else 72
        self._portrait = PortraitLabel(size=max(28, int(portrait_size or default_portrait)))

        portrait_path = plugin.random_image_path(rng) if plugin else None
        self._portrait.set_portrait(str(portrait_path) if portrait_path else None, placeholder=combatant.name)

        body = QVBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(4 if self._variant == "offsite" else 6)
        root.addWidget(self._portrait, 0, Qt.AlignmentFlag.AlignTop)
        root.addLayout(body, 1)

        self._name = QLabel(combatant.name)
        self._name.setObjectName("battleCombatantName")
        self._name.setProperty("battleVariant", self._variant)
        body.addWidget(self._name)

        self._hp = QProgressBar()
        self._hp.setObjectName("battleHpBar")
        self._hp.setProperty("battleVariant", self._variant)
        self._hp.setTextVisible(True)
        self._hp.setRange(0, max(1, int(combatant.max_hp)))
        self._hp.setValue(int(combatant.stats.hp))
        self._hp.setFormat(self._hp_format())
        body.addWidget(self._hp)

        if not compact:
            self._exp = QProgressBar()
            self._exp.setObjectName("battleExpBar")
            self._exp.setProperty("battleVariant", self._variant)
            self._exp.setTextVisible(True)
            exp_value, exp_max = self._exp_progress()
            self._exp.setRange(0, exp_max)
            self._exp.setValue(exp_value)
            self._exp.setFormat(self._exp_format())
            body.addWidget(self._exp)

        self._refresh_tooltip()

    @property
    def combatant(self) -> Combatant:
        return self._combatant

    def refresh(self) -> None:
        self._hp.setValue(int(self._combatant.stats.hp))
        self._hp.setFormat(self._hp_format())
        self._hp.update()
        if self._exp is not None:
            exp_value, exp_max = self._exp_progress()
            self._exp.setRange(0, exp_max)
            self._exp.setValue(exp_value)
            self._exp.setFormat(self._exp_format())
        self._refresh_tooltip()
        self.update()

    def pulse_anchor_global(self) -> QPointF:
        rect = self.rect()
        if self._team_side == "right":
            point = rect.center()
            point.setX(rect.left())
            return QPointF(self.mapToGlobal(point))
        point = rect.center()
        point.setX(rect.right())
        return QPointF(self.mapToGlobal(point))

    def _hp_format(self) -> str:
        return f"{max(0, int(self._combatant.stats.hp))} / {max(1, int(self._combatant.max_hp))}"

    def _exp_progress(self) -> tuple[int, int]:
        stats = self._combatant.stats
        exp_max = max(1, 100 * max(1, int(stats.level)))
        exp_value = max(0, int(stats.exp))
        return min(exp_value, exp_max), exp_max

    def _exp_format(self) -> str:
        exp_value, exp_max = self._exp_progress()
        return f"EXP {exp_value} / {exp_max}"

    def _refresh_tooltip(self) -> None:
        if self._compact:
            self._tooltip_html = ""
            return
        self._tooltip_html = build_character_stats_tooltip(
            name=self._combatant.name,
            stars=self._stars,
            stacks=self._stack_count,
            stackable=self._stack_count > 1,
            stats=self._combatant.stats,
        )

    def enterEvent(self, event: object) -> None:
        if self._tooltip_html:
            show_stained_tooltip(self, self._tooltip_html)
        try:
            super().enterEvent(event)  # type: ignore[misc]
        except Exception:
            return

    def leaveEvent(self, event: object) -> None:
        hide_stained_tooltip()
        try:
            super().leaveEvent(event)  # type: ignore[misc]
        except Exception:
            return


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

    def add_pulse(self, source: QWidget, target: QWidget, color: QColor, *, crit: bool = False) -> None:
        width = 6 if crit else 3
        self._pulses.append(LinePulse(source=source, target=target, color=color, width=width, crit=crit))
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

            start = self._anchor_point(pulse.source)
            end = self._anchor_point(pulse.target)
            if start == end:
                continue

            alpha = max(0, min(255, int(255 * (pulse.remaining_ms / 220.0))))
            color = QColor(pulse.color)
            color.setAlpha(alpha)
            pen = QPen(color)
            pen.setWidth(max(1, int(pulse.width)))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(start, end)

            self._draw_arrow_head(painter, start, end, color, width=pulse.width)

            if pulse.crit:
                progress = 1.0 - (pulse.remaining_ms / 220.0)
                progress = max(0.0, min(1.0, float(progress)))
                point = QPointF(
                    start.x() + (end.x() - start.x()) * progress,
                    start.y() + (end.y() - start.y()) * progress,
                )
                gold = QColor(255, 215, 0)
                gold.setAlpha(alpha)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(gold))
                radius = 6.0 + 4.0 * (1.0 - (alpha / 255.0))
                painter.drawEllipse(point, radius, radius)

        painter.end()

    def _anchor_point(self, widget: QWidget) -> QPointF:
        anchor = getattr(widget, "pulse_anchor_global", None)
        if callable(anchor):
            try:
                point = anchor()
            except Exception:
                point = None
            if isinstance(point, QPointF):
                return QPointF(self.mapFromGlobal(point.toPoint()))
        center = widget.mapToGlobal(widget.rect().center())
        return QPointF(self.mapFromGlobal(center))

    def _draw_arrow_head(
        self,
        painter: QPainter,
        start: QPointF,
        end: QPointF,
        color: QColor,
        *,
        width: int,
    ) -> None:
        dx = float(end.x() - start.x())
        dy = float(end.y() - start.y())
        length = (dx * dx + dy * dy) ** 0.5
        if length <= 1e-6:
            return

        ux = dx / length
        uy = dy / length
        head_len = max(10.0, float(width) * 3.0)
        head_w = max(6.0, float(width) * 2.0)

        base = QPointF(end.x() - ux * head_len, end.y() - uy * head_len)
        perp = QPointF(-uy, ux)
        left = QPointF(base.x() + perp.x() * head_w, base.y() + perp.y() * head_w)
        right = QPointF(base.x() - perp.x() * head_w, base.y() - perp.y() * head_w)

        brush = QBrush(color)
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(brush)
        painter.drawPolygon(QPolygonF([end, left, right]))
        painter.restore()


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

    def add_pulse(self, source: QWidget, target: QWidget, color: QColor, *, crit: bool = False) -> None:
        self._overlay.add_pulse(source, target, color, crit=crit)
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
