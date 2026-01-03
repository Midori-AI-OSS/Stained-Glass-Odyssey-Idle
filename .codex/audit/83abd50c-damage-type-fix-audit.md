# Audit Report: Damage Type Background Colors Fix

**Audit ID:** 83abd50c  
**Date:** 2026-01-03  
**Auditor:** GitHub Copilot (Auditor Mode)  
**Status:** ❌ **FAILED - Fix is Incomplete and Incorrect**

---

## Executive Summary

The attempted fix to transfer `damage_type` from plugin to `Stats` via `apply_plugin_overrides()` is **fundamentally broken** and will not work. The fix makes an incorrect assumption about the `CharacterPlugin` data structure and the order of operations in the call sites.

**Verdict:** This fix is **NOT complete** and will **NOT** resolve the issue. Lady Lightning and Lady Echo will **NOT** show purple backgrounds.

---

## Issues Found

### 1. ❌ CRITICAL: Plugin Structure Mismatch

**Location:** `endless_idler/combat/party_stats.py:90-92`

**Problem:** The fix attempts to access `plugin.damage_type`, but `CharacterPlugin` objects do **not** have a `damage_type` attribute.

**Evidence:**
```python
# From endless_idler/characters/plugins.py:35-44
@dataclass(frozen=True, slots=True)
class CharacterPlugin:
    char_id: str
    display_name: str
    stars: int = 1
    placement: str = "both"
    damage_type_id: str = "generic"  # ← This is the attribute name
    damage_type_random: bool = False
    base_stats: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_BASE_STATS))
    base_aggro: float | None = None
    damage_reduction_passes: int | None = None
```

**Testing:**
```python
plugin = CharacterPlugin(char_id='test', display_name='Test', damage_type_id='lightning')
damage_type = getattr(plugin, 'damage_type', None)  
# Result: None (attribute does not exist)
```

**Impact:** The line `stats.damage_type = damage_type` will never execute because `damage_type` is always `None`.

---

### 2. ❌ CRITICAL: Order of Operations Issue

**Location:** `endless_idler/ui/battle/sim.py:94-95`, `137-138`, `184-185`

**Problem:** In all three call sites (`build_party()`, `build_foes()`, `build_reserves()`), the damage_type is set **AFTER** `build_scaled_character_stats()` but **BEFORE** `apply_plugin_overrides()`:

```python
# Line 94-95
stats.damage_type = load_damage_type(resolve_damage_type_id(plugin, rng))
apply_plugin_overrides(stats, plugin=plugin)
```

**Issue:** Even if the fix worked (which it doesn't), it would be overridden immediately by the explicit assignment on line 94.

**Root Cause:** The `build_scaled_character_stats()` function internally calls `apply_plugin_overrides()` at line 162, but then `sim.py` explicitly sets `damage_type` and calls `apply_plugin_overrides()` again. This creates confusion about where damage_type should be set.

---

### 3. ⚠️ Inconsistent Data Flow

**Location:** Multiple files

**Problem:** The damage_type setting is handled inconsistently across different contexts:

1. **In `build_scaled_character_stats()`** (line 162): `apply_plugin_overrides()` is called, but damage_type is not set
2. **In `sim.py`** (lines 94, 137, 184): damage_type is explicitly set after building stats
3. **In `idle/widgets.py`** (line 203): Relies on `stats.element_id` property which reads from `stats.damage_type`

**Issue:** The idle mode (offsite cards) uses `build_scaled_character_stats()` directly without the sim.py wrapper, so it doesn't get the damage_type assignment at all.

---

### 4. ❌ Incomplete Understanding of Data Flow

**Architecture:**

1. **Character files** define `damage_type: DamageTypeBase = field(default_factory=Lightning)`
2. **AST extraction** extracts the damage type as a string ID: `"lightning"`
3. **CharacterPlugin** stores this as `damage_type_id: str`
4. **Runtime** must convert `damage_type_id` string to a `DamageTypeBase` instance

**Missing Step:** The fix doesn't account for the fact that the plugin stores a string ID, not a DamageTypeBase instance.

---

## What Actually Needs to Happen

To properly fix this issue, the damage_type must be set in `build_scaled_character_stats()` by:

1. Reading `plugin.damage_type_id` (not `plugin.damage_type`)
2. Converting it to a `DamageTypeBase` instance using `load_damage_type()`
3. Assigning it to `stats.damage_type`

**Correct implementation:**
```python
def apply_plugin_overrides(stats: Stats, *, plugin: object | None) -> None:
    if plugin is None:
        return

    # Get damage_type_id from plugin (not damage_type)
    damage_type_id = getattr(plugin, "damage_type_id", None)
    if damage_type_id is not None:
        # Convert string ID to DamageTypeBase instance
        from endless_idler.combat.damage_types import load_damage_type
        stats.damage_type = load_damage_type(damage_type_id)

    # ... rest of function
```

---

## Call Sites Analysis

### ✅ Working (but redundant): `sim.py`
- Lines 94, 137, 184 all explicitly set `damage_type` after building stats
- These work correctly, but they bypass `apply_plugin_overrides()`
- The duplicate call to `apply_plugin_overrides()` is unnecessary

### ❌ Broken: `idle/widgets.py`
- Line 193-200: Calls `build_scaled_character_stats()` directly
- No explicit damage_type assignment
- Relies entirely on `apply_plugin_overrides()` to set it
- **Result:** Offsite idle cards will show generic (no color) instead of lightning (purple)

---

## Testing Requirements

Before marking this as fixed, the following must be verified:

1. **Unit Test:** Create a test that builds stats for Lady Lightning and verifies `stats.damage_type.id == "lightning"`
2. **Idle Mode Test:** Verify offsite idle cards for Lady Lightning and Lady Echo show purple background
3. **Battle Mode Test:** Verify battle cards show purple background (likely already working due to sim.py override)
4. **Tooltip Test:** Verify tooltips show purple border for lightning characters
5. **Edge Cases:** Test characters with `damage_type_random=True` and dual-type characters

---

## Recommendations

### Immediate Actions Required

1. **Fix the implementation** in `apply_plugin_overrides()`:
   - Change `getattr(plugin, "damage_type", None)` to `getattr(plugin, "damage_type_id", None)`
   - Add `load_damage_type()` conversion
   - Import the function at the top of the file

2. **Remove redundant code** in `sim.py`:
   - The lines setting `stats.damage_type` after calling `build_scaled_character_stats()` can be removed
   - The second call to `apply_plugin_overrides()` should be removed
   - This will simplify the code and reduce confusion

3. **Add tests** to prevent regression:
   - Test damage_type is correctly set for all character types
   - Test element_id property returns correct values
   - Test color_for_damage_type_id works end-to-end

### Code Quality Issues

- **Inconsistent patterns:** The damage_type is set in multiple places with different approaches
- **Duplicate operations:** `apply_plugin_overrides()` is called twice in sim.py unnecessarily
- **Missing abstraction:** The conversion from `damage_type_id` to `DamageTypeBase` instance should be centralized

---

## Security Considerations

No security vulnerabilities identified in this change. The damage_type system is purely cosmetic and affects UI rendering only.

---

## Conclusion

The current fix is **fundamentally broken** and will not work due to:

1. Accessing a non-existent attribute (`damage_type` instead of `damage_type_id`)
2. Not converting string ID to DamageTypeBase instance
3. Being overridden by explicit assignments in sim.py
4. Missing the key call site in idle/widgets.py

**Status:** ❌ **BLOCKED** - Code must be revised before testing can proceed.

**Next Steps:**
1. Implement the correct fix as outlined above
2. Remove redundant code in sim.py
3. Add comprehensive tests
4. Re-submit for audit review

---

**Audit completed:** 2026-01-03T13:45:00Z
