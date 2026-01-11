# Prestige System Implementation

## Overview
The prestige system provides a new layer of progression where players can sacrifice their EXP gain rate for permanent stat growth multipliers. This creates strategic decisions about when to prestige for maximum benefit.

## Core Mechanics

### Unlock Condition
- Prestige becomes available when a character's **EXP multiplier >= 10**
- The prestige button appears in the UI when this condition is met
- Prestige button takes priority over rebirth button when both are available

### Prestige Effects

#### 1. EXP Multiplier Reset
When prestige is activated, the character's EXP multiplier is reset according to:

```python
new_exp_mult = max(0.01, 0.5 * (0.5 ** (prestige_count - 1)))
```

**Progression:**
- First prestige (count 0 → 1): 0.5
- Second prestige (count 1 → 2): 0.25
- Third prestige (count 2 → 3): 0.125
- Fourth prestige (count 3 → 4): 0.0625
- Fifth prestige (count 4 → 5): 0.01 (floor hit)
- All subsequent prestiges: remain at 0.01

#### 2. Stat Gain Multiplier
Each prestige doubles the stat gains per level-up:

```python
stat_gain_multiplier = 2.0 ** prestige_count
```

**Progression:**
- 0 prestiges: x1 (base)
- 1 prestige: x2
- 2 prestiges: x4
- 3 prestiges: x8
- 4 prestiges: x16
- 5 prestiges: x32
- etc.

This is applied in `_apply_weighted_stat_upgrades()` by modifying the base gain rate:
```python
base_gain_rate = 0.001  # 0.1% per stat gain
prestige_gain_rate = base_gain_rate * prestige_multiplier
stat_multiplier = 1.0 + prestige_gain_rate
```

#### 3. Post-Floor EXP Penalty
After the EXP multiplier hits the floor (0.01), additional prestiges incur a penalty:
- Each prestige after the 4th doubles the EXP requirement per level
- Formula: `penalty_multiplier = 2.0 ** (prestige_count - 4)`

**Progression:**
- 5th prestige: 2x EXP requirement
- 6th prestige: 4x EXP requirement
- 7th prestige: 8x EXP requirement
- etc.

## Implementation Details

### Data Persistence
The `prestige_count` is tracked per character in:
- `character_progress` dict in `RunSave`
- Persisted through save/load cycles
- Normalized in `save_codec.py`
- Tracked in `idle_state.py` character data

### Code Locations

#### Core Logic
- **`endless_idler/ui/idle/idle_state.py`**
  - `prestige_character(char_id: str) -> bool`: Main prestige method
  - `_apply_weighted_stat_upgrades()`: Applies stat gain multiplier
  - Character data initialization and export

#### Save System
- **`endless_idler/save.py`**
  - `reset_character_progress_for_new_run()`: Preserves prestige_count
  
- **`endless_idler/save_codec.py`**
  - `as_character_progress_dict()`: Loads prestige_count
  - `normalized_character_progress()`: Normalizes prestige_count

#### UI Components
- **`endless_idler/ui/idle/screen.py`**
  - `_prestige_character(char_id: str)`: Handles prestige with confirmation dialog
  - Shows detailed effects and warnings

- **`endless_idler/ui/idle/widgets.py`**
  - `IdleOffsiteCard`: Prestige button for offsite characters
  - Shows/hides based on exp_multiplier >= 10

- **`endless_idler/ui/onsite/card.py`**
  - `IdleOnsiteCharacterCard`: Prestige button for onsite characters
  - Prioritizes prestige over rebirth when available

## User Experience

### Prestige Button Visibility
- Button only appears when EXP multiplier >= 10
- Takes priority over rebirth button
- Available on both onsite and offsite character cards

### Confirmation Dialog
When clicking prestige, a dialog shows:
- Current and new prestige level
- Current and new EXP multiplier
- Current and new stat gain multiplier
- Warning if post-floor penalty applies
- Clear explanation of trade-offs

Example dialog text:
```
Prestige Ally?

Current Prestige Level: 0
New Prestige Level: 1

Effects:
• EXP Multiplier: 15.23 → 0.50
• Stat Gain Multiplier: x1.0 → x2.0

Your stat gains per level will double, but EXP gain rate will be reduced.
```

## Strategic Considerations

### When to Prestige
Players should consider:
1. **Current EXP multiplier**: Higher is better for more prestiges before floor
2. **Character level**: Higher level means more time invested
3. **Stat importance**: More valuable for characters you'll use long-term
4. **Floor approaching**: First 4 prestiges have no penalty

### Synergy with Rebirth
- Rebirth increases EXP multiplier over time
- Combined with prestige, creates a cycle:
  1. Rebirth to gain EXP multiplier
  2. Prestige when multiplier >= 10
  3. Stat gains accelerate with each prestige
  4. Repeat for continuous progression

## Testing Considerations

### Edge Cases Handled
1. **Prestige at exactly 10.0 multiplier**: Works correctly
2. **Multiple rapid prestiges**: Each updates state properly
3. **Save/load with prestige data**: Persists correctly
4. **Floor hit exactly at 0.01**: Penalty applied correctly
5. **UI state updates**: Buttons show/hide correctly

### Formula Validation
All formulas match the task specification:
- EXP multiplier reset: `max(0.01, 0.5 * (0.5 ** (prestige_count - 1)))`
- Stat gain multiplier: `2 ** prestige_count`
- Post-floor penalty: `2 ** (prestige_count - 4)` when at floor

## Future Enhancements (Not Implemented)

Potential additions:
1. Display prestige count on character cards
2. Prestige history/statistics
3. Visual effects when prestiging
4. Prestige-based achievements
5. Alternative prestige paths with different trade-offs

## Related Tasks
- `98bb5c95-prestige-system-unlock-mechanic.md` - Core mechanics (COMPLETE)
- `abfd16a2-prestige-system-ui.md` - UI controls (COMPLETE)

## Commits
- `3addbf1` - [FEAT] Add prestige system core mechanics
- `dd6f981` - [FEAT] Add prestige system UI controls
- `958b6da` - [TASKS] Move prestige system tasks to review
