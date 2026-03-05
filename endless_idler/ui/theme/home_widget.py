from __future__ import annotations


STYLESHEET = """
QWidget#HomePageRoot {
    background: transparent;
}

QFrame#HomePanel {
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

QLabel#HomeTitle {
    color: rgba(237, 239, 245, 240);
    font-size: 22px;
    font-weight: 760;
}

QTabBar#HomeTabs::tab {
    background-color: rgba(18, 20, 28, 135);
    border: 1px solid rgba(255, 255, 255, 18);
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    padding: 8px 12px;
    margin-right: 0px;
    font-weight: 650;
}

QTabBar#HomeTabs::tab:hover {
    background-color: rgba(255, 255, 255, 10);
    border: 1px solid rgba(255, 255, 255, 24);
}

QTabBar#HomeTabs::tab:selected {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 20),
        stop: 1 rgba(18, 20, 28, 75)
    );
    border: 1px solid rgba(16, 185, 129, 140);
}

QWidget#HomeHeadersRow {
    background: transparent;
}

QLabel#HomeHeaderLabel {
    color: rgba(237, 239, 245, 150);
    font-weight: 650;
}

QFrame#HomeDecorRow {
    border: 1px solid rgba(255, 255, 255, 12);
    border-left: 4px solid rgba(148, 163, 184, 110);
    border-radius: 0px;
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(148, 163, 184, 20),
        stop: 1 rgba(18, 20, 28, 55)
    );
}

QFrame#HomeDecorRow[stain="cyan"] {
    border-left-color: rgba(56, 189, 248, 130);
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(56, 189, 248, 22),
        stop: 1 rgba(18, 20, 28, 55)
    );
}

QFrame#HomeDecorRow[stain="emerald"] {
    border-left-color: rgba(16, 185, 129, 125);
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 rgba(16, 185, 129, 20),
        stop: 1 rgba(18, 20, 28, 55)
    );
}

QLabel#HomeRowTitle {
    color: rgba(237, 239, 245, 235);
    font-weight: 660;
}

QLabel#HomeRowNote {
    color: rgba(237, 239, 245, 160);
}
""".strip()
