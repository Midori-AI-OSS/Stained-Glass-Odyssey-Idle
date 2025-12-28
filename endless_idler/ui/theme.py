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

QFrame#characterBar {
    background-color: rgba(20, 30, 60, 120);
    border: 1px solid rgba(255, 255, 255, 24);
}

QFrame#characterTile {
    background-color: rgba(255, 255, 255, 18);
    border: 1px solid rgba(255, 255, 255, 24);
}

QLabel#characterTileName {
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
}

QFrame#dropSlot {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 20);
}

QLabel#dropSlotLabel {
    color: rgba(255, 255, 255, 220);
    font-size: 12px;
}
""".strip()


def apply_stained_glass_theme(app: QApplication) -> None:
    app.setStyleSheet(_STAINED_GLASS_STYLESHEET)
