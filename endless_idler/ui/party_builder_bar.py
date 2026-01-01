from __future__ import annotations

import json
import random
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QByteArray, QMimeData, Qt
from PySide6.QtGui import QDrag, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)
from shiboken6 import isValid

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.ui.party_builder_common import (
    MIME_TYPE,
    apply_star_rank_visuals,
    build_character_stats_tooltip,
    derive_display_name,
    sanitize_stars,
    set_pixmap,
)
from endless_idler.ui.tooltip import hide_stained_tooltip, show_stained_tooltip


class CharacterBar(QFrame):
    def __init__(
        self,
        *,
        char_ids: list[str | None],
        plugins_by_id: dict[str, CharacterPlugin],
        rng: random.Random,
        on_reroll: Callable[[], None],
        get_stack_count: Callable[[str], int],
        character_cost: int,
        can_afford: Callable[[int], bool],
        on_insufficient_funds: Callable[[], None],
    ) -> None:
        super().__init__()
        self.setObjectName("characterBar")
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self._plugins_by_id = plugins_by_id
        self._rng = rng
        self._get_stack_count = get_stack_count
        self._character_cost = max(0, int(character_cost))
        self._can_afford = can_afford
        self._on_insufficient_funds = on_insufficient_funds

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(12)
        top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(top)

        self._slots: list[ShopSlot] = []
        for index in range(6):
            slot = ShopSlot()
            self._slots.append(slot)
            top.addWidget(slot)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(8)
        layout.addLayout(footer)
        footer.addStretch(1)

        reroll = QPushButton("Reroll")
        reroll.setObjectName("partyRerollButton")
        reroll.setCursor(Qt.CursorShape.PointingHandCursor)
        reroll.clicked.connect(on_reroll)
        footer.addWidget(reroll, 0, Qt.AlignmentFlag.AlignRight)

        self.set_char_ids(char_ids)

    def has_tiles(self) -> bool:
        return any(slot.char_id is not None for slot in self._slots)

    def set_char_ids(self, char_ids: list[str | None]) -> None:
        for index, slot in enumerate(self._slots):
            char_id = char_ids[index] if index < len(char_ids) else None
            if not char_id:
                slot.clear()
                continue

            plugin = self._plugins_by_id.get(char_id)
            display_name = (
                plugin.display_name if plugin else derive_display_name(char_id)
            )
            image_path = plugin.random_image_path(self._rng) if plugin else None
            stars = sanitize_stars(plugin.stars if plugin else 1)
            placement = (plugin.placement if plugin else "both").strip().lower()
            stacks = self._get_stack_count(char_id)
            slot.set_character(
                char_id=char_id,
                display_name=display_name,
                image_path=image_path,
                stars=stars,
                placement=placement,
                stack_count=stacks,
                character_cost=self._character_cost,
                can_afford=self._can_afford,
                on_insufficient_funds=self._on_insufficient_funds,
            )

    def clear_char_id(self, char_id: str) -> None:
        for slot in self._slots:
            if slot.char_id == char_id:
                slot.clear()
                return

    def refresh_stack_badges(self) -> None:
        for slot in self._slots:
            item = slot._item  # noqa: SLF001
            if item is None or not isValid(item):
                continue
            item.set_stack_count(self._get_stack_count(item.char_id))


class ShopSlot(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("characterTile")
        self.setFixedSize(130, 150)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        self.setLayout(layout)

        self._placeholder = QLabel("Empty")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setObjectName("shopSlotPlaceholder")
        layout.addWidget(self._placeholder)

        self._item: ShopItem | None = None

    @property
    def char_id(self) -> str | None:
        return self._item.char_id if self._item else None

    def clear(self) -> None:
        if self._item is None:
            self._placeholder.show()
            return

        item = self._item
        self._item = None
        if not isValid(item):
            self._placeholder.show()
            return
        layout = self.layout()
        if layout is not None:
            try:
                layout.removeWidget(item)  # type: ignore[union-attr]
            except RuntimeError:
                pass
        try:
            item.setParent(None)
        except RuntimeError:
            pass
        try:
            item.deleteLater()
        except RuntimeError:
            pass
        self._placeholder.show()

    def set_character(
        self,
        *,
        char_id: str,
        display_name: str,
        image_path: Path | None,
        stars: int,
        placement: str,
        stack_count: int,
        character_cost: int,
        can_afford: Callable[[int], bool],
        on_insufficient_funds: Callable[[], None],
    ) -> None:
        self.clear()

        self._placeholder.hide()
        item = ShopItem(
            char_id=char_id,
            display_name=display_name,
            image_path=image_path,
            stars=stars,
            placement=placement,
            stack_count=stack_count,
            character_cost=character_cost,
            can_afford=can_afford,
            on_insufficient_funds=on_insufficient_funds,
        )
        item.destroyed.connect(self._on_item_destroyed)
        self._item = item
        self.layout().addWidget(item)  # type: ignore[union-attr]

    def _on_item_destroyed(self, _obj: object | None = None) -> None:
        sender = self.sender()
        if self._item is not None and sender is not None and sender is not self._item:
            return
        self._item = None
        self._placeholder.show()


class ShopItem(QFrame):
    def __init__(
        self,
        *,
        char_id: str,
        display_name: str,
        image_path: Path | None,
        stars: int,
        placement: str,
        stack_count: int,
        character_cost: int,
        can_afford: Callable[[int], bool],
        on_insufficient_funds: Callable[[], None],
    ) -> None:
        super().__init__()
        self.setObjectName("characterTileInner")
        self._char_id = char_id
        self._display_name = display_name
        self._image_path = image_path
        self._stars = sanitize_stars(stars)
        self._placement = placement.strip().lower()
        self._stack_count = max(0, int(stack_count))
        self._character_cost = max(0, int(character_cost))
        self._can_afford = can_afford
        self._on_insufficient_funds = on_insufficient_funds
        self._tooltip_html = ""

        apply_star_rank_visuals(self, self._stars)

        layout = QGridLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self.setLayout(layout)

        self._image = QLabel()
        self._image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._image.setFixedSize(72, 72)
        set_pixmap(
            self._image, self._image_path, size=72, placeholder=self._display_name
        )
        layout.addWidget(self._image, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self._stack_badge = QLabel()
        self._stack_badge.setObjectName("shopStackableBadge")
        self._stack_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stack_badge.setMinimumSize(20, 18)
        layout.addWidget(
            self._stack_badge,
            0,
            0,
            1,
            1,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )

        placement_badge = QFrame()
        placement_badge.setObjectName("placementBadge")
        placement_badge.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        placement_layout = QVBoxLayout()
        placement_layout.setContentsMargins(3, 3, 3, 3)
        placement_layout.setSpacing(2)
        placement_badge.setLayout(placement_layout)

        self._placement_top = QFrame()
        self._placement_top.setObjectName("placementSquare")
        self._placement_top.setFixedSize(10, 10)
        self._placement_top.setProperty("filled", False)
        placement_layout.addWidget(self._placement_top, 0, Qt.AlignmentFlag.AlignRight)

        self._placement_bottom = QFrame()
        self._placement_bottom.setObjectName("placementSquare")
        self._placement_bottom.setFixedSize(10, 10)
        self._placement_bottom.setProperty("filled", False)
        placement_layout.addWidget(
            self._placement_bottom, 0, Qt.AlignmentFlag.AlignRight
        )

        layout.addWidget(
            placement_badge,
            0,
            0,
            1,
            1,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )

        name = QLabel(display_name)
        name.setObjectName("characterTileName")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name, 1, 0, 1, 1)

        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._refresh_placement_badge()
        self._refresh_stack_badge()
        self._refresh_tooltip()

    @property
    def char_id(self) -> str:
        return self._char_id

    def set_stack_count(self, stack_count: int) -> None:
        self._stack_count = max(0, int(stack_count))
        self._refresh_stack_badge()
        self._refresh_tooltip()

    def _refresh_placement_badge(self) -> None:
        placement = self._placement
        self._placement_top.setProperty("filled", placement in {"onsite", "both"})
        self._placement_bottom.setProperty("filled", placement in {"offsite", "both"})
        self._placement_top.style().unpolish(self._placement_top)
        self._placement_top.style().polish(self._placement_top)
        self._placement_bottom.style().unpolish(self._placement_bottom)
        self._placement_bottom.style().polish(self._placement_bottom)

    def _refresh_stack_badge(self) -> None:
        if self._stack_count <= 0:
            self._stack_badge.hide()
            return
        self._stack_badge.setText("★")
        self._stack_badge.show()

    def _refresh_tooltip(self) -> None:
        self._tooltip_html = build_character_stats_tooltip(
            name=self._display_name,
            stars=self._stars,
            stackable=self._stack_count > 0,
        )
        self.setToolTip("")

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

    def mousePressEvent(self, event: object) -> None:
        try:
            button = event.button()
        except AttributeError:
            return
        if button != Qt.MouseButton.LeftButton:
            return
        hide_stained_tooltip()
        if not self._can_afford(self._character_cost):
            self._on_insufficient_funds()
            return

        mime = QMimeData()
        payload = json.dumps(
            {
                "char_id": self._char_id,
                "display_name": self._display_name,
                "image_path": str(self._image_path) if self._image_path else "",
            }
        ).encode("utf-8")
        mime.setData(MIME_TYPE, QByteArray(payload))

        drag = QDrag(self)
        drag.setMimeData(mime)

        pixmap = QPixmap(str(self._image_path)) if self._image_path else QPixmap()
        if pixmap.isNull():
            pixmap = self._image.pixmap() or QPixmap()
        if not pixmap.isNull():
            drag.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))

        result = drag.exec(
            Qt.DropAction.MoveAction,
            Qt.DropAction.MoveAction,
        )
        if result == Qt.DropAction.MoveAction:
            self.setParent(None)
            self.deleteLater()
