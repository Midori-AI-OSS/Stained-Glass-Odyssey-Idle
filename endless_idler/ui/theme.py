from PySide6.QtWidgets import QApplication

_STAINED_GLASS_STYLESHEET = """
QFrame#mainMenuPanel {
    background-color: rgba(20, 30, 60, 130);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 0px;
}

QPushButton[stainedMenu="true"] {
    background-color: rgba(255, 255, 255, 26);
    border: none;
    border-radius: 0px;
    padding: 10px 14px;
    color: rgba(255, 255, 255, 235);
    font-size: 14px;
    text-align: left;
}

QPushButton[stainedMenu="true"]:hover {
    background-color: rgba(120, 180, 255, 56);
}

QPushButton[stainedMenu="true"]:pressed {
    background-color: rgba(80, 140, 220, 72);
}

QPushButton[stainedMenu="true"]:disabled {
    background-color: rgba(255, 255, 255, 14);
    color: rgba(255, 255, 255, 120);
}

QPushButton#partyBackButton {
    background-color: rgba(255, 255, 255, 20);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 0px;
    padding: 8px 12px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
    text-align: left;
}

QPushButton#partyBackButton:hover {
    background-color: rgba(120, 180, 255, 56);
}

QPushButton#partyBackButton:pressed {
    background-color: rgba(80, 140, 220, 72);
}

QPushButton#partyShopButton {
    background-color: rgba(255, 255, 255, 20);
    border: 1px solid rgba(255, 255, 255, 28);
    border-radius: 0px;
    padding: 8px 16px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}

QPushButton#partyShopButton:hover {
    background-color: rgba(120, 180, 255, 56);
}

QPushButton#partyShopButton:checked {
    background-color: rgba(120, 180, 255, 56);
    border: 1px solid rgba(170, 220, 255, 140);
}

QPushButton#partyResetButton {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    padding: 8px 16px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}

QPushButton#partyResetButton:hover {
    background-color: rgba(255, 80, 80, 44);
}

QPushButton#partyRerollButton {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    padding: 6px 14px;
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
}

QPushButton#partyRerollButton:hover {
    background-color: rgba(120, 180, 255, 44);
}

QWidget#partyBuilderScreen {
    background-color: rgba(0, 0, 0, 170);
}

QFrame#characterBar {
    background-color: rgba(20, 30, 60, 120);
    border: 1px solid rgba(255, 255, 255, 24);
}

QFrame#characterTile {
    background-color: rgba(255, 255, 255, 18);
    border: 1px solid rgba(255, 255, 255, 24);
}

QFrame#characterTileInner {
    background-color: rgba(0, 0, 0, 25);
    border: 2px solid rgba(255, 255, 255, 18);
}

QFrame#characterTileInner[starRank="1"] { border: 2px solid #808080; }
QFrame#characterTileInner[starRank="2"] { border: 2px solid #1E90FF; }
QFrame#characterTileInner[starRank="3"] { border: 2px solid #228B22; }
QFrame#characterTileInner[starRank="4"] { border: 2px solid #800080; }
QFrame#characterTileInner[starRank="5"] { border: 2px solid #FF3B30; }
QFrame#characterTileInner[starRank="6"] { border: 2px solid #FFD700; }

QLabel#shopSlotPlaceholder {
    color: rgba(255, 255, 255, 120);
    font-size: 12px;
}

QLabel#stackBadge {
    background-color: rgba(10, 14, 26, 210);
    border: 1px solid rgba(255, 255, 255, 42);
    color: rgba(255, 255, 255, 235);
    font-size: 11px;
    padding: 0px 4px;
}

QLabel#shopStackableBadge {
    background-color: rgba(10, 14, 26, 210);
    border: 1px solid rgba(255, 255, 255, 42);
    color: #FFD700;
    font-size: 12px;
    padding: 0px 4px;
}

QLabel#characterTileName {
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
}

QFrame#dropSlot {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 20);
}

QFrame#dropSlotInner {
    background-color: rgba(0, 0, 0, 22);
    border: 2px solid rgba(255, 255, 255, 18);
}

QFrame#dropSlotInner[starRank="1"] { border: 2px solid #808080; }
QFrame#dropSlotInner[starRank="2"] { border: 2px solid #1E90FF; }
QFrame#dropSlotInner[starRank="3"] { border: 2px solid #228B22; }
QFrame#dropSlotInner[starRank="4"] { border: 2px solid #800080; }
QFrame#dropSlotInner[starRank="5"] { border: 2px solid #FF3B30; }
QFrame#dropSlotInner[starRank="6"] { border: 2px solid #FFD700; }

QLabel#dropSlotLabel {
    color: rgba(255, 255, 255, 220);
    font-size: 12px;
}

QFrame#sellZone {
    background-color: transparent;
    border: 2px solid transparent;
}

QFrame#sellZone[active="true"] {
    background-color: rgba(255, 59, 48, 38);
    border: 2px solid #FF3B30;
}

QLabel#sellZoneLabel {
    color: rgba(255, 255, 255, 235);
    font-size: 14px;
}

QLabel#tokenLabel {
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}
""".strip()


def apply_stained_glass_theme(app: QApplication) -> None:
    app.setStyleSheet(_STAINED_GLASS_STYLESHEET)
