from __future__ import annotations


STYLESHEET = """
QWidget#InventoryPageRoot {
    background: transparent;
}

QFrame#InventoryPanel {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(18, 20, 28, 0),
        stop: 0.08 rgba(18, 20, 28, 86),
        stop: 0.92 rgba(18, 20, 28, 86),
        stop: 1 rgba(18, 20, 28, 0)
    );
    border: 1px solid rgba(255, 255, 255, 14);
    border-radius: 0px;
}

QFrame#InventoryCollectionPanel,
QFrame#InventoryDetailPanel {
    background-color: rgba(13, 15, 22, 106);
    border: 1px solid rgba(255, 255, 255, 16);
    border-radius: 0px;
}

QStackedWidget#InventoryContentStack {
    background: transparent;
}

QFrame#InventoryEmptyState {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(19, 26, 35, 140),
        stop: 1 rgba(14, 15, 24, 120)
    );
    border: 1px solid rgba(255, 255, 255, 20);
    border-radius: 0px;
}

QLabel#InventoryEmptyTitle {
    color: rgba(242, 246, 253, 235);
    font-size: 15px;
    font-weight: 700;
}

QLabel#InventoryEmptyNote {
    color: rgba(220, 225, 235, 175);
    font-size: 12px;
}

QScrollArea#InventoryScroll,
QWidget#InventoryGridHost {
    background: transparent;
}

QFrame#InventorySlot {
    border: 1px solid rgba(255, 255, 255, 24);
    border-radius: 0px;
    background-color: rgba(18, 20, 28, 120);
}

QFrame#InventorySlot[slotFilled="false"] {
    background-color: rgba(18, 20, 28, 70);
    border-color: rgba(255, 255, 255, 18);
}

QFrame#InventorySlot:hover {
    border: 1px solid rgba(116, 202, 255, 105);
}

QFrame#InventorySlot:focus {
    border: 1px solid rgba(148, 220, 255, 140);
}

QFrame#InventorySlot[slotSelected="true"] {
    border: 1px solid rgba(90, 192, 255, 155);
    background-color: rgba(24, 29, 44, 150);
}

QFrame#InventorySlot[rarityStars="1"] { background-color: rgba(130, 192, 255, 110); }
QFrame#InventorySlot[rarityStars="2"] { background-color: rgba(98, 196, 124, 110); }
QFrame#InventorySlot[rarityStars="3"] { background-color: rgba(155, 110, 232, 115); }
QFrame#InventorySlot[rarityStars="4"] { background-color: rgba(214, 68, 68, 120); }
QFrame#InventorySlot[rarityStars="5"] { background-color: rgba(255, 59, 48, 125); }
QFrame#InventorySlot[rarityStars="6"] { background-color: rgba(255, 215, 0, 125); }
QFrame#InventorySlot[rarityStars="7"] { background-color: rgba(0, 255, 209, 120); }
QFrame#InventorySlot[rarityStars="8"] { background-color: rgba(232, 241, 255, 130); }
QFrame#InventorySlot[rarityStars="9"] { background-color: rgba(232, 241, 255, 130); }
QFrame#InventorySlot[rarityStars="10"] { background-color: rgba(232, 241, 255, 130); }
QFrame#InventorySlot[rarityStars="11"] { background-color: rgba(232, 241, 255, 130); }
QFrame#InventorySlot[rarityStars="12"] { background-color: rgba(232, 241, 255, 130); }

QWidget#InventorySlotHeader,
QWidget#InventorySlotFooter {
    background: transparent;
}

QLabel#InventorySlotCategoryBadge,
QLabel#InventorySlotCount {
    color: rgba(240, 246, 255, 235);
    font-size: 10px;
    font-weight: 720;
    padding: 2px 6px;
    border-radius: 0px;
}

QLabel#InventorySlotCategoryBadge {
    background-color: rgba(255, 255, 255, 12);
    border: 1px solid rgba(255, 255, 255, 22);
    color: rgba(230, 236, 248, 210);
}

QLabel#InventorySlotCount {
    background-color: rgba(17, 22, 34, 132);
    border: 1px solid rgba(255, 255, 255, 24);
}

QFrame#InventorySlotArt {
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(8, 10, 15, 128),
        stop: 1 rgba(255, 255, 255, 16)
    );
}

QLabel#InventorySlotIcon {
    background: transparent;
}

QLabel#InventorySlotName {
    background: transparent;
    color: rgba(245, 247, 252, 235);
    font-size: 12px;
    font-weight: 670;
    min-height: 30px;
}

QFrame#InventoryStarPip {
    border: 1px solid rgba(255, 255, 255, 44);
    border-radius: 3px;
    background-color: rgba(255, 255, 255, 190);
}

QLabel#InventoryDetailTitle {
    color: rgba(245, 247, 252, 240);
    font-size: 16px;
    font-weight: 730;
}

QFrame#InventoryDetailArt {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(25, 31, 44, 138),
        stop: 1 rgba(14, 15, 23, 130)
    );
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
}

QLabel#InventoryDetailIcon {
    background: transparent;
}

QLabel#InventoryDetailHint {
    color: rgba(210, 216, 231, 165);
    font-size: 11px;
}
""".strip()
