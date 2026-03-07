from __future__ import annotations

import json
import math
import random

from dataclasses import dataclass

from PySide6.QtCore import QByteArray
from PySide6.QtCore import QMimeData
from PySide6.QtCore import QPoint
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal
from PySide6.QtGui import QDrag
from PySide6.QtGui import QDragEnterEvent
from PySide6.QtGui import QDropEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.save import OFFSITE_SLOTS
from endless_idler.save import ONSITE_SLOTS
from endless_idler.save import STANDBY_SLOTS
from endless_idler.save import RunSave
from endless_idler.save import SaveManager
from endless_idler.save import new_run_save
from endless_idler.save import sanitize_save_characters
from endless_idler.ui.idle.bootstrap import bootstrap_party
from endless_idler.ui.idle.bootstrap import should_bootstrap_party
from endless_idler.ui.party_builder_common import derive_display_name
from endless_idler.ui.party_builder_common import sanitize_stars


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
        stars: int,
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
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self._char_id = char_id
        self._source_lane = source_lane
        self._source_index = source_index
        self._drag_start_pos: QPoint | None = None

        stars = sanitize_stars(stars)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        name_label = QLabel(display_name)
        name_label.setObjectName("LayoutCharacterName")
        layout.addWidget(name_label)

        stars_label = QLabel("★" * stars)
        stars_label.setObjectName("LayoutCharacterStars")
        layout.addWidget(stars_label, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.setToolTip(f"{display_name} ({stars}★)")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.position().toPoint()
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
        drag.exec(Qt.DropAction.MoveAction)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._drag_start_pos = None


class _PartySlot(QFrame):
    dropped = Signal(object)

    def __init__(self, *, lane: str, index: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._lane = lane
        self._index = index
        self._char_id: str | None = None

        self.setObjectName("LayoutSlot")
        self.setProperty("slotFilled", False)
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(78)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        title = QLabel(f"{lane.capitalize()} {index + 1}")
        title.setObjectName("LayoutSlotTitle")
        layout.addWidget(title)

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
            _repolish(self)
            return

        _clear_layout(self._body)
        chip = _CharacterChip(
            char_id=char_id,
            display_name=str(getattr(plugin, "display_name", char_id)),
            stars=int(getattr(plugin, "stars", 1) or 1),
            source_lane=self._lane,
            source_index=self._index,
        )
        self._body.addWidget(chip)
        self.setProperty("slotFilled", True)
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

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("LayoutUnassignedPanel")
        self.setAcceptDrops(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        title = QLabel("Owned / Unassigned")
        title.setObjectName("LayoutUnassignedTitle")
        root.addWidget(title)

        scroll = QScrollArea(self)
        scroll.setObjectName("LayoutUnassignedScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(scroll, 1)

        host = QWidget(scroll)
        self._chips_layout = QHBoxLayout(host)
        self._chips_layout.setContentsMargins(4, 4, 4, 4)
        self._chips_layout.setSpacing(8)
        scroll.setWidget(host)

    def set_characters(
        self,
        *,
        char_ids: list[str],
        plugin_by_id: dict[str, CharacterPlugin],
    ) -> None:
        _clear_layout(self._chips_layout)
        if not char_ids:
            empty = QLabel("No unassigned characters.")
            empty.setObjectName("LayoutUnassignedEmpty")
            self._chips_layout.addWidget(empty, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._chips_layout.addStretch(1)
            return

        for index, char_id in enumerate(char_ids):
            plugin = plugin_by_id.get(char_id)
            display_name = str(getattr(plugin, "display_name", derive_display_name(char_id)))
            stars = int(getattr(plugin, "stars", 1) or 1)
            chip = _CharacterChip(
                char_id=char_id,
                display_name=display_name,
                stars=stars,
                source_lane="unassigned",
                source_index=index,
                parent=self,
            )
            self._chips_layout.addWidget(chip, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

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
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("LayoutScreen")

        self._rng = random.Random()
        self._plugins = discover_character_plugins()
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}

        self._save_manager = SaveManager()
        self._save = self._load_or_create_save()
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
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header = QFrame(self)
        header.setObjectName("LayoutHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(12, 12, 12, 12)
        header_layout.setSpacing(4)
        root.addWidget(header)

        title = QLabel("Layout")
        title.setObjectName("LayoutTitle")
        header_layout.addWidget(title)

        subtitle = QLabel("Drag characters between Onsite, Offsite, and Owned / Unassigned.")
        subtitle.setObjectName("LayoutSubtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)

        lanes = QFrame(self)
        lanes.setObjectName("LayoutLanesPanel")
        lanes_layout = QGridLayout(lanes)
        lanes_layout.setContentsMargins(12, 12, 12, 12)
        lanes_layout.setHorizontalSpacing(10)
        lanes_layout.setVerticalSpacing(10)
        root.addWidget(lanes)

        onsite_label = QLabel("Onsite")
        onsite_label.setObjectName("LayoutLaneTitle")
        lanes_layout.addWidget(onsite_label, 0, 0, 1, 1)

        offsite_label = QLabel("Offsite")
        offsite_label.setObjectName("LayoutLaneTitle")
        lanes_layout.addWidget(offsite_label, 1, 0, 1, 1)

        onsite_row = QHBoxLayout()
        onsite_row.setContentsMargins(0, 0, 0, 0)
        onsite_row.setSpacing(8)
        self._onsite_slots: list[_PartySlot] = []
        for index in range(ONSITE_SLOTS):
            slot = _PartySlot(lane="onsite", index=index, parent=lanes)
            slot.dropped.connect(self._on_slot_drop)
            self._onsite_slots.append(slot)
            onsite_row.addWidget(slot)
        lanes_layout.addLayout(onsite_row, 0, 1, 1, 1)

        offsite_row = QHBoxLayout()
        offsite_row.setContentsMargins(0, 0, 0, 0)
        offsite_row.setSpacing(8)
        self._offsite_slots: list[_PartySlot] = []
        for index in range(OFFSITE_SLOTS):
            slot = _PartySlot(lane="offsite", index=index, parent=lanes)
            slot.dropped.connect(self._on_slot_drop)
            self._offsite_slots.append(slot)
            offsite_row.addWidget(slot)
        lanes_layout.addLayout(offsite_row, 1, 1, 1, 1)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(12)
        root.addLayout(bottom, 1)

        self._unassigned_panel = _UnassignedPanel(self)
        self._unassigned_panel.dropped.connect(self._on_unassigned_drop)
        bottom.addWidget(self._unassigned_panel, 1)

        controls = QFrame(self)
        controls.setObjectName("LayoutControlsPanel")
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        controls_layout.setSpacing(8)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        bottom.addWidget(controls, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        order_label = QLabel("Owned order")
        order_label.setObjectName("LayoutControlLabel")
        controls_layout.addWidget(order_label)

        combo = QComboBox(controls)
        combo.setObjectName("LayoutOrderCombo")
        for key, label in ORDERING_OPTIONS:
            combo.addItem(label, userData=key)
        self._ordering_combo = combo
        controls_layout.addWidget(combo)

        status = QLabel("Autosave enabled")
        status.setObjectName("LayoutSaveStatus")
        status.setWordWrap(True)
        self._status_label = status
        controls_layout.addWidget(status)
        controls_layout.addStretch(1)

        saved_order = str(getattr(self._save, "layout_owned_ordering", ORDER_SAVE))
        index = self._ordering_combo.findData(saved_order)
        self._ordering_combo.setCurrentIndex(index if index >= 0 else 0)
        self._ordering_combo.currentIndexChanged.connect(self._on_ordering_changed)

        self._refresh_views()

    def _load_or_create_save(self) -> RunSave:
        loaded = self._save_manager.load()
        is_new_save = loaded is None
        save = loaded or new_run_save()
        save = sanitize_save_characters(save=save, allowed_char_ids=set(self._plugin_by_id))
        if is_new_save and should_bootstrap_party(save):
            bootstrap_party(save=save, plugins=self._plugins, rng=self._rng)
        self._save_manager.save(save)
        return save

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

    def _set_standby_ids(self, ids: list[str]) -> None:
        interior = max(0, STANDBY_SLOTS - 2)
        trimmed = ids[:interior]
        standby: list[str | None] = [None]
        standby.extend(trimmed)
        standby.extend([None] * (interior - len(trimmed)))
        standby.append(None)
        self._save.standby = standby

    def _ordering_key(self) -> str:
        value = self._ordering_combo.currentData()
        key = str(value).strip().lower()
        if key not in {ORDER_SAVE, ORDER_RARITY, ORDER_ALPHA, ORDER_RECENT}:
            return ORDER_SAVE
        return key

    def _ordered_unassigned_ids(self) -> list[str]:
        ids = self._standby_ids()
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

    def _on_ordering_changed(self, _index: int) -> None:
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
        try:
            standby_ids.remove(char_id)
        except ValueError:
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
        self._save_manager.save(self._save)
        self._set_status(f"Saved (idle cooldown {int(math.ceil(LAYOUT_TICK_COOLDOWN_SECONDS))}s)")
        self._status_clear_timer.start()

    def _set_status(self, text: str) -> None:
        self._status_label.setText(text)

    def _clear_status(self) -> None:
        self._status_label.setText("Autosave enabled")
