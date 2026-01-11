# Crit Mod Quick Reference

## Quick Stats

| Crit Mod | Crit Chance | Crit Damage | Notes |
|----------|-------------|-------------|-------|
| 0        | 0.00%       | 1.000x      | No crits |
| 100      | 1.00%       | 1.250x      | Default |
| 200      | 1.50%       | 1.500x      | Early game |
| 300      | 2.00%       | 1.625x      | Mid-early |
| 500      | 2.50%       | 1.812x      | Mid game |
| 700      | 3.00%       | 1.953x      | Mid-late |
| 1000     | 3.38%       | 2.219x      | Late game |
| 1500     | 4.00%       | 2.531x      | End game |

## Code Examples

### Setting Crit Mod
```python
from endless_idler.combat.stats import Stats

stats = Stats()
stats.crit_mod = 300  # Gives ~2% crit rate, ~1.625x crit damage
```

### Reading Crit Values
```python
print(f"Crit Mod: {stats.crit_mod}")
print(f"Crit Rate: {stats.crit_rate * 100:.1f}%")
print(f"Crit Damage: {stats.crit_damage:.2f}x")
```

### Using in Character Definitions
```python
# In a character plugin file
base_stats = {
    "max_hp": 1200.0,
    "atk": 250.0,
    "defense": 180.0,
    "crit_mod": 200.0,  # Use crit_mod instead of crit_rate/crit_damage
    # ... other stats
}
```

### Direct Calculation (rare)
```python
from endless_idler.combat.crit_mod import calculate_crit_chance, calculate_crit_damage

crit_mod = 500
chance = calculate_crit_chance(crit_mod)  # Returns 0.025 (2.5%)
damage = calculate_crit_damage(crit_mod)  # Returns 1.8125
```

## Formula Reference

### Crit Chance
```
For each 1% crit chance:
  Points needed = 100 * 2^(n-1)
  where n is the percent number (1st, 2nd, 3rd, etc.)

Examples:
  1st percent (0→1%): 100 points
  2nd percent (1→2%): 200 points  
  3rd percent (2→3%): 400 points
  4th percent (3→4%): 800 points
```

### Crit Damage
```
Base: 1.0x
Per tier (200 points each):
  Tier 0 (0-200):   20 points per 0.05x
  Tier 1 (200-400): 40 points per 0.05x
  Tier 2 (400-600): 80 points per 0.05x
  Tier 3 (600-800): 160 points per 0.05x
  ...
```

## Migration Notes

### Old → New Conversion
- Old default: `crit_rate: 0.05` (5%), `crit_damage: 2.0` (2x)
- New default: `crit_mod: 100` → ~1% chance, ~1.25x damage
- The new system is more conservative to prevent power creep

### Backward Compatibility
```python
# These still work but are NOT recommended:
stats.crit_rate = 0.05   # Converts to crit_mod ~750
stats.crit_damage = 2.0  # Converts to crit_mod ~600

# Use this instead:
stats.crit_mod = 300  # Explicit and clear
```

## Common Mistakes

❌ **Don't:** Set crit_rate and crit_damage separately
```python
stats.crit_rate = 0.05
stats.crit_damage = 2.0  # This overwrites the crit_mod set by crit_rate!
```

✅ **Do:** Set crit_mod once
```python
stats.crit_mod = 300
```

❌ **Don't:** Try to add crit_rate and crit_damage stat effects
```python
effect.stat_modifiers["crit_rate"] = 0.02  # Won't work as expected
```

✅ **Do:** Add crit_mod stat effects
```python
effect.stat_modifiers["crit_mod"] = 100.0  # Adds ~1% crit chance
```

## Testing

```bash
# Run manual tests
python3 /tmp/test_crit_mod.py
python3 /tmp/test_stats_integration.py
python3 /tmp/test_battle_sim.py
```

## Related Files

- `endless_idler/combat/crit_mod.py` - Core calculation functions
- `endless_idler/combat/stats.py` - Stats class with crit_mod integration
- `endless_idler/combat/party_stats.py` - Stat sharing and scaling
- `endless_idler/ui/party_builder_common.py` - UI display
- `endless_idler/ui/onsite/stat_bars.py` - Stat bars display
- `.codex/implementation/crit-mod-system.md` - Full documentation
