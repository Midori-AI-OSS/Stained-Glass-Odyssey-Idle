# Resource Tooltips Implementation Audit

**Audit Date:** 2025-01-21  
**Auditor:** System Auditor  
**Focus:** Technical implementation analysis for adding tooltips to resource displays

---

## Executive Summary

This audit examines the codebase to determine the optimal approach for adding informative tooltips to resource displays (tokens/gold, party level, party HP, experience). The game already has a sophisticated tooltip system (`StainedGlassTooltip`) that is extensively used for character cards. Adding resource tooltips requires minimal new infrastructure—primarily creating tooltip content and attaching hover events to existing UI widgets.

**Key Findings:**
- ✅ Robust tooltip system already exists and is actively used
- ✅ Resource display widgets are clearly identified and accessible
- ✅ Resource metadata (descriptions, rates, bonuses) is computable from game state
- ✅ Low implementation complexity (2-3 files, ~150 lines of code)
- ⚠️ No centralized resource metadata store currently exists

---

## 1. Resource Inventory

The game has the following primary resources displayed in the UI:

### 1.1 Tokens (Gold/Currency)

**Location:** `RunSave.tokens` (integer)  
**Display Location:** `endless_idler/ui/party_builder_shop_tile.py` (`StandbyShopTile`)
- Widget: `_token_label` (QLabel) displays current token count
- Display format: Plain integer, e.g., "42"
- Update method: `set_tokens(tokens: int)`

**Relevant Code:**
```python
# party_builder_shop_tile.py:46-47
def set_tokens(self, tokens: int) -> None:
    self._token_label.setText(f"{max(0, int(tokens))}")
```

**Sources & Sinks:**
- **Gained from:**
  - Winning battles: Base 5 gold + bonus (see `calculate_gold_bonus`)
  - Losing battles: Base 3 gold + bonus
  - Selling characters: `DEFAULT_CHARACTER_COST` per stack (currently 1 token)
- **Spent on:**
  - Buying characters: `DEFAULT_CHARACTER_COST` per character (1 token)
  - Leveling party: `party_level_up_cost` (dynamic, starts at 4)
  - Rerolling shop: `DEFAULT_SHOP_REROLL_COST` (2 tokens)

**Bonus Calculation:**
```python
# run_rules.py:43-61
def calculate_gold_bonus(tokens: int, winstreak: int) -> int:
    """Each 5 tokens/gold grants +1 gold, soft cap at 100 (becomes 25:1)"""
    total = tokens + winstreak
    if total <= 100:
        return total // 5
    base_bonus = 100 // 5  # 20
    excess = total - 100
    soft_capped_bonus = excess // 25
    return base_bonus + soft_capped_bonus
```

### 1.2 Party Level

**Location:** `RunSave.party_level` (integer), `RunSave.party_level_up_cost` (integer)  
**Display Location:** `endless_idler/ui/party_builder_party_level_tile.py` (`StandbyPartyLevelTile`)
- Widget: `_value` (QLabel) displays level, `_cost` (QLabel) displays upgrade cost
- Display format: "Lv X" and "Cost: Y"
- Update methods: `set_level(level: int)`, `set_cost(cost: int)`

**Relevant Code:**
```python
# party_builder_party_level_tile.py:45-50
def set_level(self, level: int) -> None:
    self._value.setText(f"Lv {max(1, int(level))}")

def set_cost(self, cost: int) -> None:
    cost = max(0, int(cost))
    self._cost.setText(f"Cost: {cost}" if cost else "")
```

**Mechanics:**
- Affects character scaling via `party_scaling()` function
- Cost progression: `next_party_level_up_cost(new_level, previous_cost)`
  - Levels 1-9: `previous_cost * 4 + 2`
  - Level 10+: `ceil(previous_cost * 1.05)` (5% increase)
- Used in battle to determine foe level: `party_level * fight_number * 1.3`

**Cost Formula:**
```python
# save.py:308-313
def next_party_level_up_cost(*, new_level: int, previous_cost: int) -> int:
    if new_level >= 10:
        return max(1, int(math.ceil(previous_cost * 1.05)))
    return max(1, previous_cost * 4 + 2)
```

### 1.3 Party HP

**Location:** `RunSave.party_hp_current`, `RunSave.party_hp_max` (integers)  
**Display Location:** `endless_idler/ui/party_hp_bar.py` (`PartyHpHeader`)
- Widget: `_bar` (QProgressBar) displays HP as progress bar
- Display format: "X / Y" (via progress bar)
- Update method: `set_hp(current: int, max_hp: int)`
- Shown in: Party Builder, Battle Screen, Idle Screen

**Relevant Code:**
```python
# party_hp_bar.py:36-43
def set_hp(self, *, current: int, max_hp: int) -> None:
    max_hp = max(0, int(max_hp))
    current = max(0, int(current))
    current = min(current, max_hp) if max_hp else 0
    self._bar.setRange(0, max_hp if max_hp > 0 else 1)
    self._bar.setValue(current)
    self._bar.setTextVisible(max_hp > 0)
```

**Mechanics:**
```python
# run_rules.py constants
PARTY_HP_LOSS_DAMAGE_PER_FIGHT = 15  # Damage per fight number on loss
PARTY_HP_LOSS_HEAL = 2               # Heal after taking damage (loss)
PARTY_HP_WIN_HEAL = 4                # Heal on victory
IDLE_PARTY_HP_HEAL_AMOUNT = 1        # Amount healed per tick while idle
IDLE_PARTY_HP_HEAL_INTERVAL_SECONDS = 15 * 60  # 15 minutes between idle heals
```

- **Loss:** Take `15 * fight_number` damage, then heal 2 HP. Run ends if HP reaches 0.
- **Victory:** Heal 4 HP (capped at max)
- **Idle Regen:** Heal 1 HP every 15 minutes while idle (if HP < max)

### 1.4 Experience (Per-Character)

**Location:** Character progress data (`RunSave.character_progress[char_id]`)
- `level` (int)
- `exp` (float)
- `next_exp` (float)
- `exp_multiplier` (float)
- `rebirths` (int)

**Display Locations:**
1. **Idle Onsite Cards:** `endless_idler/ui/onsite/card.py` (`IdleOnsiteCharacterCard`)
   - Shows: Level, HP bar, EXP bar with rate
   - Format: "EXP X / Y +Z.ZZ/s"
   
2. **Idle Offsite Cards:** `endless_idler/ui/idle/widgets.py` (`IdleOffsiteCard`)
   - Shows: Level, HP bar, EXP bar with rate
   - Format: "EXP X / Y +Z.ZZ/s"

**Relevant Code:**
```python
# idle/widgets.py:142-148
self._level_label.setText(f"Level: {level}")
self._exp_bar.setRange(0, max(1, int(next_exp)))
self._exp_bar.setValue(int(exp))
if gain_per_second > 0:
    self._exp_bar.setFormat(f"EXP {max(0, int(exp))} / {max(1, int(next_exp))} +{gain_per_second:.2f}/s")
else:
    self._exp_bar.setFormat(f"EXP {max(0, int(exp))} / {max(1, int(next_exp))}")
```

**EXP Gain Calculation:**
- Base gain computed by `IdleGameState.get_exp_gain_per_tick(char_id)`
- Modified by:
  - `exp_multiplier` (from rebirths)
  - `exp_gain_scale` (shop idle mode uses 0.2x)
  - Idle bonuses/penalties (from battle wins/losses)
  - Shared EXP percentage (upgradeable idle stat)

---

## 2. Existing Tooltip System

### 2.1 Tooltip Infrastructure

**File:** `endless_idler/ui/tooltip.py`

**Key Components:**

1. **`StainedGlassTooltip` class** (QFrame)
   - Custom tooltip widget with stained-glass aesthetic
   - Supports rich HTML content
   - Element-based color tinting (for damage types)
   - Auto-positioning near cursor with screen-edge detection
   - Blur/shadow effects for visual polish

2. **Public API:**
   ```python
   def show_stained_tooltip(owner: QWidget, html: str, *, element_id: str | None = None) -> None
   def hide_stained_tooltip() -> None
   ```

3. **Usage Pattern:**
   ```python
   # In widget class
   def enterEvent(self, event: object) -> None:
       html = self._build_tooltip_html()
       show_stained_tooltip(self, html, element_id=self._element_id)
       super().enterEvent(event)
   
   def leaveEvent(self, event: object) -> None:
       hide_stained_tooltip()
       super().leaveEvent(event)
   ```

### 2.2 Current Tooltip Usage

**Character Cards:**
- Party Builder shop tiles (`party_builder_bar.py:359-370`)
- Party Builder slot tiles (`party_builder_slot.py:421`)
- Onsite character cards (`onsite/card.py:273`)
- Battle combatant cards (`battle/widgets.py:211`)

**Tooltip Content:**
- Generated by `build_character_stats_tooltip()` in `party_builder_common.py:109-241`
- Shows: Name, stars, level, exp, stats table, passive abilities
- Full HTML with styling, tables, conditional sections

### 2.3 Tooltip HTML Structure Example

```python
# From party_builder_common.py
def build_character_stats_tooltip(...) -> str:
    return (
        "<div style='min-width: 280px; max-width: 340px;'>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        # Header with name and stars
        "<tr><td colspan='2'>...</td></tr>"
        # Stats table with alternating row backgrounds
        "<tr><td>ATK</td><td>1234</td></tr>"
        # Passive abilities section (conditional)
        "</table>"
        "</div>"
    )
```

---

## 3. Recommended Implementation Approach

### 3.1 Architecture

**Strategy:** Extend existing widgets with hover event handlers and tooltip content generation.

**Files to Modify:**
1. `endless_idler/ui/party_builder_shop_tile.py` - Add tooltip to tokens display
2. `endless_idler/ui/party_builder_party_level_tile.py` - Add tooltip to party level tile
3. `endless_idler/ui/party_hp_bar.py` - Add tooltip to party HP bar

**New Files (Optional but Recommended):**
4. `endless_idler/ui/resource_tooltips.py` - Centralized tooltip content generators

### 3.2 Implementation Steps

#### Step 1: Create Resource Tooltip Content Generators

Create `endless_idler/ui/resource_tooltips.py`:

```python
from __future__ import annotations

import html


def build_tokens_tooltip(*, current: int, bonus: int, winstreak: int) -> str:
    """Generate tooltip HTML for tokens/gold display."""
    safe_current = max(0, int(current))
    safe_bonus = max(0, int(bonus))
    safe_winstreak = max(0, int(winstreak))
    
    total = safe_current + safe_winstreak
    soft_capped = total > 100
    
    return (
        "<div style='min-width: 240px;'>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        "<tr><td colspan='2' style='padding: 8px 10px; border-bottom: 2px solid #FFD700;'>"
        "<b style='font-size: 13px; color: #FFD700;'>Tokens (Gold)</b>"
        "</td></tr>"
        
        "<tr><td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Current:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: rgba(255,255,255,235);'><b>{safe_current}</b></td></tr>"
        
        "<tr style='background: rgba(255,255,255,0.04);'>"
        "<td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Winstreak:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: rgba(255,255,255,235);'><b>{safe_winstreak}</b></td></tr>"
        
        "<tr><td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Battle Bonus:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: #FFD700;'><b>+{safe_bonus}</b></td></tr>"
        
        "<tr><td colspan='2' style='padding: 10px; border-top: 1px solid rgba(255,255,255,0.1);'>"
        "<div style='color: rgba(255,255,255,180); font-size: 11px; line-height: 1.4;'>"
        "<b>Earning:</b><br/>"
        "• Win: 5 + bonus<br/>"
        "• Loss: 3 + bonus<br/>"
        "• Sell character: 1 per stack<br/><br/>"
        "<b>Spending:</b><br/>"
        "• Buy character: 1<br/>"
        "• Level up party: varies<br/>"
        "• Reroll shop: 2<br/><br/>"
        f"<b>Bonus Formula:</b><br/>"
        f"Every 5 tokens+winstreak = +1 gold<br/>"
        + (f"<span style='color: #FF3B30;'>Soft cap active (100+)</span>" if soft_capped else "")
        + "</div>"
        "</td></tr>"
        "</table>"
        "</div>"
    )


def build_party_level_tooltip(
    *, 
    level: int, 
    cost: int,
    next_cost: int | None = None,
) -> str:
    """Generate tooltip HTML for party level display."""
    safe_level = max(1, int(level))
    safe_cost = max(0, int(cost))
    
    cost_info = f"Next: {safe_cost} tokens"
    if next_cost is not None and next_cost != safe_cost:
        cost_info += f" (then {next_cost})"
    
    scaling_desc = "Characters scale with party level"
    foe_desc = "Foe level = Party Level × Fight# × 1.3"
    
    cost_formula = (
        "Levels 1-9: Cost × 4 + 2<br/>"
        "Level 10+: Cost × 1.05 (rounded up)"
    )
    
    return (
        "<div style='min-width: 260px;'>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        "<tr><td colspan='2' style='padding: 8px 10px; border-bottom: 2px solid #4A9EFF;'>"
        "<b style='font-size: 13px; color: #4A9EFF;'>Party Level</b>"
        "</td></tr>"
        
        "<tr><td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Current Level:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: rgba(255,255,255,235);'><b>{safe_level}</b></td></tr>"
        
        "<tr style='background: rgba(255,255,255,0.04);'>"
        "<td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Upgrade Cost:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: #FFD700;'><b>{safe_cost}</b> tokens</td></tr>"
        
        "<tr><td colspan='2' style='padding: 10px; border-top: 1px solid rgba(255,255,255,0.1);'>"
        "<div style='color: rgba(255,255,255,180); font-size: 11px; line-height: 1.4;'>"
        f"<b>Effect:</b><br/>{html.escape(scaling_desc)}<br/><br/>"
        f"<b>Foe Scaling:</b><br/>{html.escape(foe_desc)}<br/><br/>"
        f"<b>Cost Growth:</b><br/>{cost_formula}"
        "</div>"
        "</td></tr>"
        "</table>"
        "</div>"
    )


def build_party_hp_tooltip(
    *,
    current: int,
    max_hp: int,
    fight_number: int,
) -> str:
    """Generate tooltip HTML for party HP display."""
    safe_current = max(0, int(current))
    safe_max = max(1, int(max_hp))
    safe_fight = max(1, int(fight_number))
    
    percentage = (safe_current / safe_max * 100) if safe_max > 0 else 0
    loss_damage = 15 * safe_fight
    
    status = "Healthy"
    status_color = "#4AFF4A"
    if percentage < 25:
        status = "Critical"
        status_color = "#FF3B30"
    elif percentage < 50:
        status = "Wounded"
        status_color = "#FF9500"
    
    return (
        "<div style='min-width: 260px;'>"
        "<table style='width: 100%; border-collapse: collapse;'>"
        "<tr><td colspan='2' style='padding: 8px 10px; border-bottom: 2px solid #FF3B30;'>"
        "<b style='font-size: 13px; color: #FF3B30;'>Party HP</b>"
        "</td></tr>"
        
        "<tr><td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Current HP:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: rgba(255,255,255,235);'>"
        f"<b>{safe_current} / {safe_max}</b></td></tr>"
        
        "<tr style='background: rgba(255,255,255,0.04);'>"
        "<td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Status:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: {status_color};'><b>{status}</b> ({percentage:.1f}%)</td></tr>"
        
        "<tr><td style='padding: 6px 10px; color: rgba(255,255,255,170);'>Next Loss Damage:</td>"
        f"<td style='padding: 6px 10px; text-align: right; color: #FF9500;'><b>{loss_damage}</b></td></tr>"
        
        "<tr><td colspan='2' style='padding: 10px; border-top: 1px solid rgba(255,255,255,0.1);'>"
        "<div style='color: rgba(255,255,255,180); font-size: 11px; line-height: 1.4;'>"
        "<b>Mechanics:</b><br/>"
        "• Loss: Take (15 × Fight#) damage, then heal 2<br/>"
        "• Victory: Heal 4 HP<br/>"
        "• Idle: Heal 1 HP every 15 minutes<br/>"
        "• Run ends when HP reaches 0"
        "</div>"
        "</td></tr>"
        "</table>"
        "</div>"
    )
```

**Estimated Size:** ~200 lines

#### Step 2: Add Hover Events to Token Display

Modify `endless_idler/ui/party_builder_shop_tile.py`:

```python
# Add imports at top
from endless_idler.ui.tooltip import hide_stained_tooltip, show_stained_tooltip
from endless_idler.ui.resource_tooltips import build_tokens_tooltip

class StandbyShopTile(QFrame):
    # ... existing code ...
    
    def __init__(self, *, tokens: int = 0, open_: bool = True) -> None:
        # ... existing initialization ...
        
        # Store for tooltip generation
        self._current_tokens = tokens
        self._bonus = 0
        self._winstreak = 0
        
        # Make token label accept mouse events
        self._token_label.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
    
    def set_tokens(self, tokens: int, *, bonus: int = 0, winstreak: int = 0) -> None:
        self._current_tokens = max(0, int(tokens))
        self._bonus = max(0, int(bonus))
        self._winstreak = max(0, int(winstreak))
        self._token_label.setText(f"{self._current_tokens}")
    
    def enterEvent(self, event: object) -> None:
        html = build_tokens_tooltip(
            current=self._current_tokens,
            bonus=self._bonus,
            winstreak=self._winstreak,
        )
        show_stained_tooltip(self, html)
        try:
            super().enterEvent(event)
        except Exception:
            pass
    
    def leaveEvent(self, event: object) -> None:
        hide_stained_tooltip()
        try:
            super().leaveEvent(event)
        except Exception:
            pass
```

**Changes:** ~30 lines added/modified

#### Step 3: Add Hover Events to Party Level Display

Modify `endless_idler/ui/party_builder_party_level_tile.py`:

```python
# Add imports
from endless_idler.ui.tooltip import hide_stained_tooltip, show_stained_tooltip
from endless_idler.ui.resource_tooltips import build_party_level_tooltip

class StandbyPartyLevelTile(QFrame):
    # ... existing code ...
    
    def __init__(self, *, level: int = 1, cost: int = 0) -> None:
        # ... existing initialization ...
        
        # Store for tooltip
        self._level = level
        self._cost = cost
        
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
    
    def set_level(self, level: int) -> None:
        self._level = max(1, int(level))
        self._value.setText(f"Lv {self._level}")
    
    def set_cost(self, cost: int) -> None:
        self._cost = max(0, int(cost))
        self._cost.setText(f"Cost: {self._cost}" if self._cost else "")
    
    def enterEvent(self, event: object) -> None:
        # Calculate next cost for preview
        from endless_idler.save import next_party_level_up_cost
        next_cost = next_party_level_up_cost(
            new_level=self._level + 1,
            previous_cost=self._cost
        )
        
        html = build_party_level_tooltip(
            level=self._level,
            cost=self._cost,
            next_cost=next_cost,
        )
        show_stained_tooltip(self, html)
        try:
            super().enterEvent(event)
        except Exception:
            pass
    
    def leaveEvent(self, event: object) -> None:
        hide_stained_tooltip()
        try:
            super().leaveEvent(event)
        except Exception:
            pass
```

**Changes:** ~35 lines added/modified

#### Step 4: Add Hover Events to Party HP Bar

Modify `endless_idler/ui/party_hp_bar.py`:

```python
# Add imports
from endless_idler.ui.tooltip import hide_stained_tooltip, show_stained_tooltip
from endless_idler.ui.resource_tooltips import build_party_hp_tooltip

class PartyHpHeader(QFrame):
    # ... existing code ...
    
    def __init__(self, parent: QFrame | None = None) -> None:
        # ... existing initialization ...
        
        # Store for tooltip
        self._current = 0
        self._max_hp = 0
        self._fight_number = 1
        
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
    
    def set_hp(self, *, current: int, max_hp: int, fight_number: int = 1) -> None:
        self._max_hp = max(0, int(max_hp))
        self._current = max(0, int(current))
        self._current = min(self._current, self._max_hp) if self._max_hp else 0
        self._fight_number = max(1, int(fight_number))
        
        self._bar.setRange(0, self._max_hp if self._max_hp > 0 else 1)
        self._bar.setValue(self._current)
        self._bar.setTextVisible(self._max_hp > 0)
    
    def enterEvent(self, event: object) -> None:
        html = build_party_hp_tooltip(
            current=self._current,
            max_hp=self._max_hp,
            fight_number=self._fight_number,
        )
        show_stained_tooltip(self, html)
        try:
            super().enterEvent(event)
        except Exception:
            pass
    
    def leaveEvent(self, event: object) -> None:
        hide_stained_tooltip()
        try:
            super().leaveEvent(event)
        except Exception:
            pass
```

**Changes:** ~35 lines added/modified

#### Step 5: Update Callers to Pass Additional Context

Modify callers of these widgets to pass bonus/winstreak/fight_number data:

**In `party_builder.py`:**
```python
# Around line 1031-1034
def _refresh_tokens(self) -> None:
    if self._shop_tile is None:
        return
    bonus = calculate_gold_bonus(self._save.tokens, self._save.winstreak)
    self._shop_tile.set_tokens(
        self._save.tokens, 
        bonus=bonus, 
        winstreak=self._save.winstreak
    )

# Around line 1035-1041
def _refresh_party_hp(self) -> None:
    if self._party_hp_header is None:
        return
    self._party_hp_header.set_hp(
        current=int(getattr(self._save, "party_hp_current", 0)),
        max_hp=int(getattr(self._save, "party_hp_max", 0)),
        fight_number=int(getattr(self._save, "fight_number", 1)),
    )
```

**Similar changes needed in:**
- `endless_idler/ui/idle/screen.py` (lines ~126-128, 226-228)
- `endless_idler/ui/battle/screen.py` (lines ~155-157, 288-290)

**Estimated Changes:** ~10 lines per file × 3 files = 30 lines

---

## 4. Code Locations Reference

### 4.1 Resource Display Widgets

| Resource | File | Class | Display Widget | Update Method |
|----------|------|-------|----------------|---------------|
| Tokens | `ui/party_builder_shop_tile.py` | `StandbyShopTile` | `_token_label` (QLabel) | `set_tokens(tokens)` |
| Party Level | `ui/party_builder_party_level_tile.py` | `StandbyPartyLevelTile` | `_value`, `_cost` (QLabel) | `set_level()`, `set_cost()` |
| Party HP | `ui/party_hp_bar.py` | `PartyHpHeader` | `_bar` (QProgressBar) | `set_hp(current, max_hp)` |
| Character EXP | `ui/onsite/card.py` | `IdleOnsiteCharacterCard` | Inherited from base | `set_exp()` |
| Character EXP | `ui/idle/widgets.py` | `IdleOffsiteCard` | `_exp_bar` (QProgressBar) | Direct setting |

### 4.2 Resource Logic & Constants

| Logic | File | Function/Constant |
|-------|------|-------------------|
| Gold bonus calculation | `run_rules.py` | `calculate_gold_bonus(tokens, winstreak)` |
| Party level cost | `save.py` | `next_party_level_up_cost(new_level, previous_cost)` |
| Party HP damage/heal | `run_rules.py` | Constants + `apply_battle_result()` |
| EXP gain calculation | `ui/idle/idle_state.py` | `get_exp_gain_per_second()`, `get_exp_gain_per_tick()` |

### 4.3 Tooltip System

| Component | File | Line Range |
|-----------|------|------------|
| Tooltip widget | `ui/tooltip.py` | 44-177 |
| Public API | `ui/tooltip.py` | 24-42 |
| Character tooltip builder | `ui/party_builder_common.py` | 109-241 |
| Usage examples | `ui/party_builder_bar.py` | 359-382 |

---

## 5. Implementation Complexity Estimate

### 5.1 Time Estimate

**Total Development Time:** 3-4 hours for experienced developer

Breakdown:
- Create `resource_tooltips.py`: 1.5 hours
  - Write 3 tooltip builders with HTML formatting
  - Test rendering and layout
- Modify 3 widget files: 1.5 hours
  - Add hover events
  - Store necessary state
  - Test tooltip display
- Update callers: 1 hour
  - Pass bonus/winstreak/fight_number
  - Test in all 3 screens (Party Builder, Battle, Idle)

### 5.2 Risk Assessment

**Low Risk Implementation**

✅ **Strengths:**
- Tooltip system is mature and well-tested
- Changes are localized to specific widgets
- No database/save format changes required
- Easy to test and iterate

⚠️ **Potential Issues:**
- Need to ensure hover events don't interfere with click events
- Must test tooltip positioning on all screens
- HTML formatting may need adjustment for readability

🔧 **Mitigation:**
- Follow existing hover event patterns from character cards
- Test on different screen sizes/resolutions
- Copy HTML styling from `build_character_stats_tooltip()` for consistency

### 5.3 Testing Checklist

- [ ] Tokens tooltip shows correct bonus calculation
- [ ] Tokens tooltip updates when winstreak changes
- [ ] Party level tooltip shows correct cost progression
- [ ] Party HP tooltip shows correct next damage amount
- [ ] Tooltips display correctly near screen edges
- [ ] Tooltips don't block clickable areas
- [ ] Tooltips hide properly on mouse leave
- [ ] All tooltips render correctly in Party Builder
- [ ] Party HP tooltip works in Idle screen
- [ ] Party HP tooltip works in Battle screen
- [ ] HTML formatting is consistent with character tooltips

---

## 6. Alternative Approaches Considered

### 6.1 Centralized Resource Metadata Store

**Approach:** Create a `resources.py` module with resource definitions.

```python
@dataclass
class ResourceDefinition:
    id: str
    display_name: str
    description: str
    icon: str | None = None
    
RESOURCES = {
    "tokens": ResourceDefinition(
        id="tokens",
        display_name="Tokens",
        description="Currency earned from battles...",
    ),
    # ...
}
```

**Pros:**
- Centralized documentation
- Easy to add more resources later
- Consistent descriptions

**Cons:**
- Adds complexity for current needs
- Tooltip content still needs per-widget context
- Not necessary for small number of resources

**Recommendation:** Skip for now, implement if more resources are added

### 6.2 Qt Native Tooltips

**Approach:** Use `QWidget.setToolTip(text)` with plain text.

**Pros:**
- Simplest implementation
- No custom code needed

**Cons:**
- Plain text only (no formatting)
- Doesn't match game aesthetic
- Less informative than rich HTML

**Recommendation:** Don't use, inconsistent with existing game UI

### 6.3 Tooltip Manager Service

**Approach:** Create a tooltip manager that registers widgets and handles all events.

**Pros:**
- Centralized tooltip logic
- Automatic event handling

**Cons:**
- Over-engineered for current needs
- Harder to customize per-widget
- More complex debugging

**Recommendation:** Current approach is sufficient, avoid premature abstraction

---

## 7. Recommendations for Coder

### 7.1 Implementation Priority

**Recommended Order:**
1. ✅ Create `ui/resource_tooltips.py` with all 3 builders (tokens, party level, party HP)
2. ✅ Add tooltip to tokens display (most valuable for players)
3. ✅ Add tooltip to party level (second most valuable)
4. ✅ Add tooltip to party HP (useful but less critical)
5. ✅ Update all callers to pass context data
6. ✅ Test on all 3 screens

**Rationale:** Tokens and party level are clicked frequently for upgrades, making tooltips most valuable there. Party HP is informative but less actionable.

### 7.2 Code Style Guidelines

**Follow Existing Patterns:**
- Use same HTML structure as `build_character_stats_tooltip()`
- Use same color scheme: `#FFD700` (gold), `#4A9EFF` (blue), `#FF3B30` (red)
- Use same enter/leave event pattern as `party_builder_bar.py:359-382`
- Handle exceptions in event handlers (tooltip bugs shouldn't crash game)

**HTML Styling:**
- Use inline styles (no external CSS)
- Use `rgba(255,255,255,X)` for text transparency
- Use alternating row backgrounds for tables: `rgba(255,255,255,0.04)`
- Keep tooltip width between 240-340px
- Use 11px font for body text, 13px for headers

### 7.3 Testing Strategy

**Manual Testing:**
1. Launch game and enter Party Builder
2. Hover over tokens display → verify tooltip shows
3. Win/lose battles → verify bonus updates correctly
4. Hover over party level → verify cost formula matches actual
5. Hover over party HP → verify damage calculation is accurate
6. Navigate to Idle screen → verify party HP tooltip still works
7. Navigate to Battle screen → verify party HP tooltip still works
8. Test near screen edges → verify tooltip repositions

**Edge Cases:**
- Tokens = 0 (should still show tooltip)
- Party HP = 0 (run should end, but test if it reaches this state)
- Very high party level (test cost formula at level 100+)
- Winstreak = 0 vs. winstreak > 100 (test soft cap display)

### 7.4 Known Gotchas

1. **Event Handler Exceptions:** Wrap `super().enterEvent()` in try/except to prevent crashes
2. **Widget State:** Store current values in widget to avoid querying parent/save on every hover
3. **Caller Updates:** Must update ALL callers that create HP bars (3 screens: party builder, battle, idle)
4. **Fight Number:** Not available in `PartyHpHeader` by default, must pass as parameter
5. **Tooltip Singleton:** Only one tooltip can show at a time (managed by `_TOOLTIP` global in `tooltip.py`)

### 7.5 Future Enhancements

**After Initial Implementation:**
- Add tooltip to character EXP bars (show rebirth info, multipliers)
- Add tooltip to shop reroll button (show cost, explain reroll mechanics)
- Add tooltip to idle mode stat upgrades (show formulas, current effect)
- Add animated transitions when tooltip content changes
- Add keyboard shortcut to toggle persistent tooltip mode

**Resource Metadata System:**
If more resources are added (e.g., gems, crystals, special currencies), consider refactoring to:
- `resources.py` with resource definitions
- Tooltip builder that takes resource ID + current state
- Automatic tooltip attachment via decorator or mixin

---

## 8. Conclusion

**Implementation Verdict:** ✅ **Ready to Implement**

The codebase is well-structured for adding resource tooltips with minimal changes. The existing `StainedGlassTooltip` system provides all necessary infrastructure. Implementation requires:

- **New Code:** ~200 lines (1 new file)
- **Modified Code:** ~100 lines (4 existing files)
- **Total Effort:** 3-4 hours for complete implementation and testing
- **Risk Level:** Low (localized changes, mature tooltip system)

**Key Success Factors:**
1. Follow existing tooltip patterns from character cards
2. Store necessary state in widget classes for hover events
3. Update all callers to pass context data (bonus, winstreak, fight_number)
4. Test on all 3 screens (Party Builder, Battle, Idle)
5. Match existing HTML styling for visual consistency

**Immediate Next Step:**
Create `endless_idler/ui/resource_tooltips.py` with the three tooltip builder functions, then incrementally add hover events to each widget class.

---

## Appendix A: File Structure Summary

```
endless_idler/
├── ui/
│   ├── tooltip.py                          # ✅ Existing - Tooltip system
│   ├── resource_tooltips.py                # 🆕 New - Tooltip content builders
│   ├── party_builder_shop_tile.py          # ✏️ Modify - Add hover events
│   ├── party_builder_party_level_tile.py   # ✏️ Modify - Add hover events
│   ├── party_hp_bar.py                     # ✏️ Modify - Add hover events
│   ├── party_builder.py                    # ✏️ Modify - Update callers
│   ├── idle/
│   │   └── screen.py                       # ✏️ Modify - Update HP bar caller
│   └── battle/
│       └── screen.py                       # ✏️ Modify - Update HP bar caller
├── save.py                                 # ✅ Reference - Resource data, cost formula
└── run_rules.py                            # ✅ Reference - HP mechanics, gold bonus

Legend:
✅ Existing - No changes needed
🆕 New - Create new file
✏️ Modify - Update existing file
```

---

**End of Audit Report**
