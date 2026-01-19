# Add Tooltips for Off-Site Characters in Fight Mode

## Issue Reference
Part of: Fix tooltip styling, correct character stats display outside combat, and normalize off-site character experience and tooltips

## Problem
Off-site characters (reserves) in Fight mode have no tooltips when hovering over them. Players cannot see stats, level, or other information for reserve characters during combat.

## Current State
- File: `endless_idler/ui/battle/widgets.py`
- Class: `CombatantCard` (lines 71-225+)
- The class has `enterEvent` and `leaveEvent` methods (lines 213-225)
- Tooltips work for on-site characters but may not work correctly for off-site (variant="offsite")
- Line 98: `self.setProperty("battleVariant", self._variant)` distinguishes offsite cards

## ⚠️ AUDITOR BLOCK: Verification Required Before Implementation

**Finding:** The existing tooltip infrastructure in `CombatantCard` SHOULD already work for offsite variants!

**Evidence:**
1. Line 203: Tooltips are disabled only for `compact=True` mode
2. Line 233 in `battle/screen.py`: Offsite cards use `variant="offsite"` but NOT `compact=True`
3. Line 260 in `battle/screen.py`: Only enemy foes use `compact=True`
4. Line 151 & 175: `_refresh_tooltip()` is called in `__init__` and `refresh()` for ALL variants

**Conclusion:** Tooltips should already be functional for offsite cards. This task may require:
- Manual testing to confirm tooltips work
- If tooltips DON'T work, investigate WHY (might be a display/visibility issue, not a tooltip generation issue)
- If they DO work, this task can be closed immediately

## Current Code Analysis
```python
# Line 213-225 in CombatantCard
def enterEvent(self, event: object) -> None:
    """Show tooltip on mouse enter."""
    if self._tooltip_html:
        show_stained_tooltip(self, self._tooltip_html)
        super().enterEvent(event)  # type: ignore[misc]

def leaveEvent(self, event: object) -> None:
    """Hide tooltip on mouse leave."""
    hide_stained_tooltip()
    super().leaveEvent(event)  # type: ignore[misc]
```

## Technical Approach

### ⚠️ MANDATORY Investigation Phase - DO THIS FIRST
**Before writing any code:**

1. **Run the game and manually test**:
   - Start a battle with reserve (offsite) characters
   - Hover over an offsite character card
   - **If tooltip appears correctly, CLOSE THIS TASK - it's already working**
   
2. **If tooltips don't appear**, debug:
   - Add print statement in `CombatantCard.__init__`: `print(f"Card variant: {self._variant}, tooltip: {self._tooltip_html[:50] if self._tooltip_html else 'NONE'}")`
   - Check if `_tooltip_html` is populated for offsite variants
   - Trace where tooltips are built - likely in `__init__` or a setup method
   
3. **Only proceed to implementation if issue is confirmed**

### Implementation Phase

If tooltips are not working for offsite cards:

1. **In `endless_idler/ui/battle/widgets.py`**, locate where `_tooltip_html` is set (likely in `__init__` or an update method)

2. **Ensure tooltip is built for all variants**:
   ```python
   # In CombatantCard.__init__ or similar
   self._tooltip_html = self._build_tooltip()  # Should work for both onsite and offsite
   ```

3. **If tooltip building method exists but skips offsite**, remove that restriction:
   ```python
   def _build_tooltip(self) -> str:
       """Build tooltip for this combatant."""
       # Should NOT have: if self._variant == "offsite": return ""
       
       display_name = self._combatant.name
       stats = self._combatant.stats
       
       return build_character_stats_tooltip(
           name=display_name,
           stars=self._stars,
           stacks=self._stack_count,
           stackable=False,
           stats=stats,
       )
   ```

4. **If no tooltip building exists at all**, add it following the pattern from `IdleOffsiteCard` task

### Alternative: Check `_build_tooltip_html()` method
The class might have a method that builds tooltips but isn't called for offsite cards. Look for:
- Methods that generate tooltip HTML
- Conditions that skip tooltip generation based on variant
- Constructor logic that only sets tooltips for certain variants

## Reference Implementations
- `endless_idler/ui/battle/screen.py` - lines 224-237 show how reserve cards are created
- `endless_idler/ui/party_builder_common.py` - `build_character_stats_tooltip()` function
- Task `d7fb182a` (Add tooltips for off-site in Idle) - similar approach

## Testing
1. Start a battle with off-site characters (reserves)
2. During combat, hover over an off-site character card on the left side
3. Verify tooltip appears with correct stats
4. Verify tooltip shows current combat stats (HP, ATK, etc.)
5. Verify tooltip updates if stats change during combat
6. Test with multiple reserve characters

## Success Criteria
- [ ] Hovering over off-site characters in Fight mode shows a tooltip
- [ ] Tooltip displays character name, level, and stars
- [ ] Tooltip shows current combat stats (HP, ATK, Defense, etc.)
- [ ] Tooltip matches the format used in other screens
- [ ] Tooltip works for all reserve characters
- [ ] Stack count is displayed correctly if character is stacked

## Files to Investigate/Modify
- `endless_idler/ui/battle/widgets.py` (primary - `CombatantCard` class)
- `endless_idler/ui/battle/screen.py` (reference - how reserves are created)

## Notes
- This is part D requirement #2 from the main issue
- The tooltip infrastructure already exists in `CombatantCard` (enterEvent/leaveEvent)
- The issue is likely that `_tooltip_html` is not being populated for offsite variants
- If the existing tooltip logic works, this might be a very quick fix
- Use the same tooltip format as other character displays for consistency
