#!/usr/bin/env python3
"""
Visual QA Testing Script for Tooltips
Programmatically tests tooltip appearance across all screens.
"""
import sys
import time
from pathlib import Path

from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from endless_idler.app import main


class TooltipQATester:
    """Automated tooltip QA testing"""
    
    def __init__(self, app):
        self.app = app
        self.screenshot_dir = Path("/tmp/agents-artifacts")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.screenshot_count = 1
        self.findings = []
        
    def capture_screenshot(self, name: str):
        """Capture a screenshot of the application"""
        filename = f"{self.screenshot_count:02d}-{name}.png"
        filepath = self.screenshot_dir / filename
        
        # Get the main window
        windows = [w for w in self.app.topLevelWidgets() if w.isVisible()]
        if windows:
            window = windows[0]
            pixmap = window.grab()
            pixmap.save(str(filepath))
            print(f"✓ Captured: {filename}")
            self.screenshot_count += 1
            return filepath
        return None
        
    def find_widgets_recursive(self, widget, widget_type=None):
        """Recursively find all widgets of a specific type"""
        widgets = []
        
        if widget_type is None or isinstance(widget, widget_type):
            widgets.append(widget)
            
        for child in widget.children():
            if isinstance(child, QWidget):
                widgets.extend(self.find_widgets_recursive(child, widget_type))
                
        return widgets
        
    def trigger_tooltip(self, widget, delay_ms=1000):
        """Trigger a tooltip by simulating hover"""
        if not widget.isVisible():
            return False
            
        # Move mouse to widget center
        global_pos = widget.mapToGlobal(widget.rect().center())
        
        # For custom tooltips, they respond to enterEvent
        # For QToolTip, we need to wait a bit after hover
        from PySide6.QtGui import QEnterEvent
        event = QEnterEvent(widget.rect().center(), global_pos, global_pos)
        QApplication.sendEvent(widget, event)
        
        # Process events and wait
        QApplication.processEvents()
        time.sleep(delay_ms / 1000.0)
        QApplication.processEvents()
        
        return True
        
    def test_party_builder_tooltips(self):
        """Test tooltips in Party Builder screen"""
        print("\n=== Testing Party Builder Tooltips ===")
        
        windows = [w for w in self.app.topLevelWidgets() if w.isVisible()]
        if not windows:
            print("✗ No visible windows found")
            return
            
        main_window = windows[0]
        self.capture_screenshot("party-builder-main")
        
        # Find party builder components
        from endless_idler.ui.party_builder_slot import PartyBuilderSlot
        from endless_idler.ui.party_builder_bar import PartyBuilderBar
        
        slots = self.find_widgets_recursive(main_window, PartyBuilderSlot)
        print(f"Found {len(slots)} PartyBuilderSlot widgets")
        
        # Test first few slots
        for i, slot in enumerate(slots[:4]):
            if slot.isVisible():
                print(f"Testing slot {i+1}...")
                self.trigger_tooltip(slot, 500)
                self.capture_screenshot(f"party-slot-{i+1}-tooltip")
                
        # Test party bars
        bars = self.find_widgets_recursive(main_window, PartyBuilderBar)
        print(f"Found {len(bars)} PartyBuilderBar widgets")
        
        for i, bar in enumerate(bars[:2]):
            if bar.isVisible():
                print(f"Testing bar {i+1}...")
                # Test level tiles
                children = self.find_widgets_recursive(bar, QWidget)
                for j, child in enumerate(children[:3]):
                    if hasattr(child, 'toolTip') and child.toolTip():
                        self.trigger_tooltip(child, 500)
                        self.capture_screenshot(f"party-bar-{i+1}-element-{j+1}")
                        
    def test_battle_screen_tooltips(self):
        """Test tooltips in Battle Screen"""
        print("\n=== Testing Battle Screen Tooltips ===")
        
        windows = [w for w in self.app.topLevelWidgets() if w.isVisible()]
        if not windows:
            return
            
        main_window = windows[0]
        
        # Try to navigate to battle screen
        # Look for tab widget or navigation buttons
        from PySide6.QtWidgets import QTabWidget, QPushButton
        
        tabs = self.find_widgets_recursive(main_window, QTabWidget)
        if tabs:
            tab_widget = tabs[0]
            # Find battle tab
            for i in range(tab_widget.count()):
                if "battle" in tab_widget.tabText(i).lower():
                    print(f"Switching to battle tab: {tab_widget.tabText(i)}")
                    tab_widget.setCurrentIndex(i)
                    QApplication.processEvents()
                    time.sleep(0.5)
                    self.capture_screenshot("battle-screen-main")
                    break
        
        # Test battle widgets
        from endless_idler.ui.battle.widgets import CombatantCard
        
        cards = self.find_widgets_recursive(main_window, CombatantCard)
        print(f"Found {len(cards)} CombatantCard widgets")
        
        for i, card in enumerate(cards[:4]):
            if card.isVisible():
                print(f"Testing combat card {i+1}...")
                self.trigger_tooltip(card, 500)
                self.capture_screenshot(f"battle-card-{i+1}-tooltip")
                
    def test_onsite_tooltips(self):
        """Test tooltips in Onsite/Idle screen"""
        print("\n=== Testing Onsite/Idle Screen Tooltips ===")
        
        windows = [w for w in self.app.topLevelWidgets() if w.isVisible()]
        if not windows:
            return
            
        main_window = windows[0]
        
        # Try to navigate to idle/onsite screen
        from PySide6.QtWidgets import QTabWidget
        
        tabs = self.find_widgets_recursive(main_window, QTabWidget)
        if tabs:
            tab_widget = tabs[0]
            for i in range(tab_widget.count()):
                tab_text = tab_widget.tabText(i).lower()
                if "idle" in tab_text or "onsite" in tab_text:
                    print(f"Switching to onsite tab: {tab_widget.tabText(i)}")
                    tab_widget.setCurrentIndex(i)
                    QApplication.processEvents()
                    time.sleep(0.5)
                    self.capture_screenshot("onsite-screen-main")
                    break
        
        # Test onsite cards
        from endless_idler.ui.onsite.card import OnsiteCard
        
        cards = self.find_widgets_recursive(main_window, OnsiteCard)
        print(f"Found {len(cards)} OnsiteCard widgets")
        
        for i, card in enumerate(cards[:4]):
            if card.isVisible():
                print(f"Testing onsite card {i+1}...")
                self.trigger_tooltip(card, 500)
                self.capture_screenshot(f"onsite-card-{i+1}-tooltip")
                
    def run_tests(self):
        """Run all tooltip tests"""
        print("Starting Visual QA Testing for Tooltips")
        print("=" * 50)
        
        # Wait for app to be ready
        time.sleep(2)
        QApplication.processEvents()
        
        try:
            self.test_party_builder_tooltips()
            self.test_battle_screen_tooltips()
            self.test_onsite_tooltips()
            
            print("\n" + "=" * 50)
            print(f"Testing complete! Captured {self.screenshot_count - 1} screenshots")
            print(f"Screenshots saved to: {self.screenshot_dir}")
            
        except Exception as e:
            print(f"\n✗ Error during testing: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Close the app after a short delay
            QTimer.singleShot(1000, self.app.quit)


def run_qa_tests():
    """Main entry point for QA testing"""
    app = QApplication.instance()
    if app is None:
        # Start the application
        sys.argv = ["test_tooltips_qa.py"]
        app = QApplication(sys.argv)
        
        # Import and start the main window
        from endless_idler.ui.main_window import MainWindow
        from endless_idler.logic.game_state import GameState
        
        game_state = GameState()
        window = MainWindow(game_state)
        window.show()
    
    # Schedule testing to start after UI is loaded
    tester = TooltipQATester(app)
    QTimer.singleShot(2000, tester.run_tests)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_qa_tests())
