from __future__ import annotations


STYLESHEET = """
QFrame#partyHpHeader {
    background-color: rgba(20, 30, 60, 120);
    border: 1px solid rgba(255, 255, 255, 22);
}

QLabel#partyHpHeaderLabel {
    color: rgba(255, 255, 255, 210);
    font-size: 12px;
    font-weight: 700;
}

QProgressBar#partyHpHeaderBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    text-align: center;
    height: 14px;
}

QProgressBar#partyHpHeaderBar::chunk {
    background-color: rgba(46, 204, 113, 165);
}
""".strip()
