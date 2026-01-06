# Fix Loss Reward System: Grant Gold/Tokens on Defeat

**Priority:** High  
**Status:** Ready for Review  
**Category:** Game Balance / Bug Fix  
**Task ID:** 633fd1dc  
**Implementation Date:** 2025-01-06

## Problem Statement

Players are reporting that they do not receive any gold/tokens when they lose a battle. In an idle/incremental game, players should receive some compensation even when losing to maintain engagement and progression, especially for newer players who may lose frequently.

## Current Implementation Analysis

### Reward System Flow

After analyzing the codebase, here's what currently happens:

**Victory Flow** (`ui/battle/screen.py`, lines 586-589):
```python
if party_alive and not foes_alive:
    self._award_gold(self._foe_kills)  # ✅ Gold awarded based on foe kills
    self._set_status("Victory")
    self._apply_idle_exp_bonus()
```

**Defeat Flow** (`ui/battle/screen.py`, lines 590-592):
```python
elif foes_alive and not party_alive:
    self._set_status("Defeat")
    self._apply_idle_exp_penalty()  # ❌ NO gold awarded
```

### Gold Calculation Logic

The `_award_gold` method (`ui/battle/screen.py`, lines 647-664) includes a bonus system:

```python
def _award_gold(self, kills: int) -> None:
    gold = max(0, int(kills))
    if gold <= 0:
        return
    
    tokens = max(0, int(save.tokens))
    winstreak = max(0, int(getattr(save, "winstreak", 0)))
    bonus = calculate_gold_bonus(tokens, winstreak)  # Bonus from tokens + winstreak
    
    total_gold = gold + bonus
    save.tokens = tokens + total_gold
```

The `calculate_gold_bonus` function (`run_rules.py`, lines 43-61) provides:
- +1 gold per 5 tokens/winstreak up to 100
- +1 gold per 25 tokens/winstreak after 100 (soft cap)

### Issue Identified

**Root Cause:** The `_award_gold()` method is ONLY called on victory, never on defeat. When a player loses:
1. No gold is awarded from foe kills
2. The player only receives an idle EXP penalty
3. They lose party HP and potentially reset their run with no compensation

This creates a negative feedback loop for struggling players:
- They lose → get no rewards → can't buy upgrades → lose more

## Proposed Solution

### Design Principles
1. **Maintain Progression:** Even losing players should make some progress
2. **Reward Effort:** Grant partial rewards based on foes killed before defeat
3. **Balance:** Loss rewards should be meaningful but less than victory rewards
4. **Consistency:** Use existing gold calculation systems

### Implementation Plan

**Option A: Partial Loss Rewards (Recommended)**
- Award gold for foes killed even on defeat
- Apply a multiplier (e.g., 50%) to loss rewards to maintain win incentive
- Still give full bonus from `calculate_gold_bonus()` to help struggling players

**Option B: Minimum Loss Rewards**
- Award a flat minimum amount on loss (e.g., 1-2 gold)
- Plus partial credit for foes killed
- Simpler but less engaging

### Recommended Implementation (Option A)

Modify `_on_battle_over()` in `/home/midori-ai/workspace/endless_idler/ui/battle/screen.py`:

**Current Code (lines 586-594):**
```python
if party_alive and not foes_alive:
    self._award_gold(self._foe_kills)
    self._set_status("Victory")
    self._apply_idle_exp_bonus()
elif foes_alive and not party_alive:
    self._set_status("Defeat")
    self._apply_idle_exp_penalty()
else:
    self._set_status("Over")
```

**Proposed Change:**
```python
if party_alive and not foes_alive:
    self._award_gold(self._foe_kills, victory=True)
    self._set_status("Victory")
    self._apply_idle_exp_bonus()
elif foes_alive and not party_alive:
    self._award_gold(self._foe_kills, victory=False)  # NEW: Award partial gold on loss
    self._set_status("Defeat")
    self._apply_idle_exp_penalty()
else:
    self._set_status("Over")
```

**Update `_award_gold()` method (lines 647-664):**
```python
def _award_gold(self, kills: int, victory: bool = True) -> None:
    """Award gold based on foe kills.
    
    Args:
        kills: Number of foes defeated
        victory: If True, award full gold. If False, award 50% of base kills only.
    """
    gold = max(0, int(kills))
    if gold <= 0:
        return

    try:
        manager = SaveManager()
        save = manager.load() or RunSave()
        
        tokens = max(0, int(save.tokens))
        winstreak = max(0, int(getattr(save, "winstreak", 0)))
        bonus = calculate_gold_bonus(tokens, winstreak)
        
        if victory:
            # Full rewards on victory: base kills + bonus
            total_gold = gold + bonus
        else:
            # Partial rewards on loss: 50% of base kills + full bonus
            # Bonus helps struggling players, reduced base maintains win incentive
            loss_gold = max(1, gold // 2)  # Minimum 1 gold for killing any foes
            total_gold = loss_gold + bonus
        
        save.tokens = tokens + total_gold
        manager.save(save)
    except Exception:
        return
```

### Alternative: Separate Loss Method

If preferred for clarity, create a separate `_award_loss_gold()` method:

```python
def _award_loss_gold(self, kills: int) -> None:
    """Award reduced gold on defeat to maintain player engagement."""
    gold = max(0, int(kills))
    if gold <= 0:
        # Award minimum 1 gold even with 0 kills to soften defeat
        gold = 1

    try:
        manager = SaveManager()
        save = manager.load() or RunSave()
        
        tokens = max(0, int(save.tokens))
        winstreak = max(0, int(getattr(save, "winstreak", 0)))
        bonus = calculate_gold_bonus(tokens, winstreak)
        
        # 50% of base kills + full bonus
        loss_gold = max(1, gold // 2)
        total_gold = loss_gold + bonus
        
        save.tokens = tokens + total_gold
        manager.save(save)
    except Exception:
        return
```

Then call it:
```python
elif foes_alive and not party_alive:
    self._award_loss_gold(self._foe_kills)
    self._set_status("Defeat")
    self._apply_idle_exp_penalty()
```

## Testing Requirements

1. **Victory Test:** Verify full gold rewards still work correctly
2. **Defeat Test:** Verify partial gold is awarded on defeat
3. **Zero Kills Test:** Verify behavior when player is defeated with 0 foe kills
4. **Bonus Test:** Verify `calculate_gold_bonus()` applies correctly on loss
5. **Edge Cases:** Test with various foe kill counts (1, 2, 5, 10)

## Expected Behavior After Fix

### Before:
- Win with 5 kills → Get 5 gold + bonus ✅
- Lose with 3 kills → Get 0 gold ❌

### After:
- Win with 5 kills → Get 5 gold + bonus ✅
- Lose with 3 kills → Get 1-2 gold + bonus ✅ (50% of 3 = 1-2)
- Lose with 0 kills → Get 0 gold (or 1 minimum if implemented)

## Balance Considerations

**Why 50% multiplier?**
- Maintains strong incentive to win (2x rewards)
- Provides meaningful progression even when losing
- Helps new players who lose frequently
- Doesn't trivialize victories

**Why full bonus on loss?**
- Bonus comes from player's existing tokens/winstreak investment
- Helps struggling players catch up faster
- Small relative to base rewards at low levels
- Creates positive feedback: more tokens → better bonuses → faster recovery

## Files to Modify

- `/home/midori-ai/workspace/endless_idler/ui/battle/screen.py`
  - Modify `_on_battle_over()` method (around line 586-594)
  - Modify `_award_gold()` method (lines 647-664)
  - OR add new `_award_loss_gold()` method if using separate method approach

## Documentation Updates

After implementation, update:
- `.codex/implementation/combat-damage-types.md` (if reward section exists)
- Create new `.codex/implementation/reward-system.md` if needed

## Success Criteria

- [x] Task created with clear requirements
- [x] Coder implements one of the proposed solutions (Option A - Modified `_award_gold` method)
- [x] Manual testing confirms gold awarded on defeat
- [x] Manual testing confirms victory rewards unchanged
- [ ] Auditor verifies implementation
- [x] Task moved to review folder

## Implementation Notes

**Implemented by:** Coder  
**Date:** 2025-01-06  
**Implementation:** Option A (Recommended)

**Changes Made:**
1. Modified `_award_gold()` method in `endless_idler/ui/battle/screen.py` to accept `victory` parameter
2. Updated `_on_battle_over()` to call `_award_gold()` on both victory and defeat
3. Defeat rewards: 50% of base kills (min 1) + full bonus
4. Victory rewards: Unchanged (full base kills + bonus)

**Testing:**
- Created comprehensive test suite (`test_loss_rewards.py` and `test_integration.py`)
- All test scenarios pass
- Logic validated for various kill counts and bonus scenarios
- Created implementation documentation in `.codex/implementation/loss-reward-system.md`

**Ready for Auditor Review**

## Notes

- This is a gameplay balance issue that affects player retention
- Loss rewards should feel meaningful but not remove the incentive to win
- Consider player feedback after implementation for further tuning
- The bonus system already exists, we're just extending when `_award_gold` is called
