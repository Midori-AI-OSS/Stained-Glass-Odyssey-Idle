from __future__ import annotations

import json
import random

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QByteArray
from PySide6.QtCore import Qt
from PySide6.QtCore import QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QLabel

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.ui.party_builder_bar import ShopItem
from endless_idler.ui.party_builder_common import apply_star_rank_visuals
from endless_idler.ui.party_builder_common import build_character_stats_tooltip
from endless_idler.ui.party_builder_common import clear_star_rank_visuals
from endless_idler.ui.party_builder_common import derive_display_name
from endless_idler.ui.party_builder_common import MIME_TYPE
from endless_idler.ui.party_builder_common import set_pixmap
from endless_idler.ui.tooltip import hide_stained_tooltip
from endless_idler.ui.tooltip import show_stained_tooltip


class DropSlot(QFrame):
    def __init__(
        self,
        *,
        empty_label: str,
        slot_id: str,
        plugins_by_id: dict[str, CharacterPlugin],
        rng: random.Random,
        character_cost: int,
        can_afford: Callable[[int], bool],
        purchase_character: Callable[[str, str, str | None], bool],
        is_in_party: Callable[[str], bool],
        is_primary_stack_slot: Callable[[str, str], bool],
        on_slot_changed: Callable[[str, str | None], None],
        on_drag_active_changed: Callable[[bool], None],
        get_stack_count: Callable[[str], int],
        allow_stacking: bool = True,
        show_stack_badge: bool = True,
    ) -> None:
        super().__init__()
        self.setObjectName("dropSlot")
        self.setAcceptDrops(True)

        self._empty_label = empty_label
        self._slot_id = slot_id
        self._slot_kind = slot_id.split("_", 1)[0].strip().lower()
        self._plugins_by_id = plugins_by_id
        self._rng = rng
        self._character_cost = max(0, int(character_cost))
        self._can_afford = can_afford
        self._purchase_character = purchase_character
        self._is_in_party = is_in_party
        self._is_primary_stack_slot = is_primary_stack_slot
        self._on_slot_changed = on_slot_changed
        self._on_drag_active_changed = on_drag_active_changed
        self._get_stack_count = get_stack_count
        self._allow_stacking = bool(allow_stacking)
        self._show_stack_badge = bool(show_stack_badge)

        self._char_id: str | None = None
        self._display_name: str | None = None
        self._image_path: Path | None = None
        self._stars: int | None = None
        self._tooltip_html = ""
        self._suspend_notify = False

        outer = QVBoxLayout()
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(0)
        self.setLayout(outer)

        self._inner = QFrame()
        self._inner.setObjectName("dropSlotInner")
        outer.addWidget(self._inner)

        layout = QGridLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self._inner.setLayout(layout)

        self._image = QLabel()
        self._image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image.setMinimumSize(64, 64)
        layout.addWidget(self._image, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel(empty_label)
        self._label.setObjectName("dropSlotLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label, 1, 0, 1, 1)

        self._stack_badge = QLabel()
        self._stack_badge.setObjectName("stackBadge")
        self._stack_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stack_badge.setMinimumSize(20, 18)
        layout.addWidget(self._stack_badge, 0, 0, 1, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._stack_badge.hide()

        self._placement_badge = QFrame()
        self._placement_badge.setObjectName("placementBadge")
        self._placement_badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        placement_layout = QVBoxLayout()
        placement_layout.setContentsMargins(3, 3, 3, 3)
        placement_layout.setSpacing(2)
        self._placement_badge.setLayout(placement_layout)

        self._placement_top = QFrame()
        self._placement_top.setObjectName("placementSquare")
        self._placement_top.setFixedSize(10, 10)
        self._placement_top.setProperty("filled", False)
        placement_layout.addWidget(self._placement_top, 0, Qt.AlignmentFlag.AlignRight)

        self._placement_bottom = QFrame()
        self._placement_bottom.setObjectName("placementSquare")
        self._placement_bottom.setFixedSize(10, 10)
        self._placement_bottom.setProperty("filled", False)
        placement_layout.addWidget(self._placement_bottom, 0, Qt.AlignmentFlag.AlignRight)

        layout.addWidget(self._placement_badge, 0, 0, 1, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        self._placement_badge.hide()

        self.setFixedSize(110, 130)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._refresh()

    def _allows_char_id(self, char_id: str) -> bool:
        plugin = self._plugins_by_id.get(char_id)
        placement = (plugin.placement if plugin else "both").strip().lower()

        if self._slot_kind == "onsite":
            return placement in {"onsite", "both"}
        if self._slot_kind == "offsite":
            return placement in {"offsite", "both"}
        return True

    def load_char_id(self, char_id: str | None) -> None:
        self._suspend_notify = True
        try:
            if not char_id:
                self._clear()
                return

            plugin = self._plugins_by_id.get(char_id)
            display_name = plugin.display_name if plugin else derive_display_name(char_id)
            image_path = plugin.random_image_path(self._rng) if plugin else None
            stars = plugin.stars if plugin else 1
            self._set_character(char_id, display_name, image_path, stars)
        finally:
            self._suspend_notify = False

    def dragEnterEvent(self, event: object) -> None:
        if not hasattr(event, "mimeData"):
            return
        mime = event.mimeData()
        if not mime.hasFormat(MIME_TYPE):
            return

        raw = bytes(mime.data(MIME_TYPE))
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return
        incoming = str(data.get("char_id", "")).strip()
        if not incoming:
            return
        if not self._allows_char_id(incoming):
            return

        source = event.source() if hasattr(event, "source") else None
        if source is self:
            return
        if isinstance(source, DropSlot):
            if self._slot_kind in {"onsite", "offsite"} and self._is_in_party(incoming):
                if source._slot_kind not in {"onsite", "offsite"}:  # noqa: SLF001
                    return
            if self._char_id is not None and not source._allows_char_id(self._char_id):  # noqa: SLF001
                return
            event.acceptProposedAction()
            return

        if isinstance(source, ShopItem):
            if not self._can_afford(self._character_cost):
                return
            if self._char_id is None:
                event.acceptProposedAction()
                return
            if self._allow_stacking and self._char_id == incoming:
                event.acceptProposedAction()
            return

        if self._char_id is None and self._can_afford(self._character_cost):
            event.acceptProposedAction()

    def mousePressEvent(self, event: object) -> None:
        try:
            button = event.button()
        except AttributeError:
            return
        if button != Qt.MouseButton.LeftButton:
            return
        if not self._char_id or not self._display_name:
            return

        hide_stained_tooltip()
        self._on_drag_active_changed(True)
        mime = QMimeData()
        payload = json.dumps(
            {
                "char_id": self._char_id,
                "display_name": self._display_name,
                "image_path": str(self._image_path) if self._image_path else "",
            }
        ).encode("utf-8")
        mime.setData(MIME_TYPE, QByteArray(payload))

        try:
            drag = QDrag(self)
            drag.setMimeData(mime)

            pixmap = QPixmap(str(self._image_path)) if self._image_path else QPixmap()
            if pixmap.isNull():
                pixmap = self._image.pixmap() or QPixmap()
            if not pixmap.isNull():
                drag.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))

            result = drag.exec(
                Qt.DropAction.MoveAction | Qt.DropAction.CopyAction,
                Qt.DropAction.MoveAction,
            )
            if result == Qt.DropAction.MoveAction:
                self._clear()
        finally:
            self._on_drag_active_changed(False)

    def dropEvent(self, event: object) -> None:
        if not hasattr(event, "mimeData"):
            return
        mime = event.mimeData()
        if not mime.hasFormat(MIME_TYPE):
            return

        source = event.source() if hasattr(event, "source") else None
        if source is self:
            if hasattr(event, "ignore"):
                event.ignore()
            return
        if (
            not isinstance(source, DropSlot)
            and not isinstance(source, ShopItem)
            and self._char_id is not None
        ):
            return

        raw = bytes(mime.data(MIME_TYPE))
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return

        char_id = str(data.get("char_id", "")).strip()
        display_name = str(data.get("display_name", "")).strip()
        image_raw = str(data.get("image_path", "")).strip()
        image_path = Path(image_raw).expanduser() if image_raw else None
        if not char_id:
            return
        if not self._allows_char_id(char_id):
            return

        plugin = self._plugins_by_id.get(char_id)
        if not display_name:
            display_name = plugin.display_name if plugin else char_id

        chosen_image: Path | None = None
        if image_path and image_path.is_file():
            chosen_image = image_path
        elif plugin:
            chosen_image = plugin.random_image_path(self._rng)

        if isinstance(source, DropSlot) and source is not self:
            if self._char_id is not None:
                if not source._allows_char_id(self._char_id):  # noqa: SLF001
                    return
                previous = (
                    self._char_id,
                    self._display_name or self._char_id,
                    self._image_path,
                    self._stars or 1,
                )
                source._set_character(*previous)  # noqa: SLF001

                stars = plugin.stars if plugin else 1
                self._set_character(char_id, display_name, chosen_image, stars)
                event.setDropAction(Qt.DropAction.CopyAction)
                event.accept()
                return

            stars = plugin.stars if plugin else 1
            self._set_character(char_id, display_name, chosen_image, stars)
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
            return

        if isinstance(source, ShopItem):
            if self._char_id is not None and self._char_id != char_id:
                return
            if not self._allow_stacking and self._char_id is not None:
                return
            target_char_id = self._char_id
            if not self._purchase_character(char_id, self._slot_kind, target_char_id):
                return
            if target_char_id is not None:
                self._refresh()
                event.setDropAction(Qt.DropAction.MoveAction)
                event.accept()
                return

        stars = plugin.stars if plugin else 1
        self._set_character(char_id, display_name, chosen_image, stars)
        event.setDropAction(Qt.DropAction.MoveAction)
        event.accept()

    def _set_character(self, char_id: str, display_name: str, image_path: Path | None, stars: int) -> None:
        self._char_id = char_id
        self._display_name = display_name
        self._image_path = image_path
        self._stars = stars
        self._refresh()
        if not self._suspend_notify:
            self._on_slot_changed(self._slot_id, char_id)

    def _clear(self) -> None:
        self._char_id = None
        self._display_name = None
        self._image_path = None
        self._stars = None
        self._refresh()
        if not self._suspend_notify:
            self._on_slot_changed(self._slot_id, None)

    def _refresh(self) -> None:
        if not self._char_id or not self._display_name:
            self._label.setText(self._empty_label)
            set_pixmap(self._image, None, size=72)
            clear_star_rank_visuals(self._inner)
            self._stack_badge.hide()
            self._placement_badge.hide()
            self._tooltip_html = ""
            self.setToolTip("")
            return

        self._label.setText(self._display_name)
        set_pixmap(self._image, self._image_path, size=72, placeholder=self._display_name)
        apply_star_rank_visuals(self._inner, self._stars or 1)

        stacks = self._get_stack_count(self._char_id)
        primary_stack = self._is_primary_stack_slot(self._slot_id, self._char_id)
        if not self._show_stack_badge or stacks <= 1 or not primary_stack:
            self._stack_badge.hide()
        else:
            self._stack_badge.setText(str(stacks))
            self._stack_badge.show()

        plugin = self._plugins_by_id.get(self._char_id)
        placement = (plugin.placement if plugin else "both").strip().lower()
        self._placement_top.setProperty("filled", placement in {"onsite", "both"})
        self._placement_bottom.setProperty("filled", placement in {"offsite", "both"})
        self._placement_top.style().unpolish(self._placement_top)
        self._placement_top.style().polish(self._placement_top)
        self._placement_bottom.style().unpolish(self._placement_bottom)
        self._placement_bottom.style().polish(self._placement_bottom)
        self._placement_badge.show()

        self._tooltip_html = (
            build_character_stats_tooltip(
                name=self._display_name,
                stars=self._stars or 1,
                stacks=stacks if (self._show_stack_badge and primary_stack) else None,
            )
        )
        self.setToolTip("")

    def refresh_view(self) -> None:
        self._refresh()

    @property
    def char_id(self) -> str | None:
        return self._char_id

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
