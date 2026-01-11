# Crit Mod System

## Overview

The crit mod system replaces the old dual-stat system (crit rate + crit damage) with a single unified stat called `crit_mod`. This stat determines both critical hit chance and critical damage multiplier through non-linear formulas.

## Design Goals

1. **Simplification**: One stat instead of two reduces complexity for players
2. **Non-linear Progression**: Diminishing returns prevent extreme stat stacking
3. **Balanced Growth**: Early investment is rewarding, but min-maxing has limits
4. **Strategic Choices**: Players must balance crit mod with other stats

## Formulas

### Crit Chance

Every 100 points of crit mod adds 1% crit chance, but it takes 2x more points for each additional 1%.

**Progression Table:**
- 0-100 points: 0% → 1% (100 points needed)
- 100-300 points: 1% → 2% (200 points needed)
- 300-700 points: 2% → 3% (400 points needed)
- 700-1500 points: 3% → 4% (800 points needed)

**Formula:** For the nth percent, the cumulative points needed is `100 * (2^n - 1)`

**Implementation:** `calculate_crit_chance(crit_mod: float) -> float`
- Returns crit chance as a decimal (0.0 to 1.0)
- Capped at 100% (1.0)
- Uses iterative calculation to find the tier and partial progress

### Crit Damage

Every 20 points of crit mod adds 0.05x to the crit damage multiplier (starting at 1.0x base). Every 200 points doubles the points needed per 0.05x increase.

**Progression Table:**
- 0-200 points: 20 points per 0.05x increase
  - At 200: 1.0x + (10 × 0.05x) = 1.5x
- 200-400 points: 40 points per 0.05x increase
  - At 400: 1.5x + (5 × 0.05x) = 1.75x
- 400-600 points: 80 points per 0.05x increase
  - At 600: 1.75x + (2.5 × 0.05x) = 1.875x

**Implementation:** `calculate_crit_damage(crit_mod: float) -> float`
- Returns crit damage multiplier (minimum 1.0x)
- Processes each 200-point tier with appropriate point costs

## Default Values

The default crit mod value is **100 points**, which provides:
- **1.00% crit chance** (down from old 5%)
- **1.25x crit damage** (down from old 2.0x)

This makes crits rarer but keeps them meaningful. The old default values were:
- `crit_rate: 0.05` (5%)
- `crit_damage: 2.0` (2.0x)

## Implementation Details

### Core Module

**File:** `endless_idler/combat/crit_mod.py`

Functions:
- `calculate_crit_chance(crit_mod: float) -> float`
- `calculate_crit_damage(crit_mod: float) -> float`
- `convert_legacy_crit_stats_to_mod(crit_rate: float, crit_damage: float) -> float` (for migration)

### Stats Class Integration

**File:** `endless_idler/combat/stats.py`

Changes:
- Replaced `_base_crit_rate` and `_base_crit_damage` with `_base_crit_mod: float = 100.0`
- Added `crit_mod` property for direct access
- Modified `crit_rate` and `crit_damage` properties to calculate from `crit_mod`
- Kept setters for backward compatibility (approximate conversions)

### Character System

**File:** `endless_idler/characters/metadata.py`
- Updated `DEFAULT_BASE_STATS` to use `crit_mod: 100.0`

**File:** `endless_idler/characters/foe_base.py`
- Replaced `base_crit_rate` and `base_crit_damage` with `base_crit_mod: float = 100.0`

### Party Stats

**File:** `endless_idler/combat/party_stats.py`
- Updated `STAT_SHARE_KEYS` to include `crit_mod` instead of `crit_rate` and `crit_damage`
- Updated `apply_scaled_bases` to handle `crit_mod`

### UI Updates

**File:** `endless_idler/ui/party_builder_common.py`
- Added crit mod display before crit rate and crit damage
- Shows all three values: `Crit Mod: 100`, `Crit Rate: 1.0%`, `Crit Dmg: 1.25x`

**File:** `endless_idler/ui/onsite/stat_bars.py`
- Replaced `crit_rate` bar with `crit_mod` bar
- Tooltip shows crit mod value plus derived rate and damage
- Example: `"Crit Mod 300 (Rate: 2.0%, Dmg: 1.625x)"`

**File:** `endless_idler/ui/theme.py`
- Renamed CSS selectors from `crit_rate` to `crit_mod`
- Kept the same gold/yellow color scheme

### Idle Progression

**File:** `endless_idler/ui/idle/idle_state.py`
- Updated `_apply_weighted_stat_upgrades` to use `crit_mod` instead of `crit_rate` and `crit_damage`
- Adjusted weight calculation: crit_mod values are divided by 10 to account for higher base values

## Backward Compatibility

The `crit_rate` and `crit_damage` properties still exist for backward compatibility:

```python
# Setting crit_rate approximates equivalent crit_mod
stats.crit_rate = 0.05  # Sets crit_mod to ~750

# Setting crit_damage approximates equivalent crit_mod
stats.crit_damage = 2.0  # Sets crit_mod to ~600
```

These are **rough approximations** and are intended only for legacy code compatibility. New code should use `crit_mod` directly.

## Testing

Manual tests confirmed:
- Default value (100) produces expected results (1% rate, 1.25x damage)
- Formula progression matches specification
- Stats class integration works correctly
- Backward compatibility setters function as expected

## Migration Notes

Existing saved games will need to migrate old crit stats to crit_mod. Options:
1. Use `convert_legacy_crit_stats_to_mod()` helper function
2. Reset all characters to default crit_mod of 100
3. Calculate rough equivalents (e.g., 5% rate + 2.0x damage ≈ 300-500 crit mod)

The system is designed to be more conservative than the old system at default values, which helps prevent power creep.

## Balance Considerations

- **Early Game**: 100-300 crit mod is achievable, providing 1-2% crit chance and 1.25-1.625x damage
- **Mid Game**: 300-700 crit mod gives 2-3% crit chance and 1.625-1.953x damage
- **Late Game**: 700+ crit mod provides diminishing returns, encouraging stat diversity
- **Min-Maxing**: Extremely high crit mod (1500+) is possible but requires significant investment

The non-linear formulas ensure that investing in crit mod remains useful throughout the game without becoming overpowered.
