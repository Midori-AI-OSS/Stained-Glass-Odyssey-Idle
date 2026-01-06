# Tutorial Overlay Bug Analysis

**Audit ID:** f9429e28  
**Date:** 2025-01-21  
**Auditor:** AI Auditor  
**Severity:** HIGH - Blocks user experience, tutorial cannot be completed  

---

## Executive Summary

The tutorial overlay system has multiple critical bugs that prevent users from completing the tutorial. The issues stem from:
1. **QPainter lifecycle violations** causing the reported errors
2. **Missing painter cleanup** in two paintEvent implementations
3. **Auto-start behavior** that doesn't respect user intent
4. **Widget hierarchy issues** causing button removal on hover

---

## Issue 1: QPainter Lifecycle Violations (CRITICAL)

### Location
- `endless_idler/ui/tutorial_overlay.py`
  - Line 202-251: `TutorialArrow.paintEvent()`
  - Line 532-554: `TutorialOverlay.paintEvent()`

### Root Cause
Both `TutorialArrow.paintEvent()` and `TutorialOverlay.paintEvent()` create QPainter instances but **never call `painter.end()`**. This leaves the painter in an active state, causing the following issues:

1. **Resource leak**: QPainter resources are not properly released
2. **State corruption**: Subsequent paint operations can conflict with the active painter
3. **Concurrent painter errors**: Qt's "only one painter at a time" error occurs when the widget's parent or children try to paint

### Evidence
The error logs show:
```
QPainter::setWorldTransform: Painter not active
QPainter::begin: A paint device can only be painted by one painter at a time.
```

These errors occur because:
- The overlay's painter is left active when child widgets (buttons, labels) try to paint themselves
- On hover events, Qt triggers repaints of buttons, which conflict with the still-active overlay painter
- The arrow widget's painter similarly conflicts with the overlay's painter

### Comparison with Correct Implementation
File: `endless_idler/ui/main_menu.py` (lines 90-106)
```python
def paintEvent(self, event: object) -> None:
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    # ... drawing code ...
    painter.end()  # ✓ CORRECT: Properly ends painter
```

File: `endless_idler/ui/party_builder_common.py` (line 98)
```python
painter.end()  # ✓ CORRECT
```

File: `endless_idler/ui/tooltip.py` (line 165)
```python
painter.end()  # ✓ CORRECT
```

### Impact
- **HIGH**: Causes buttons to disappear on hover
- **HIGH**: Prevents tutorial completion as navigation becomes impossible
- **MEDIUM**: Memory/resource leak over time
- **LOW**: Console spam with QPainter errors

### Recommended Fix

**File: `endless_idler/ui/tutorial_overlay.py`**

#### Fix 1: TutorialArrow.paintEvent() (Line 202)
```python
def paintEvent(self, event: object) -> None:
    """Draw arrow from start to end."""
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    start = self._start
    end = self._end

    if start == end:
        painter.end()  # ADD: End painter before early return
        return

    # Draw line
    pen = QPen()
    pen.setWidth(3)
    pen.setColor(QColor(120, 180, 255, 255))
    painter.setPen(pen)
    painter.drawLine(start, end)

    # Draw arrowhead
    dx = end.x() - start.x()
    dy = end.y() - start.y()
    length = math.hypot(dx, dy)

    if length <= 0.0:
        painter.end()  # ADD: End painter before early return
        return

    # Unit vectors
    ux = dx / length
    uy = dy / length
    px = -uy
    py = ux

    # Arrowhead dimensions
    head_len = 14.0
    head_w = 8.0
    tip = end
    base_x = end.x() - int(round(ux * head_len))
    base_y = end.y() - int(round(uy * head_len))
    left = QPoint(
        base_x + int(round(px * head_w)),
        base_y + int(round(py * head_w)),
    )
    right = QPoint(
        base_x - int(round(px * head_w)),
        base_y - int(round(py * head_w)),
    )

    painter.setBrush(QColor(120, 180, 255, 255))
    painter.drawPolygon(QPolygon([tip, left, right]))
    painter.end()  # ADD: End painter at function exit
```

#### Fix 2: TutorialOverlay.paintEvent() (Line 532)
```python
def paintEvent(self, event: object) -> None:
    """Draw dark overlay with spotlight cutout."""
    painter = QPainter(self)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # Fill entire widget with semi-transparent dark
    painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

    # Cut out spotlight region (clear area over target widget)
    if self._spotlight_rect:
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        # Draw rounded rect for spotlight
        path = QPainterPath()
        path.addRoundedRect(
            self._spotlight_rect.x(),
            self._spotlight_rect.y(),
            self._spotlight_rect.width(),
            self._spotlight_rect.height(),
            8,
            8,
        )
        painter.fillPath(path, QColor(0, 0, 0, 0))
    
    painter.end()  # ADD: End painter at function exit
```

---

## Issue 2: Tutorial Auto-Start Behavior (HIGH PRIORITY)

### Location
- `endless_idler/ui/main_menu.py` (lines 151-156)

### Current Behavior
```python
# Check if tutorial should run (delayed to allow UI to fully render)
if self._settings_manager.should_show_tutorial(self._settings):
    logger.info("Tutorial should be shown - scheduling start")
    QTimer.singleShot(500, self._start_tutorial)
```

The tutorial **automatically starts** on first launch without user consent. This is intrusive and can confuse users who:
- Want to explore the UI themselves first
- Are returning users on a new device/account
- Accidentally triggered first-launch conditions

### Recommended Approach

#### Option 1: Show a Modal Dialog (Recommended)
Display a friendly dialog asking if the user wants to take the tutorial:

```python
# In MainMenuWindow.__init__ after line 149
if self._settings_manager.should_show_tutorial(self._settings):
    logger.info("First launch detected - showing tutorial prompt")
    QTimer.singleShot(500, self._prompt_tutorial)

def _prompt_tutorial(self) -> None:
    """Ask user if they want to take the tutorial."""
    from PySide6.QtWidgets import QMessageBox
    
    msg = QMessageBox(self)
    msg.setWindowTitle("Welcome to Stained Glass Odyssey!")
    msg.setText("This is your first time launching the game.")
    msg.setInformativeText(
        "Would you like a quick tutorial to learn the basics?\n\n"
        "You can always access it later from the Settings menu."
    )
    msg.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg.setDefaultButton(QMessageBox.StandardButton.Yes)
    msg.setIcon(QMessageBox.Icon.Question)
    
    result = msg.exec()
    
    if result == QMessageBox.StandardButton.Yes:
        self._start_tutorial()
    else:
        # Mark as skipped so we don't ask again
        self._settings = self._settings_manager.mark_tutorial_skipped(self._settings)
        self._settings_manager.save(self._settings)
        logger.info("User declined tutorial")
```

#### Option 2: Add a "Start Tutorial" Button to Main Menu
Add a visible button on the main menu that users can click to start the tutorial.

#### Option 3: Settings Menu Access (Already Planned)
The code has a TODO comment at line 270-271:
```python
def _stub_settings(self) -> None:
    # TODO: Implement settings screen
    # When implemented, add "Reset Tutorial" button that calls self._start_tutorial()
```

**Recommendation**: Implement both Option 1 (prompt) AND Option 3 (settings access) so users can:
1. Choose whether to start the tutorial on first launch
2. Replay the tutorial any time from Settings

---

## Issue 3: Button Removal on Hover (CAUSED BY ISSUE 1)

### Manifestation
When hovering over tutorial card buttons (Previous, Next, Skip), they disappear or become unresponsive.

### Root Cause
This is a **direct consequence** of Issue 1 (QPainter lifecycle violations). When buttons hover:
1. Button's hover state triggers a repaint of the button
2. Button tries to create its own QPainter
3. Parent overlay widget's painter is still active (not ended)
4. Qt's "one painter at a time" rule is violated
5. Button's paint fails, causing it to not render or render incorrectly

### Evidence Path
```
TutorialOverlay.paintEvent() creates painter
  └─> painter.end() NEVER CALLED (bug)
      └─> TutorialCard child widget tries to paint button
          └─> Button hover triggers repaint
              └─> QPainter conflict: "only one painter at a time"
                  └─> Button fails to render
```

### Fix
**This issue will be resolved automatically by fixing Issue 1.** No separate fix needed.

---

## Issue 4: Tutorial Completion Flow Issues

### Current Flow Analysis

**File: `endless_idler/ui/main_menu.py`**
```python
def __init__(self) -> None:
    # ... initialization ...
    
    # Initialize tutorial overlay (line 146)
    self._tutorial_overlay = TutorialOverlay(self)
    self._tutorial_overlay.finished.connect(self._on_tutorial_finished)
    
    # Auto-start check (line 151-156)
    if self._settings_manager.should_show_tutorial(self._settings):
        QTimer.singleShot(500, self._start_tutorial)

def _on_tutorial_finished(self, completed: bool) -> None:
    """Handle tutorial completion or skip."""
    if completed:
        self._settings = self._settings_manager.mark_tutorial_completed(self._settings)
    else:
        self._settings = self._settings_manager.mark_tutorial_skipped(self._settings)
    
    self._settings_manager.save(self._settings)
```

**File: `endless_idler/ui/tutorial_overlay.py`**
```python
def _on_next(self) -> None:
    """Handle next button click."""
    if self._current_step_index < len(self._steps) - 1:
        self._current_step_index += 1
        self._show_current_step()
    else:
        # Tutorial complete
        self._complete_tutorial()

def _complete_tutorial(self) -> None:
    """Handle tutorial completion."""
    self.finished.emit(True)  # Emits signal to MainMenuWindow
    self._fade_out()

def _on_skip(self) -> None:
    """Handle skip button click."""
    self.finished.emit(False)  # Emits signal to MainMenuWindow
    self._fade_out()
```

**File: `endless_idler/settings.py`**
```python
def should_show_tutorial(self, settings: SettingsSave) -> bool:
    """Determine if tutorial should be shown."""
    return settings.first_launch and not settings.tutorial_completed and not settings.tutorial_skipped

def mark_tutorial_completed(self, settings: SettingsSave) -> SettingsSave:
    """Mark tutorial as completed."""
    settings.tutorial_completed = True
    settings.first_launch = False  # Also marks as not first launch
    return settings

def mark_tutorial_skipped(self, settings: SettingsSave) -> SettingsSave:
    """Mark tutorial as skipped."""
    settings.tutorial_skipped = True
    settings.first_launch = False  # Also marks as not first launch
    return settings
```

### Flow Assessment

The completion flow is **architecturally sound**:
1. ✅ Tutorial emits `finished(bool)` signal on completion or skip
2. ✅ MainMenuWindow receives signal and updates settings
3. ✅ Settings are persisted to disk
4. ✅ `first_launch` flag is properly cleared to prevent re-showing

**However**, the flow is **currently broken** due to Issue 1 preventing users from reaching the completion buttons.

### Testing Recommendations

After fixing Issue 1, verify:
1. Completing tutorial sets `tutorial_completed = True` and `first_launch = False`
2. Skipping tutorial sets `tutorial_skipped = True` and `first_launch = False`
3. Settings file is written to `~/.midoriai/stained-glass-odyssey/settings.json`
4. Restarting the app does not show the tutorial again
5. Tutorial can be manually restarted from Settings menu (when implemented)

---

## Issue 5: Widget Finding Logic Fragility

### Location
- `endless_idler/ui/tutorial_overlay.py` (lines 484-491)

### Current Code
```python
def _find_widget(self, object_name: str) -> QWidget | None:
    """Find a widget by its object name."""
    parent_window = self.parent()
    if not parent_window:
        return None

    # Search recursively for widget with matching object name
    return parent_window.findChild(QWidget, object_name)
```

### Issue
The function relies on `findChild()` to search the entire widget tree. This can fail if:
1. Target widget hasn't been created yet (lazy initialization)
2. Widget is in a different screen that's not in the tree yet
3. Object name is misspelled or changed

### Example from Tutorial Steps
```python
TutorialStep(
    step_id="skills_button",
    target_widget_name="mainMenuButton_skills",  # Must match object name exactly
    # ...
)
```

### Verification
File: `endless_idler/ui/main_menu.py` (line 68)
```python
menu_layout.addWidget(self._make_button("Skills", self.skills_requested.emit))

def _make_button(self, label: str, on_click: Callable[[], None]) -> QPushButton:
    button = QPushButton(label)
    button.setObjectName(f"mainMenuButton_{label.lower().replace(' ', '_')}")
    # For "Skills", this creates: "mainMenuButton_skills" ✓ MATCHES
```

### Assessment
- **Currently working correctly** for main menu buttons
- **Potential future issue** if:
  - Party builder screen widgets aren't created until opened
  - Object names change without updating tutorial content

### Recommended Enhancement
Add validation logging to help debug widget finding issues:

```python
def _find_widget(self, object_name: str) -> QWidget | None:
    """Find a widget by its object name."""
    parent_window = self.parent()
    if not parent_window:
        logger.warning(f"Tutorial: No parent window when searching for '{object_name}'")
        return None

    # Search recursively for widget with matching object name
    widget = parent_window.findChild(QWidget, object_name)
    
    if widget is None:
        logger.warning(f"Tutorial: Widget '{object_name}' not found in widget tree")
    else:
        logger.debug(f"Tutorial: Found widget '{object_name}': visible={widget.isVisible()}")
    
    return widget
```

---

## Issue 6: Screen Switching Logic Incompleteness

### Location
- `endless_idler/ui/tutorial_overlay.py` (lines 458-482)

### Current Code
```python
def _switch_to_screen(self, screen_name: str | None) -> None:
    """Switch to the specified screen."""
    if not screen_name:
        return

    # Find the parent MainMenuWindow
    parent_window = self.parent()
    if not parent_window:
        return

    # Access the stacked widget
    if hasattr(parent_window, "_stack"):
        stack = parent_window._stack
        if screen_name == "main_menu" and hasattr(parent_window, "_main_menu_widget"):
            # Switch to main menu
            if hasattr(parent_window, "_menu_screen") and parent_window._menu_screen:
                stack.setCurrentWidget(parent_window._menu_screen)
        elif screen_name == "party_builder":
            # Open party builder if not already open
            if hasattr(parent_window, "_open_party_builder"):
                parent_window._open_party_builder()
        elif screen_name == "skills":
            # Open skills screen if needed
            if hasattr(parent_window, "_open_skills_screen"):
                parent_window._open_skills_screen()
```

### Issues

1. **Defensive programming creates silent failures**: Using `hasattr()` everywhere means errors fail silently
2. **Incomplete screen handling**: Only handles 3 screen types
3. **No error logging**: When screen switch fails, there's no indication why

### Current Tutorial Requirements
From `endless_idler/ui/tutorial_content.py`:
```python
MAIN_TUTORIAL_STEPS = [
    # Step 1: target_screen="main_menu"
    # Step 2: target_screen="main_menu"
    # Step 3: target_screen="main_menu"
    # Step 4: target_screen="main_menu"
]
```

**Assessment**: Current tutorial only uses "main_menu" screen, so the incomplete switching logic **doesn't affect current functionality**. However, it will break if tutorial steps are added for other screens.

### Recommended Enhancement
Add error handling and logging:

```python
def _switch_to_screen(self, screen_name: str | None) -> None:
    """Switch to the specified screen."""
    if not screen_name:
        return

    parent_window = self.parent()
    if not parent_window:
        logger.error("Tutorial: No parent window for screen switching")
        return

    if not hasattr(parent_window, "_stack"):
        logger.error("Tutorial: Parent window missing _stack attribute")
        return

    stack = parent_window._stack

    try:
        if screen_name == "main_menu":
            if hasattr(parent_window, "_menu_screen") and parent_window._menu_screen:
                stack.setCurrentWidget(parent_window._menu_screen)
                logger.debug(f"Tutorial: Switched to main_menu screen")
            else:
                logger.warning("Tutorial: main_menu screen not available")
        
        elif screen_name == "party_builder":
            if hasattr(parent_window, "_open_party_builder"):
                parent_window._open_party_builder()
                logger.debug(f"Tutorial: Opened party_builder screen")
            else:
                logger.warning("Tutorial: party_builder not available")
        
        elif screen_name == "skills":
            if hasattr(parent_window, "_open_skills_screen"):
                parent_window._open_skills_screen()
                logger.debug(f"Tutorial: Opened skills screen")
            else:
                logger.warning("Tutorial: skills screen not available")
        
        else:
            logger.warning(f"Tutorial: Unknown screen name '{screen_name}'")
    
    except Exception as e:
        logger.error(f"Tutorial: Failed to switch to '{screen_name}': {e}")
```

---

## Priority Summary

### P0 - Critical (Fix Immediately)
1. **Issue 1**: Add `painter.end()` to both paintEvent implementations
   - Fixes QPainter errors
   - Fixes button removal on hover
   - Fixes tutorial navigation

### P1 - High (Fix Soon)
2. **Issue 2**: Change auto-start to user-prompted
   - Better UX
   - Respects user agency
   - Prevents confusion

### P2 - Medium (Recommended)
3. **Issue 5**: Add widget finding validation logging
   - Helps debug future issues
   - No current functional impact

4. **Issue 6**: Add screen switching error logging
   - Helps debug future issues
   - No current functional impact

### P3 - Low (Optional)
5. Add "Replay Tutorial" button in Settings menu (already has TODO)
6. Add tutorial step validation on startup
7. Add telemetry for tutorial completion rates

---

## Testing Checklist

After implementing fixes, verify:

### Basic Functionality
- [ ] Tutorial starts without QPainter errors in logs
- [ ] Hover over buttons works correctly (buttons don't disappear)
- [ ] "Previous" button navigates backward through steps
- [ ] "Next" button advances through steps
- [ ] "Skip Tutorial" button exits tutorial
- [ ] "Finish" button (last step) completes tutorial
- [ ] Overlay fades in/out smoothly

### State Persistence
- [ ] Completing tutorial writes `tutorial_completed=true` to settings
- [ ] Skipping tutorial writes `tutorial_skipped=true` to settings
- [ ] `first_launch` flag becomes `false` after tutorial
- [ ] Restarting app doesn't show tutorial again
- [ ] Settings file exists at `~/.midoriai/stained-glass-odyssey/settings.json`

### Visual Elements
- [ ] Spotlight highlights correct widgets
- [ ] Arrow points from card to target widget
- [ ] Card positions correctly (left/right/top/bottom/center)
- [ ] Card stays on screen (doesn't go off edge)
- [ ] Stained glass theme applies correctly

### Edge Cases
- [ ] Resizing window during tutorial repositions elements
- [ ] Rapidly clicking Next/Previous doesn't break state
- [ ] Tutorial works on different screen resolutions
- [ ] Clicking outside tutorial card doesn't dismiss it
- [ ] Pressing ESC doesn't dismiss tutorial (intentional)

### User-Initiated Start (After Issue 2 fix)
- [ ] First launch shows prompt dialog
- [ ] "Yes" starts tutorial
- [ ] "No" marks tutorial as skipped
- [ ] Settings menu can restart tutorial (when implemented)

---

## Implementation Notes

### File Changes Required

1. **`endless_idler/ui/tutorial_overlay.py`** (CRITICAL)
   - Line 211: Add `painter.end()` before early return
   - Line 226: Add `painter.end()` before early return  
   - Line 251: Add `painter.end()` at end of function
   - Line 554: Add `painter.end()` at end of function

2. **`endless_idler/ui/main_menu.py`** (HIGH PRIORITY)
   - Replace auto-start (lines 151-156) with user prompt
   - Add `_prompt_tutorial()` method
   - Import QMessageBox

3. **Optional: Add logging enhancements**
   - Update `_find_widget()` with validation logging
   - Update `_switch_to_screen()` with error logging

### Code Review Checklist
- [ ] All QPainter instances have matching `end()` calls
- [ ] All early returns in paintEvent call `painter.end()` first
- [ ] User consent is obtained before starting tutorial
- [ ] Settings persistence is properly tested
- [ ] Error logging is added for debugging

---

## Additional Observations

### Code Quality Notes

**Positive:**
- Clean separation of concerns (overlay/content/settings)
- Good use of signals/slots for decoupling
- Comprehensive tutorial content with rich text
- Proper dataclass usage for tutorial steps
- Settings migration logic for backward compatibility

**Areas for Improvement:**
- Missing painter cleanup (the main bug)
- Auto-start without user consent
- Silent failures in screen switching
- Limited error logging for debugging

### Architecture Assessment

The tutorial system architecture is **well-designed**:
- Modular: `tutorial_overlay.py` (UI) + `tutorial_content.py` (data) + `settings.py` (persistence)
- Extensible: Easy to add new tutorial steps
- Maintainable: Clear separation of responsibilities
- Testable: Signal-based communication

**The bugs are implementation issues, not design flaws.**

---

## Conclusion

This tutorial system has solid architecture but critical implementation bugs. The primary issue is **missing `painter.end()` calls** in two paintEvent methods, causing cascading failures:

1. QPainter stays active → 
2. Child widgets can't paint → 
3. Buttons disappear on hover → 
4. Tutorial becomes unusable

**The fix is simple but critical**: Add 4 lines of code to properly end painters.

Secondary issue is **user experience**: Auto-starting the tutorial is intrusive. A prompt dialog would be more respectful of user choice.

After these fixes, the tutorial system should work correctly and provide a smooth onboarding experience.

---

## References

### Files Analyzed
- `endless_idler/ui/tutorial_overlay.py` (561 lines)
- `endless_idler/ui/tutorial_content.py` (99 lines)
- `endless_idler/ui/main_menu.py` (289 lines)
- `endless_idler/settings.py` (173 lines)
- `endless_idler/app.py` (30 lines)

### Qt Documentation
- [QPainter Class Reference](https://doc.qt.io/qt-6/qpainter.html)
- [Paint Events and Widgets](https://doc.qt.io/qt-6/paintsystem.html)

### Related Issues
- QPainter lifecycle management
- Widget hierarchy and paint device conflicts
- Tutorial UX best practices
