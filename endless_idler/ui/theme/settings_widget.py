from __future__ import annotations


STYLESHEET = """
QWidget#SettingsPageRoot {
    background-color: rgba(0, 0, 0, 105);
}

QWidget#SettingsHeader,
QWidget#SettingsCard {
    background-color: rgba(18, 20, 28, 165);
    border: 1px solid rgba(255, 255, 255, 25);
    border-radius: 0px;
}

QLabel#SettingsHeaderTitle {
    font-size: 18px;
    font-weight: 750;
    color: rgba(237, 239, 245, 245);
}

QWidget#SettingsNavPanel {
    background-color: rgba(18, 20, 28, 95);
    border: 1px solid rgba(255, 255, 255, 14);
    border-radius: 0px;
}

QLabel#SettingsNavSection {
    color: rgba(237, 239, 245, 145);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    margin-top: 8px;
    margin-bottom: 2px;
    padding: 2px 6px;
}

QToolButton#SettingsNavButton {
    text-align: left;
    padding: 9px 10px;
    border: 1px solid rgba(255, 255, 255, 14);
    background-color: rgba(18, 20, 28, 95);
    color: rgba(237, 239, 245, 220);
    border-radius: 0px;
    font-weight: 620;
}

QToolButton#SettingsNavButton:hover {
    border: 1px solid rgba(56, 189, 248, 70);
    background-color: rgba(56, 189, 248, 20);
}

QToolButton#SettingsNavButton:checked {
    border: 1px solid rgba(56, 189, 248, 110);
    background-color: rgba(56, 189, 248, 62);
}

QToolButton#SettingsNavButton:checked:hover {
    border: 1px solid rgba(56, 189, 248, 130);
    background-color: rgba(56, 189, 248, 76);
}

QLabel#SettingsPaneTitle {
    font-size: 16px;
    font-weight: 760;
    color: rgba(237, 239, 245, 245);
}

QLabel#SettingsPaneSubtitle {
    color: rgba(237, 239, 245, 160);
}

QLabel#SettingsSaveValue {
    color: rgba(237, 239, 245, 220);
    background-color: rgba(18, 20, 28, 150);
    border: 1px solid rgba(255, 255, 255, 16);
    padding: 8px 10px;
}

QLabel#SettingsSaveHelp {
    color: rgba(237, 239, 245, 150);
}

QWidget#SettingsPageRoot QCheckBox {
    spacing: 10px;
}

QWidget#SettingsPageRoot QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 0px;
    border: 1px solid rgba(255, 255, 255, 35);
    background-color: rgba(18, 20, 28, 170);
}

QWidget#SettingsPageRoot QCheckBox::indicator:hover {
    border: 1px solid rgba(56, 189, 248, 70);
    background-color: rgba(18, 20, 28, 200);
}

QWidget#SettingsPageRoot QCheckBox::indicator:checked {
    background-color: rgba(16, 185, 129, 165);
    border: 1px solid rgba(16, 185, 129, 180);
}

QWidget#SettingsPageRoot QCheckBox::indicator:checked:hover {
    background-color: rgba(16, 185, 129, 195);
    border: 1px solid rgba(16, 185, 129, 220);
}

QWidget#SettingsPageRoot QComboBox {
    background-color: rgba(18, 20, 28, 190);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    padding: 9px 34px 9px 10px;
    selection-background-color: rgba(56, 189, 248, 85);
}

QWidget#SettingsPageRoot QComboBox:hover {
    border: 1px solid rgba(56, 189, 248, 60);
    background-color: rgba(18, 20, 28, 210);
}

QWidget#SettingsPageRoot QComboBox:focus {
    border: 1px solid rgba(56, 189, 248, 120);
    background-color: rgba(18, 20, 28, 225);
}

QWidget#SettingsPageRoot QComboBox:disabled {
    background-color: rgba(18, 20, 28, 90);
    color: rgba(237, 239, 245, 130);
    border: 1px solid rgba(255, 255, 255, 14);
}

QWidget#SettingsPageRoot QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid rgba(255, 255, 255, 14);
    background-color: rgba(18, 20, 28, 120);
    border-top-right-radius: 0px;
    border-bottom-right-radius: 0px;
}

QWidget#SettingsPageRoot QComboBox::drop-down:hover {
    background-color: rgba(56, 189, 248, 30);
}

QWidget#SettingsPageRoot QComboBox QAbstractItemView {
    background-color: rgba(18, 20, 28, 240);
    border: 1px solid rgba(255, 255, 255, 22);
    outline: 0px;
    selection-background-color: rgba(56, 189, 248, 85);
}

QWidget#SettingsPageRoot QComboBox QAbstractItemView::item {
    padding: 8px 10px;
}

QWidget#SettingsPageRoot QSlider::groove:horizontal {
    height: 6px;
    border: 1px solid rgba(255, 255, 255, 20);
    background: rgba(18, 20, 28, 140);
    border-radius: 0px;
}

QWidget#SettingsPageRoot QSlider::sub-page:horizontal {
    background: rgba(56, 189, 248, 90);
    border-radius: 0px;
}

QWidget#SettingsPageRoot QSlider::add-page:horizontal {
    background: rgba(18, 20, 28, 140);
    border-radius: 0px;
}

QWidget#SettingsPageRoot QSlider::handle:horizontal {
    width: 10px;
    margin: -4px 0px;
    border: 1px solid rgba(56, 189, 248, 120);
    background: rgba(237, 239, 245, 240);
    border-radius: 0px;
}

QWidget#SettingsPageRoot QSlider::handle:horizontal:hover {
    border: 1px solid rgba(56, 189, 248, 170);
}

QWidget#SettingsPageRoot QSlider::handle:horizontal:pressed {
    border: 1px solid rgba(56, 189, 248, 210);
}

QWidget#SettingsPageRoot QAbstractSpinBox {
    min-height: 36px;
    background-color: rgba(18, 20, 28, 190);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    padding: 0px 8px;
    selection-background-color: rgba(56, 189, 248, 85);
}

QWidget#SettingsPageRoot QAbstractSpinBox:hover {
    border: 1px solid rgba(56, 189, 248, 60);
    background-color: rgba(18, 20, 28, 210);
}

QWidget#SettingsPageRoot QAbstractSpinBox:focus {
    border: 1px solid rgba(56, 189, 248, 120);
    background-color: rgba(18, 20, 28, 225);
}

QWidget#SettingsPageRoot QAbstractSpinBox:disabled {
    background-color: rgba(18, 20, 28, 90);
    color: rgba(237, 239, 245, 130);
    border: 1px solid rgba(255, 255, 255, 14);
}

QWidget#SettingsPageRoot QAbstractSpinBox::up-button,
QWidget#SettingsPageRoot QAbstractSpinBox::down-button {
    width: 20px;
    border: 0px;
    border-left: 1px solid rgba(255, 255, 255, 14);
    background-color: rgba(18, 20, 28, 120);
    border-radius: 0px;
}

QWidget#SettingsPageRoot QAbstractSpinBox::up-button:hover,
QWidget#SettingsPageRoot QAbstractSpinBox::down-button:hover {
    background-color: rgba(56, 189, 248, 30);
}

QWidget#SettingsPageRoot QAbstractSpinBox::up-button:pressed,
QWidget#SettingsPageRoot QAbstractSpinBox::down-button:pressed {
    background-color: rgba(56, 189, 248, 60);
}

QPushButton#SettingsSaveActionButton,
QPushButton#SettingsSaveDangerButton {
    min-height: 36px;
    padding: 0px 12px;
    border-radius: 0px;
    color: rgba(237, 239, 245, 230);
}

QPushButton#SettingsSaveActionButton {
    background-color: rgba(18, 20, 28, 170);
    border: 1px solid rgba(255, 255, 255, 18);
}

QPushButton#SettingsSaveActionButton:hover {
    border: 1px solid rgba(56, 189, 248, 80);
    background-color: rgba(56, 189, 248, 26);
}

QPushButton#SettingsSaveActionButton:pressed {
    border: 1px solid rgba(56, 189, 248, 120);
    background-color: rgba(56, 189, 248, 52);
}

QPushButton#SettingsSaveDangerButton {
    background-color: rgba(60, 18, 24, 170);
    border: 1px solid rgba(255, 120, 120, 42);
}

QPushButton#SettingsSaveDangerButton:hover {
    border: 1px solid rgba(255, 120, 120, 90);
    background-color: rgba(140, 40, 52, 80);
}

QPushButton#SettingsSaveDangerButton:pressed {
    border: 1px solid rgba(255, 120, 120, 130);
    background-color: rgba(160, 40, 52, 120);
}
""".strip()
