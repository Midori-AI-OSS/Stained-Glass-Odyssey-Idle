from __future__ import annotations


STYLESHEET = """
QFrame#stainedTooltipPanel {
    background-color: rgba(0, 0, 0, 0);
    border: 1px solid rgba(255, 255, 255, 90);
    border-radius: 0px;
}

QFrame#stainedTooltipPanel[elementId="fire"] { border: 1px solid rgba(255, 160, 120, 110); }
QFrame#stainedTooltipPanel[elementId="ice"] { border: 1px solid rgba(160, 235, 255, 110); }
QFrame#stainedTooltipPanel[elementId="lightning"] { border: 1px solid rgba(255, 250, 160, 110); }
QFrame#stainedTooltipPanel[elementId="wind"] { border: 1px solid rgba(180, 255, 225, 110); }
QFrame#stainedTooltipPanel[elementId="dark"] { border: 1px solid rgba(165, 145, 190, 110); }
QFrame#stainedTooltipPanel[elementId="light"] { border: 1px solid rgba(255, 240, 185, 110); }

QLabel#stainedTooltipContent {
    color: rgba(255, 255, 255, 235);
    font-size: 12px;
}

QToolTip {
    background-color: rgba(30, 40, 60, 230);
    color: rgba(255, 255, 255, 245);
    border: 1px solid rgba(255, 255, 255, 90);
    border-radius: 0px;
    padding: 8px 10px;
    font-size: 12px;
}
""".strip()
