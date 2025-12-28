from __future__ import annotations

import json
import random

from pathlib import Path
from typing import Callable

from PySide6.QtCore import QByteArray
from PySide6.QtCore import Qt
from PySide6.QtCore import QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.ui.party_builder_common import apply_star_rank_visuals
from endless_idler.ui.party_builder_common import derive_display_name
from endless_idler.ui.party_builder_common import MIME_TYPE
from endless_idler.ui.party_builder_common import sanitize_stars
from endless_idler.ui.party_builder_common import set_pixmap


class CharacterBar(QFrame):
    def __init__(
        self,
        *,
        char_ids: list[str],
        plugins_by_id: dict[str, CharacterPlugin],
        rng: random.Random,
        on_reroll: Callable[[], None],
    ) -> None:
        super().__init__()
        self.setObjectName("characterBar")
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self._plugins_by_id = plugins_by_id
        self._rng = rng

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

    def set_char_ids(self, char_ids: list[str]) -> None:
        for index, slot in enumerate(self._slots):
            char_id = char_ids[index] if index < len(char_ids) else None
            if not char_id:
                slot.clear()
                continue

            plugin = self._plugins_by_id.get(char_id)
            display_name = plugin.display_name if plugin else derive_display_name(char_id)
            image_path = plugin.random_image_path(self._rng) if plugin else None
            stars = sanitize_stars(plugin.stars if plugin else 1)
            slot.set_character(char_id=char_id, display_name=display_name, image_path=image_path, stars=stars)

    def clear_char_id(self, char_id: str) -> None:
        for slot in self._slots:
            if slot.char_id == char_id:
                slot.clear()
                return


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
        item.setParent(None)
        item.deleteLater()
        self._placeholder.show()

    def set_character(self, *, char_id: str, display_name: str, image_path: Path | None, stars: int) -> None:
        self.clear()

        self._placeholder.hide()
        item = ShopItem(char_id=char_id, display_name=display_name, image_path=image_path, stars=stars)
        item.destroyed.connect(self._on_item_destroyed)
        self._item = item
        self.layout().addWidget(item)  # type: ignore[union-attr]

    def _on_item_destroyed(self) -> None:
        self._item = None
        self._placeholder.show()


class ShopItem(QFrame):
    def __init__(self, *, char_id: str, display_name: str, image_path: Path | None, stars: int) -> None:
        super().__init__()
        self.setObjectName("characterTileInner")
        self._char_id = char_id
        self._display_name = display_name
        self._image_path = image_path
        self._stars = sanitize_stars(stars)

        apply_star_rank_visuals(self, self._stars)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self.setLayout(layout)

        self._image = QLabel()
        self._image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._image.setFixedSize(72, 72)
        set_pixmap(self._image, self._image_path, size=72, placeholder=self._display_name)
        layout.addWidget(self._image, 0, Qt.AlignmentFlag.AlignCenter)

        name = QLabel(display_name)
        name.setObjectName("characterTileName")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)

        self.setCursor(Qt.CursorShape.OpenHandCursor)

    @property
    def char_id(self) -> str:
        return self._char_id

    def mousePressEvent(self, event: object) -> None:
        try:
            button = event.button()
        except AttributeError:
            return
        if button != Qt.MouseButton.LeftButton:
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
