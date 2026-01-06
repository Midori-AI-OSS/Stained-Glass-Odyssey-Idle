# Audit: Tutorial/Onboarding System Code Structure

## Date
2025-01-06

## Auditor
Code Auditor Agent (Auditor Mode)

## Scope
Technical audit of the Stained Glass Odyssey Idle codebase to design and recommend implementation of an onboarding tutorial system that addresses critical discoverability issues identified in the UI usability audit.

## Methodology
1. Examined existing UI framework (PySide6/Qt) capabilities for overlay systems
2. Analyzed game entry points and flow architecture
3. Reviewed settings/preferences system and save data structures
4. Studied existing overlay implementations (MergeFxOverlay, tooltips)
5. Mapped key UI elements requiring tutorial highlights
6. Reviewed original UI audit findings for requirements

## Executive Summary

The codebase has **excellent infrastructure** for implementing a tutorial system:
- **PySide6/Qt framework** provides robust overlay and animation capabilities
- **Existing overlay examples** (MergeFxOverlay, StainedGlassTooltip) demonstrate spotlight patterns
- **Save system** is extensible for tutorial completion tracking
- **MainMenuWindow** with QStackedWidget provides ideal entry point
- **Stained glass aesthetic** can be leveraged for beautiful tutorial overlays

**Recommendation**: Implement a **spotlight-based tutorial overlay** system with 5-7 key steps focusing on the most critical discoverability issues.

## Findings

### 1. UI Framework Capabilities (EXCELLENT)

#### PySide6/Qt Overlay System
The codebase already demonstrates overlay capabilities:

**File: `endless_idler/ui/party_builder_merge_fx.py`**
- `MergeFxOverlay` class shows full-screen transparent overlay pattern
- Uses `WA_TransparentForMouseEvents` for click-through regions
- Implements animations with `QPropertyAnimation` and `QGraphicsOpacityEffect`
- Pattern: Child widgets on overlay for visual effects

**File: `endless_idler/ui/tooltip.py`**
- `StainedGlassTooltip` demonstrates frameless window overlays
- Uses `QFrame` with `ToolTip` window flags
- Implements "stained glass" aesthetic with blur and color effects
- Shows HTML content rendering capability

**File: `endless_idler/ui/party_builder.py` (lines 103-104, 146-150)**
- Grid layout overlay system (`_overlay_layout: QGridLayout`)
- Overlay widgets placed on top of main content
- Example: Merge FX overlay, rewards plane overlay

**Technical Capabilities Available:**
- ✅ Full-screen semi-transparent overlays
- ✅ Spotlight effect via opacity masks and blur
- ✅ Animation system (fade in/out, pulse, movement)
- ✅ Rich text HTML rendering in Qt widgets
- ✅ Event filtering for selective click-through
- ✅ Z-order layering with QStackedWidget
- ✅ Programmatic widget highlighting via geometry mapping

### 2. Game Flow and Entry Points (CLEAR STRUCTURE)

#### Application Entry Point
**File: `endless_idler/app.py`**
```python
def main() -> int:
    app = QApplication(sys.argv)
    app.setOrganizationName("Midori AI")
    app.setApplicationName("Stained Glass Odyssey Idle")
    apply_stained_glass_theme(app)
    
    window = MainMenuWindow()  # ← PRIMARY ENTRY POINT
    window.show()
    
    return app.exec()
```

**Ideal Tutorial Trigger Point**: `MainMenuWindow.__init__()` after UI construction

#### Main Menu Structure
**File: `endless_idler/ui/main_menu.py`**

**MainMenuWindow class (lines 102-238)**:
- Uses `QStackedWidget` to manage screens
- Screens: Main menu, Party Builder, Battle, Idle, Skills
- Entry point: Main menu (default screen)
- Navigation: Signal-based screen switching

**Tutorial Integration Points**:
1. **First Launch**: Check tutorial flag in `__init__`, show overlay if needed
2. **Manual Trigger**: "Help" button to replay tutorial
3. **Context-Sensitive**: Trigger specific hints on screen transitions

**MainMenuWidget class (lines 24-77)**:
- Right-side menu panel with buttons:
  - "Run" → Party Builder (main gameplay)
  - "Warp" → Not implemented
  - "Skills" → Skills screen ⭐ **CRITICAL TUTORIAL TARGET**
  - "Inventory" → Not implemented
  - "Guidebook" → Not implemented
  - "Settings" → Not implemented (tutorial flag storage target)
  - "Feedback" → Not implemented

**Key Observations**:
- Settings button exists but not implemented (stub at line 220)
- Skills screen exists and functional (line 187-192)
- Keyboard shortcut 'K' already bound to Skills (lines 205-218)
- Most features are stubs showing "not implemented" dialogs

### 3. Settings/Preferences System (NEEDS EXTENSION)

#### Current Save System
**File: `endless_idler/save.py`**

**RunSave dataclass (lines 40-64)**:
- Current fields: tokens, party_level, fight_number, character data, idle bonuses
- Save format: JSON file at `~/.midoriai/idlesave.json`
- Version system: `SAVE_VERSION = 8`
- **NO SETTINGS/PREFERENCES CURRENTLY**

**SaveManager class (lines 66-173)**:
- Load: `load() -> RunSave | None`
- Save: `save(save: RunSave) -> None`
- Path: `_default_save_path()` uses `~/.midoriai/idlesave.json`

**Gap Analysis**:
❌ No separate settings/preferences file
❌ No "tutorial_completed" flag
❌ No UI preferences (volume, graphics, accessibility)

**Recommendation**: 
- **Option A (Simple)**: Add `tutorial_completed: bool = False` to RunSave dataclass
- **Option B (Better)**: Create separate `SettingsSave` class for preferences
  - Path: `~/.midoriai/settings.json`
  - Fields: `tutorial_completed`, `show_tooltips`, `audio_volume`, etc.
  - Keeps game state and preferences separated

**Implementation Complexity**:
- Option A: ~30 minutes (add field, update save version, migration)
- Option B: ~2 hours (new save class, manager, integration)

### 4. Key UI Elements for Tutorial Highlighting

Based on UI audit findings, these are the CRITICAL elements to highlight:

#### Priority 1: Most Critical (P0)

**1. Skills Button** (`main_menu.py` line 62)
- **Issue**: Passive abilities completely undiscoverable (UI Audit Issue #1)
- **Location**: Main menu, right panel, 3rd button
- **Widget ID**: `mainMenuButton_skills`
- **Action**: Highlight + explain "View passive abilities here [K]"
- **Importance**: ⭐⭐⭐⭐⭐ HIGHEST

**2. Resource Indicators** (Top of screen in Party Builder)
- **Issue**: Resource meanings unclear (UI Audit Issue #2)
- **Location**: `party_builder.py` - token display, party HP header
- **Widgets**: `_token_label`, `PartyHpHeader`
- **Action**: Point out + explain "These show your resources"
- **Importance**: ⭐⭐⭐⭐

**3. Party Builder Main Areas** (`party_builder.py`)
- **Issue**: Navigation unclear (UI Audit Issue #4)
- **Location**: Three main zones: Bar (shop), Onsite (active party), Offsite (reserves)
- **Widgets**: `CharacterBar`, onsite slots, offsite slots
- **Action**: Explain drag-and-drop system, party zones
- **Importance**: ⭐⭐⭐⭐

#### Priority 2: Important (P1)

**4. Settings Button** (When implemented)
- **Issue**: Settings not found (UI Audit Issue #6)
- **Location**: Main menu, right panel, 6th button
- **Action**: Show where settings will be
- **Importance**: ⭐⭐⭐

**5. Fight/Idle Buttons** (`party_builder.py`)
- **Issue**: Progression systems hidden (UI Audit Issue #7)
- **Location**: Bottom action bar in Party Builder
- **Widgets**: `FightBar`, `IdleBar`
- **Action**: Explain main gameplay loop
- **Importance**: ⭐⭐⭐

#### Priority 3: Nice to Have (P2)

**6. Guidebook Button**
- **Issue**: No help system (UI Audit Issue #3)
- **Location**: Main menu, 5th button
- **Action**: Explain future help location
- **Importance**: ⭐⭐

**7. Keyboard Shortcuts**
- **Issue**: No visible hotkey hints (UI Audit Issue #8)
- **Location**: Various
- **Action**: Show common shortcuts (K for Skills, ESC for back)
- **Importance**: ⭐⭐

### 5. Existing Components That Can Be Leveraged

#### MergeFxOverlay Pattern
**File: `endless_idler/ui/party_builder_merge_fx.py`**

**Reusable patterns**:
```python
class MergeFxOverlay(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
```

**Key techniques**:
- Transparent background for overlay
- Mouse event pass-through
- Animation with `QPropertyAnimation`
- Opacity effects with `QGraphicsOpacityEffect`

#### StainedGlassTooltip Aesthetic
**File: `endless_idler/ui/tooltip.py`**

**Reusable aesthetic elements**:
- Blur effect background (line 62-63)
- Drop shadow (line 69-73)
- Rich text HTML content (line 83-84)
- Stained glass color overlay (lines 142-166)

**Can be adapted for tutorial panels!**

#### Theme System
**File: `endless_idler/ui/theme.py`**

**Existing stylesheet system**:
- Centralized styling with `apply_stained_glass_theme(app)`
- Consistent color palette: `rgba(20, 30, 60, 130)` panels
- Semi-transparent buttons: `rgba(255, 255, 255, 26)`
- Hover states: `rgba(120, 180, 255, 56)`

**Tutorial styling should match this aesthetic!**

## Recommended Tutorial Architecture

### System Design: Spotlight Tutorial Overlay

#### Architecture Pattern: **Modal Overlay with Spotlight**

```
┌─────────────────────────────────────────────────────────┐
│ MainMenuWindow (QMainWindow)                            │
│  ├─ _stack (QStackedWidget)                             │
│  │   ├─ Main Menu Screen                                │
│  │   ├─ Party Builder Screen                            │
│  │   ├─ Skills Screen                                   │
│  │   └─ ...                                             │
│  └─ _tutorial_overlay (NEW: TutorialOverlay)            │ ← Add this
│      ├─ Semi-transparent dark background                │
│      ├─ Spotlight widget (clear area over target)       │
│      ├─ Tutorial card with text/arrow                   │
│      └─ Next/Skip buttons                               │
└─────────────────────────────────────────────────────────┘
```

#### Implementation Approach

**1. New Files to Create**:
- `endless_idler/ui/tutorial_overlay.py` - Main tutorial system
- `endless_idler/ui/tutorial_content.py` - Tutorial step definitions
- `endless_idler/settings.py` - Settings save system (if using Option B)

**2. Files to Modify**:
- `endless_idler/ui/main_menu.py` - Add tutorial trigger
- `endless_idler/save.py` - Add tutorial_completed flag (if using Option A)

#### Core Components

**Component 1: TutorialOverlay Widget**

```python
# File: endless_idler/ui/tutorial_overlay.py

class TutorialOverlay(QWidget):
    """Full-screen overlay for tutorial steps with spotlight effect."""
    
    finished = Signal()  # Emitted when tutorial completes or is skipped
    
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        # Set up as overlay
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.Widget | Qt.WindowType.FramelessWindowHint)
        
        # Components:
        # - Dark overlay background (semi-transparent)
        # - Spotlight region (uses QPainterPath for cutout)
        # - Tutorial card (StainedGlassPanel with text)
        # - Arrow pointing to target
        # - Progress indicator (Step 1 of 7)
        # - Next/Skip buttons
        
    def start_tutorial(self, steps: list[TutorialStep]) -> None:
        """Begin tutorial sequence."""
        pass
        
    def show_step(self, step: TutorialStep) -> None:
        """Display a single tutorial step."""
        # 1. Find target widget by object name
        # 2. Calculate spotlight geometry
        # 3. Position tutorial card
        # 4. Animate in
        pass
        
    def paintEvent(self, event: QPaintEvent) -> None:
        """Draw dark overlay with spotlight cutout."""
        painter = QPainter(self)
        
        # Fill entire widget with semi-transparent dark
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
        
        # Cut out spotlight region (clear area over target widget)
        if self._spotlight_rect:
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            # Draw rounded rect or ellipse for spotlight
            painter.drawRoundedRect(self._spotlight_rect, 8, 8)
```

**Component 2: Tutorial Step Data**

```python
# File: endless_idler/ui/tutorial_content.py

from dataclasses import dataclass
from enum import Enum

class TutorialTarget(Enum):
    """Where to position tutorial card relative to target."""
    RIGHT = "right"
    BOTTOM = "bottom"
    LEFT = "left"
    TOP = "top"
    CENTER = "center"

@dataclass
class TutorialStep:
    """Definition of a single tutorial step."""
    
    # Identification
    step_id: str  # e.g., "skills_button"
    title: str  # e.g., "Finding Your Skills"
    
    # Content
    message: str  # Main text (can use HTML)
    
    # Target highlighting
    target_widget_id: str | None  # Object name to highlight (None = no highlight)
    target_screen: str | None  # Which screen to show ("main_menu", "party_builder")
    card_position: TutorialTarget  # Where to put the tutorial card
    
    # Optional
    hotkey_hint: str | None = None  # e.g., "Press [K]"
    requires_action: bool = False  # Wait for user to perform action?
    auto_advance_seconds: float | None = None  # Auto-next after N seconds


# Pre-defined tutorial sequence
MAIN_TUTORIAL_STEPS = [
    TutorialStep(
        step_id="welcome",
        title="Welcome to Stained Glass Odyssey!",
        message="This quick tutorial will show you the essential features. You can skip at any time.",
        target_widget_id=None,
        target_screen="main_menu",
        card_position=TutorialTarget.CENTER,
    ),
    
    TutorialStep(
        step_id="skills_button",
        title="Skills & Passive Abilities",
        message=(
            "Your characters have <b>passive abilities</b> that make them unique!<br><br>"
            "Click the <b>Skills</b> button to view all character abilities.<br>"
            "Hotkey: Press <b>[K]</b> anytime to open this screen."
        ),
        target_widget_id="mainMenuButton_skills",
        target_screen="main_menu",
        card_position=TutorialTarget.RIGHT,
        hotkey_hint="Press [K]",
    ),
    
    TutorialStep(
        step_id="run_button",
        title="Starting Your Run",
        message=(
            "Click <b>Run</b> to enter the Party Builder.<br><br>"
            "This is where you'll assemble your team and prepare for battles."
        ),
        target_widget_id="mainMenuButton_run",
        target_screen="main_menu",
        card_position=TutorialTarget.RIGHT,
    ),
    
    TutorialStep(
        step_id="resources",
        title="Your Resources",
        message=(
            "These indicators show your <b>tokens</b> (for buying characters) "
            "and <b>party HP</b> (your team's health).<br><br>"
            "Hover over them for detailed tooltips."
        ),
        target_widget_id="partyHpHeader",  # or token label
        target_screen="party_builder",
        card_position=TutorialTarget.BOTTOM,
    ),
    
    TutorialStep(
        step_id="party_zones",
        title="Party Management",
        message=(
            "Your team has three areas:<br>"
            "• <b>Bar</b> (top): Available characters to buy<br>"
            "• <b>Onsite</b> (middle): Active fighters<br>"
            "• <b>Offsite</b> (middle): Reserve support<br><br>"
            "Drag and drop characters to move them!"
        ),
        target_widget_id=None,  # Could highlight whole middle section
        target_screen="party_builder",
        card_position=TutorialTarget.CENTER,
    ),
    
    TutorialStep(
        step_id="fight_button",
        title="Into Battle!",
        message=(
            "When you're ready, click <b>Fight</b> to test your party!<br><br>"
            "You can also use <b>Idle</b> mode to earn experience passively."
        ),
        target_widget_id=None,  # Would need to identify fight bar button
        target_screen="party_builder",
        card_position=TutorialTarget.BOTTOM,
    ),
    
    TutorialStep(
        step_id="complete",
        title="You're Ready!",
        message=(
            "That covers the basics!<br><br>"
            "• Press <b>[K]</b> to view Skills anytime<br>"
            "• Check the <b>Guidebook</b> for more help (coming soon)<br>"
            "• Visit <b>Settings</b> to replay this tutorial<br><br>"
            "Good luck on your journey!"
        ),
        target_widget_id=None,
        target_screen="main_menu",
        card_position=TutorialTarget.CENTER,
    ),
]
```

**Component 3: Settings Manager (Option B - Recommended)**

```python
# File: endless_idler/settings.py

from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class SettingsSave:
    """User preferences and settings."""
    
    # Tutorial
    tutorial_completed: bool = False
    tutorial_skipped: bool = False
    
    # UI Preferences (future expansion)
    show_tooltips: bool = True
    tooltip_delay_ms: int = 500
    
    # Audio (future)
    audio_enabled: bool = True
    audio_volume: float = 0.8
    music_volume: float = 0.6
    sfx_volume: float = 0.8
    
    # Accessibility (future)
    reduced_motion: bool = False
    high_contrast: bool = False


class SettingsManager:
    """Manages user settings persistence."""
    
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or self._default_path()
        
    def load(self) -> SettingsSave:
        """Load settings, returning defaults if file doesn't exist."""
        try:
            raw = self._path.read_text(encoding="utf-8")
            data = json.loads(raw)
            return SettingsSave(**{k: v for k, v in data.items() if k in SettingsSave.__dataclass_fields__})
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            return SettingsSave()
            
    def save(self, settings: SettingsSave) -> None:
        """Persist settings to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "tutorial_completed": settings.tutorial_completed,
            "tutorial_skipped": settings.tutorial_skipped,
            "show_tooltips": settings.show_tooltips,
            "tooltip_delay_ms": settings.tooltip_delay_ms,
            "audio_enabled": settings.audio_enabled,
            "audio_volume": settings.audio_volume,
            "music_volume": settings.music_volume,
            "sfx_volume": settings.sfx_volume,
            "reduced_motion": settings.reduced_motion,
            "high_contrast": settings.high_contrast,
        }
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(self._path)
        
    @staticmethod
    def _default_path() -> Path:
        """Default settings path: ~/.midoriai/settings.json"""
        return Path.home() / ".midoriai" / "settings.json"
```

**Component 4: Integration into MainMenuWindow**

```python
# File: endless_idler/ui/main_menu.py (modifications)

class MainMenuWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        # ... existing initialization ...
        
        # NEW: Settings manager
        from endless_idler.settings import SettingsManager
        self._settings_manager = SettingsManager()
        self._settings = self._settings_manager.load()
        
        # NEW: Tutorial overlay
        from endless_idler.ui.tutorial_overlay import TutorialOverlay
        from endless_idler.ui.tutorial_content import MAIN_TUTORIAL_STEPS
        
        self._tutorial_overlay = TutorialOverlay(self)
        self._tutorial_overlay.finished.connect(self._on_tutorial_finished)
        self._tutorial_overlay.hide()
        
        # Check if tutorial should run
        if not self._settings.tutorial_completed and not self._settings.tutorial_skipped:
            # Delay tutorial start slightly so UI is fully rendered
            QTimer.singleShot(500, lambda: self._tutorial_overlay.start_tutorial(MAIN_TUTORIAL_STEPS))
            
    def _on_tutorial_finished(self, completed: bool) -> None:
        """Handle tutorial completion or skip."""
        if completed:
            self._settings.tutorial_completed = True
        else:
            self._settings.tutorial_skipped = True
        self._settings_manager.save(self._settings)
        
    def _stub_settings(self) -> None:
        # When Settings screen is implemented, add:
        # "Reset Tutorial" button that calls self._tutorial_overlay.start_tutorial(...)
        pass
        
    def resizeEvent(self, event: QResizeEvent) -> None:
        """Keep tutorial overlay sized to window."""
        super().resizeEvent(event)
        if hasattr(self, "_tutorial_overlay"):
            self._tutorial_overlay.resize(self.size())
```

### Visual Design: Stained Glass Tutorial Aesthetic

#### Tutorial Card Appearance

```
┌────────────────────────────────────────────┐
│  ╔══════════════════════════════════════╗  │
│  ║  Step 2 of 7                         ║  │ ← Progress indicator
│  ║                                      ║  │
│  ║  Skills & Passive Abilities          ║  │ ← Title (bold, larger)
│  ║  ────────────────────────────────    ║  │
│  ║                                      ║  │
│  ║  Your characters have passive        ║  │ ← Body text (HTML)
│  ║  abilities that make them unique!    ║  │
│  ║                                      ║  │
│  ║  Click the Skills button to view     ║  │
│  ║  all character abilities.            ║  │
│  ║                                      ║  │
│  ║  Hotkey: Press [K]                   ║  │ ← Hotkey hint
│  ║                                      ║  │
│  ║  [ Skip Tutorial ]    [ Next → ]     ║  │ ← Action buttons
│  ╚══════════════════════════════════════╝  │
└────────────────────────────────────────────┘
      ↓ ← Arrow pointing to target widget
```

**Styling**:
- Background: Same as tooltip (stained glass overlay with blur)
- Border: `rgba(255, 255, 255, 28)` - 1px
- Text: `rgba(255, 255, 255, 235)`
- Buttons: Match existing stained glass button style
- Drop shadow for depth
- Rounded corners: 0px (matches theme's sharp aesthetic)

#### Spotlight Effect

```
┌─────────────────────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← Dark overlay
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │   (80% opacity)
│ ░░░░░░░┌──────────────────┐░░░░░░░░░░░░░░░░░░ │
│ ░░░░░░░│                  │░░░░░░░░░░░░░░░░░░ │ ← Clear area
│ ░░░░░░░│  Target Widget   │░░░░░░░░░░░░░░░░░░ │   (spotlight)
│ ░░░░░░░│                  │░░░░░░░░░░░░░░░░░░ │
│ ░░░░░░░└──────────────────┘░░░░░░░░░░░░░░░░░░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────────────────────┘
```

**Implementation**:
- Use `QPainter` with composition modes
- `CompositionMode_SourceOver` for dark layer
- `CompositionMode_Clear` for spotlight cutout
- Optional: Pulsing glow around spotlight edge

### Tutorial Content Outline

#### Minimal Effective Tutorial (5-7 Steps)

**Goal**: Address P0 critical issues only, keep under 2 minutes

| Step | Title | Target | Priority | Addresses Issue |
|------|-------|--------|----------|-----------------|
| 1 | Welcome | None (centered) | P0 | Overall orientation |
| 2 | Skills Button | `mainMenuButton_skills` | P0 | Issue #1 (passives undiscoverable) |
| 3 | Run Button | `mainMenuButton_run` | P0 | Navigation clarity |
| 4 | Resources | Token/HP displays | P0 | Issue #2 (resource meanings) |
| 5 | Party Zones | Party Builder areas | P0 | Issue #4 (navigation unclear) |
| 6 | Fight/Idle | Action buttons | P1 | Issue #7 (progression hidden) |
| 7 | Complete | None (centered) | P0 | Summary + next steps |

**Estimated Time**: 90-120 seconds for average user

**Skip Option**: Available on every step (button: "Skip Tutorial")

**Replay**: Available from Settings menu (when implemented)

#### Step-by-Step Detailed Content

See **Component 2: Tutorial Step Data** section above for full content definitions.

## Implementation Complexity Analysis

### Effort Estimates

#### Phase 1: Core Tutorial System (4-6 hours)
- Create `TutorialOverlay` widget with spotlight effect (2-3 hours)
- Create `TutorialStep` data structures (30 min)
- Implement tutorial card UI with stained glass styling (1-2 hours)
- Add navigation (Next/Skip buttons, step tracking) (1 hour)

#### Phase 2: Content & Integration (2-3 hours)
- Write tutorial step content (1 hour)
- Integrate into `MainMenuWindow` (30 min)
- Add settings persistence system (1-1.5 hours)
- Test tutorial flow and animations (30 min)

#### Phase 3: Polish & Testing (1-2 hours)
- Adjust positioning and timing (30 min)
- Add transitions/animations (30 min)
- Handle edge cases (window resize, etc.) (30 min)
- User testing and refinement (30 min)

**Total Estimated Effort**: 7-11 developer hours

**Complexity Rating**: ⭐⭐⭐ (Medium)
- Leverages existing patterns (overlays, tooltips)
- Well-defined requirements from UI audit
- Clear integration points
- Qt framework provides needed capabilities

### Risk Assessment

**Low Risks**:
- ✅ Framework supports all required features
- ✅ Existing overlay patterns to follow
- ✅ Clear requirements from UI audit
- ✅ No external dependencies needed

**Medium Risks**:
- ⚠️ Widget targeting: Need reliable way to find target widgets
  - *Mitigation*: Use object names (already set in code)
- ⚠️ Screen transitions: Tutorial must track current screen
  - *Mitigation*: Listen to QStackedWidget signals
- ⚠️ Window resizing: Overlay must stay positioned
  - *Mitigation*: Override `resizeEvent` (see integration code)

**High Risks**:
- ❌ None identified

## Recommendations for Implementation

### Priority 1: Immediate Actions

1. **Create Settings System First** (Option B recommended)
   - File: `endless_idler/settings.py`
   - Effort: 1-2 hours
   - Benefit: Foundation for tutorial + future features
   - Pattern: Mirror `SaveManager` structure

2. **Build Tutorial Overlay Framework**
   - File: `endless_idler/ui/tutorial_overlay.py`
   - Effort: 2-3 hours
   - Start with basic overlay + spotlight, no animations yet
   - Get widget targeting working

3. **Define Tutorial Content**
   - File: `endless_idler/ui/tutorial_content.py`
   - Effort: 1 hour
   - Use data from this audit's "Tutorial Content Outline"
   - Focus on 5 core steps initially

4. **Integrate into MainMenuWindow**
   - File: `endless_idler/ui/main_menu.py` (modify)
   - Effort: 30 min
   - Add tutorial trigger on first launch
   - Wire up completion tracking

### Priority 2: Polish & Enhancement

5. **Add Animations**
   - Fade in/out tutorial card
   - Pulsing spotlight glow
   - Arrow animations
   - Use existing `QPropertyAnimation` patterns

6. **Implement Settings Screen**
   - Create settings UI panel
   - Add "Reset Tutorial" button
   - Include other preferences (audio, graphics, etc.)

7. **Add Context-Sensitive Help**
   - "?" button in top-right corner
   - Click to get help about current screen
   - Reuses tutorial card UI

### Code Locations to Modify

#### New Files (Create)
```
endless_idler/
  settings.py                      # Settings save manager
  ui/
    tutorial_overlay.py            # Tutorial overlay widget
    tutorial_content.py            # Tutorial step definitions
```

#### Existing Files (Modify)
```
endless_idler/
  ui/
    main_menu.py                   # Add tutorial trigger
      - Line 103: Add settings manager initialization
      - Line 133: Add tutorial overlay widget
      - Line 220: Implement _stub_settings with tutorial reset
```

#### Optional Files (Future Enhancement)
```
endless_idler/
  ui/
    settings_screen.py             # Settings UI panel (new)
    help_overlay.py                # Context-sensitive help (new)
```

### Testing Strategy

#### Manual Testing Checklist
- [ ] Tutorial appears on first launch (new user simulation)
- [ ] Tutorial can be skipped at any step
- [ ] Tutorial can be completed fully
- [ ] Tutorial doesn't show on second launch
- [ ] Spotlight correctly highlights each target widget
- [ ] Tutorial card positions correctly for each step
- [ ] Window resize doesn't break tutorial positioning
- [ ] Navigation buttons (Next/Skip) work correctly
- [ ] Settings persistence works (tutorial_completed flag)
- [ ] Tutorial can be replayed from Settings (when implemented)

#### Edge Cases to Test
- [ ] Very small window size (<800px width)
- [ ] Very large window size (>2000px width)
- [ ] Rapid window resizing during tutorial
- [ ] Clicking target widgets during tutorial
- [ ] Pressing keyboard shortcuts during tutorial (e.g., K key)
- [ ] Alt+Tab during tutorial
- [ ] Tutorial while on different screens

### Success Metrics

**Quantitative**:
- Tutorial completion rate: Target >70% (industry standard ~50%)
- Tutorial skip rate: Target <30%
- Time to completion: Target 90-120 seconds
- User can find Skills button: Target <10 seconds after tutorial

**Qualitative**:
- User feedback: "I understand the basics now"
- Reduction in "where is X?" questions
- Zero confusion about passive abilities location

### Alternative Approaches Considered

#### Alternative 1: Video Tutorial (REJECTED)
**Pros**: Professional, high production value
**Cons**: 
- Not interactive
- Hard to maintain/update
- Large file size
- Doesn't pause for user experimentation
**Decision**: Interactive overlay is better for onboarding

#### Alternative 2: Separate Tutorial Mode (REJECTED)
**Pros**: Isolated testing environment
**Cons**:
- Requires duplicate UI setup
- Disconnected from actual gameplay
- Users might not transfer knowledge
**Decision**: In-place highlighting is more effective

#### Alternative 3: Tooltip-Only Approach (REJECTED)
**Pros**: Minimal implementation
**Cons**:
- Not prominent enough
- Easy to miss
- Doesn't solve discoverability (users don't know to look)
**Decision**: Spotlight overlay is necessary for critical issues

#### Alternative 4: First-Time Hints Only (CONSIDERED)
**Pros**: Non-intrusive, respects user agency
**Cons**: 
- Still requires some discoverability
- Might miss critical info
**Decision**: Hybrid approach - use spotlight tutorial for P0 issues, tooltips for P1/P2

## Integration with Settings System

### Settings Menu Structure (Future)

When Settings screen is implemented, include:

```
Settings
├─ Gameplay
│  └─ [ ] Show tooltips
├─ Tutorial
│  └─ [Reset Tutorial] button
├─ Audio
│  ├─ [x] Enable audio
│  ├─ Master volume: ████████░░ 80%
│  ├─ Music volume:  ██████░░░░ 60%
│  └─ SFX volume:    ████████░░ 80%
├─ Graphics
│  └─ [ ] Reduced motion
├─ Controls
│  └─ Hotkey reference (read-only display)
└─ About
   └─ Version, credits, etc.
```

### Settings File Location

**Path**: `~/.midoriai/settings.json`

**Example Content**:
```json
{
  "tutorial_completed": true,
  "tutorial_skipped": false,
  "show_tooltips": true,
  "tooltip_delay_ms": 500,
  "audio_enabled": true,
  "audio_volume": 0.8,
  "music_volume": 0.6,
  "sfx_volume": 0.8,
  "reduced_motion": false,
  "high_contrast": false
}
```

### Settings Access Points

1. **Main Menu** → Settings button (implement stub)
2. **Keyboard Shortcut** → ESC or Alt+S (when implemented)
3. **Tutorial Reset** → Available in Settings panel
4. **First Launch** → Tutorial auto-triggers (reads settings)

## Positive Observations

1. **Excellent Framework**: PySide6/Qt provides all needed capabilities
2. **Existing Patterns**: MergeFxOverlay and StainedGlassTooltip show clear implementation paths
3. **Clean Architecture**: QStackedWidget makes screen management simple
4. **Extensible Save System**: Easy to add settings persistence
5. **Consistent Styling**: Theme system makes tutorial styling straightforward
6. **Clear Requirements**: UI audit provides specific, actionable guidance

## Conclusion

The Stained Glass Odyssey Idle codebase is **well-suited for tutorial implementation**. The UI framework provides robust overlay capabilities, existing patterns demonstrate the approach, and integration points are clear.

**Key Takeaways**:
1. ✅ **Feasible**: 7-11 hours of focused development
2. ✅ **Low Risk**: Leverages existing patterns and Qt capabilities
3. ✅ **High Impact**: Addresses all P0 discoverability issues from UI audit
4. ✅ **Maintainable**: Clean separation (tutorial_overlay.py, tutorial_content.py)
5. ✅ **Extensible**: Settings system enables future enhancements

**Recommended Approach**:
- **Spotlight overlay tutorial** with 5-7 steps
- **Settings persistence** (separate settings.json file)
- **Stained glass aesthetic** matching existing theme
- **Skippable** at any step
- **Replayable** from Settings menu

**Priority Implementation Order**:
1. Settings system (1-2 hours)
2. Tutorial overlay framework (2-3 hours)
3. Tutorial content (1 hour)
4. Integration & testing (2-3 hours)
5. Polish & animations (1-2 hours)

This tutorial system will transform the new user experience from "confusing and opaque" to "guided and accessible" - directly addressing the critical issues identified in the UI usability audit.

## Next Steps for Coder

1. **Read this audit** thoroughly
2. **Review existing overlay patterns**: `party_builder_merge_fx.py`, `tooltip.py`
3. **Start with settings system**: Create `settings.py` using recommended structure
4. **Build tutorial overlay**: Create `tutorial_overlay.py` with basic spotlight
5. **Define content**: Create `tutorial_content.py` with 5-7 steps
6. **Integrate**: Modify `main_menu.py` to trigger tutorial on first launch
7. **Test**: Use checklist in Testing Strategy section
8. **Polish**: Add animations and refinements
9. **Document**: Update README with tutorial skip instructions

**Questions?** Refer back to:
- **Architecture Pattern** section for structure
- **Core Components** section for detailed code
- **Code Locations** section for integration points
- **UI Audit** (`.codex/audit/ui-issues-found.md`) for requirements

Good luck! The foundation is solid - this will be a great addition to the game. 🎮✨
