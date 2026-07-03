from __future__ import annotations


STYLESHEET = """
QWidget#WarpScreenRoot {
    background: transparent;
}

QFrame#WarpBannerPanel {
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

QFrame#WarpResultPanel {
    background-color: rgba(13, 15, 22, 106);
    border: 1px solid rgba(255, 255, 255, 16);
    border-radius: 0px;
}

QPushButton#WarpPullButton {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 50),
        stop: 1 rgba(18, 20, 28, 95)
    );
    border: 1px solid rgba(16, 185, 129, 140);
    border-radius: 0px;
    color: rgba(237, 239, 245, 240);
    font-weight: 700;
    font-size: 14px;
    padding: 12px 24px;
    min-height: 40px;
}

QPushButton#WarpPullButton:hover {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 70),
        stop: 1 rgba(18, 20, 28, 115)
    );
}

QPushButton#WarpPullButton:pressed {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 30),
        stop: 1 rgba(18, 20, 28, 75)
    );
}

QPushButton#WarpPullButton:disabled {
    background-color: rgba(18, 20, 28, 70);
    border: 1px solid rgba(255, 255, 255, 10);
    color: rgba(237, 239, 245, 90);
}

QTabBar {
    background-color: transparent;
}

QTabBar::tab {
    background-color: rgba(18, 20, 28, 135);
    border: 1px solid rgba(255, 255, 255, 18);
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    padding: 8px 12px;
    margin-right: 0px;
    font-weight: 650;
    color: rgba(237, 239, 245, 180);
}

QTabBar::tab:hover {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 24);
}

QTabBar::tab:selected {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 20),
        stop: 1 rgba(18, 20, 28, 75)
    );
    border: 1px solid rgba(16, 185, 129, 140);
    color: rgba(237, 239, 245, 235);
}

QLabel#WarpCostLabel {
    color: rgba(237, 239, 245, 210);
    font-size: 13px;
    font-weight: 650;
}

QLabel#WarpBalanceLabel {
    color: rgba(237, 239, 245, 210);
    font-size: 13px;
    font-weight: 650;
}

QFrame#WarpYoloPrefsPanel {
    background-color: rgba(13, 15, 22, 106);
    border: 1px solid rgba(255, 255, 255, 16);
    border-radius: 0px;
}

QLabel#WarpYoloPrefsHeader {
    color: rgba(237, 239, 245, 235);
    font-size: 14px;
    font-weight: 700;
}

QLabel#WarpYoloPrefsHint {
    color: rgba(210, 216, 231, 165);
    font-size: 11px;
}

QPushButton#WarpYoloPrefButton {
    background-color: rgba(18, 20, 28, 95);
    border: 1px solid rgba(255, 255, 255, 18);
    border-radius: 0px;
    padding: 8px 16px;
    color: rgba(237, 239, 245, 200);
    font-weight: 650;
    font-size: 12px;
}

QPushButton#WarpYoloPrefButton:hover {
    background-color: rgba(255, 255, 255, 12);
    border: 1px solid rgba(255, 255, 255, 30);
}

QPushButton#WarpYoloPrefButton:checked {
    border: 1px solid rgba(16, 185, 129, 140);
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 30),
        stop: 1 rgba(18, 20, 28, 85)
    );
    color: rgba(237, 239, 245, 240);
}

QPushButton#WarpYoloPrefButton:disabled {
    background-color: rgba(18, 20, 28, 50);
    border: 1px solid rgba(255, 255, 255, 8);
    color: rgba(237, 239, 245, 80);
}

QPushButton#WarpYoloPrefButton:checked[damageType="fire"] {
    border-color: rgba(255, 90, 40, 160);
}
QPushButton#WarpYoloPrefButton:checked[damageType="ice"] {
    border-color: rgba(80, 200, 255, 160);
}
QPushButton#WarpYoloPrefButton:checked[damageType="wind"] {
    border-color: rgba(80, 230, 170, 160);
}
QPushButton#WarpYoloPrefButton:checked[damageType="lightning"] {
    border-color: rgba(255, 220, 0, 160);
}
QPushButton#WarpYoloPrefButton:checked[damageType="light"] {
    border-color: rgba(255, 220, 120, 160);
}
QPushButton#WarpYoloPrefButton:checked[damageType="dark"] {
    border-color: rgba(75, 45, 100, 160);
}
""".strip()
