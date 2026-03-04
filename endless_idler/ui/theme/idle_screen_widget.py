from __future__ import annotations


STYLESHEET = """
QWidget#idleScreen {
    background-color: rgba(0, 0, 0, 180);
}

QFrame#idleArena {
    background-color: rgba(10, 14, 26, 140);
    border: 1px solid rgba(255, 255, 255, 18);
}

QPushButton#idleBackButton {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    padding: 8px 16px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}

QPushButton#idleBackButton:hover {
    background-color: rgba(120, 180, 255, 44);
}

QLabel#idleTitle {
    color: rgba(255, 255, 255, 240);
    font-size: 18px;
    font-weight: 700;
}

QFrame#idleModsPanel {
    background-color: rgba(20, 30, 60, 120);
    border: 1px solid rgba(255, 255, 255, 18);
}

QLabel#idleModsTitle,
QLabel#idleRRTitle,
QLabel#idleSharedExpLabel,
QLabel#idleRRLabel {
    color: rgba(255, 255, 255, 235);
    font-size: 14px;
    font-weight: 700;
}

QLabel#idleModsHelp {
    color: rgba(255, 255, 255, 160);
    font-size: 10px;
}

QSlider#idleSharedExpSlider,
QSlider#idleRRSlider {
    height: 20px;
}

QSlider#idleSharedExpSlider::groove:horizontal,
QSlider#idleRRSlider::groove:horizontal {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    height: 6px;
    border-radius: 3px;
}

QSlider#idleSharedExpSlider::handle:horizontal,
QSlider#idleRRSlider::handle:horizontal {
    background-color: rgba(120, 180, 255, 200);
    border: 1px solid rgba(255, 255, 255, 100);
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider#idleSharedExpSlider::handle:horizontal:hover,
QSlider#idleRRSlider::handle:horizontal:hover {
    background-color: rgba(140, 200, 255, 220);
}

QSlider#idleSharedExpSlider::sub-page:horizontal {
    background-color: rgba(46, 204, 113, 140);
    border-radius: 3px;
}

QSlider#idleRRSlider::sub-page:horizontal {
    background-color: rgba(231, 76, 60, 140);
    border-radius: 3px;
}
""".strip()
