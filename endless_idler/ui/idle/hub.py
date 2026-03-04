from __future__ import annotations

import random

from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.save import RunSave
from endless_idler.save import SaveManager
from endless_idler.save import new_run_save
from endless_idler.save import sanitize_save_characters
from endless_idler.ui.idle.bootstrap import bootstrap_party
from endless_idler.ui.idle.bootstrap import should_bootstrap_party


class IdleHubWidget(QWidget):
    back_requested = Signal()
    start_requested = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("idleHubScreen")
        self._rng = random.Random()
        self._save_manager = SaveManager()
        self._plugins = discover_character_plugins()
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}
        self._save: RunSave | None = None

        root = QVBoxLayout()
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(root)

        panel = QFrame()
        panel.setObjectName("idleHubPanel")
        panel.setFixedWidth(460)
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.setSpacing(12)
        panel.setLayout(panel_layout)
        root.addWidget(panel, 0, Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Idle Hub")
        title.setObjectName("idleHubTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(title)

        subtitle = QLabel("Focus mode: idle progression only")
        subtitle.setObjectName("idleHubSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(subtitle)

        self._onsite_label = QLabel("Onsite: 0")
        self._onsite_label.setObjectName("idleHubInfoLabel")
        panel_layout.addWidget(self._onsite_label)

        self._offsite_label = QLabel("Offsite: 0")
        self._offsite_label.setObjectName("idleHubInfoLabel")
        panel_layout.addWidget(self._offsite_label)

        self._party_level_label = QLabel("Party Level: 1")
        self._party_level_label.setObjectName("idleHubInfoLabel")
        panel_layout.addWidget(self._party_level_label)

        self._empty_notice = QLabel("")
        self._empty_notice.setObjectName("idleHubNotice")
        self._empty_notice.setWordWrap(True)
        panel_layout.addWidget(self._empty_notice)

        start = QPushButton("Start Idle")
        start.setObjectName("idleHubStartButton")
        start.setCursor(Qt.CursorShape.PointingHandCursor)
        start.clicked.connect(self._start_idle)
        panel_layout.addWidget(start)

        back = QPushButton("Back")
        back.setObjectName("idleHubBackButton")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(self.back_requested.emit)
        panel_layout.addWidget(back)

        self.reload_save()

    def reload_save(self) -> None:
        save = self._save_manager.load() or new_run_save()
        save = sanitize_save_characters(save=save, allowed_char_ids=set(self._plugin_by_id))
        was_empty = should_bootstrap_party(save)
        if was_empty:
            bootstrap_party(save, plugins=self._plugins, rng=self._rng)
        self._save_manager.save(save)
        self._save = save
        self._refresh_labels(was_empty=was_empty)

    def _refresh_labels(self, *, was_empty: bool) -> None:
        if self._save is None:
            return

        onsite = [item for item in self._save.onsite if item]
        offsite = [item for item in self._save.offsite if item]
        self._onsite_label.setText(f"Onsite: {len(onsite)} / {len(self._save.onsite)}")
        self._offsite_label.setText(f"Offsite: {len(offsite)} / {len(self._save.offsite)}")
        self._party_level_label.setText(f"Party Level: {max(1, int(self._save.party_level))}")
        if was_empty:
            self._empty_notice.setText(
                "No active party found. Auto-filled available slots from placement rules."
            )
        else:
            self._empty_notice.setText("")

    def _build_payload(self) -> dict[str, object]:
        if self._save is None:
            return {}

        return {
            "party_level": int(self._save.party_level),
            "onsite": list(self._save.onsite),
            "offsite": list(self._save.offsite),
            "stacks": dict(self._save.stacks),
        }

    def _start_idle(self) -> None:
        self.start_requested.emit(self._build_payload())
