from __future__ import annotations

import json
import random

from pathlib import Path

from PySide6.QtCore import QByteArray
from PySide6.QtCore import Qt
from PySide6.QtCore import QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.characters.plugins import default_character_roots
from endless_idler.characters.plugins import discover_character_plugins


_MIME_TYPE = "application/x-endless-idler-character"


class PartyBuilderWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Party Builder")
        self.resize(1100, 650)

        self.setCentralWidget(PartyBuilderWidget())


class PartyBuilderWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        rng = random.Random()
        plugins = discover_character_plugins(roots=default_character_roots())

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)
        self.setLayout(root)

        char_bar = CharacterBar(plugins=plugins, rng=rng)
        root.addWidget(char_bar)

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
            slot = DropSlot(empty_label=label, slot_id=f"{label.lower()}_{index + 1}")
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
    def __init__(self, *, plugin: CharacterPlugin, image_path: Path) -> None:
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
        _set_pixmap(self._image, self._image_path, size=72)
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
                "image_path": str(self._image_path),
            }
        ).encode("utf-8")
        mime.setData(_MIME_TYPE, QByteArray(payload))

        drag = QDrag(self)
        drag.setMimeData(mime)

        pixmap = QPixmap(str(self._image_path))
        if not pixmap.isNull():
            drag.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))

        drag.exec(Qt.DropAction.CopyAction)


class DropSlot(QFrame):
    def __init__(self, *, empty_label: str, slot_id: str) -> None:
        super().__init__()
        self.setObjectName("dropSlot")
        self.setAcceptDrops(True)

        self._slot_id = slot_id
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

    def dragEnterEvent(self, event: object) -> None:
        if not hasattr(event, "mimeData"):
            return
        mime = event.mimeData()
        if mime.hasFormat(_MIME_TYPE):
            event.acceptProposedAction()

    def dropEvent(self, event: object) -> None:
        if not hasattr(event, "mimeData"):
            return
        mime = event.mimeData()
        if not mime.hasFormat(_MIME_TYPE):
            return

        raw = bytes(mime.data(_MIME_TYPE))
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return

        char_id = str(data.get("char_id", "")).strip()
        display_name = str(data.get("display_name", "")).strip()
        image_path = Path(str(data.get("image_path", ""))).expanduser()
        if not char_id or not display_name or not image_path.is_file():
            return

        self._char_id = char_id
        self._display_name = display_name
        self._image_path = image_path
        self._label.setText(display_name)
        _set_pixmap(self._image, image_path, size=72)
        event.acceptProposedAction()


def _set_pixmap(label: QLabel, path: Path, *, size: int) -> None:
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
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
