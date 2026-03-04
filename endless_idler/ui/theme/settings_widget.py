from __future__ import annotations


STYLESHEET = """
QWidget#SettingsPageRoot {
    background-color: rgba(0, 0, 0, 170);
}

QWidget#SettingsHeader,
QWidget#SettingsCard {
    background-color: rgba(20, 30, 60, 130);
    border: 1px solid rgba(255, 255, 255, 24);
}

QLabel#SettingsHeaderTitle {
    color: rgba(255, 255, 255, 245);
    font-size: 20px;
    font-weight: 700;
}

QToolButton#SettingsBackButton {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 24);
    border-radius: 0px;
    padding: 8px 12px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}

QToolButton#SettingsBackButton:hover {
    background-color: rgba(120, 180, 255, 44);
}

QWidget#SettingsNavPanel {
    background-color: rgba(10, 14, 26, 145);
    border: 1px solid rgba(255, 255, 255, 20);
}

QWidget#SettingsPaneHost {
    background-color: rgba(11, 16, 30, 150);
    border: 1px solid rgba(255, 255, 255, 16);
    padding: 10px;
}

QLabel#SettingsNavSection {
    color: rgba(170, 220, 255, 235);
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    padding-top: 6px;
}

QToolButton#SettingsNavButton {
    background-color: rgba(255, 255, 255, 14);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    padding: 8px 10px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
    text-align: left;
}

QToolButton#SettingsNavButton:hover {
    background-color: rgba(120, 180, 255, 46);
}

QToolButton#SettingsNavButton:checked {
    background-color: rgba(56, 132, 230, 64);
    border-color: rgba(170, 220, 255, 140);
}

QLabel#SettingsPaneTitle {
    color: rgba(255, 255, 255, 245);
    font-size: 18px;
    font-weight: 700;
}

QLabel#SettingsPaneSubtitle,
QLabel#SettingsPaneLabel {
    color: rgba(255, 255, 255, 185);
    font-size: 12px;
}

QLabel#SettingsPaneLabel {
    color: rgba(170, 220, 255, 235);
    font-weight: 600;
}

QWidget#SettingsPageRoot QCheckBox,
QWidget#SettingsPageRoot QLabel,
QWidget#SettingsPageRoot QPushButton,
QWidget#SettingsPageRoot QToolButton {
    color: rgba(255, 255, 255, 230);
}

QWidget#SettingsPageRoot QComboBox,
QWidget#SettingsPageRoot QDoubleSpinBox {
    background-color: rgba(255, 255, 255, 14);
    border: 1px solid rgba(255, 255, 255, 24);
    border-radius: 0px;
    min-height: 30px;
    padding: 4px 8px;
    color: rgba(255, 255, 255, 230);
}

QWidget#SettingsPageRoot QComboBox::drop-down {
    width: 26px;
    border: none;
}

QSlider#SettingsVolumeSlider::groove:horizontal,
QSlider#RadioControlVolumeSlider::groove:horizontal {
    background: rgba(255, 255, 255, 20);
    border-radius: 4px;
    height: 8px;
}

QSlider#SettingsVolumeSlider::handle:horizontal,
QSlider#RadioControlVolumeSlider::handle:horizontal {
    background: rgba(170, 220, 255, 235);
    border: 1px solid rgba(255, 255, 255, 150);
    border-radius: 6px;
    width: 12px;
    margin: -3px 0;
}

QPushButton#SettingsRadioPlayButton {
    background-color: rgba(255, 255, 255, 16);
    border: 1px solid rgba(255, 255, 255, 24);
    border-radius: 0px;
    padding: 8px 12px;
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
}

QPushButton#SettingsRadioPlayButton:hover {
    background-color: rgba(120, 180, 255, 44);
}

QWidget#RadioControlRoot {
    background-color: rgba(255, 255, 255, 8);
    border: 1px solid rgba(255, 255, 255, 22);
}

QToolButton#RadioControlButton {
    background-color: rgba(255, 255, 255, 14);
    border: 1px solid rgba(255, 255, 255, 20);
    border-radius: 0px;
}

QWidget#RadioControlSliderWrap {
    background-color: transparent;
}
""".strip()
