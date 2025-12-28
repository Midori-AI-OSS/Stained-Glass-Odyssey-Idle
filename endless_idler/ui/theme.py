from PySide6.QtWidgets import QApplication

from endless_idler.ui.icons import lucide_icon
from endless_idler.ui.icons import lucide_service


_STAINED_GLASS_STYLESHEET = """
QFrame#mainMenuPanel {
    background-color: rgba(16, 16, 18, 175);
    border: 1px solid rgba(255, 160, 120, 60);
    border-radius: 14px;
}

QLabel#mainMenuTitle {
    color: rgba(255, 255, 255, 230);
    font-size: 16px;
    font-weight: 600;
    padding: 6px 4px;
}

QPushButton[stainedMenu="true"] {
    background-color: rgba(40, 40, 44, 210);
    border: 1px solid rgba(255, 255, 255, 35);
    border-radius: 10px;
    padding: 12px 14px;
    color: rgba(255, 255, 255, 235);
    font-size: 14px;
    text-align: left;
}

QPushButton[stainedMenu="true"]:hover {
    background-color: rgba(54, 54, 62, 225);
    border-color: rgba(255, 140, 90, 155);
}

QPushButton[stainedMenu="true"]:pressed {
    background-color: rgba(255, 120, 80, 95);
    border-color: rgba(255, 120, 80, 215);
}

QPushButton[stainedMenu="true"]:disabled {
    background-color: rgba(40, 40, 44, 120);
    border-color: rgba(255, 255, 255, 22);
    color: rgba(255, 255, 255, 120);
}
""".strip()


def apply_stained_glass_theme(app: QApplication) -> None:
    app.setStyleSheet(_STAINED_GLASS_STYLESHEET)
    service = lucide_service()
    service.ensure_svg("diamond")
    app.setWindowIcon(lucide_icon("diamond", 24))

    def _maybe_set_window_icon(name: str) -> None:
        if name != "diamond":
            return
        app.setWindowIcon(lucide_icon("diamond", 24))

    service.svg_ready.connect(_maybe_set_window_icon)
