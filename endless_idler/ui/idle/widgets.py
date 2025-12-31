from __future__ import annotations

import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


class IdleArena(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("idleArena")


class IdleCharacterCard(QFrame):
    def __init__(
        self,
        *,
        char_id: str,
        plugin: object,
        idle_state: object,
        rng: random.Random,
        stack_count: int,
    ) -> None:
        super().__init__()
        self.setObjectName("idleCharacterCard")
        self._char_id = char_id
        self._plugin = plugin
        self._idle_state = idle_state
        self._rng = rng
        self._stack_count = stack_count

        self.setFixedSize(420, 180)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        self.setLayout(layout)

        self._portrait = QLabel()
        self._portrait.setObjectName("idlePortrait")
        self._portrait.setFixedSize(128, 156)
        self._portrait.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._portrait.setScaledContents(False)

        portrait_path = plugin.random_image_path(rng) if plugin else None
        if portrait_path:
            pixmap = QPixmap(str(portrait_path))
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    128,
                    156,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._portrait.setPixmap(scaled)
        layout.addWidget(self._portrait, 0, Qt.AlignmentFlag.AlignVCenter)

        info_column = QVBoxLayout()
        info_column.setSpacing(6)
        info_column.setContentsMargins(0, 0, 0, 0)

        display_name = getattr(plugin, "display_name", char_id) if plugin else char_id
        self._name_label = QLabel(display_name)
        self._name_label.setObjectName("idleCharName")
        info_column.addWidget(self._name_label)

        self._level_label = QLabel("Level: 1")
        self._level_label.setObjectName("idleCharLevel")
        info_column.addWidget(self._level_label)

        self._stack_label = QLabel(f"Stack: {stack_count}")
        self._stack_label.setObjectName("idleCharStack")
        info_column.addWidget(self._stack_label)

        self._exp_bar = QProgressBar()
        self._exp_bar.setObjectName("idleExpBar")
        self._exp_bar.setFixedHeight(12)
        self._exp_bar.setTextVisible(False)
        self._exp_bar.setRange(0, 30)
        self._exp_bar.setValue(0)
        info_column.addWidget(self._exp_bar)

        self._exp_label = QLabel("EXP: 0 / 30")
        self._exp_label.setObjectName("idleExpLabel")
        info_column.addWidget(self._exp_label)

        self._hp_bar = QProgressBar()
        self._hp_bar.setObjectName("idleHpBar")
        self._hp_bar.setFixedHeight(12)
        self._hp_bar.setTextVisible(False)
        self._hp_bar.setRange(0, 1000)
        self._hp_bar.setValue(1000)
        info_column.addWidget(self._hp_bar)

        self._hp_label = QLabel("HP: 1000 / 1000")
        self._hp_label.setObjectName("idleHpLabel")
        info_column.addWidget(self._hp_label)

        info_column.addStretch(1)
        layout.addLayout(info_column, 1)

    def update_display(self) -> None:
        data = self._idle_state.get_char_data(self._char_id)
        if not data:
            return

        level = int(data.get("level", 1))
        exp = float(data.get("exp", 0))
        next_exp = float(data.get("next_exp", 30))
        hp = float(data.get("hp", 0))
        max_hp = float(data.get("max_hp", 1000))

        self._level_label.setText(f"Level: {level}")
        self._exp_label.setText(f"EXP: {int(exp)} / {int(next_exp)}")
        self._hp_label.setText(f"HP: {int(hp)} / {int(max_hp)}")

        self._exp_bar.setRange(0, max(1, int(next_exp)))
        self._exp_bar.setValue(int(exp))

        self._hp_bar.setRange(0, max(1, int(max_hp)))
        self._hp_bar.setValue(int(hp))
