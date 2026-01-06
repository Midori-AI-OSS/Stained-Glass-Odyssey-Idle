import logging
import sys

from PySide6.QtWidgets import QApplication

from endless_idler.ui.main_menu import MainMenuWindow
from endless_idler.ui.theme import apply_stained_glass_theme


def main() -> int:
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/tmp/tutorial_debug.log')
        ]
    )
    
    app = QApplication(sys.argv)
    app.setOrganizationName("Midori AI")
    app.setApplicationName("Stained Glass Odyssey Idle")
    apply_stained_glass_theme(app)

    window = MainMenuWindow()
    window.show()

    return app.exec()
