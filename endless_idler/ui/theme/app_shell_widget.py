from __future__ import annotations


STYLESHEET = """
QWidget#AppShellRoot {
    background-color: rgba(0, 0, 0, 105);
}

QFrame#AppTopBar {
    background-color: rgba(18, 20, 28, 165);
    border: 1px solid rgba(255, 255, 255, 25);
    border-radius: 0px;
}

QToolButton[appNav="true"],
QToolButton[appStub="true"] {
    color: rgba(237, 239, 245, 235);
    background-color: rgba(18, 20, 28, 135);
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 0px;
    padding: 9px 12px;
    font-weight: 600;
}

QToolButton[appNav="true"]:hover,
QToolButton[appStub="true"]:hover {
    background-color: rgba(56, 189, 248, 30);
    border: 1px solid rgba(56, 189, 248, 80);
}

QToolButton[appNav="true"]:pressed,
QToolButton[appStub="true"]:pressed {
    background-color: rgba(56, 189, 248, 70);
    border: 1px solid rgba(56, 189, 248, 100);
}

QToolButton[appNav="true"]:checked {
    background-color: rgba(56, 189, 248, 62);
    border: 1px solid rgba(56, 189, 248, 110);
}

QToolButton[appNav="true"]:checked:hover {
    background-color: rgba(56, 189, 248, 76);
    border: 1px solid rgba(56, 189, 248, 130);
}

QLabel#AppIdleStartupLabel {
    color: rgba(237, 239, 245, 170);
    font-size: 14px;
    font-weight: 620;
}
""".strip()
