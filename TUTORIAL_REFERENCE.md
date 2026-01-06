# Tutorial System Quick Reference

## For Users

### First Launch
The tutorial will automatically appear when you launch the game for the first time. It guides you through:
1. Welcome and introduction
2. Skills button (where to find character abilities)
3. Run button (how to start playing)
4. Final tips and hotkeys

### Controls
- **Next**: Advance to next step
- **Previous**: Go back to previous step (disabled on first step)
- **Skip Tutorial**: Exit tutorial immediately (can't replay without resetting)

### Resetting Tutorial
Currently: Delete `~/.midoriai/settings.json` and restart the game
Future: Settings screen will have "Reset Tutorial" button

## For Developers

### File Structure
```
endless_idler/
├── settings.py                    # Settings persistence
└── ui/
    ├── tutorial_content.py       # Step definitions
    ├── tutorial_overlay.py       # UI components
    └── main_menu.py              # Integration point
```

### Adding New Tutorial Steps
Edit `endless_idler/ui/tutorial_content.py`:

```python
TutorialStep(
    step_id="my_new_step",
    title="Step Title",
    message="<b>HTML</b> content supported<br>Multiple lines OK",
    target_widget_name="widgetObjectName",  # or None for center
    target_screen="main_menu",  # or "party_builder", "skills"
    card_position=TutorialPosition.RIGHT,  # or CENTER, LEFT, TOP, BOTTOM
    hotkey_hint="Press [X]",  # optional
)
```

### Widget Object Names
For spotlight highlighting, widgets need object names:
- Main menu buttons: `mainMenuButton_<name>`
- Party builder: `partyHpHeader`, etc.
- Add names: `widget.setObjectName("myWidgetName")`

### Settings Fields
Edit `endless_idler/settings.py` to add new settings:

```python
@dataclass
class SettingsSave:
    # Tutorial
    tutorial_completed: bool = False
    
    # Your new setting
    my_new_setting: str = "default"
```

Update `save()` and `load()` methods accordingly.

### Customizing Appearance
Styles in `endless_idler/ui/tutorial_overlay.py`:
- `TutorialCard.__init__()`: Card styling (lines ~40-160)
- `TutorialOverlay.paintEvent()`: Overlay and spotlight (lines ~520-550)
- Colors: Match existing rgba() values for consistency

### Testing
```bash
# Delete settings to trigger tutorial
rm ~/.midoriai/settings.json

# Run game
python -m endless_idler

# Check settings after completion
cat ~/.midoriai/settings.json
```

### Programmatic Control
```python
# In main_menu.py or other widget

# Start tutorial manually
self._start_tutorial()

# Check if should show
if self._settings_manager.should_show_tutorial(self._settings):
    self._start_tutorial()

# Mark as completed
self._settings = self._settings_manager.mark_tutorial_completed(self._settings)
self._settings_manager.save(self._settings)
```

## Common Tasks

### Change Tutorial Content
1. Edit `ui/tutorial_content.py`
2. Modify `MAIN_TUTORIAL_STEPS` list
3. Test by deleting settings file

### Add More Steps
1. Add new `TutorialStep` to `MAIN_TUTORIAL_STEPS`
2. Set appropriate `target_widget_name`
3. Choose card position (RIGHT, LEFT, TOP, BOTTOM, CENTER)

### Change Spotlight Size
In `tutorial_overlay.py`, `_show_current_step()`:
```python
# Adjust padding (currently ±12px)
self._spotlight_rect.adjust(-12, -12, 12, 12)
```

### Disable Tutorial Auto-Start
In `main_menu.py`, `__init__()`:
```python
# Comment out or remove:
# if self._settings_manager.should_show_tutorial(self._settings):
#     QTimer.singleShot(500, self._start_tutorial)
```

### Change Tutorial Timing
In `main_menu.py`, `__init__()`:
```python
# Change delay (currently 500ms)
QTimer.singleShot(1000, self._start_tutorial)  # 1 second delay
```

### Trigger Tutorial on Different Event
```python
# In any widget, connect to your event
def on_some_event(self):
    # Get parent window
    window = self.window()
    if hasattr(window, '_start_tutorial'):
        window._start_tutorial()
```

## Troubleshooting

### Tutorial Doesn't Appear
- Check `~/.midoriai/settings.json` - delete to reset
- Verify `first_launch: true` in fresh settings
- Check console for errors

### Spotlight Not Highlighting Widget
- Verify widget has object name: `widget.setObjectName("name")`
- Check widget is visible: `widget.isVisible()`
- Ensure widget is in current screen

### Card Positioning Wrong
- Adjust `card_position` in tutorial step
- Check window size (tutorial card is 420px wide)
- Verify target widget coordinates

### Settings Not Saving
- Check directory permissions: `~/.midoriai/`
- Look for OSError exceptions
- Verify JSON format in settings file

### Tutorial Appears Every Launch
- Settings file might be corrupted
- Check `tutorial_completed` field in JSON
- Verify save() is called on completion

## Architecture Notes

### Why Separate Overlay Widget?
- Non-modal: Doesn't block UI interactions
- Reusable: Can be added to any window
- Flexible: Easy to position and animate
- Clean: Keeps tutorial code isolated

### Why JSON Settings?
- Human-readable for debugging
- Easy to edit manually
- Simple versioning
- No dependencies

### Why Spotlight Pattern?
- Focuses attention on specific elements
- Industry standard (Duolingo, Slack, etc.)
- Non-intrusive but effective
- Supports skip option

### Design Decisions
- **4 steps**: Balance between thorough and quick
- **Main menu only**: Avoids screen-switching complexity  
- **Auto-start delay**: Ensures UI is fully rendered
- **Fade animations**: Professional polish
- **HTML support**: Rich formatting in messages

## Performance Notes

- Overlay painting is efficient (uses composition modes)
- Settings I/O is async-safe (atomic writes with temp files)
- Widget lookups cached during step display
- No continuous polling or timers during tutorial
- Minimal memory footprint (~1MB)

## Security Notes

- Settings file in user home directory (not system-wide)
- No network access required
- No sensitive data stored
- JSON parsing with error handling
- File I/O with permission checks

## Accessibility Notes

- Text is scalable (Qt handles DPI)
- High contrast mode planned (settings field exists)
- Keyboard navigation supported (Tab, Enter)
- Skip option always available
- No time limits on reading

## Future Enhancements

### Planned
- [ ] Reset button in Settings screen
- [ ] Context-sensitive help (? button)
- [ ] Extended Party Builder tutorial
- [ ] Hotkey hints overlay

### Under Consideration
- [ ] Interactive tutorial (wait for user actions)
- [ ] Animated arrow with pulse effect
- [ ] Audio narration option
- [ ] Multiple tutorial tracks (beginner/advanced)
- [ ] Tutorial completion achievements

### Not Planned
- Video tutorials (too large, hard to maintain)
- Online-only tutorials (requires internet)
- Forced tutorials (always skippable)

## Support

For issues or questions:
1. Check `TUTORIAL_TESTING.md` for test cases
2. Review `IMPLEMENTATION_SUMMARY.md` for architecture
3. Read code comments in source files
4. Test with debug prints in overlay methods

## Version History

- v1.0 (2025-01-06): Initial implementation
  - Settings system
  - 4-step tutorial
  - Spotlight overlay
  - Navigation controls
