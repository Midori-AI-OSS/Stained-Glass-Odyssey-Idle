from __future__ import annotations

from PySide6.QtCore import QEvent
from PySide6.QtCore import QObject
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QResizeEvent
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from shiboken6 import isValid

from endless_idler.inventory.presentation import build_owned_inventory_items
from endless_idler.run_save_store import RunSaveStore
from endless_idler.ui.components.inventory_slot import InventorySlot


class InventoryPage(QWidget):
    """Inventory page with owned-items grid and item detail panel."""

    _DESKTOP_COLUMNS = 6

    def __init__(
        self,
        *,
        save_store: RunSaveStore,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._save_store = save_store
        self.setObjectName("InventoryPageRoot")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        panel = QFrame(self)
        panel.setObjectName("InventoryPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.setSpacing(10)
        root.addWidget(panel, 1)

        body = QWidget(panel)
        body_row = QHBoxLayout(body)
        body_row.setContentsMargins(0, 0, 0, 0)
        body_row.setSpacing(10)
        panel_layout.addWidget(body, 1)

        collection_panel = QFrame(body)
        collection_panel.setObjectName("InventoryCollectionPanel")
        collection_col = QVBoxLayout(collection_panel)
        collection_col.setContentsMargins(8, 8, 8, 8)
        collection_col.setSpacing(8)
        body_row.addWidget(collection_panel, 1)

        self._content_stack = QStackedWidget(collection_panel)
        self._content_stack.setObjectName("InventoryContentStack")
        collection_col.addWidget(self._content_stack, 1)

        empty_state = QFrame(self._content_stack)
        empty_state.setObjectName("InventoryEmptyState")
        empty_col = QVBoxLayout(empty_state)
        empty_col.setContentsMargins(24, 24, 24, 24)
        empty_col.setSpacing(6)
        empty_col.addStretch(1)
        empty_title = QLabel("Inventory is currently empty", empty_state)
        empty_title.setObjectName("InventoryEmptyTitle")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_col.addWidget(empty_title, 0)
        empty_note = QLabel(
            "Collect shard drops and materials during idle runs to populate your stash.",
            empty_state,
        )
        empty_note.setObjectName("InventoryEmptyNote")
        empty_note.setWordWrap(True)
        empty_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_col.addWidget(empty_note, 0)
        empty_col.addStretch(1)
        self._content_stack.addWidget(empty_state)

        scroll = QScrollArea(collection_panel)
        scroll.setObjectName("InventoryScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._content_stack.addWidget(scroll)

        grid_host = QWidget(scroll)
        grid_host.setObjectName("InventoryGridHost")
        self._grid = QGridLayout(grid_host)
        self._grid.setContentsMargins(6, 6, 6, 6)
        self._grid.setHorizontalSpacing(10)
        self._grid.setVerticalSpacing(10)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(grid_host)
        self._grid_host = grid_host

        detail = QFrame(body)
        detail.setObjectName("InventoryDetailPanel")
        detail.setFixedWidth(286)
        detail_col = QVBoxLayout(detail)
        detail_col.setContentsMargins(12, 12, 12, 12)
        detail_col.setSpacing(8)
        body_row.addWidget(detail, 0)

        self._detail_title = QLabel("No item selected", detail)
        self._detail_title.setObjectName("InventoryDetailTitle")
        self._detail_title.setWordWrap(True)
        detail_col.addWidget(self._detail_title, 0)

        detail_icon_frame = QFrame(detail)
        detail_icon_frame.setObjectName("InventoryDetailArt")
        detail_icon_frame.setMinimumHeight(220)
        detail_icon_col = QVBoxLayout(detail_icon_frame)
        detail_icon_col.setContentsMargins(8, 8, 8, 8)
        detail_icon_col.setSpacing(0)
        self._detail_icon_frame = detail_icon_frame
        self._detail_icon = QLabel(detail_icon_frame)
        self._detail_icon.setObjectName("InventoryDetailIcon")
        self._detail_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detail_icon_col.addWidget(self._detail_icon, 1)
        self._detail_icon.installEventFilter(self)
        self._detail_icon_frame.installEventFilter(self)
        detail_col.addWidget(detail_icon_frame, 0)

        self._detail_hint = QLabel("Select a card to view its lore entry.", detail)
        self._detail_hint.setObjectName("InventoryDetailHint")
        self._detail_hint.setWordWrap(True)
        detail_col.addWidget(self._detail_hint, 0)
        detail_col.addStretch(1)

        self._slots: list[InventorySlot] = []
        self._selected_slot: InventorySlot | None = None
        self._detail_source_pixmap: QPixmap | None = None
        self._pending_detail_refresh = False

        self.refresh_from_save()

    def refresh_from_save(self) -> None:
        self._selected_slot = None
        self._slots.clear()
        while self._grid.count() > 0:
            layout_item = self._grid.takeAt(0)
            widget = layout_item.widget() if layout_item else None
            if widget is not None:
                widget.deleteLater()

        owned_items = build_owned_inventory_items(self._save_store.current.inventory)
        if not owned_items:
            self._content_stack.setCurrentIndex(0)
            self._set_detail_item(None)
            return

        self._content_stack.setCurrentIndex(1)
        for index, owned_item in enumerate(owned_items):
            slot = InventorySlot(
                item_id=owned_item.item_id,
                item_name=owned_item.name,
                category_label=owned_item.category_label,
                rarity_label=owned_item.rarity_label,
                flavor_text=owned_item.flavor_text,
                icon_path=owned_item.icon_path,
                quantity=owned_item.quantity,
                rarity_stars=owned_item.rarity_stars,
                parent=self._grid_host,
            )
            slot.selected.connect(self._on_slot_selected)
            row = index // self._DESKTOP_COLUMNS
            column = index % self._DESKTOP_COLUMNS
            self._grid.addWidget(slot, row, column)
            self._slots.append(slot)

        self._select_slot(self._slots[0])

    def _on_slot_selected(self) -> None:
        slot = self.sender()
        if isinstance(slot, InventorySlot):
            self._select_slot(slot)

    def _select_slot(self, slot: InventorySlot) -> None:
        self._selected_slot = slot
        for candidate in self._slots:
            candidate.set_selected(candidate is slot)
        slot.setFocus(Qt.FocusReason.MouseFocusReason)
        self._set_detail_item(slot)

    def _set_detail_item(self, slot: InventorySlot | None) -> None:
        if slot is None:
            self._detail_title.setText("No item selected")
            self._detail_source_pixmap = None
            self._detail_icon.clear()
            self._detail_hint.setText(
                "Collect shard drops and materials to fill your inventory."
            )
            return

        self._detail_title.setText(slot.item_name)
        pixmap = QPixmap(str(slot.icon_path))
        if pixmap.isNull():
            raise ValueError(f"Failed to load inventory icon at {slot.icon_path}.")
        self._detail_source_pixmap = pixmap
        self._schedule_detail_icon_refresh()
        self._detail_hint.setText(slot.flavor_text)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._schedule_detail_icon_refresh()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._schedule_detail_icon_refresh()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched in (self._detail_icon, self._detail_icon_frame) and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.Show,
            QEvent.Type.LayoutRequest,
        ):
            self._schedule_detail_icon_refresh()
        return False

    def _refresh_detail_icon_pixmap(self) -> None:
        if not isValid(self._detail_icon) or not isValid(self._detail_icon_frame):
            return
        if self._detail_source_pixmap is None:
            self._detail_icon.clear()
            return

        target = self._detail_icon.contentsRect().size()
        if target.width() <= 0 or target.height() <= 0:
            target = self._detail_icon_frame.contentsRect().size()
        if target.width() <= 0 or target.height() <= 0:
            return

        self._detail_icon.setPixmap(
            self._detail_source_pixmap.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _schedule_detail_icon_refresh(self) -> None:
        if self._pending_detail_refresh:
            return
        self._pending_detail_refresh = True
        QTimer.singleShot(0, self._apply_scheduled_detail_refresh)

    def _apply_scheduled_detail_refresh(self) -> None:
        self._pending_detail_refresh = False
        if not isValid(self):
            return
        self._refresh_detail_icon_pixmap()
