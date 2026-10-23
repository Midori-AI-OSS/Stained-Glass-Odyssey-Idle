from __future__ import annotations


STYLESHEET = """
QWidget#RadioControlRoot {
    background: transparent;
}

QToolButton#RadioControlButton {
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    padding: 0px;
    color: rgba(237, 239, 245, 235);
    background-color: rgba(18, 20, 28, 135);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
}

QToolButton#RadioControlButton:hover {
    background-color: rgba(56, 189, 248, 30);
    border: 1px solid rgba(56, 189, 248, 80);
}

QToolButton#RadioControlButton:pressed {
    background-color: rgba(56, 189, 248, 70);
    border: 1px solid rgba(56, 189, 248, 100);
}

QToolButton#RadioControlButton:disabled {
    background-color: rgba(18, 20, 28, 90);
    color: rgba(237, 239, 245, 130);
    border: 1px solid rgba(255, 255, 255, 14);
}

QWidget#RadioControlSliderWrap {
    background: transparent;
    border: 0px;
}

QSlider#RadioControlVolumeSlider::groove:horizontal {
    height: 6px;
    border: 1px solid rgba(255, 255, 255, 20);
    background: rgba(18, 20, 28, 140);
    border-radius: 0px;
}

QSlider#RadioControlVolumeSlider::sub-page:horizontal {
    background: rgba(56, 189, 248, 90);
    border-radius: 0px;
}

QSlider#RadioControlVolumeSlider::handle:horizontal {
    width: 10px;
    margin: -4px 0px;
    border: 1px solid rgba(56, 189, 248, 120);
    background: rgba(237, 239, 245, 240);
    border-radius: 0px;
}

QSlider#RadioControlVolumeSlider::handle:horizontal:hover {
    border: 1px solid rgba(56, 189, 248, 170);
}
""".strip()
