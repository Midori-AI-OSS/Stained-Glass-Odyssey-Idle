from __future__ import annotations


STYLESHEET = """
QFrame#blessingPanel {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 16);
}

QFrame#blessingPanel[elementId="fire"] {
    background-color: rgba(255, 90, 40, 50);
    border: 1px solid rgba(255, 90, 40, 70);
}

QFrame#blessingPanel[elementId="ice"] {
    background-color: rgba(80, 200, 255, 50);
    border: 1px solid rgba(80, 200, 255, 70);
}

QFrame#blessingPanel[elementId="lightning"] {
    background-color: rgba(255, 220, 0, 45);
    border: 1px solid rgba(255, 220, 0, 65);
}

QFrame#blessingPanel[elementId="wind"] {
    background-color: rgba(80, 230, 170, 50);
    border: 1px solid rgba(80, 230, 170, 70);
}

QFrame#blessingPanel[elementId="dark"] {
    background-color: rgba(75, 45, 100, 50);
    border: 1px solid rgba(75, 45, 100, 70);
}

QFrame#blessingPanel[elementId="light"] {
    background-color: rgba(255, 220, 120, 50);
    border: 1px solid rgba(255, 220, 120, 70);
}

QLabel#blessingPanelName {
    color: rgba(255, 255, 255, 230);
    font-size: 12px;
    font-weight: 600;
    min-width: 100px;
}

QLabel#blessingPanelModValue {
    color: rgba(255, 255, 255, 200);
    font-size: 11px;
    font-weight: 500;
    min-width: 60px;
}

QWidget#blessingPanelProgressBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
}
""".strip()
