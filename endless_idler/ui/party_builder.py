from __future__ import annotations

import random

from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.save import BAR_SLOTS
from endless_idler.save import DEFAULT_CHARACTER_COST
from endless_idler.save import DEFAULT_RUN_TOKENS
from endless_idler.save import OFFSITE_SLOTS
from endless_idler.save import ONSITE_SLOTS
from endless_idler.save import RunSave
from endless_idler.save import SaveManager
from endless_idler.ui.party_builder_bar import CharacterBar
from endless_idler.ui.party_builder_slot import DropSlot


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
        self.setObjectName("partyBuilderScreen")

        self._rng = random.Random()
        self._root_layout: QVBoxLayout | None = None
        self._plugins = discover_character_plugins()
        self._plugin_by_id = {plugin.char_id: plugin for plugin in self._plugins}
        self._save_manager = SaveManager()
        self._save = self._save_manager.load() or self._new_run_save()
        self._save_manager.save(self._save)
        self._slots_by_id: dict[str, DropSlot] = {}
        self._shop_open = True

        root = QVBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)
        self.setLayout(root)
        self._root_layout = root

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

        self._shop_button = QPushButton("Shop")
        self._shop_button.setObjectName("partyShopButton")
        self._shop_button.setCheckable(True)
        self._shop_button.setChecked(True)
        self._shop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._shop_button.toggled.connect(self._set_shop_open)
        header.addWidget(self._shop_button, 0, Qt.AlignmentFlag.AlignHCenter)

        header.addStretch(1)

        self._token_label = QLabel()
        self._token_label.setObjectName("tokenLabel")
        header.addWidget(self._token_label, 0, Qt.AlignmentFlag.AlignRight)
        self._refresh_tokens()

        self._char_bar: CharacterBar | None = None
        self._maybe_build_char_bar()

        root.addStretch(1)

        grid = QVBoxLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)
        root.addLayout(grid)

        grid.addLayout(self._make_row("OnSite", count=ONSITE_SLOTS, center=True))
        grid.addLayout(self._make_row("Offsite", count=OFFSITE_SLOTS))

        self._load_slots_from_save()

    def _maybe_build_char_bar(self) -> None:
        if not self._shop_open:
            return

        bar = CharacterBar(
            char_ids=self._save.bar,
            plugins_by_id=self._plugin_by_id,
            rng=self._rng,
            on_reroll=self._reroll_shop,
        )

        bar.destroyed.connect(self._on_char_bar_destroyed)
        self._char_bar = bar
        if self._root_layout is not None:
            self._root_layout.insertWidget(1, bar, 0, Qt.AlignmentFlag.AlignHCenter)

    def _on_char_bar_destroyed(self) -> None:
        self._char_bar = None
        self._shop_button.setChecked(False)

    def _set_shop_open(self, open_: bool) -> None:
        self._shop_open = open_

        if self._char_bar is not None and self._root_layout is not None:
            bar = self._char_bar
            self._root_layout.removeWidget(self._char_bar)
            self._char_bar.hide()
            self._char_bar.setParent(None)
            bar.deleteLater()

        self._char_bar = None

        if open_:
            self._maybe_build_char_bar()

    def _new_run_save(self) -> RunSave:
        bar: list[str] = []
        if self._plugins:
            count = min(BAR_SLOTS, len(self._plugins))
            bar = [plugin.char_id for plugin in self._rng.sample(self._plugins, k=count)]

        return RunSave(tokens=DEFAULT_RUN_TOKENS, bar=bar)

    def _make_row(self, label: str, *, count: int, center: bool = False) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        if center:
            row.addStretch(1)

        for index in range(count):
            slot_id = f"{label.lower()}_{index + 1}"
            slot = DropSlot(
                empty_label=label,
                slot_id=slot_id,
                plugins_by_id=self._plugin_by_id,
                rng=self._rng,
                character_cost=DEFAULT_CHARACTER_COST,
                can_afford=self._can_afford,
                purchase_character=self._purchase_character,
                on_slot_changed=self._on_slot_changed,
            )
            self._slots_by_id[slot_id] = slot
            row.addWidget(slot)

        row.addStretch(1)

        return row

    def _can_afford(self, cost: int) -> bool:
        return self._save.tokens >= cost

    def _purchase_character(self, char_id: str) -> bool:
        if self._save.tokens < DEFAULT_CHARACTER_COST:
            return False
        if char_id not in self._save.bar:
            return False

        self._save.tokens -= DEFAULT_CHARACTER_COST
        self._save.bar = [item for item in self._save.bar if item != char_id]
        self._refresh_tokens()
        self._save_manager.save(self._save)
        return True

    def _reroll_shop(self) -> None:
        occupied = {item for item in (self._save.onsite + self._save.offsite) if item}
        candidates = [plugin.char_id for plugin in self._plugins if plugin.char_id not in occupied]
        if not candidates:
            self._save.bar = []
        else:
            count = min(BAR_SLOTS, len(candidates))
            self._save.bar = [plugin_id for plugin_id in self._rng.sample(candidates, k=count)]

        self._save_manager.save(self._save)
        if self._char_bar is not None:
            self._char_bar.set_char_ids(self._save.bar)

    def _on_slot_changed(self, slot_id: str, char_id: str | None) -> None:
        prefix, index_raw = slot_id.split("_", 1)
        try:
            index = int(index_raw) - 1
        except ValueError:
            return

        if prefix == "onsite" and 0 <= index < len(self._save.onsite):
            self._save.onsite[index] = char_id
        elif prefix == "offsite" and 0 <= index < len(self._save.offsite):
            self._save.offsite[index] = char_id
        else:
            return

        self._save_manager.save(self._save)

    def _load_slots_from_save(self) -> None:
        for index, char_id in enumerate(self._save.onsite):
            slot = self._slots_by_id.get(f"onsite_{index + 1}")
            if slot:
                slot.load_char_id(char_id)

        for index, char_id in enumerate(self._save.offsite):
            slot = self._slots_by_id.get(f"offsite_{index + 1}")
            if slot:
                slot.load_char_id(char_id)

    def _refresh_tokens(self) -> None:
        self._token_label.setText(f"Tokens: {self._save.tokens} (Cost: {DEFAULT_CHARACTER_COST})")
