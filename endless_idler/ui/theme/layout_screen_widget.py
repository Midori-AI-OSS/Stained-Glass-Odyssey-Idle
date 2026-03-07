from __future__ import annotations


STYLESHEET = """
QWidget#LayoutScreen {
    background-color: rgba(0, 0, 0, 180);
}

QFrame#LayoutHeader,
QFrame#LayoutLanesPanel,
QFrame#LayoutUnassignedPanel,
QFrame#LayoutControlsPanel {
    background-color: rgba(18, 20, 28, 145);
    border: 1px solid rgba(255, 255, 255, 18);
}

QLabel#LayoutTitle {
    color: rgba(255, 255, 255, 240);
    font-size: 20px;
    font-weight: 700;
}

QLabel#LayoutSubtitle,
QLabel#LayoutUnassignedEmpty,
QLabel#LayoutSaveStatus {
    color: rgba(255, 255, 255, 170);
    font-size: 12px;
}

QLabel#LayoutLaneTitle,
QLabel#LayoutControlLabel,
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
    border-color: rgba(56, 189, 248, 110);
    background-color: rgba(24, 42, 68, 145);
}

QLabel#LayoutSlotTitle {
    color: rgba(255, 255, 255, 185);
    font-size: 11px;
    font-weight: 650;
}

QLabel#LayoutSlotPlaceholder {
    color: rgba(255, 255, 255, 145);
    font-size: 11px;
}

QFrame#LayoutCharacterChip {
    background-color: rgba(20, 24, 36, 170);
    border: 1px solid rgba(255, 255, 255, 24);
}

QFrame#LayoutCharacterChip[layoutChipRole="assigned"] {
    border-color: rgba(56, 189, 248, 110);
}

QLabel#LayoutCharacterName {
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
    font-weight: 620;
}

QLabel#LayoutCharacterStars {
    color: rgba(255, 214, 102, 235);
    font-size: 11px;
    font-weight: 700;
}

QComboBox#LayoutOrderCombo {
    color: rgba(255, 255, 255, 235);
    background-color: rgba(18, 20, 28, 135);
    border: 1px solid rgba(255, 255, 255, 28);
    padding: 6px 8px;
}

QComboBox#LayoutOrderCombo:hover {
    border-color: rgba(56, 189, 248, 90);
}
""".strip()
