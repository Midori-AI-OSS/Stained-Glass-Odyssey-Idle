from __future__ import annotations


STYLESHEET = """
QLabel#idleOffsitePortrait {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
}

QLabel#idleOffsiteName {
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
    font-weight: 700;
}

QPushButton#idleRebirthButton,
QPushButton#idlePrestigeButton {
    background-color: rgba(255, 255, 255, 14);
    border: 1px solid rgba(255, 255, 255, 20);
    border-radius: 0px;
    padding: 4px 8px;
    color: rgba(255, 255, 255, 230);
    font-size: 11px;
}

QPushButton#idleRebirthButton:hover,
QPushButton#idlePrestigeButton:hover {
    background-color: rgba(120, 180, 255, 44);
}

QProgressBar#idleExpBar,
QProgressBar#idleHpBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    text-align: center;
}

QProgressBar#idleExpBar::chunk {
    background-color: rgba(52, 152, 219, 170);
}

QProgressBar#idleHpBar::chunk {
    background-color: rgba(46, 204, 113, 165);
}
""".strip()
