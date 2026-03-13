from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent
from PySide6.QtCore import QObject
from PySide6.QtCore import QSize
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QResizeEvent
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from shiboken6 import isValid


class InventorySlot(QFrame):
    """Inventory card widget with icon, metadata, and selection state."""

    selected = Signal()

    def __init__(
        self,
        *,
        item_id: str,
        item_name: str,
        category_label: str,
        rarity_label: str,
        flavor_text: str,
        icon_path: Path,
        quantity: int,
        rarity_stars: int = 1,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._item_id = item_id
        self._item_name = item_name
        self._category_label = category_label
        self._rarity_label = rarity_label
        self._flavor_text = flavor_text
        self._quantity = max(1, int(quantity))
        self._icon_path = icon_path
        self._source_pixmap: QPixmap | None = None
        self._pending_icon_refresh = False

        self.setObjectName("InventorySlot")
        self.setProperty("rarityStars", 1)
        self.setProperty("slotSelected", False)
        self.setProperty("slotFilled", True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(156, 202)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        header = QWidget(self)
        header.setObjectName("InventorySlotHeader")
        header_row = QHBoxLayout(header)
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(6)

        header_row.addStretch(1)

        self._category_badge = QLabel(header)
        self._category_badge.setObjectName("InventorySlotCategoryBadge")
        header_row.addWidget(self._category_badge, 0)
        root.addWidget(header, 0)

        self._art = QFrame(self)
        self._art.setObjectName("InventorySlotArt")
        art_layout = QVBoxLayout(self._art)
        art_layout.setContentsMargins(6, 6, 6, 6)
        art_layout.setSpacing(0)

        self._icon = QLabel(self._art)
        self._icon.setObjectName("InventorySlotIcon")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        art_layout.addWidget(self._icon, 1)
        root.addWidget(self._art, 1)
        self._icon.installEventFilter(self)
        self._art.installEventFilter(self)

        self._name = QLabel(self)
        self._name.setObjectName("InventorySlotName")
        self._name.setWordWrap(True)
        self._name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._name, 0)

        footer = QWidget(self)
        footer.setObjectName("InventorySlotFooter")
        footer_row = QHBoxLayout(footer)
        footer_row.setContentsMargins(0, 0, 0, 0)
        footer_row.setSpacing(6)

        pip_row = QWidget(footer)
        self._pip_layout = QHBoxLayout(pip_row)
        self._pip_layout.setContentsMargins(0, 0, 0, 0)
        self._pip_layout.setSpacing(3)
        footer_row.addWidget(pip_row, 1)

        self._count = QLabel(footer)
        self._count.setObjectName("InventorySlotCount")
        self._count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_row.addWidget(self._count, 0)
        root.addWidget(footer, 0)

        self.set_rarity_stars(rarity_stars)
        self._name.setText(item_name)
        self._category_badge.setText(category_label)
        self.set_item(icon_path=icon_path, quantity=quantity)

    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def item_name(self) -> str:
        return self._item_name

    @property
    def category_label(self) -> str:
        return self._category_label

    @property
    def rarity_label(self) -> str:
        return self._rarity_label

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def flavor_text(self) -> str:
        return self._flavor_text

    @property
    def rarity_stars(self) -> int:
        value = self.property("rarityStars")
        if isinstance(value, int):
            return value
        return 1

    @property
    def icon_path(self) -> Path:
        return self._icon_path

    def set_rarity_stars(self, stars: int) -> None:
        normalized = max(1, min(12, int(stars)))
        self.setProperty("rarityStars", normalized)
        _repolish(self)
        self._render_pips(normalized)

    def set_filled(self, filled: bool) -> None:
        self.setProperty("slotFilled", bool(filled))
        _repolish(self)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("slotSelected", bool(selected))
        _repolish(self)

    def set_item(self, *, icon_path: Path, quantity: int) -> None:
        self._icon_path = icon_path
        self._quantity = max(1, int(quantity))
        pixmap = QPixmap(str(icon_path))
        if pixmap.isNull():
            raise ValueError(f"Failed to load inventory icon at {icon_path}.")
        self._source_pixmap = pixmap
        self._schedule_icon_refresh()
        self._count.setText(f"x{self._quantity}")
        self.set_filled(True)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._schedule_icon_refresh()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._schedule_icon_refresh()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched in (self._icon, self._art) and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.Show,
            QEvent.Type.LayoutRequest,
        ):
            self._schedule_icon_refresh()
        return False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.selected.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def _render_pips(self, stars: int) -> None:
        while self._pip_layout.count() > 0:
            layout_item = self._pip_layout.takeAt(0)
            widget = layout_item.widget() if layout_item else None
            if widget is not None:
                widget.deleteLater()
        shown = min(stars, 8)
        for _ in range(shown):
            pip = QFrame(self)
            pip.setObjectName("InventoryStarPip")
            pip.setFixedSize(7, 7)
            self._pip_layout.addWidget(pip)
        self._pip_layout.addStretch(1)

    def _refresh_icon_pixmap(self) -> None:
        if not isValid(self._icon) or not isValid(self._art):
            return
        if self._source_pixmap is None:
            self._icon.clear()
            return

        available = self._icon.contentsRect().size()
        if available.width() <= 0 or available.height() <= 0:
            available = self._art.contentsRect().size()

        side = min(available.width(), available.height())
        if side <= 0:
            return

        target = QSize(side, side)

        self._icon.setPixmap(
            self._source_pixmap.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _schedule_icon_refresh(self) -> None:
        if self._pending_icon_refresh:
            return
        self._pending_icon_refresh = True
        QTimer.singleShot(0, self._apply_scheduled_icon_refresh)

    def _apply_scheduled_icon_refresh(self) -> None:
        self._pending_icon_refresh = False
        if not isValid(self):
            return
        self._refresh_icon_pixmap()


def _repolish(widget: QWidget) -> None:
    style = widget.style()
    if style is None:
        return
    style.unpolish(widget)
    style.polish(widget)
    widget.update()
