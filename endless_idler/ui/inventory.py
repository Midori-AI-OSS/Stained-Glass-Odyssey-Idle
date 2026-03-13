from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from endless_idler.inventory import get_all_items
from endless_idler.inventory.presentation import resolve_item_rarity_stars
from endless_idler.ui.components.inventory_slot import InventorySlot


class InventoryPage(QWidget):
    """Desktop-first inventory prototype grid."""

    _DESKTOP_COLUMNS = 8

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("InventoryPageRoot")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        panel = QFrame(self)
        panel.setObjectName("InventoryPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.setSpacing(0)
        root.addWidget(panel, 1)

        scroll = QScrollArea(panel)
        scroll.setObjectName("InventoryScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        panel_layout.addWidget(scroll, 1)

        grid_host = QWidget(scroll)
        grid_host.setObjectName("InventoryGridHost")
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(grid_host)

        item_ids = tuple(sorted(get_all_items().keys()))
        for index, item_id in enumerate(item_ids):
            stars = resolve_item_rarity_stars(item_id)
            slot = InventorySlot(rarity_stars=stars, filled=True, parent=grid_host)
            row = index // self._DESKTOP_COLUMNS
            column = index % self._DESKTOP_COLUMNS
            grid.addWidget(slot, row, column)
