# Manual Testing Guide for Idle Mode Stat Persistence Fix

## Bug Description
Previously, when entering idle mode and then exiting, character stats would reset to their state from before entering idle mode. This was caused by the party builder's shop exp state overwriting the saved idle mode stats on reload.

## The Fix
Modified `party_builder.py`'s `reload_save()` method to clear the shop exp state when reloading the save. This ensures that stats saved by idle mode are not overwritten by stale shop exp state data.

## Manual Test Steps

### Test 1: Basic Idle Mode Persistence
1. Launch the game: `uv run endless-idler`
2. Start a new run and add at least one character to OnSite
3. Note the character's level and stats (hover over character card)
4. Click the "Idle" button to enter idle mode
5. Wait for the character to gain several levels (should see level ups)
6. Click "Back" to exit idle mode
7. **VERIFY**: Character level and stats should remain at the new values
8. **BUG BEHAVIOR**: Stats would reset to pre-idle values

### Test 2: Multiple Idle Sessions
1. Enter idle mode and gain 2-3 levels
2. Exit idle mode and verify stats are preserved
3. Re-enter idle mode immediately
4. **VERIFY**: Character should continue from where they left off (not reset)
5. Gain more levels
6. Exit again
7. **VERIFY**: All progress is cumulative and preserved

### Test 3: Idle Mode with Offsite Characters
1. Add characters to both OnSite (4 max) and Offsite (6 max)
2. Note all character levels
3. Enable "Shared EXP" slider in idle mode
4. Let all characters gain levels
5. Exit idle mode
6. **VERIFY**: Both OnSite and Offsite character stats are preserved

### Test 4: Stat Growth Verification
1. Enter idle mode with a level 1 character
2. Record initial stats (ATK, Defense, Crit Rate, etc.)
3. Let character level up 5-10 times
4. Record new stats
5. Exit idle mode
6. **VERIFY**: Stats should be higher than initial (growth applied during idle)
7. **BUG BEHAVIOR**: Stats would reset to initial values

### Test 5: Battle vs Idle Interaction
1. Enter idle mode and gain a few levels
2. Exit idle mode - verify stats preserved
3. Start a battle (Fight button)
4. Complete or abandon the battle
5. Return to party builder
6. **VERIFY**: Idle mode stats are still preserved (not reset)

### Test 6: Shop EXP with Idle Mode
1. In party builder, wait a few seconds (shop exp accumulates slowly)
2. Note the character level/exp
3. Enter idle mode
4. Gain several levels quickly
5. Exit idle mode
6. **VERIFY**: Stats from idle mode are preserved (shop exp state doesn't overwrite)

## Expected Results
✓ All character progress (levels, exp, stats) gained in idle mode persists after exiting
✓ Subsequent idle sessions continue from the last saved state
✓ Both OnSite and Offsite characters preserve their progress
✓ Stat increases from level-ups are maintained
✓ Shop exp state doesn't interfere with idle mode progress

## Automated Tests
Two test scripts verify the fix:
1. `test_idle_stat_persistence.py` - Tests basic persistence
2. `test_shop_exp_interaction.py` - Tests shop exp state doesn't interfere

Run with:
```bash
uv run python test_idle_stat_persistence.py
uv run python test_shop_exp_interaction.py
```

Both should output "ALL TESTS PASSED".

## Files Modified
- `endless_idler/ui/party_builder.py` - Fixed `reload_save()` method to clear shop exp state
