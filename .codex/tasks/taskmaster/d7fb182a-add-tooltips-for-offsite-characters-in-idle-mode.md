# Add Tooltips for Off-Site Characters in Idle Mode

## Issue Reference
Part of: Fix tooltip styling, correct character stats display outside combat, and normalize off-site character experience and tooltips

## Problem
Off-site characters in Idle mode have no tooltips when hovering over them. This prevents players from seeing important information like level, stats, and experience for characters not actively in combat.

## Current State
- File: `endless_idler/ui/idle/widgets.py`
- Class: `IdleOffsiteCard` (lines 23-250+)
- The widget displays basic info (portrait, name, level, HP bar, EXP bar)
- No `enterEvent` or `leaveEvent` methods implemented for tooltip display

## Requirements
1. Off-site characters must show tooltips on hover in Idle mode
2. Tooltip content must match existing character tooltip format used elsewhere
3. Display: Name, Level, Experience, Key stats (HP, ATK, Defense, etc.)
4. Use the existing `StainedGlassTooltip` system from `endless_idler/ui/tooltip.py`

## Technical Approach

### Implementation in `endless_idler/ui/idle/widgets.py`

1. **Import tooltip functions** (add to imports at top):
   ```python
   from endless_idler.ui.tooltip import hide_stained_tooltip
   from endless_idler.ui.tooltip import show_stained_tooltip
   from endless_idler.ui.party_builder_common import build_character_stats_tooltip
   ```

2. **Add tooltip HTML generation** to `IdleOffsiteCard`:
   ```python
   def _build_tooltip(self) -> str:
       """Build tooltip HTML for this off-site character."""
       data = self._idle_state.get_char_data(self._char_id)
       if not data:
           return ""
       
       # Get display name from plugin
       display_name = getattr(self._plugin, "display_name", self._char_id) if self._plugin else self._char_id
       stars = int(getattr(self._plugin, "stars", 1) or 1) if self._plugin else 1
       
       # Build stats from current data
       from endless_idler.combat.stats import Stats
       stats = Stats()
       stats.level = int(data.get("level", 1))
       stats.exp = int(data.get("exp", 0))
       stats.exp_multiplier = float(data.get("exp_multiplier", 1.0))
       stats.hp = float(data.get("hp", 0))
       stats.max_hp = float(data.get("max_hp", 1000))
       stats.atk = float(data.get("atk", 0))
       stats.defense = float(data.get("defense", 0))
       stats.regain = float(data.get("regain", 0))
       stats.vitality = float(data.get("vitality", 1.0))
       stats.mitigation = float(data.get("mitigation", 0.0))
       stats.crit_mod = float(data.get("crit_mod", 0))
       stats.effect_hit_rate = float(data.get("effect_hit_rate", 0.0))
       stats.effect_resistance = float(data.get("effect_resistance", 0.0))
       stats.dodge_odds = float(data.get("dodge_odds", 0.0))
       stats.passive_modifier = float(data.get("passive_modifier", 1.0))
       stats.aggro = float(data.get("aggro", 0.0))
       stats.summon_slot_capacity = int(data.get("summon_slot_capacity", 0))
       
       return build_character_stats_tooltip(
           name=display_name,
           stars=stars,
           stacks=self._stack_count,
           stackable=False,
           stats=stats,
       )
   ```

3. **Add event handlers**:
   ```python
   def enterEvent(self, event: object) -> None:
       """Show tooltip when mouse enters the card."""
       html = self._build_tooltip()
       if html:
           show_stained_tooltip(self, html)
       super().enterEvent(event)  # type: ignore[misc]

   def leaveEvent(self, event: object) -> None:
       """Hide tooltip when mouse leaves the card."""
       hide_stained_tooltip()
       super().leaveEvent(event)  # type: ignore[misc]
   ```

4. **Update tooltip on display refresh**: Modify `update_display()` to rebuild tooltip if it's showing:
   ```python
   def update_display(self) -> None:
       # ... existing code ...
       
       # Update tooltip if mouse is currently over the widget
       if self.underMouse():
           html = self._build_tooltip()
           if html:
               show_stained_tooltip(self, html)
   ```

## Reference Implementations
- `endless_idler/ui/battle/widgets.py` - `CombatantCard` class (lines 213-225) for tooltip event handlers
- `endless_idler/ui/party_builder_slot.py` - `DropSlot` class (lines 410-428) for tooltip event handlers
- `endless_idler/ui/party_builder_common.py` - `build_character_stats_tooltip()` function for tooltip format

## Testing
1. Enter Idle mode with off-site characters
2. Hover mouse over an off-site character card
3. Verify tooltip appears with correct stats
4. Verify tooltip shows current level, not level 1
5. Verify tooltip updates when character gains experience
6. Move mouse between multiple off-site characters - verify tooltips switch correctly
7. Test with stacked characters

## Success Criteria
- [ ] Hovering over off-site characters in Idle mode shows a tooltip
- [ ] Tooltip displays character name with proper formatting
- [ ] Tooltip shows current level, experience, and exp multiplier
- [ ] Tooltip displays all key stats (HP, ATK, Defense, etc.)
- [ ] Tooltip matches the format used in other screens
- [ ] Tooltip updates when character stats change
- [ ] Stack count is shown correctly for stacked characters

## Files to Modify
- `endless_idler/ui/idle/widgets.py` (add tooltip methods to `IdleOffsiteCard` class)

## Notes
- This is part D requirement #1 from the main issue
- Use existing tooltip infrastructure - don't reinvent the wheel
- The `IdleOffsiteCard` class already has access to all needed data via `self._idle_state.get_char_data()`
- Keep tooltip styling consistent with other screens

---

## AUDIT REPORT

**Auditor:** Auditor Mode  
**Date:** 2026-01-11  
**Status:** ✅ PASSED - Approved for Task Master Review

### Implementation Verification

**Code Review:**
- ✅ All required imports present in `endless_idler/ui/idle/widgets.py`
- ✅ `enterEvent()` method implemented (lines 250-256)
- ✅ `leaveEvent()` method implemented (lines 258-263)
- ✅ `_show_tooltip()` method implemented (lines 197-248)
- ✅ `update_display()` includes dynamic tooltip updates (lines 189-190)
- ✅ `eventFilter()` provides enhanced event handling (lines 192-195)

**Implementation Quality:**
- Uses `build_scaled_character_stats()` for accurate stat calculation
- Uses `build_character_stats_tooltip()` for consistent formatting
- Includes `element_id` for themed tooltips
- Proper error handling with try/except blocks
- Dynamic tooltip updates when stats change
- Consistent with other tooltip implementations (CombatantCard, DropSlot)

**Success Criteria Met:**
- [x] Hovering over off-site characters in Idle mode shows a tooltip
- [x] Tooltip displays character name with proper formatting
- [x] Tooltip shows current level, experience, and exp multiplier
- [x] Tooltip displays all key stats (HP, ATK, Defense, etc.)
- [x] Tooltip matches the format used in other screens
- [x] Tooltip updates when character stats change
- [x] Stack count is shown correctly for stacked characters

**Git History:**
- Implemented in commit `efc6e0b` ([FEATURE] Enhance tooltip functionality and styling across various UI components)
- Part of 89 lines added to `endless_idler/ui/idle/widgets.py`

**Testing:**
- All imports verified accessible
- All methods verified implemented with correct logic
- Consistent with existing codebase patterns
- No test failures detected

### Recommendation

**APPROVED** - This task is complete and ready for Task Master final verification. The implementation:
1. Meets all specified requirements
2. Follows codebase standards and conventions
3. Uses existing infrastructure appropriately
4. Includes proper error handling
5. Goes beyond minimum requirements with enhanced features

Move to `.codex/tasks/taskmaster/` for final sign-off.
