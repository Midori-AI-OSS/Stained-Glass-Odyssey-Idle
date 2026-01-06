# Code Audit: Skills/Passives UI Implementation

## Date
2025-01-06

## Auditor
Copilot Auditor Agent

## Scope
Technical audit of the Skills/Passives system implementation to determine the current state and provide actionable recommendations for adding a Skills/Passives UI panel.

---

## Executive Summary

The passive abilities system is **fully implemented and functional** at the backend level, but **has no UI representation**. Characters have passive abilities that trigger during combat, but players have no way to view what passives their characters possess or what they do.

**Key Finding**: Adding a Skills/Passives UI panel is straightforward - the infrastructure exists, we just need to surface it to users.

---

## Current Implementation Status

### 1. Passive System Backend (✅ Fully Implemented)

**Location**: `endless_idler/passives/`

The passive system is well-architected with complete infrastructure:

#### Core Components
- **Base Classes**: `endless_idler/passives/base.py`
  - `PassiveBase` protocol defining the interface
  - `Passive` abstract base class for implementations
  
- **Trigger System**: `endless_idler/passives/triggers.py`
  - `PassiveTrigger` enum with 8 trigger points (TURN_START, TURN_END, PRE_DAMAGE, etc.)
  - `TriggerContext` dataclass containing all combat state information
  
- **Registry**: `endless_idler/passives/registry.py`
  - Global registry `_PASSIVE_REGISTRY` mapping passive IDs to classes
  - `register_passive()` decorator for automatic registration
  - `load_passive()` to instantiate passives by ID
  - `list_passives()` to enumerate all registered passives

- **Execution Utilities**: `endless_idler/passives/execution.py`
  - `trigger_passives_for_characters()` - generic passive triggering
  - `trigger_turn_start_passives()` - TURN_START trigger
  - `apply_pre_damage_passives()` - damage modifiers
  - `apply_target_selection_passives()` - target redirection

#### Current Passive Implementations
**Count**: 3 implemented passives (plus many more in character files)

1. **Lady Light: Radiant Aegis** (`lady_light_radiant_aegis`)
   - File: `endless_idler/passives/implementations/lady_light_radiant_aegis.py`
   - Trigger: TURN_START
   - Effect: When offsite, heals all party members for 50% of regain stat

2. **Lady Darkness: Eclipsing Veil** (`lady_darkness_eclipsing_veil`)
   - File: `endless_idler/passives/implementations/lady_darkness_eclipsing_veil.py`
   - Trigger: PRE_DAMAGE
   - Effect: 2x damage multiplier, ignore 50% defense

3. **Trinity Synergy** (`trinity_synergy`)
   - File: `endless_idler/passives/implementations/trinity_synergy.py`
   - Triggers: TURN_START, TARGET_SELECTION
   - Effect: Synergy bonuses when Lady Light, Lady Darkness, and Persona are together

#### Character Integration
**Location**: Character files in `endless_idler/characters/`

Characters define their passives via the `passives: list[str]` field:

```python
# Example from endless_idler/characters/lady_light.py
passives: list[str] = field(default_factory=lambda: ["lady_light_radiant_aegis", "trinity_synergy"])
```

**Metadata Extraction**: `endless_idler/characters/metadata.py` (line 274-326)
- `_extract_passives_from_classdef()` extracts passive IDs from character classes via AST parsing
- Handles both direct lists and `field(default_factory=lambda: [...])` patterns
- Passives are loaded into character metadata during plugin discovery

**Combat Integration**: `endless_idler/ui/battle/sim.py`
- `load_passives_for_character()` (lines 34-53) loads passive instances
- Stores loaded passives in `stats._passive_instances`
- Called during character creation in `build_party()` and `build_reserves()`

---

### 2. UI Framework (PySide6 / Qt)

**Location**: `endless_idler/ui/`

**Framework**: PySide6 (Qt for Python)

#### Main Window Architecture
**File**: `endless_idler/ui/main_menu.py`

The application uses a `QStackedWidget` to switch between screens:
```python
class MainMenuWindow(QMainWindow):
    def __init__(self):
        self._stack = QStackedWidget()  # Line 124
        # Screens are added as widgets to the stack
        self._stack.addWidget(screen_widget)
        self._stack.setCurrentWidget(active_widget)
```

**Current Screens**:
- Main Menu (`MainMenuWidget`)
- Party Builder (`PartyBuilderWidget`)
- Battle Screen (`BattleScreenWidget`)
- Idle Screen (`IdleScreenWidget`)

#### UI Patterns for Information Display

**Tooltips**: `endless_idler/ui/tooltip.py`
- `StainedGlassTooltip` - Custom tooltip widget with stained glass theme
- `show_stained_tooltip()` / `hide_stained_tooltip()` - Global tooltip functions
- Supports HTML content with element-based color tinting
- Used throughout the UI for hover information

**Character Stats Display**: `endless_idler/ui/party_builder_common.py`
- `build_character_stats_tooltip()` (lines 109-212) generates HTML tooltip with:
  - Character name and star rating
  - Level, EXP, EXP multiplier
  - All combat stats (HP, ATK, Defense, Regain, etc.)
  - Stack count for stackable characters
- **Note**: No passive information included currently

**Stat Bars Panel**: `endless_idler/ui/onsite/stat_bars.py`
- `StatBarsPanel` - Visual stat comparison panel
- Used in battle/idle onsite character cards
- Shows progress bars for ATK, Defense, Speed, Crit Rate, etc.
- Opened via 👁 button on character cards

**Popup Pattern**: `endless_idler/ui/onsite/card.py` (lines 50-80)
- `OnsiteStatsPopup` - QFrame with WindowType.Popup flag
- Used for character stat detail popups
- Pattern for modal/semi-modal overlays

#### Theme System
**File**: `endless_idler/ui/theme.py`
- `apply_stained_glass_theme()` - Applies custom Qt stylesheet
- Stained glass aesthetic with color-coded star ranks
- Custom button styles, panels, and visual effects

---

## Gap Analysis: What's Missing for Skills/Passives UI

### No UI Representation of Passives

**Current State**: Passives are invisible to players
- Character tooltips show stats but not passives
- No way to see what passives a character has
- No way to read passive descriptions
- No indication of which passives are active in combat

**Evidence**:
```python
# endless_idler/ui/party_builder_common.py, build_character_stats_tooltip()
# Lines 109-212 - No passive information included
stat_pairs: list[tuple[str, object]] = [
    ("HP", f"{stats.hp} / {stats.max_hp}"),
    ("ATK", stats.atk),
    # ... other stats ...
    # MISSING: Passive abilities
]
```

### No Skills/Passives Screen

**Current State**: No dedicated view for skills
- Main menu has buttons for Run, Warp, Inventory, Guidebook, Settings, Feedback
- All buttons except "Run" show "not implemented yet" dialogs
- No "Skills" or "Passives" menu option exists

**File**: `endless_idler/ui/main_menu.py` (lines 58-64)
```python
menu_layout.addWidget(self._make_button("Run", self.play_requested.emit))
menu_layout.addWidget(self._make_button("Warp", self.warp_requested.emit))
menu_layout.addWidget(self._make_button("Inventory", self.inventory_requested.emit))
menu_layout.addWidget(self._make_button("Guidebook", self.guidebook_requested.emit))
menu_layout.addWidget(self._make_button("Settings", self.settings_requested.emit))
menu_layout.addWidget(self._make_button("Feedback", self.feedback_requested.emit))
# MISSING: Skills/Passives button
```

---

## Technical Architecture Analysis

### Data Flow for Passives

```
Character Definition (characters/*.py)
    ↓
    passives: list[str] = ["passive_id_1", "passive_id_2"]
    ↓
Metadata Extraction (metadata.py)
    ↓
    _extract_passives_from_classdef() → passive IDs
    ↓
Character Plugin Discovery (plugins.py)
    ↓
    CharacterPlugin.passives: list[str]
    ↓
Combat Character Loading (ui/battle/sim.py)
    ↓
    load_passives_for_character() → passive instances
    ↓
Stats Object
    ↓
    stats._passive_instances: list[Passive]
    ↓
Combat Execution (ui/battle/screen.py)
    ↓
    trigger_turn_start_passives() / apply_pre_damage_passives() / etc.
```

### Access Points for UI

To build a Skills/Passives UI, we need access to:

1. **Character List**: Available via `discover_character_plugins()`
   - File: `endless_idler/characters/plugins.py`
   - Returns: `list[CharacterPlugin]`
   - Each plugin has: `char_id`, `display_name`, `passives: list[str]`

2. **Passive Definitions**: Available via registry functions
   - File: `endless_idler/passives/registry.py`
   - `list_passives()` → all registered passive IDs
   - `load_passive(passive_id)` → passive instance with metadata
   - Each passive has: `id`, `display_name`, `description`, `triggers`

3. **Player's Characters**: Available via save system
   - File: `endless_idler/save.py`
   - `SaveManager.load()` → `RunSave`
   - `RunSave.bar_characters: list[str]` - characters in bar slots
   - `RunSave.character_progress: dict[str, CharacterProgress]` - per-character data

---

## Recommendations for Implementation

### Option A: Add to Main Menu (Recommended)

**Approach**: Add a "Skills" button to the main menu that opens a dedicated screen

**Pros**:
- Follows existing pattern (Run, Warp, Inventory, etc.)
- Dedicated space for comprehensive passive display
- Can show all characters and their passives
- Easy to implement using `QStackedWidget` pattern

**Cons**:
- One more navigation hop to view passives
- Not contextual to party building

**Implementation Steps**:

1. **Create Skills Widget** (`endless_idler/ui/skills_screen.py`)
   ```python
   class SkillsScreenWidget(QWidget):
       back_requested = Signal()
       
       def __init__(self, parent: QWidget | None = None):
           # Layout with:
           # - Back button
           # - Character list (left panel)
           # - Selected character's passives (right panel)
           # - Passive details when clicked
   ```

2. **Add to Main Menu** (`endless_idler/ui/main_menu.py`)
   ```python
   # In MainMenuWidget.__init__:
   menu_layout.addWidget(self._make_button("Skills", self.skills_requested.emit))
   
   # In MainMenuWindow.__init__:
   menu.skills_requested.connect(self._open_skills_screen)
   
   def _open_skills_screen(self):
       if self._skills_screen is None:
           self._skills_screen = SkillsScreenWidget()
           self._skills_screen.back_requested.connect(self._open_main_menu)
           self._stack.addWidget(self._skills_screen)
       self._stack.setCurrentWidget(self._skills_screen)
   ```

3. **Character List Component**
   - Scrollable list of characters (similar to party builder)
   - Show character portrait, name, level
   - Click to select and view passives

4. **Passive Display Component**
   - Show all passives for selected character
   - For each passive:
     - Display name
     - Description
     - Trigger points (when it activates)
     - Visual indicator if passive is multi-trigger
   - Use stained glass theme for consistency

### Option B: Add to Character Tooltips (Quick Win)

**Approach**: Extend `build_character_stats_tooltip()` to include passive information

**Pros**:
- Minimal code changes
- Contextual - shows passives where characters are displayed
- No new screens needed
- Quick to implement

**Cons**:
- Limited space in tooltips
- May make tooltips very tall
- Only shows passives when hovering

**Implementation**:

**File**: `endless_idler/ui/party_builder_common.py`

```python
def build_character_stats_tooltip(
    *,
    name: str,
    stars: int | None = None,
    stacks: int | None = None,
    stackable: bool | None = None,
    stats: Stats | None = None,
    passive_ids: list[str] | None = None,  # NEW PARAMETER
) -> str:
    # ... existing code ...
    
    # After stat_rows, add passive section:
    passive_section = ""
    if passive_ids:
        from endless_idler.passives.registry import load_passive
        passive_rows = []
        for passive_id in passive_ids:
            passive = load_passive(passive_id)
            if passive:
                passive_rows.append(
                    f"<tr><td colspan='2' style='padding: 4px 10px;'>"
                    f"<b>{html.escape(passive.display_name)}</b><br/>"
                    f"<span style='color: rgba(255, 255, 255, 170); font-size: 11px;'>"
                    f"{html.escape(passive.description)}</span>"
                    f"</td></tr>"
                )
        if passive_rows:
            passive_section = (
                "<tr><td colspan='2' style='padding: 6px 10px 2px 10px;'>"
                "<b>Passive Abilities</b>"
                "</td></tr>"
                + "".join(passive_rows)
            )
    
    return (
        "<div style='min-width: 280px; max-width: 340px;'>"
        # ... existing header and stats ...
        + passive_section  # ADD THIS
        + "</table></div>"
    )
```

**Call Sites to Update**:
1. `endless_idler/ui/party_builder_bar.py` (line 344)
2. `endless_idler/ui/party_builder_slot.py` (line 393)
3. `endless_idler/ui/battle/widgets.py` (line 197)
4. `endless_idler/ui/onsite/card.py` (line 231)

Each call site needs to pass `passive_ids=plugin.passives` where `plugin` is the `CharacterPlugin`.

### Option C: Hybrid Approach (Best User Experience)

**Approach**: Combine both options

1. **Quick Win**: Add passive info to tooltips (Option B)
   - Gives immediate visibility
   - Low effort, high value

2. **Full Feature**: Add dedicated Skills screen (Option A)
   - Provides comprehensive view
   - Better for learning and exploration
   - Can show additional info (trigger details, mechanics, etc.)

**Recommended Implementation Order**:
1. Phase 1: Add passives to tooltips (1-2 hours)
2. Phase 2: Create Skills screen (4-6 hours)
3. Phase 3: Add visual indicators for active passives in combat (future enhancement)

---

## Code Locations Reference

### Files to Modify for Tooltip Enhancement (Option B)

**Core Tooltip Builder**:
- `endless_idler/ui/party_builder_common.py`
  - Function: `build_character_stats_tooltip()` (lines 109-212)
  - Add: `passive_ids` parameter and passive section rendering

**Call Sites** (4 locations):
1. `endless_idler/ui/party_builder_bar.py`
   - Line 344: `build_character_stats_tooltip(...)` call
   - Add: `passive_ids=self._plugin.passives if self._plugin else None`

2. `endless_idler/ui/party_builder_slot.py`
   - Line 393: `build_character_stats_tooltip(...)` call
   - Add: `passive_ids=plugin.passives if plugin else None`

3. `endless_idler/ui/battle/widgets.py`
   - Line 197: `build_character_stats_tooltip(...)` call
   - Context: Need to pass plugin reference or passive_ids
   - Note: May need to add passive_ids to `CombatantCard` constructor

4. `endless_idler/ui/onsite/card.py`
   - Line 231: `build_character_stats_tooltip(...)` call
   - Context: `OnsiteCharacterCardBase` base class
   - Note: May need to add passive_ids to constructor parameters

### Files to Create for Skills Screen (Option A)

**New Files**:
1. `endless_idler/ui/skills_screen.py`
   - `SkillsScreenWidget` - Main screen widget
   - `CharacterListPanel` - Left panel with character list
   - `PassiveDetailsPanel` - Right panel with passive info

**Files to Modify**:
1. `endless_idler/ui/main_menu.py`
   - Add "Skills" button to menu (line ~62)
   - Add `skills_requested` signal (line ~28)
   - Add `_open_skills_screen()` method
   - Add `_skills_screen` instance variable
   - Wire up screen to stack widget

### Existing Patterns to Follow

**Screen Widget Pattern**:
```python
# From endless_idler/ui/battle/screen.py
class SkillsScreenWidget(QWidget):
    finished = Signal()  # or back_requested = Signal()
    
    def __init__(self, *, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("skillsScreen")
        # Setup layout...
```

**Tooltip Pattern**:
```python
# From endless_idler/ui/party_builder_slot.py
from endless_idler.ui.tooltip import show_stained_tooltip, hide_stained_tooltip

def enterEvent(self, event):
    html = build_character_stats_tooltip(...)
    show_stained_tooltip(self, html, element_id=damage_type_id)

def leaveEvent(self, event):
    hide_stained_tooltip()
```

**List/Grid Layout Pattern**:
```python
# From endless_idler/ui/party_builder.py
from PySide6.QtWidgets import QGridLayout, QScrollArea

layout = QGridLayout()
layout.setSpacing(8)
for index, item in enumerate(items):
    widget = ItemWidget(item)
    row = index // columns
    col = index % columns
    layout.addWidget(widget, row, col)
```

---

## Testing Considerations

### Manual Testing Checklist

**For Tooltip Enhancement**:
- [ ] Hover over character in party builder bar - passives shown
- [ ] Hover over character in party builder slots - passives shown
- [ ] Hover over character in battle - passives shown
- [ ] Hover over character in idle - passives shown
- [ ] Character with no passives - no passive section shown
- [ ] Character with multiple passives - all shown correctly
- [ ] Passive descriptions are readable and properly formatted
- [ ] Tooltip doesn't exceed screen bounds with many passives

**For Skills Screen**:
- [ ] Skills button appears in main menu
- [ ] Clicking Skills opens the skills screen
- [ ] Back button returns to main menu
- [ ] Character list shows all available characters
- [ ] Clicking a character shows their passives
- [ ] Passive names and descriptions are displayed correctly
- [ ] Trigger information is shown (TURN_START, PRE_DAMAGE, etc.)
- [ ] Screen follows stained glass theme
- [ ] Layout is responsive to window resizing

### Edge Cases

1. **Character with no passives**: `passives: list[str] = field(default_factory=list)`
   - Should not show passive section in tooltip
   - Should show "No passive abilities" message in Skills screen

2. **Unregistered passive ID**: Character has `["invalid_passive_id"]`
   - `load_passive()` returns `None`
   - Should skip gracefully, not crash

3. **Many passives**: Character with 5+ passive abilities
   - Tooltip may become very tall
   - Consider truncation or "... and X more" message
   - Skills screen should handle scrolling

4. **Long descriptions**: Passive with 200+ character description
   - Ensure word wrap works correctly
   - Test tooltip readability

---

## Performance Considerations

### Tooltip Rendering
- `load_passive()` is called for each passive every time tooltip is shown
- **Optimization**: Cache passive instances or use registry's `get_passive()` to avoid instantiation
- Expected impact: Negligible (tooltips are shown on hover, not in tight loop)

### Skills Screen
- Loading all characters and their passives once on screen open
- **Optimization**: Not needed initially, only ~20-30 characters exist
- Future: Add lazy loading if character count exceeds 100+

### Registry Lookup
- `_PASSIVE_REGISTRY` is a dict, O(1) lookup
- No performance concerns

---

## Dependencies and Prerequisites

### Python Dependencies
All required dependencies are already installed:
- `PySide6` - Qt framework for UI
- No additional packages needed

### Code Dependencies
All required modules exist:
- `endless_idler.passives` - Passive system
- `endless_idler.characters.plugins` - Character discovery
- `endless_idler.ui` - UI framework and widgets
- `endless_idler.save` - Save system for player data

### Asset Requirements
**Optional**: Passive ability icons
- Current: No icons exist for passives
- Future enhancement: Add icons in `endless_idler/assets/icons/passives/`
- Format: PNG, 64x64 or 128x128
- Not required for initial implementation (can use text-only)

---

## Integration Points Summary

### Where Passives Are Accessed in Combat

1. **Character Creation** (`endless_idler/ui/battle/sim.py`)
   - `build_party()` (line 121): `load_passives_for_character()`
   - `build_reserves()` (line 167): `load_passives_for_character()`

2. **Combat Triggers** (`endless_idler/ui/battle/screen.py`)
   - Line 387: `trigger_turn_start_passives()` - TURN_START trigger
   - Line 500: `apply_target_selection_passives()` - TARGET_SELECTION for party attacks
   - Line 583: `apply_target_selection_passives()` - TARGET_SELECTION for foe attacks
   - Line 641: `apply_target_selection_passives()` - TARGET_SELECTION for reserve attacks

3. **Damage Calculation** (`endless_idler/ui/battle/sim.py`)
   - `calculate_damage()` calls `apply_pre_damage_passives()` when context provided

### Where to Surface Passive Info (UI Integration Points)

1. **Party Builder**
   - Character bar (`endless_idler/ui/party_builder_bar.py`)
   - Character slots (`endless_idler/ui/party_builder_slot.py`)
   - **Opportunity**: Add passive indicators to character cards

2. **Battle Screen**
   - Combatant cards (`endless_idler/ui/battle/widgets.py`)
   - **Opportunity**: Show passive trigger notifications in combat log

3. **Idle Screen**
   - Onsite cards (`endless_idler/ui/onsite/card.py`)
   - **Opportunity**: Add passive info to character details

4. **Main Menu**
   - Menu buttons (`endless_idler/ui/main_menu.py`)
   - **Opportunity**: Add dedicated Skills/Passives screen

---

## Known Issues and Limitations

### Backend Limitations

1. **Passive Cooldowns**: Not implemented
   - Passives can trigger every turn if conditions met
   - No way to limit frequency (e.g., "once per 3 turns")

2. **Passive Visual Effects**: Not implemented
   - No animations when passives trigger
   - No visual indicators of active passives in combat

3. **Passive Stacks/Counters**: Not implemented
   - No way to track how many times a passive triggered
   - No "this passive has activated X times this battle" tracking

4. **Conditional Passives**: Limited
   - Conditions are hard-coded in `can_trigger()`
   - No declarative condition system
   - No game state/progression-based activation

### UI Limitations

1. **No Passive UI**: Primary gap (this audit's focus)

2. **No Combat Log for Passives**:
   - Battle screen has no log showing passive activations
   - Players don't see when/why passives trigger

3. **No Passive Management**:
   - Can't enable/disable specific passives
   - Can't prioritize passive execution order

---

## Security and Validation

### Input Validation

**Character Plugin Loading**:
- AST parsing ensures no code execution during metadata extraction
- Safe: `_extract_passives_from_classdef()` uses AST, not `eval()` or `exec()`

**Passive ID Validation**:
- `load_passive()` returns `None` for invalid IDs (safe)
- Registry uses dict lookup (no injection risk)

**Save Data**:
- `RunSave.character_progress` is a dict of character IDs
- Validation needed: Ensure character IDs match known plugins
- Current: `sanitize_save_characters()` handles this

### Error Handling

**Passive Loading Failures**:
```python
# From endless_idler/ui/battle/sim.py, lines 47-52
for passive_id in plugin.passives:
    passive = load_passive(passive_id)
    if passive:  # Graceful handling of None
        loaded_passives.append(passive)
```

**Passive Execution Failures**:
- Wrapped in try-except in execution utilities
- Combat continues even if passive fails
- Silently fails (by design)

**Recommendation**: Add optional logging for passive load failures in development mode.

---

## Documentation Status

### Existing Documentation (✅ Excellent)

**File**: `.codex/implementation/passive-system.md`
- Comprehensive architecture documentation
- Clear examples for creating new passives
- Integration point details
- Testing guidelines
- Well-maintained and accurate

### Missing Documentation

1. **UI Integration Guide**: No docs on how to display passive info in UI
2. **Passive Design Guide**: No guidelines on what makes a good passive ability
3. **Trigger Point Guide**: When to use which trigger (TURN_START vs PRE_DAMAGE, etc.)

### Recommendations

1. Create `.codex/implementation/ui-passives-display.md` after implementing UI
2. Add passive design patterns to `.codex/implementation/passive-system.md`
3. Document trigger selection guidelines in passive system docs

---

## Conclusion

### Summary

The Skills/Passives system is **technically sound and fully functional** at the backend level. The infrastructure is well-designed, documented, and tested. The only gap is **UI representation** - players cannot see what passives their characters have or what they do.

### Priority Assessment

**Priority: HIGH** - This is a user-facing feature gap that impacts player understanding and engagement.

**Effort: LOW to MEDIUM**
- Tooltip enhancement: 1-2 hours
- Full Skills screen: 4-6 hours
- Combined approach: 5-8 hours total

**Impact: HIGH**
- Improves player understanding of character abilities
- Enhances strategic decision-making
- Completes the passive system implementation

### Recommended Implementation Path

**Phase 1: Quick Win (1-2 hours)**
1. Extend `build_character_stats_tooltip()` to include passive info
2. Update 4 call sites to pass passive IDs
3. Test tooltips across all screens
4. Commit with: `[FEAT] Show passive abilities in character tooltips`

**Phase 2: Dedicated UI (4-6 hours)**
1. Create `SkillsScreenWidget` in `endless_idler/ui/skills_screen.py`
2. Add "Skills" button to main menu
3. Implement character list and passive details panels
4. Test navigation and display
5. Commit with: `[FEAT] Add dedicated Skills/Passives screen`

**Phase 3: Future Enhancements** (as needed)
1. Add passive trigger notifications in combat log
2. Add passive icons/visual indicators
3. Add passive management (enable/disable)
4. Add passive activation counters/stats

### Next Steps for Coder

1. **Review this audit** to understand the system
2. **Choose implementation approach** (Option A, B, or C)
3. **Create task file** in `.codex/tasks/wip/ui/` for implementation
4. **Reference files** listed in "Code Locations Reference" section
5. **Follow patterns** documented in "Existing Patterns to Follow" section
6. **Test thoroughly** using "Testing Considerations" checklist
7. **Update documentation** after implementation

### Questions for Task Master

1. **Scope preference**: Tooltip only (Phase 1) or full implementation (Phase 1+2)?
2. **Priority**: Should this be implemented before or after other UI features (Inventory, Guidebook)?
3. **Design approval**: Does the recommended approach align with UX vision?

---

## Appendix: Code Snippets

### A. Sample Character Passive Declaration

```python
# From endless_idler/characters/lady_light.py
from dataclasses import dataclass, field

@dataclass
class LadyLight(PlayerBase):
    id = "lady_light"
    name = "Lady Light"
    placement = "offsite"
    passives: list[str] = field(default_factory=lambda: [
        "lady_light_radiant_aegis",
        "trinity_synergy"
    ])
```

### B. Sample Passive Implementation

```python
# From endless_idler/passives/implementations/lady_light_radiant_aegis.py
from endless_idler.passives.base import Passive
from endless_idler.passives.registry import register_passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext

@register_passive
class LadyLightRadiantAegis(Passive):
    def __init__(self) -> None:
        super().__init__()
        self.id = "lady_light_radiant_aegis"
        self.display_name = "Radiant Aegis"
        self.description = (
            "When Lady Light is offsite, heal all party members "
            "(onsite + offsite) for 50% of her regain stat at the "
            "start of each turn."
        )
        self.triggers = [PassiveTrigger.TURN_START]
        self.heal_multiplier = 0.50
    
    def can_trigger(self, context: TriggerContext) -> bool:
        return context.owner_stats in context.offsite_allies
    
    def execute(self, context: TriggerContext) -> dict[str, Any]:
        base_heal = int(context.owner_stats.regain * self.heal_multiplier)
        # ... healing logic ...
        return {"healed": healed_targets, "total_healing": total_healing}
```

### C. Accessing Passives in UI

```python
# Example: Getting passives for a character
from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.passives.registry import load_passive

# Discover all characters
plugins = discover_character_plugins()
plugin_by_id = {p.char_id: p for p in plugins}

# Get specific character
char_plugin = plugin_by_id.get("lady_light")
if char_plugin and char_plugin.passives:
    print(f"{char_plugin.display_name} has {len(char_plugin.passives)} passives:")
    
    for passive_id in char_plugin.passives:
        passive = load_passive(passive_id)
        if passive:
            print(f"  - {passive.display_name}")
            print(f"    {passive.description}")
            print(f"    Triggers: {[t.value for t in passive.triggers]}")
```

### D. Sample Tooltip HTML Addition

```python
# Extension to build_character_stats_tooltip()
passive_section = ""
if passive_ids:
    from endless_idler.passives.registry import load_passive
    passive_items = []
    
    for passive_id in passive_ids:
        passive = load_passive(passive_id)
        if passive:
            triggers = ", ".join(t.value.upper() for t in passive.triggers)
            passive_items.append(
                f"<div style='margin-bottom: 8px;'>"
                f"<b style='color: #FFD700;'>{html.escape(passive.display_name)}</b><br/>"
                f"<span style='color: rgba(255, 255, 255, 180); font-size: 11px;'>"
                f"{html.escape(passive.description)}</span><br/>"
                f"<span style='color: rgba(255, 200, 100, 150); font-size: 10px; font-style: italic;'>"
                f"Triggers: {triggers}</span>"
                f"</div>"
            )
    
    if passive_items:
        passive_section = (
            "<tr><td colspan='2' style='padding: 10px 10px 4px 10px; "
            "border-top: 1px solid rgba(255, 255, 255, 0.1);'>"
            "<b style='color: rgba(255, 255, 255, 220);'>Passive Abilities</b>"
            "</td></tr>"
            "<tr><td colspan='2' style='padding: 4px 10px 8px 10px;'>"
            + "".join(passive_items)
            + "</td></tr>"
        )
```

---

**End of Audit Report**
