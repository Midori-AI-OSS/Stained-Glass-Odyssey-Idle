from __future__ import annotations


STYLESHEET = """
QFrame#onsiteCharacterCard {
    border: 1px solid rgba(255, 255, 255, 18);
    background-color: rgba(255, 255, 255, 10);
}

QFrame#onsiteCharacterCard[elementId="fire"] { background-color: rgba(255, 90, 40, 60); }
QFrame#onsiteCharacterCard[elementId="ice"] { background-color: rgba(80, 200, 255, 60); }
QFrame#onsiteCharacterCard[elementId="lightning"] { background-color: rgba(255, 220, 0, 55); }
QFrame#onsiteCharacterCard[elementId="wind"] { background-color: rgba(80, 230, 170, 60); }
QFrame#onsiteCharacterCard[elementId="dark"] { background-color: rgba(75, 45, 100, 60); }
QFrame#onsiteCharacterCard[elementId="light"] { background-color: rgba(255, 220, 120, 60); }

QLabel#onsitePortrait {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
}

QLabel#onsiteCharName {
    color: rgba(255, 255, 255, 235);
    font-size: 13px;
    font-weight: 700;
}

QLabel#onsiteStackPlus {
    color: rgba(255, 255, 255, 170);
    font-size: 11px;
    font-weight: 700;
}

QLabel#onsiteCharLevel,
QLabel#onsiteCharStack {
    color: rgba(255, 255, 255, 170);
    font-size: 11px;
}

QPushButton#onsiteStatsButton,
QPushButton#onsiteActionButton {
    background-color: rgba(255, 255, 255, 14);
    border: 1px solid rgba(255, 255, 255, 20);
    border-radius: 0px;
    padding: 6px 10px;
    color: rgba(255, 255, 255, 230);
    font-size: 12px;
}

QPushButton#onsiteStatsButton:hover,
QPushButton#onsiteActionButton:hover {
    background-color: rgba(120, 180, 255, 44);
}

QPushButton#onsiteStatsButton:checked {
    background-color: rgba(120, 180, 255, 32);
}

QProgressBar#onsiteHpBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    text-align: center;
    height: 16px;
}

QProgressBar#onsiteHpBar::chunk {
    background-color: rgba(46, 204, 113, 165);
}

QProgressBar#onsiteExpBar {
    background-color: rgba(0, 0, 0, 35);
    border: 1px solid rgba(255, 255, 255, 20);
    color: rgba(255, 255, 255, 210);
    font-size: 10px;
    text-align: center;
    height: 13px;
}

QProgressBar#onsiteExpBar::chunk {
    background-color: rgba(52, 152, 219, 170);
}

QFrame#onsiteStatPopup {
    background-color: rgba(10, 14, 26, 235);
    border: 1px solid rgba(255, 255, 255, 24);
}

QFrame#onsiteStatBars {
    background-color: rgba(0, 0, 0, 18);
    border: 1px solid rgba(255, 255, 255, 14);
}

QLabel#onsiteStatLabel {
    color: rgba(255, 255, 255, 185);
    font-size: 9px;
    font-weight: 700;
}

QProgressBar#onsiteStatBar {
    background-color: rgba(0, 0, 0, 40);
    border: 1px solid rgba(255, 255, 255, 18);
    height: 10px;
}

QProgressBar#onsiteStatBar::chunk {
    background-color: rgba(155, 89, 182, 165);
}

QProgressBar#onsiteStatBar[statKey="atk"]::chunk {
    background-color: rgba(231, 76, 60, 170);
}

QProgressBar#onsiteStatBar[statKey="defense"]::chunk {
    background-color: rgba(52, 152, 219, 175);
}

QProgressBar#onsiteStatBar[statKey="atk_speed"]::chunk {
    background-color: rgba(46, 204, 113, 175);
}

QProgressBar#onsiteStatBar[statKey="crit_mod"]::chunk {
    background-color: rgba(241, 196, 15, 185);
}

QProgressBar#onsiteStatBar[statKey="dodge_odds"]::chunk {
    background-color: rgba(26, 188, 156, 175);
}

QProgressBar#onsiteStatBar[statKey="regain"]::chunk {
    background-color: rgba(155, 89, 182, 175);
}

QProgressBar#onsiteStatBar[statKey="mitigation"]::chunk {
    background-color: rgba(149, 165, 166, 175);
}

/* Shard Progress Bar */
QWidget#shardProgressBarWidget {
    background-color: transparent;
    min-height: 18px;
}

QLabel#shardProgressBarLabel {
    color: rgba(255, 255, 255, 220);
    font-size: 10px;
    font-weight: 500;
}
""".strip()
