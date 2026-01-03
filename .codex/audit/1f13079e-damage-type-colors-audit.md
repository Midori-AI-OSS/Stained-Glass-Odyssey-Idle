# Audit Report: Damage Type Background Colors Not Working in Idle/Shop/Tooltip Modes

**Audit ID:** 1f13079e  
**Date:** 2026-01-03  
**Auditor:** GitHub Copilot (Auditor Mode)  
**Severity:** High - Visual bug affecting user experience across multiple screens  
**Status:** Root Cause Identified

---

## Executive Summary

Investigation confirmed that damage type background colors work correctly in **battle mode** but fail in **idle mode**, **shop/party builder**, and **tooltips**. The root cause is that the `build_scaled_character_stats()` function does NOT set the `damage_type` attribute on Stats objects, causing the `element_id` property to return the default "generic" value instead of the character's actual element type (e.g., "lightning", "fire", "dark").

---

## User Report Summary

User provided screenshots showing:
1. **Tooltip (Image 1)**: Wrong color - tooltip not showing correct damage type color
2. **Idle Mode (Image 2)**: All cards showing wrong colors:
   - Lady Lightning (should be lightning/purple, showing wrong)
   - Lady Echo (should be lightning/purple, showing wrong)
   - Hilander, Persona Ice, Ixia, Bubbles, Lady Fire, Carly, Lady Darkness (all wrong)
3. **Battle Mode (Image 3)**: Correct colors shown for all characters

User hypothesis: "damage type is not getting passed to the shop menu / idle mode"

---

## Investigation Findings

### 1. Character Element Data Verification

**Finding:** Lady Lightning and Lady Echo ARE correctly defined as Lightning type.

**Evidence:**
- `endless_idler/characters/lady_lightning.py` line 47: `damage_type: DamageTypeBase = field(default_factory=Lightning)`
- `endless_idler/characters/lady_echo.py` line 38: `damage_type: DamageTypeBase = field(default_factory=Lightning)`

**Conclusion:** Character definitions are correct. The issue is NOT in the character data.

---

### 2. Stats Class Element ID Property

**Finding:** The Stats class has a property `element_id` that derives from the `damage_type` attribute.

**Evidence:**
```python
# endless_idler/combat/stats.py lines 246-251
@property
def element_id(self) -> str:
    dt = self.damage_type
    if isinstance(dt, str):
        return dt
    ident = getattr(dt, "id", None) or getattr(dt, "name", None)
    return str(ident or dt)
```

The Stats class has a default `damage_type` of `Generic()` (line 45):
```python
damage_type: DamageTypeBase = field(default_factory=Generic)
```

**Conclusion:** If `damage_type` is not explicitly set after Stats creation, `element_id` will return "generic".

---

### 3. Battle Mode Implementation (WORKING)

**Finding:** Battle mode explicitly sets `stats.damage_type` after calling `build_scaled_character_stats()`.

**Evidence:**
```python
# endless_idler/ui/battle/sim.py lines 86-94
stats = build_scaled_character_stats(
    plugin=plugin,
    party_level=party_level,
    stars=stars,
    stacks=stack_count,
    progress=progress_by_id.get(char_id),
    saved_base_stats=stats_by_id.get(char_id),
)
stats.damage_type = load_damage_type(resolve_damage_type_id(plugin, rng))
```

This pattern appears in 3 locations in `battle/sim.py`:
- Line 94 (in `build_party`)
- Line 137 (in `build_foe_party`)
- Line 184 (in `build_boss_party`)

**Conclusion:** Battle mode works because it manually sets `damage_type` after building stats.

---

### 4. Idle Mode Implementation (BROKEN)

**Finding:** Idle mode calls `build_scaled_character_stats()` but does NOT set `stats.damage_type`.

**Evidence:**
```python
# endless_idler/ui/idle/widgets.py lines 193-207
stats = build_scaled_character_stats(
    plugin=self._plugin,
    party_level=party_level,
    stars=stars,
    stacks=stack_count,
    progress=progress,
    saved_base_stats=saved_base_stats,
)

from endless_idler.ui.battle.colors import color_for_damage_type_id
element_id = getattr(stats, "element_id", "generic")  # Returns "generic" because damage_type not set!
color = color_for_damage_type_id(element_id)
```

**Conclusion:** Idle mode gets "generic" because `stats.damage_type` is never set.

---

### 5. Onsite Cards (Idle Screen) - BROKEN

**Finding:** Onsite character cards also fail to set `damage_type`.

**Evidence:**
```python
# endless_idler/ui/onsite/card.py lines 437-444, then 250-256
stats = build_scaled_character_stats(
    plugin=self._plugin,
    party_level=party_level,
    stars=stars,
    stacks=stack_count,
    progress=progress,
    saved_base_stats=saved_base_stats,
)
# No damage_type assignment here!

# Later in _apply_element_tint:
element_id = getattr(stats, "element_id", "generic")  # Returns "generic"
```

**Conclusion:** Onsite cards have the same bug.

---

### 6. Shop/Party Builder Tooltips (BROKEN)

**Finding:** Tooltips get their stats from `_tooltip_stats_for_character()` which also fails to set `damage_type`.

**Evidence:**
```python
# endless_idler/ui/party_builder.py lines 857-864
stats = build_scaled_character_stats(
    plugin=plugin,
    party_level=party_level,
    stars=stars,
    stacks=stacks,
    progress=self._save.character_progress.get(char_id),
    saved_base_stats=self._save.character_stats.get(char_id),
)
# No damage_type assignment!
# Returns stats with element_id = "generic"
```

Then the tooltip receives the wrong element_id:
```python
# endless_idler/ui/party_builder_slot.py lines 418-419
element_id = getattr(stats, "element_id", None) if stats else None
show_stained_tooltip(self, self._tooltip_html, element_id=element_id)
```

**Conclusion:** Tooltips show wrong colors because they receive "generic" as element_id.

---

### 7. Root Cause Analysis

**ROOT CAUSE:** The `build_scaled_character_stats()` function in `endless_idler/combat/party_stats.py` does NOT set the `damage_type` attribute from the plugin.

**Evidence:** The function `apply_plugin_overrides()` at lines 86-96 only sets:
- `base_aggro`
- `damage_reduction_passes`

It does NOT set `damage_type`.

**All 16 calls to `build_scaled_character_stats()` in the codebase are affected**, but only the 3 calls in `battle/sim.py` work around the issue by explicitly setting `damage_type` after the function returns.

**Locations affected:**
1. ✅ `ui/battle/sim.py` line 86 - **WORKS** (manually sets damage_type on line 94)
2. ✅ `ui/battle/sim.py` line 137 - **WORKS** (manually sets damage_type on line 137)
3. ✅ `ui/battle/sim.py` line 176 - **WORKS** (manually sets damage_type on line 184)
4. ❌ `ui/idle/widgets.py` line 193 - **BROKEN** (no damage_type set)
5. ❌ `ui/idle/screen.py` line 354 - **BROKEN** (no damage_type set)
6. ❌ `ui/idle/idle_state.py` line 224 - **BROKEN** (no damage_type set)
7. ❌ `ui/idle/idle_state.py` line 260 - **BROKEN** (no damage_type set)
8. ❌ `ui/onsite/card.py` line 437 - **BROKEN** (no damage_type set)
9. ❌ `ui/party_builder.py` line 857 - **BROKEN** (tooltips)
10. ❌ `ui/party_builder.py` line 891 - **BROKEN** (offsite reserves)

---

## Answers to User Questions

### 1. Why does battle mode work but idle mode doesn't?

**Answer:** Battle mode explicitly sets `stats.damage_type = load_damage_type(resolve_damage_type_id(plugin, rng))` after calling `build_scaled_character_stats()`. Idle mode does not, so stats.damage_type remains the default Generic() and element_id returns "generic".

### 2. Why are tooltips not showing correct colors?

**Answer:** Tooltips get their stats from `_tooltip_stats_for_character()` which calls `build_scaled_character_stats()` without setting damage_type. The tooltip receives element_id="generic" and displays the wrong color.

### 3. Are Lady Echo and Lady Lightning actually lightning type?

**Answer:** YES. Both are correctly defined with `damage_type: DamageTypeBase = field(default_factory=Lightning)` in their character files. The issue is NOT the character data—it's that the Stats objects never receive this damage_type value.

### 4. Idle mode specific issue - is damage type not being passed?

**Answer:** Correct hypothesis! The damage_type from the plugin is NOT being transferred to the Stats object in idle mode (or anywhere except battle mode).

### 5. Where is the data flow breaking?

**Answer:** The data flow breaks in `build_scaled_character_stats()` and `apply_plugin_overrides()`. The plugin HAS the damage_type data, but these functions don't copy it to the Stats object.

---

## Recommended Fix

### Option 1: Fix `apply_plugin_overrides()` (RECOMMENDED)

Add damage_type handling to `apply_plugin_overrides()` in `endless_idler/combat/party_stats.py`:

```python
def apply_plugin_overrides(stats: Stats, *, plugin: object | None) -> None:
    if plugin is None:
        return
    
    # Add this block:
    damage_type = getattr(plugin, "damage_type", None)
    if damage_type is not None:
        stats.damage_type = damage_type

    base_aggro = getattr(plugin, "base_aggro", None)
    if isinstance(base_aggro, (int, float)):
        stats.base_aggro = float(base_aggro)

    passes = getattr(plugin, "damage_reduction_passes", None)
    if isinstance(passes, int):
        stats.damage_reduction_passes = int(passes)
```

**Why this is best:** 
- Fixes all 16 call sites with a single change
- Maintains consistency with how other plugin attributes are applied
- No need to modify battle mode's workaround (it will just be redundant but harmless)
- DRY principle - don't repeat damage_type assignment everywhere

### Option 2: Add damage_type to every call site (NOT RECOMMENDED)

Manually add `stats.damage_type = load_damage_type(resolve_damage_type_id(plugin, rng))` after every `build_scaled_character_stats()` call.

**Why this is worse:**
- Requires changes in 10+ locations
- Easy to miss locations
- Not DRY
- More maintenance burden

---

## Testing Requirements

After implementing the fix, verify:

1. ✅ Battle mode still shows correct colors (regression test)
2. ✅ Idle offsite cards show correct colors for all characters
3. ✅ Onsite cards (idle screen center) show correct colors
4. ✅ Shop/party builder tooltips show correct colors
5. ✅ Lady Lightning shows purple/lightning color (not dark)
6. ✅ Lady Echo shows purple/lightning color (not dark)
7. ✅ All other characters show their correct element colors

---

## Additional Findings

### Recent Fix Verification

The recent implementation correctly added:
- `QFrame#widgetName` selectors with `!important` flags
- Alpha increased from 20-30 to 60 for better visibility
- Applied to onsite cards, idle widgets, and tooltips

These changes were correct for the styling layer. The issue is in the data layer (Stats.damage_type not being set).

---

## Files Requiring Changes

**Primary fix location:**
- `endless_idler/combat/party_stats.py` - Modify `apply_plugin_overrides()` function (lines 86-96)

**No changes needed in:**
- `endless_idler/ui/onsite/card.py` (styling is correct)
- `endless_idler/ui/idle/widgets.py` (styling is correct)
- `endless_idler/ui/tooltip.py` (styling is correct)
- `endless_idler/ui/battle/sim.py` (battle mode works, manual assignment will become redundant but harmless)
- Character definition files (data is correct)

---

## Impact Assessment

**User Impact:** High - Visual bug affects core gameplay experience and character identification  
**Technical Complexity:** Low - Single function change fixes all instances  
**Risk:** Low - Change is localized and testable  
**Breaking Changes:** None  

---

## Conclusion

The damage type background color system is working correctly at the styling/UI layer. The bug is in the data layer where `build_scaled_character_stats()` fails to transfer the `damage_type` attribute from character plugins to Stats objects. This causes all non-battle mode displays to show "generic" coloring instead of character-specific element colors.

The fix is straightforward: modify `apply_plugin_overrides()` to copy the damage_type from the plugin to the stats object, matching how it already handles base_aggro and damage_reduction_passes.
