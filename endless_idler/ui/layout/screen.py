from __future__ import annotations

import json
import math
import random

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QByteArray
from PySide6.QtCore import QEvent
from PySide6.QtCore import QMimeData
from PySide6.QtCore import QObject
from PySide6.QtCore import QPoint
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal
from PySide6.QtGui import QDrag
from PySide6.QtGui import QDragEnterEvent
from PySide6.QtGui import QDropEvent
from PySide6.QtGui import QEnterEvent
from PySide6.QtGui import QFontMetrics
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.placement_rules import MISPLACED_EXP_MULTIPLIER
from endless_idler.characters.placement_rules import MISPLACED_STAT_MULTIPLIER
from endless_idler.characters.placement_rules import lane_allows_placement
from endless_idler.characters.placement_rules import plugin_lane_mismatch
from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.combat.damage_types import normalize_damage_type_id
from endless_idler.combat.party_stats import apply_base_stat_multiplier
from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.save import OFFSITE_SLOTS
from endless_idler.save import ONSITE_SLOTS
from endless_idler.save import STANDBY_SLOTS
from endless_idler.run_save_store import RunSaveStore
from endless_idler.ui.party_builder_common import build_character_stats_tooltip
from endless_idler.ui.party_builder_common import derive_display_name
from endless_idler.ui.party_builder_common import sanitize_stars
from endless_idler.ui.party_builder_common import set_pixmap
from endless_idler.ui.theme.colors import color_for_damage_type_id
from endless_idler.ui.theme.colors import normalize_element_id
from endless_idler.ui.tooltip import hide_stained_tooltip
from endless_idler.ui.tooltip import show_stained_tooltip


LAYOUT_AUTOSAVE_DEBOUNCE_MS = 450
LAYOUT_STATUS_CLEAR_MS = 1200
LAYOUT_TICK_COOLDOWN_SECONDS = 5.0
_LAYOUT_MIME_TYPE = "application/x-endless-idler-layout-char"

ORDER_SAVE = "save_order"
ORDER_RARITY = "rarity_desc"
ORDER_ALPHA = "alphabetical"
ORDER_RECENT = "recent"
ORDERING_OPTIONS: tuple[tuple[str, str], ...] = (
    (ORDER_SAVE, "Current save order"),
    (ORDER_RARITY, "Rarity (high to low)"),
    (ORDER_ALPHA, "Alphabetical"),
    (ORDER_RECENT, "Most recently obtained"),
)
ORDERING_BUTTON_LABELS: dict[str, str] = {
    ORDER_SAVE: "Save",
    ORDER_RARITY: "Rarity",
    ORDER_ALPHA: "A-Z",
    ORDER_RECENT: "Recent",
}
_ORDERING_VALUES = frozenset(ORDERING_BUTTON_LABELS)
LAYOUT_CHIP_PORTRAIT_SIZE = 68
LAYOUT_SLOT_WIDTH = 124
LAYOUT_SLOT_HEIGHT = 144
LAYOUT_STANDBY_SLOT_WIDTH = 110
LAYOUT_STANDBY_SLOT_HEIGHT = 118
LAYOUT_STANDBY_PANEL_HEIGHT = LAYOUT_STANDBY_SLOT_HEIGHT + 60
LAYOUT_TOOLTIP_REFRESH_INTERVAL_MS = 500  # ~5 idle ticks at 0.1s/tick


@dataclass(frozen=True, slots=True)
class _DragData:
    char_id: str
    source_lane: str
    source_index: int


def _repolish(widget: QWidget) -> None:
    style = widget.style()
    if style is None:
        return
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def _clear_layout(layout: QHBoxLayout | QVBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        if item is None:
            continue
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()


def _normalized_damage_type_key(value: str | None) -> str:
    normalized = normalize_damage_type_id(str(value or "generic"))
    if "/" in normalized:
        normalized = normalized.split("/", 1)[0].strip()
    return normalize_element_id(normalized)


def _make_damage_glow_effect(widget: QWidget, element_id: str) -> QGraphicsDropShadowEffect:
    glow = QGraphicsDropShadowEffect(widget)
    glow.setBlurRadius(20)
    glow.setOffset(0, 0)
    color = color_for_damage_type_id(element_id)
    color.setAlpha(165)
    glow.setColor(color)
    return glow


def _coerce_int(value: object, default: int) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    try:
        return int(default)
    except (TypeError, ValueError):
        return default


def _coerce_float(value: object, default: float) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    try:
        return float(default)
    except (TypeError, ValueError):
        return default


def _encode_drag_data(payload: _DragData) -> QByteArray:
    raw = json.dumps(
        {
            "char_id": payload.char_id,
            "source_lane": payload.source_lane,
            "source_index": payload.source_index,
        }
    ).encode("utf-8")
    return QByteArray(raw)


def _decode_drag_data(mime_data: QMimeData) -> _DragData | None:
    if not mime_data.hasFormat(_LAYOUT_MIME_TYPE):
        return None
    raw = bytes(mime_data.data(_LAYOUT_MIME_TYPE).data())
    if not raw:
        return None
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None

    char_id = str(payload.get("char_id", "")).strip()
    source_lane = str(payload.get("source_lane", "")).strip()
    source_index_raw = payload.get("source_index", -1)
    try:
        source_index = int(source_index_raw)
    except (TypeError, ValueError):
        return None

    if not char_id:
        return None
    if source_lane not in {"onsite", "offsite", "unassigned"}:
        return None
    if source_lane != "unassigned" and source_index < 0:
        return None
    return _DragData(char_id=char_id, source_lane=source_lane, source_index=source_index)


class _CharacterChip(QFrame):
    def __init__(
        self,
        *,
        char_id: str,
        display_name: str,
        image_path: Path | None,
        stars: int,
        placement: str,
        element_id: str,
        tooltip_provider: Callable[[], tuple[str, str | None]],
        source_lane: str,
        source_index: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("LayoutCharacterChip")
        self.setProperty(
            "layoutChipRole",
            "unassigned" if source_lane == "unassigned" else "assigned",
        )
        self.setProperty("elementId", element_id)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self._char_id = char_id
        self._source_lane = source_lane
        self._source_index = source_index
        self._tooltip_provider = tooltip_provider
        self._drag_start_pos: QPoint | None = None
        self._tooltip_refresh_timer = QTimer(self)
        self._tooltip_refresh_timer.setInterval(LAYOUT_TOOLTIP_REFRESH_INTERVAL_MS)
        self._tooltip_refresh_timer.timeout.connect(self._refresh_tooltip_while_hovered)

        stars = sanitize_stars(stars)
        layout = QGridLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setHorizontalSpacing(4)
        layout.setVerticalSpacing(2)

        portrait = QLabel()
        portrait.setObjectName("LayoutCharacterPortrait")
        portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        portrait.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        portrait.setFixedSize(LAYOUT_CHIP_PORTRAIT_SIZE, LAYOUT_CHIP_PORTRAIT_SIZE)
        set_pixmap(
            portrait,
            image_path,
            size=LAYOUT_CHIP_PORTRAIT_SIZE,
            placeholder=display_name,
        )
        layout.addWidget(
            portrait,
            0,
            0,
            1,
            1,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
        )

        placement_badge = QFrame(self)
        placement_badge.setObjectName("LayoutPlacementBadge")
        placement_badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        placement_layout = QVBoxLayout(placement_badge)
        placement_layout.setContentsMargins(2, 2, 2, 2)
        placement_layout.setSpacing(2)

        placement_top = QFrame(placement_badge)
        placement_top.setObjectName("LayoutPlacementSquare")
        placement_top.setProperty("placementSlot", "onsite")
        placement_top.setFixedSize(10, 10)
        placement_layout.addWidget(
            placement_top,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )

        placement_bottom = QFrame(placement_badge)
        placement_bottom.setObjectName("LayoutPlacementSquare")
        placement_bottom.setProperty("placementSlot", "offsite")
        placement_bottom.setFixedSize(10, 10)
        placement_layout.addWidget(
            placement_bottom,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )

        placement_key = str(placement or "both").strip().lower()
        if placement_key not in {"onsite", "offsite", "both"}:
            placement_key = "both"
        mismatch = source_lane in {"onsite", "offsite"} and not lane_allows_placement(
            lane=source_lane,
            placement=placement_key,
        )
        self.setProperty("placementMismatch", mismatch)
        placement_top.setProperty("mismatch", mismatch)
        placement_bottom.setProperty("mismatch", mismatch)
        placement_top.setProperty("filled", placement_key in {"onsite", "both"})
        placement_bottom.setProperty("filled", placement_key in {"offsite", "both"})
        _repolish(placement_top)
        _repolish(placement_bottom)
        layout.addWidget(
            placement_badge,
            0,
            0,
            1,
            1,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )

        name_label = QLabel(display_name)
        name_label.setObjectName("LayoutCharacterName")
        name_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        name_label.setWordWrap(False)
        name_label.setText(
            QFontMetrics(name_label.font()).elidedText(
                display_name,
                Qt.TextElideMode.ElideRight,
                max(40, LAYOUT_SLOT_WIDTH - 24),
            )
        )
        layout.addWidget(
            name_label,
            1,
            0,
            1,
            1,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        )

        stars_label = QLabel("★" * stars)
        stars_label.setObjectName("LayoutCharacterStars")
        stars_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        stars_label.setProperty("starRank", stars)
        _repolish(stars_label)
        layout.addWidget(
            stars_label,
            2,
            0,
            1,
            1,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
        )
        self.setGraphicsEffect(_make_damage_glow_effect(self, element_id))
        # The layout screen uses custom stained tooltip rendering only.
        self.setToolTip("")
        for widget in (
            portrait,
            name_label,
            stars_label,
            placement_badge,
            placement_top,
            placement_bottom,
        ):
            widget.installEventFilter(self)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.position().toPoint()
            self._tooltip_refresh_timer.stop()
            hide_stained_tooltip()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return super().mouseMoveEvent(event)
        if self._drag_start_pos is None:
            return super().mouseMoveEvent(event)
        if (
            event.position().toPoint() - self._drag_start_pos
        ).manhattanLength() < 8:
            return super().mouseMoveEvent(event)

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setData(
            _LAYOUT_MIME_TYPE,
            _encode_drag_data(
                _DragData(
                    char_id=self._char_id,
                    source_lane=self._source_lane,
                    source_index=self._source_index,
                )
            ),
        )
        drag.setMimeData(mime_data)
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self._tooltip_refresh_timer.stop()
        hide_stained_tooltip()
        drag.exec(Qt.DropAction.MoveAction)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._drag_start_pos = None

    def _show_tooltip(self) -> None:
        tooltip_html, tooltip_element_id = self._tooltip_provider()
        if not tooltip_html:
            hide_stained_tooltip()
            return
        show_stained_tooltip(
            self,
            tooltip_html,
            element_id=tooltip_element_id,
        )

    def _refresh_tooltip_while_hovered(self) -> None:
        if self.underMouse():
            self._show_tooltip()
            return
        self._tooltip_refresh_timer.stop()
        hide_stained_tooltip()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Enter:
            self._show_tooltip()
            self._tooltip_refresh_timer.start()
        return super().eventFilter(watched, event)

    def enterEvent(self, event: QEnterEvent) -> None:
        self._show_tooltip()
        self._tooltip_refresh_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        QTimer.singleShot(0, self._refresh_tooltip_while_hovered)
        super().leaveEvent(event)


class _PartySlot(QFrame):
    dropped = Signal(object)

    def __init__(
        self,
        *,
        lane: str,
        index: int,
        resolve_image_path: Callable[[str, CharacterPlugin | None], Path | None],
        build_tooltip_data: Callable[[str, CharacterPlugin | None], tuple[str, str | None]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._lane = lane
        self._index = index
        self._char_id: str | None = None
        self._resolve_image_path = resolve_image_path
        self._build_tooltip_data = build_tooltip_data

        self.setObjectName("LayoutSlot")
        self.setProperty("slotFilled", False)
        self.setProperty("elementId", "generic")
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(LAYOUT_SLOT_WIDTH, LAYOUT_SLOT_HEIGHT)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(0)

        self._body = QVBoxLayout()
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(0)
        layout.addLayout(self._body)
        self._render_empty()

    def set_character(self, *, char_id: str | None, plugin: CharacterPlugin | None) -> None:
        self._char_id = char_id
        if not char_id or plugin is None:
            self._render_empty()
            self.setProperty("slotFilled", False)
            self.setProperty("elementId", "generic")
            _repolish(self)
            return

        _clear_layout(self._body)
        element_id = _normalized_damage_type_key(getattr(plugin, "damage_type_id", "generic"))
        chip = _CharacterChip(
            char_id=char_id,
            display_name=str(getattr(plugin, "display_name", char_id)),
            image_path=self._resolve_image_path(char_id, plugin),
            stars=int(getattr(plugin, "stars", 1) or 1),
            placement=str(getattr(plugin, "placement", "both") or "both"),
            element_id=element_id,
            tooltip_provider=lambda char_id=char_id, plugin=plugin: self._build_tooltip_data(
                char_id, plugin
            ),
            source_lane=self._lane,
            source_index=self._index,
        )
        self._body.addWidget(chip)
        self.setProperty("slotFilled", True)
        self.setProperty("elementId", element_id)
        _repolish(self)

    def _render_empty(self) -> None:
        _clear_layout(self._body)
        placeholder = QLabel("Drop character here")
        placeholder.setObjectName("LayoutSlotPlaceholder")
        self._body.addWidget(placeholder)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        drag_data = _decode_drag_data(event.mimeData())
        if drag_data is None:
            event.ignore()
            return
        if drag_data.source_lane == self._lane and drag_data.source_index == self._index:
            event.ignore()
            return
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        drag_data = _decode_drag_data(event.mimeData())
        if drag_data is None:
            event.ignore()
            return
        self.dropped.emit(
            {
                "target_lane": self._lane,
                "target_index": self._index,
                "drag_data": drag_data,
            }
        )
        event.acceptProposedAction()


class _UnassignedPanel(QFrame):
    dropped = Signal(object)

    def __init__(
        self,
        *,
        resolve_image_path: Callable[[str, CharacterPlugin | None], Path | None],
        build_tooltip_data: Callable[[str, CharacterPlugin | None], tuple[str, str | None]],
        on_cycle_sort: Callable[[bool], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._resolve_image_path = resolve_image_path
        self._build_tooltip_data = build_tooltip_data
        self.setObjectName("LayoutUnassignedPanel")
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(LAYOUT_STANDBY_PANEL_HEIGHT)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        root.addLayout(header)

        title = QLabel("Standby")
        title.setObjectName("LayoutUnassignedTitle")
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.addStretch(1)

        sort_button = QPushButton("Sort: Save", self)
        sort_button.setObjectName("LayoutOrderCycleButton")
        sort_button.setCursor(Qt.CursorShape.PointingHandCursor)
        sort_button.clicked.connect(on_cycle_sort)
        self._sort_button = sort_button
        header.addWidget(sort_button, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        scroll = QScrollArea(self)
        scroll.setObjectName("LayoutUnassignedScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(scroll, 1)

        host = QWidget(scroll)
        self._chips_layout = QHBoxLayout(host)
        self._chips_layout.setContentsMargins(4, 2, 4, 2)
        self._chips_layout.setSpacing(10)
        scroll.setWidget(host)

    @property
    def sort_button(self) -> QPushButton:
        return self._sort_button

    def set_characters(
        self,
        *,
        char_ids: list[str],
        plugin_by_id: dict[str, CharacterPlugin],
    ) -> None:
        _clear_layout(self._chips_layout)
        for index, char_id in enumerate(char_ids):
            plugin = plugin_by_id.get(char_id)
            display_name = str(getattr(plugin, "display_name", derive_display_name(char_id)))
            stars = int(getattr(plugin, "stars", 1) or 1)
            element_id = _normalized_damage_type_key(getattr(plugin, "damage_type_id", "generic"))
            chip = _CharacterChip(
                char_id=char_id,
                display_name=display_name,
                image_path=self._resolve_image_path(char_id, plugin),
                stars=stars,
                placement=str(getattr(plugin, "placement", "both") or "both"),
                element_id=element_id,
                tooltip_provider=lambda char_id=char_id, plugin=plugin: self._build_tooltip_data(
                    char_id, plugin
                ),
                source_lane="unassigned",
                source_index=index,
                parent=self,
            )
            self._chips_layout.addWidget(
                chip,
                0,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            )

        self._chips_layout.addStretch(1)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        drag_data = _decode_drag_data(event.mimeData())
        if drag_data is None:
            event.ignore()
            return
        if drag_data.source_lane == "unassigned":
            event.ignore()
            return
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        drag_data = _decode_drag_data(event.mimeData())
        if drag_data is None:
            event.ignore()
            return
        if drag_data.source_lane == "unassigned":
            event.ignore()
            return
        self.dropped.emit(drag_data)
        event.acceptProposedAction()


class LayoutScreenWidget(QWidget):
    def __init__(self, *, save_store: RunSaveStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("LayoutScreen")

        self._rng = random.Random()
        self._save_store = save_store
        self._plugins = discover_character_plugins()
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}
        self._portrait_by_id: dict[str, Path | None] = {}
        self._ordering_key_value = ORDER_SAVE
        self._ordering_cycle_button: QPushButton | None = None
        self._status_label: QLabel | None = None

        self._save = self._save_store.current
        self._dirty = False

        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.setInterval(LAYOUT_AUTOSAVE_DEBOUNCE_MS)
        self._autosave_timer.timeout.connect(self._persist_layout)

        self._status_clear_timer = QTimer(self)
        self._status_clear_timer.setSingleShot(True)
        self._status_clear_timer.setInterval(LAYOUT_STATUS_CLEAR_MS)
        self._status_clear_timer.timeout.connect(self._clear_status)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        lanes = QFrame(self)
        lanes.setObjectName("LayoutLanesPanel")
        lanes_layout = QGridLayout(lanes)
        lanes_layout.setContentsMargins(14, 14, 14, 14)
        lanes_layout.setHorizontalSpacing(12)
        lanes_layout.setVerticalSpacing(12)
        root.addWidget(lanes)

        onsite_label = QLabel("Onsite")
        onsite_label.setObjectName("LayoutLaneTitle")
        lanes_layout.addWidget(onsite_label, 0, 0, 1, 1)

        offsite_label = QLabel("Offsite")
        offsite_label.setObjectName("LayoutLaneTitle")
        lanes_layout.addWidget(offsite_label, 1, 0, 1, 1)

        onsite_row = QHBoxLayout()
        onsite_row.setContentsMargins(0, 0, 0, 0)
        onsite_row.setSpacing(12)
        onsite_row.addStretch(1)
        self._onsite_slots: list[_PartySlot] = []
        for index in range(ONSITE_SLOTS):
            slot = _PartySlot(
                lane="onsite",
                index=index,
                resolve_image_path=self._resolve_image_path,
                build_tooltip_data=self._build_tooltip_data,
                parent=lanes,
            )
            slot.dropped.connect(self._on_slot_drop)
            self._onsite_slots.append(slot)
            onsite_row.addWidget(slot)
        onsite_row.addStretch(1)
        lanes_layout.addLayout(onsite_row, 0, 1, 1, 1)

        offsite_row = QHBoxLayout()
        offsite_row.setContentsMargins(0, 0, 0, 0)
        offsite_row.setSpacing(12)
        offsite_row.addStretch(1)
        self._offsite_slots: list[_PartySlot] = []
        for index in range(OFFSITE_SLOTS):
            slot = _PartySlot(
                lane="offsite",
                index=index,
                resolve_image_path=self._resolve_image_path,
                build_tooltip_data=self._build_tooltip_data,
                parent=lanes,
            )
            slot.dropped.connect(self._on_slot_drop)
            self._offsite_slots.append(slot)
            offsite_row.addWidget(slot)
        offsite_row.addStretch(1)
        lanes_layout.addLayout(offsite_row, 1, 1, 1, 1)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(12)
        root.addLayout(bottom, 1)

        self._unassigned_panel = _UnassignedPanel(
            resolve_image_path=self._resolve_image_path,
            build_tooltip_data=self._build_tooltip_data,
            on_cycle_sort=self._on_ordering_cycle_clicked,
            parent=self,
        )
        self._unassigned_panel.dropped.connect(self._on_unassigned_drop)
        bottom.addWidget(self._unassigned_panel, 1)
        self._ordering_cycle_button = self._unassigned_panel.sort_button

        self._set_ordering_key(str(getattr(self._save, "layout_owned_ordering", ORDER_SAVE)))

        self._refresh_views()

    def _lane_list(self, lane: str) -> list[str | None]:
        if lane == "onsite":
            return self._save.onsite
        if lane == "offsite":
            return self._save.offsite
        raise ValueError(f"Unsupported lane: {lane}")

    def _standby_ids(self) -> list[str]:
        ids: list[str] = []
        for index in range(1, max(1, STANDBY_SLOTS - 1)):
            char_id = self._save.standby[index]
            if char_id:
                ids.append(char_id)
        return ids

    def _owned_unassigned_ids(self) -> list[str]:
        ids: list[str] = []
        seen: set[str] = set()

        def collect(char_id: str | None) -> None:
            if not char_id:
                return
            clean = str(char_id).strip()
            if not clean or clean in seen:
                return
            if clean not in self._plugin_by_id:
                return
            if self._is_assigned(clean):
                return
            seen.add(clean)
            ids.append(clean)

        for char_id in self._standby_ids():
            collect(char_id)
        for source in (
            self._save.stacks.keys(),
            self._save.character_progress.keys(),
            self._save.character_stats.keys(),
        ):
            for char_id in source:
                collect(char_id)

        return ids

    def _set_standby_ids(self, ids: list[str]) -> None:
        interior = max(0, STANDBY_SLOTS - 2)
        trimmed = ids[:interior]
        standby: list[str | None] = [None]
        standby.extend(trimmed)
        standby.extend([None] * (interior - len(trimmed)))
        standby.append(None)
        self._save.standby = standby

    def _resolve_image_path(self, char_id: str, plugin: CharacterPlugin | None) -> Path | None:
        if char_id in self._portrait_by_id:
            return self._portrait_by_id[char_id]
        image_path = plugin.random_image_path(self._rng) if plugin else None
        self._portrait_by_id[char_id] = image_path
        return image_path

    def _assigned_lane_for_char(self, char_id: str) -> str:
        if char_id in self._save.onsite:
            return "onsite"
        if char_id in self._save.offsite:
            return "offsite"
        return "unassigned"

    def _live_idle_tooltip_snapshot(self, char_id: str) -> tuple[dict[str, object], int] | None:
        host = self.parentWidget()
        if host is None:
            return None

        idle_screen = getattr(host, "_idle_screen", None)
        if idle_screen is None:
            return None

        idle_state = getattr(idle_screen, "_idle_state", None)
        if idle_state is None:
            return None

        get_char_data = getattr(idle_state, "get_char_data", None)
        if not callable(get_char_data):
            return None
        data = get_char_data(char_id)
        if not isinstance(data, dict):
            return None
        typed_data: dict[str, object] = data

        party_level = max(1, int(self._save.party_level))
        get_party_level = getattr(idle_state, "get_party_level", None)
        if callable(get_party_level):
            party_level = max(1, _coerce_int(get_party_level(), party_level))
        return typed_data, party_level

    def _sync_tooltip_save_snapshot(self) -> None:
        self._save = self._save_store.current

    def _build_tooltip_data(
        self,
        char_id: str,
        plugin: CharacterPlugin | None,
    ) -> tuple[str, str | None]:
        if plugin is None:
            return "", None

        live_snapshot = self._live_idle_tooltip_snapshot(char_id)
        if live_snapshot is None:
            self._sync_tooltip_save_snapshot()

        stars = sanitize_stars(int(getattr(plugin, "stars", 1) or 1))
        party_level = max(1, int(self._save.party_level))
        stacks = max(1, int(self._save.stacks.get(char_id, 1)))
        progress_raw = self._save.character_progress.get(char_id, {})
        progress: dict[str, float | int] = (
            dict(progress_raw) if isinstance(progress_raw, dict) else {}
        )
        saved_base_stats_raw = self._save.character_stats.get(char_id, {})
        saved_base_stats: dict[str, float] = (
            dict(saved_base_stats_raw) if isinstance(saved_base_stats_raw, dict) else {}
        )

        current_hp: int | None = None
        if live_snapshot is not None:
            live_data, live_party_level = live_snapshot
            party_level = max(1, int(live_party_level))
            stacks = max(1, _coerce_int(live_data.get("stack", stacks), stacks))

            progress = {
                "level": max(1, _coerce_int(live_data.get("level", progress.get("level", 1)), 1)),
                "exp": max(0.0, _coerce_float(live_data.get("exp", progress.get("exp", 0.0)), 0.0)),
                "exp_multiplier": float(
                    max(
                        0.0,
                        _coerce_float(
                            live_data.get("exp_multiplier", progress.get("exp_multiplier", 1.0)),
                            1.0,
                        ),
                    )
                ),
                "max_hp_level_bonus_version": max(
                    0,
                    _coerce_int(
                        live_data.get(
                            "max_hp_level_bonus_version",
                            progress.get("max_hp_level_bonus_version", 0),
                        ),
                        0,
                    ),
                ),
            }
            base_stats = live_data.get("base_stats")
            if isinstance(base_stats, dict):
                saved_base_stats = dict(base_stats)
            hp_value = _coerce_float(live_data.get("hp"), -1.0)
            if hp_value >= 0.0:
                current_hp = max(0, int(hp_value))

        stats = build_scaled_character_stats(
            plugin=plugin,
            party_level=party_level,
            stars=stars,
            stacks=stacks,
            progress=progress,
            saved_base_stats=saved_base_stats,
        )
        lane = self._assigned_lane_for_char(char_id)
        mismatch = plugin_lane_mismatch(lane=lane, plugin=plugin)
        if mismatch:
            apply_base_stat_multiplier(
                stats=stats,
                multiplier=MISPLACED_STAT_MULTIPLIER,
            )
        if current_hp is not None:
            stats.hp = max(0, min(stats.max_hp, current_hp))

        tooltip_html = build_character_stats_tooltip(
            name=str(getattr(plugin, "display_name", derive_display_name(char_id))),
            stars=stars,
            stacks=stacks if stacks > 1 else None,
            stackable=stacks > 1,
            stats=stats,
            mismatch=mismatch,
            exp_multiplier_override=(
                stats.exp_multiplier * MISPLACED_EXP_MULTIPLIER
                if mismatch
                else None
            ),
        )
        element_id = str(getattr(stats, "element_id", "generic") or "generic")
        return tooltip_html, element_id

    def _set_ordering_key(self, key: str) -> None:
        normalized = str(key).strip().lower()
        if normalized not in _ORDERING_VALUES:
            normalized = ORDER_SAVE
        self._ordering_key_value = normalized
        if self._ordering_cycle_button is not None:
            label = ORDERING_BUTTON_LABELS.get(normalized, "Save")
            self._ordering_cycle_button.setText(f"Sort: {label}")
            self._ordering_cycle_button.setProperty("orderMode", normalized)
            _repolish(self._ordering_cycle_button)

    def _ordering_key(self) -> str:
        return self._ordering_key_value

    def _ordered_unassigned_ids(self) -> list[str]:
        ids = self._owned_unassigned_ids()
        ordering = self._ordering_key()
        if ordering == ORDER_SAVE:
            return ids
        if ordering == ORDER_RECENT:
            return list(reversed(ids))
        if ordering == ORDER_ALPHA:
            return sorted(
                ids,
                key=lambda char_id: str(
                    getattr(self._plugin_by_id.get(char_id), "display_name", derive_display_name(char_id))
                ).casefold(),
            )
        if ordering == ORDER_RARITY:
            return sorted(
                ids,
                key=lambda char_id: (
                    -int(getattr(self._plugin_by_id.get(char_id), "stars", 1) or 1),
                    str(getattr(self._plugin_by_id.get(char_id), "display_name", derive_display_name(char_id))).casefold(),
                ),
            )
        return ids

    def _is_assigned(self, char_id: str) -> bool:
        return char_id in {item for item in [*self._save.onsite, *self._save.offsite] if item}

    def _on_ordering_cycle_clicked(self, _checked: bool = False) -> None:
        order_keys = [key for key, _label in ORDERING_OPTIONS]
        current = self._ordering_key()
        try:
            index = order_keys.index(current)
        except ValueError:
            index = 0
        next_key = order_keys[(index + 1) % len(order_keys)]
        self._set_ordering_key(next_key)
        self._save.layout_owned_ordering = self._ordering_key()
        self._refresh_unassigned()
        self._schedule_persist("Sorting updated...")

    def _refresh_views(self) -> None:
        self._refresh_slots()
        self._refresh_unassigned()

    def _refresh_slots(self) -> None:
        for index, slot in enumerate(self._onsite_slots):
            char_id = self._save.onsite[index]
            slot.set_character(char_id=char_id, plugin=self._plugin_by_id.get(char_id or ""))
        for index, slot in enumerate(self._offsite_slots):
            char_id = self._save.offsite[index]
            slot.set_character(char_id=char_id, plugin=self._plugin_by_id.get(char_id or ""))

    def _refresh_unassigned(self) -> None:
        self._unassigned_panel.set_characters(
            char_ids=self._ordered_unassigned_ids(),
            plugin_by_id=self._plugin_by_id,
        )

    def _on_slot_drop(self, payload: object) -> None:
        if not isinstance(payload, dict):
            return
        target_lane = str(payload.get("target_lane", "")).strip()
        target_index_raw = payload.get("target_index", -1)
        drag_data = payload.get("drag_data")
        if not isinstance(drag_data, _DragData):
            return
        try:
            target_index = int(target_index_raw)
        except (TypeError, ValueError):
            return

        changed = False
        if drag_data.source_lane == "unassigned":
            changed = self._move_from_unassigned_to_slot(
                char_id=drag_data.char_id,
                target_lane=target_lane,
                target_index=target_index,
            )
        elif drag_data.source_lane in {"onsite", "offsite"}:
            changed = self._move_between_slots(
                source_lane=drag_data.source_lane,
                source_index=drag_data.source_index,
                target_lane=target_lane,
                target_index=target_index,
            )

        if not changed:
            return
        self._refresh_views()
        self._schedule_persist("Saving layout...")

    def _on_unassigned_drop(self, drag_data: object) -> None:
        if not isinstance(drag_data, _DragData):
            return
        if drag_data.source_lane not in {"onsite", "offsite"}:
            return

        changed = self._move_slot_to_unassigned(
            source_lane=drag_data.source_lane,
            source_index=drag_data.source_index,
        )
        if not changed:
            return
        self._refresh_views()
        self._schedule_persist("Saving layout...")

    def _move_between_slots(
        self,
        *,
        source_lane: str,
        source_index: int,
        target_lane: str,
        target_index: int,
    ) -> bool:
        source_list = self._lane_list(source_lane)
        target_list = self._lane_list(target_lane)
        if source_index < 0 or source_index >= len(source_list):
            return False
        if target_index < 0 or target_index >= len(target_list):
            return False
        if source_lane == target_lane and source_index == target_index:
            return False

        source_char = source_list[source_index]
        target_char = target_list[target_index]
        if not source_char:
            return False

        source_list[source_index] = target_char
        target_list[target_index] = source_char
        return True

    def _move_from_unassigned_to_slot(
        self,
        *,
        char_id: str,
        target_lane: str,
        target_index: int,
    ) -> bool:
        target_list = self._lane_list(target_lane)
        if target_index < 0 or target_index >= len(target_list):
            return False
        if self._is_assigned(char_id):
            self._set_status("Character is already assigned.")
            return False

        standby_ids = self._standby_ids()
        if char_id in standby_ids:
            standby_ids.remove(char_id)
        elif char_id not in self._owned_unassigned_ids():
            return False

        displaced = target_list[target_index]
        target_list[target_index] = char_id
        if displaced:
            standby_ids.append(displaced)
        self._set_standby_ids(standby_ids)
        return True

    def _move_slot_to_unassigned(self, *, source_lane: str, source_index: int) -> bool:
        source_list = self._lane_list(source_lane)
        if source_index < 0 or source_index >= len(source_list):
            return False
        char_id = source_list[source_index]
        if not char_id:
            return False

        source_list[source_index] = None
        standby_ids = self._standby_ids()
        standby_ids.append(char_id)
        self._set_standby_ids(standby_ids)
        return True

    def _schedule_persist(self, status_text: str) -> None:
        self._dirty = True
        self._set_status(status_text)
        self._autosave_timer.start()

    def _persist_layout(self) -> None:
        if not self._dirty:
            return
        self._dirty = False
        self._save.layout_owned_ordering = self._ordering_key()
        self._save.layout_tick_cooldown_seconds = LAYOUT_TICK_COOLDOWN_SECONDS
        self._save_store.persist()
        self._set_status(f"Saved (idle cooldown {int(math.ceil(LAYOUT_TICK_COOLDOWN_SECONDS))}s)")
        self._status_clear_timer.start()

    def cancel_pending_persist(self) -> None:
        self._dirty = False
        self._autosave_timer.stop()
        self._status_clear_timer.stop()
        self._clear_status()

    def persist_now(self) -> None:
        self._autosave_timer.stop()
        self._status_clear_timer.stop()
        self._persist_layout()

    def _set_status(self, text: str) -> None:
        if self._status_label is None:
            return
        self._status_label.setText(text)

    def _clear_status(self) -> None:
        if self._status_label is None:
            return
        self._status_label.setText("")
