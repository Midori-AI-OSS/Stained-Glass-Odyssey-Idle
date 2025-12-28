from __future__ import annotations

import json
import random

from pathlib import Path

from PySide6.QtCore import QByteArray
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtCore import QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.characters.plugins import discover_character_plugins


_MIME_TYPE = "application/x-endless-idler-character"


class PartyBuilderWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Party Builder")
        self.resize(1100, 650)

        self.setCentralWidget(PartyBuilderWidget())


class PartyBuilderWidget(QWidget):
    back_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._rng = random.Random()
        self._plugins = discover_character_plugins()
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)
        self.setLayout(root)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        root.addLayout(header)

        back = QPushButton("Back")
        back.setObjectName("partyBackButton")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(self.back_requested.emit)
        header.addWidget(back, 0, Qt.AlignmentFlag.AlignLeft)
        header.addStretch(1)

        self._char_bar = CharacterBar(plugins=self._plugins, rng=self._rng)
        root.addWidget(self._char_bar)

        grid = QVBoxLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)
        root.addLayout(grid)

        grid.addLayout(self._make_row("OnSite", count=4))
        grid.addLayout(self._make_row("Offsite", count=10))
        root.addStretch(1)

    def _make_row(self, label: str, *, count: int) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        for index in range(count):
            slot = DropSlot(
                empty_label=label,
                slot_id=f"{label.lower()}_{index + 1}",
                plugins_by_id=self._plugin_by_id,
                rng=self._rng,
            )
            row.addWidget(slot)
        row.addStretch(1)

        return row


class CharacterBar(QFrame):
    def __init__(self, *, plugins: list[CharacterPlugin], rng: random.Random) -> None:
        super().__init__()
        self.setObjectName("characterBar")

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        self.setLayout(layout)

        chosen: list[CharacterPlugin] = []
        if plugins:
            count = min(6, len(plugins))
            chosen = rng.sample(plugins, k=count)

        if not chosen:
            empty = QLabel("No character plugins found.")
            empty.setObjectName("characterBarEmpty")
            layout.addWidget(empty)
            layout.addStretch(1)
            return

        for plugin in chosen:
            image_path = plugin.random_image_path(rng)
            tile = CharacterTile(plugin=plugin, image_path=image_path)
            layout.addWidget(tile)

        layout.addStretch(1)


class CharacterTile(QFrame):
    def __init__(self, *, plugin: CharacterPlugin, image_path: Path | None) -> None:
        super().__init__()
        self.setObjectName("characterTile")
        self._plugin = plugin
        self._image_path = image_path

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        self.setLayout(layout)

        self._image = QLabel()
        self._image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._image.setFixedSize(72, 72)
        _set_pixmap(self._image, self._image_path, size=72, placeholder=self._plugin.display_name)
        layout.addWidget(self._image, 0, Qt.AlignmentFlag.AlignCenter)

        name = QLabel(plugin.display_name)
        name.setObjectName("characterTileName")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)

        self.setCursor(Qt.CursorShape.OpenHandCursor)

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
                "char_id": self._plugin.char_id,
                "display_name": self._plugin.display_name,
                "image_path": str(self._image_path) if self._image_path else "",
            }
        ).encode("utf-8")
        mime.setData(_MIME_TYPE, QByteArray(payload))

        drag = QDrag(self)
        drag.setMimeData(mime)

        pixmap = QPixmap(str(self._image_path)) if self._image_path else _placeholder_pixmap(self._plugin.display_name, size=64)
        if not pixmap.isNull():
            drag.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))

        result = drag.exec(
            Qt.DropAction.MoveAction,
            Qt.DropAction.MoveAction,
        )
        if result == Qt.DropAction.MoveAction:
            self.setParent(None)
            self.deleteLater()


class DropSlot(QFrame):
    def __init__(
        self,
        *,
        empty_label: str,
        slot_id: str,
        plugins_by_id: dict[str, CharacterPlugin],
        rng: random.Random,
    ) -> None:
        super().__init__()
        self.setObjectName("dropSlot")
        self.setAcceptDrops(True)

        self._empty_label = empty_label
        self._slot_id = slot_id
        self._plugins_by_id = plugins_by_id
        self._rng = rng
        self._char_id: str | None = None
        self._display_name: str | None = None
        self._image_path: Path | None = None

        layout = QGridLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self.setLayout(layout)

        self._image = QLabel()
        self._image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image.setMinimumSize(64, 64)
        layout.addWidget(self._image, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel(empty_label)
        self._label.setObjectName("dropSlotLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label, 1, 0, 1, 1)

        self.setFixedSize(110, 130)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def dragEnterEvent(self, event: object) -> None:
        if not hasattr(event, "mimeData"):
            return
        mime = event.mimeData()
        if not mime.hasFormat(_MIME_TYPE):
            return

        source = event.source() if hasattr(event, "source") else None
        if isinstance(source, DropSlot):
            event.acceptProposedAction()
            return

        if self._char_id is None:
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

        mime = QMimeData()
        payload = json.dumps(
            {
                "char_id": self._char_id,
                "display_name": self._display_name,
                "image_path": str(self._image_path) if self._image_path else "",
            }
        ).encode("utf-8")
        mime.setData(_MIME_TYPE, QByteArray(payload))

        drag = QDrag(self)
        drag.setMimeData(mime)

        pixmap = QPixmap(str(self._image_path)) if self._image_path else _placeholder_pixmap(self._display_name, size=64)
        if not pixmap.isNull():
            drag.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))

        result = drag.exec(
            Qt.DropAction.MoveAction | Qt.DropAction.CopyAction,
            Qt.DropAction.MoveAction,
        )
        if result == Qt.DropAction.MoveAction:
            self._clear()

    def dropEvent(self, event: object) -> None:
        if not hasattr(event, "mimeData"):
            return
        mime = event.mimeData()
        if not mime.hasFormat(_MIME_TYPE):
            return

        source = event.source() if hasattr(event, "source") else None
        if not isinstance(source, DropSlot) and self._char_id is not None:
            return

        raw = bytes(mime.data(_MIME_TYPE))
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
                previous = (self._char_id, self._display_name or self._char_id, self._image_path)
                source._set_character(*previous)  # noqa: SLF001
                self._set_character(char_id, display_name, chosen_image)
                event.setDropAction(Qt.DropAction.CopyAction)
                event.accept()
                return

            self._set_character(char_id, display_name, chosen_image)
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
            return

        if self._char_id is not None:
            return

        self._set_character(char_id, display_name, chosen_image)
        event.setDropAction(Qt.DropAction.MoveAction)
        event.accept()

    def _set_character(self, char_id: str, display_name: str, image_path: Path | None) -> None:
        self._char_id = char_id
        self._display_name = display_name
        self._image_path = image_path
        self._label.setText(display_name)
        _set_pixmap(self._image, image_path, size=72, placeholder=display_name)

    def _clear(self) -> None:
        self._char_id = None
        self._display_name = None
        self._image_path = None
        self._label.setText(self._empty_label)
        _set_pixmap(self._image, None, size=72)


def _set_pixmap(
    label: QLabel,
    path: Path | None,
    *,
    size: int,
    placeholder: str | None = None,
) -> None:
    pixmap = QPixmap(str(path)) if path else QPixmap()
    if pixmap.isNull():
        if placeholder:
            label.setPixmap(_placeholder_pixmap(placeholder, size=size))
        else:
            label.clear()
        return
    label.setPixmap(
        pixmap.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    )


def _placeholder_pixmap(text: str, *, size: int) -> QPixmap:
    initials = _initials(text)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.fillRect(pixmap.rect(), Qt.GlobalColor.darkGray)
    painter.setPen(Qt.GlobalColor.white)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, initials)
    painter.end()
    return pixmap


def _initials(text: str) -> str:
    parts = [part for part in text.replace("_", " ").split(" ") if part]
    if not parts:
        return "?"
    return "".join(part[0].upper() for part in parts[:2])
