from __future__ import annotations


STYLESHEET = """
QFrame#idleCharacterCard {
    border: 1px solid rgba(255, 255, 255, 18);
}

QLabel#idlePortrait {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
}

QLabel#idleCharName {
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
    font-weight: 700;
}

QPushButton#idleActionButton {
    background-color: rgba(255, 255, 255, 14);
    border: 1px solid rgba(255, 255, 255, 20);
    border-radius: 0px;
    padding: 6px 10px;
    color: rgba(255, 255, 255, 230);
    font-size: 12px;
}

QPushButton#idleActionButton:hover {
    background-color: rgba(120, 180, 255, 44);
}

QPushButton#idleActionButton:disabled,
QPushButton#idleRebirthButton:disabled,
QPushButton#idlePrestigeButton:disabled {
    background-color: rgba(255, 255, 255, 7);
    border: 1px solid rgba(255, 255, 255, 12);
    color: rgba(255, 255, 255, 95);
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

QProgressBar#idleExpBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    text-align: center;
}

QProgressBar#idleExpBar::chunk {
    background-color: rgba(52, 152, 219, 170);
}

/* Shard Progress Bar */
QWidget#shardProgressBarWidget {
    background-color: transparent;
    min-height: 18px;
}

QLabel#shardProgressBarLabel {
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    font-weight: 500;
}
""".strip()
