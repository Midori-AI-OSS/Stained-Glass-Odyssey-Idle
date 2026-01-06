# Tutorial System - README Section

*This content can be added to the main README.md*

---

## 🎓 Onboarding Tutorial

The game includes an interactive tutorial that appears automatically on first launch. The tutorial guides new players through essential features with spotlight highlighting and step-by-step instructions.

### Features
- **Automatic first-launch detection**
- **4-step guided tour** covering:
  - Welcome and introduction
  - Skills & passive abilities ([K] hotkey)
  - Party Builder basics
  - Essential hotkeys and tips
- **Spotlight highlighting** on important UI elements
- **Skip option** available at any time
- **Navigation controls**: Next, Previous, and Skip buttons

### For Users

#### First Launch
The tutorial appears automatically 500ms after the game starts for the first time. You can:
- **Click "Next"** to advance through steps
- **Click "Previous"** to review earlier steps
- **Click "Skip Tutorial"** to exit at any time

#### Replaying the Tutorial
To replay the tutorial, delete the settings file:
```bash
rm ~/.midoriai/settings.json
```
Then restart the game.

> **Note:** A "Reset Tutorial" button will be added to the Settings screen in a future update.

### For Developers

#### File Locations
```
endless_idler/
├── settings.py                    # Settings persistence
└── ui/
    ├── tutorial_content.py       # Tutorial step definitions
    ├── tutorial_overlay.py       # Overlay UI components
    └── main_menu.py              # Integration point
```

#### Adding Tutorial Steps
Edit `endless_idler/ui/tutorial_content.py` and add to `MAIN_TUTORIAL_STEPS`:

```python
TutorialStep(
    step_id="my_step",
    title="Step Title",
    message="HTML <b>formatted</b> message<br>Multiple lines supported",
    target_widget_name="widgetObjectName",  # Widget to highlight
    target_screen="main_menu",  # Screen to display on
    card_position=TutorialPosition.RIGHT,  # Card placement
    hotkey_hint="Press [X]",  # Optional hotkey hint
)
```

#### Widget Object Names
For spotlight highlighting, set object names on widgets:
```python
button.setObjectName("myButtonName")
```

#### Testing
```bash
# Delete settings to trigger tutorial
rm ~/.midoriai/settings.json

# Run game
python -m endless_idler
```

### Documentation
For comprehensive information, see:
- **TUTORIAL_TESTING.md** - Testing guide and test cases
- **TUTORIAL_REFERENCE.md** - Developer quick reference
- **IMPLEMENTATION_SUMMARY.md** - Architecture and design decisions

### Technical Details
- **Storage:** `~/.midoriai/settings.json`
- **Framework:** PySide6/Qt overlay system
- **Pattern:** Spotlight overlay with navigation controls
- **Styling:** Stained glass aesthetic matching game theme
- **Animation:** 300ms fade in/out transitions

---
