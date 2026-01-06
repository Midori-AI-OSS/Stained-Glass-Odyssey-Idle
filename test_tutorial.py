#!/usr/bin/env python3
"""Test script to demonstrate the tutorial system."""

import sys
from pathlib import Path

# Add the workspace to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from endless_idler.ui.main_menu import MainMenuWindow
from endless_idler.ui.theme import apply_stained_glass_theme


def test_tutorial():
    """Test the tutorial system."""
    app = QApplication(sys.argv)
    app.setOrganizationName("Midori AI")
    app.setApplicationName("Stained Glass Odyssey Idle")
    apply_stained_glass_theme(app)

    window = MainMenuWindow()
    window.show()

    # Take screenshots at intervals
    screenshot_times = [1000, 3000, 5000, 7000]  # milliseconds
    screenshot_names = ["welcome", "skills-button", "run-button", "complete"]

    def take_screenshot(name: str) -> None:
        """Take a screenshot and save it."""
        pixmap = window.grab()
        path = f"/tmp/agents-artifacts/tutorial-{name}.png"
        pixmap.save(path)
        print(f"Screenshot saved: {path}")

    # Schedule screenshots
    for time_ms, name in zip(screenshot_times, screenshot_names):
        QTimer.singleShot(time_ms, lambda n=name: take_screenshot(n))

    # Close after screenshots
    QTimer.singleShot(8000, app.quit)

    return app.exec()


if __name__ == "__main__":
    # Remove settings file to trigger tutorial
    settings_file = Path.home() / ".midoriai" / "settings.json"
    if settings_file.exists():
        settings_file.unlink()
        print("Deleted existing settings file")

    sys.exit(test_tutorial())
