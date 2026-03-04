from __future__ import annotations


STYLESHEET = """
QWidget#idleHubScreen {
    background-color: rgba(0, 0, 0, 180);
}

QFrame#idleHubPanel {
    background-color: rgba(20, 30, 60, 130);
    border: 1px solid rgba(255, 255, 255, 24);
}

QLabel#idleHubTitle {
    color: rgba(255, 255, 255, 245);
    font-size: 20px;
    font-weight: 700;
}

QLabel#idleHubSubtitle {
    color: rgba(255, 255, 255, 180);
    font-size: 12px;
}

QLabel#idleHubInfoLabel {
    color: rgba(255, 255, 255, 220);
    font-size: 13px;
}

QLabel#idleHubNotice {
    color: rgba(170, 220, 255, 235);
    font-size: 12px;
}

QPushButton#idleHubStartButton,
QPushButton#idleHubBackButton {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 24);
    border-radius: 0px;
    padding: 8px 12px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}

QPushButton#idleHubStartButton:hover,
QPushButton#idleHubBackButton:hover {
    background-color: rgba(120, 180, 255, 44);
}
""".strip()
