from __future__ import annotations


STYLESHEET = """
QWidget#LayoutScreen {
    background-color: rgba(0, 0, 0, 180);
}

QFrame#LayoutLanesPanel {
    background-color: rgba(18, 20, 28, 145);
    border: 1px solid rgba(255, 255, 255, 18);
}

QFrame#LayoutUnassignedPanel {
    background-color: transparent;
    border: 0px;
}

QScrollArea#LayoutUnassignedScroll {
    background-color: transparent;
    border: 0px;
}

QLabel#LayoutLaneTitle,
QLabel#LayoutUnassignedTitle {
    color: rgba(255, 255, 255, 230);
    font-size: 13px;
    font-weight: 660;
}

QFrame#LayoutSlot {
    background-color: rgba(20, 24, 36, 125);
    border: 1px dashed rgba(255, 255, 255, 22);
}

QFrame#LayoutSlot[slotFilled="true"] {
    border-style: solid;
    border-color: rgba(235, 235, 240, 110);
    background-color: rgba(22, 30, 46, 145);
}

QLabel#LayoutSlotPlaceholder {
    color: rgba(255, 255, 255, 145);
    font-size: 11px;
}

QFrame#LayoutStandbySlot {
    background-color: rgba(20, 24, 36, 125);
    border: 1px dashed rgba(255, 255, 255, 22);
}

QLabel#LayoutStandbySlotPlaceholder {
    color: rgba(255, 255, 255, 145);
    font-size: 11px;
    font-weight: 620;
}

QFrame#LayoutCharacterChip {
    background-color: rgba(18, 22, 36, 175);
    border: 0px;
    min-height: 112px;
}

QFrame#LayoutCharacterChip[layoutChipRole="assigned"] {
    background-color: rgba(24, 32, 48, 155);
}

QFrame#LayoutSlot[slotFilled="true"][elementId="fire"] { border-color: rgba(255, 90, 40, 140); }
QFrame#LayoutSlot[slotFilled="true"][elementId="ice"] { border-color: rgba(80, 200, 255, 140); }
QFrame#LayoutSlot[slotFilled="true"][elementId="lightning"] { border-color: rgba(255, 220, 0, 140); }
QFrame#LayoutSlot[slotFilled="true"][elementId="wind"] { border-color: rgba(80, 230, 170, 140); }
QFrame#LayoutSlot[slotFilled="true"][elementId="water"] { border-color: rgba(60, 130, 255, 140); }
QFrame#LayoutSlot[slotFilled="true"][elementId="nature"] { border-color: rgba(80, 200, 120, 140); }
QFrame#LayoutSlot[slotFilled="true"][elementId="arcane"] { border-color: rgba(255, 80, 200, 140); }
QFrame#LayoutSlot[slotFilled="true"][elementId="dark"] { border-color: rgba(165, 145, 190, 140); }
QFrame#LayoutSlot[slotFilled="true"][elementId="light"] { border-color: rgba(255, 220, 120, 140); }
QFrame#LayoutSlot[slotFilled="true"][elementId="physical"] { border-color: rgba(180, 180, 190, 140); }
QFrame#LayoutSlot[slotFilled="true"][elementId="generic"] { border-color: rgba(235, 235, 240, 120); }

QLabel#LayoutCharacterPortrait {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
}

QFrame#LayoutPlacementBadge {
    background-color: rgba(10, 14, 24, 170);
    border: 1px solid rgba(255, 255, 255, 35);
}

QFrame#LayoutPlacementSquare {
    background-color: rgba(10, 14, 24, 170);
    border: 1px solid rgba(255, 255, 255, 42);
}

QFrame#LayoutPlacementSquare[filled="true"] {
    background-color: rgba(255, 255, 255, 215);
    border-color: rgba(255, 255, 255, 235);
}

QFrame#LayoutPlacementSquare[filled="false"] {
    background-color: rgba(255, 255, 255, 48);
    border-color: rgba(255, 255, 255, 96);
}

QLabel#LayoutCharacterName {
    color: rgba(255, 255, 255, 235);
    font-size: 11px;
    font-weight: 680;
}

QLabel#LayoutCharacterStars {
    font-size: 10px;
    font-weight: 700;
}

QLabel#LayoutCharacterStars[starRank="1"] { color: #808080; }
QLabel#LayoutCharacterStars[starRank="2"] { color: #1E90FF; }
QLabel#LayoutCharacterStars[starRank="3"] { color: #228B22; }
QLabel#LayoutCharacterStars[starRank="4"] { color: #800080; }
QLabel#LayoutCharacterStars[starRank="5"] { color: #FF3B30; }
QLabel#LayoutCharacterStars[starRank="6"] { color: #FFD700; }
QLabel#LayoutCharacterStars[starRank="7"] { color: #00FFD1; }

QPushButton#LayoutOrderCycleButton {
    color: rgba(255, 255, 255, 235);
    background-color: rgba(255, 255, 255, 12);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 0px;
    padding: 4px 10px;
    min-width: 120px;
    font-size: 11px;
    font-weight: 620;
}

QPushButton#LayoutOrderCycleButton:hover {
    border-color: rgba(56, 189, 248, 90);
    background-color: rgba(56, 189, 248, 28);
}

QPushButton#LayoutOrderCycleButton[orderMode="save_order"] {
    border-color: rgba(235, 235, 240, 120);
}

QPushButton#LayoutOrderCycleButton[orderMode="rarity_desc"] {
    border-color: rgba(255, 214, 102, 135);
}

QPushButton#LayoutOrderCycleButton[orderMode="alphabetical"] {
    border-color: rgba(160, 220, 255, 135);
}

QPushButton#LayoutOrderCycleButton[orderMode="recent"] {
    border-color: rgba(56, 189, 248, 135);
    background-color: rgba(56, 189, 248, 22);
}
""".strip()
