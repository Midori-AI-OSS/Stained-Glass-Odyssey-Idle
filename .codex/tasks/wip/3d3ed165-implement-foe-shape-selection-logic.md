# Task: Implement foe shape selection logic

## Priority
High - Links foe stats to visual representation

## Category
Feature

## Description
Implement deterministic shape selection for foes based on their stats. Same stats should always produce the same shape choice.

## Requirements
1. Create a function that selects a shape template based on foe stats:
   ```python
   def select_shape_for_foe(stats: Stats) -> str:
       """Select shape ID based on foe stats.
       
       Deterministic: same stats -> same shape.
       Returns: shape_id from palette
       """
   ```

2. **FINALIZED** Selection criteria - use this concrete approach:
   - **Method**: Use weighted stat hash for deterministic selection
   - **Weighting formula**: 
     ```python
     # Normalize stats relative to level to get stat "profile"
     hp_ratio = max_hp / (level * 10)  # baseline: 10 hp per level
     atk_ratio = atk / (level * 2)     # baseline: 2 atk per level
     def_ratio = defense / level       # baseline: 1 def per level
     spd_ratio = atk_speed / 1.0       # baseline: 1.0 atk_speed
     
     # Create fingerprint
     fingerprint = int(hp_ratio * 1000 + atk_ratio * 500 + def_ratio * 250 + spd_ratio * 125)
     shape_index = fingerprint % 25
     ```
   - This ensures same stats → same shape, different profiles → variety
   - All 25 shapes reachable through different stat combinations

3. Implementation approach:
   - Calculate a "stat fingerprint" hash from key stats
   - Use modulo to map to shape index (0-24)
   - Ensure determinism: same input stats always return same shape
   - Consider weighting by stat ratios, not absolute values

4. Make the mapping visible for debugging:
   - Log shape selection with stat summary during development
   - Add ability to inspect "why this shape" for testing

## Acceptance Criteria
- [ ] Function takes Stats object and returns shape_id
- [ ] Same stats always return same shape (deterministic)
- [ ] Different stat profiles produce different shapes (variety)
- [ ] Selection is based on stat characteristics, not random
- [ ] All 25 shapes can potentially be selected
- [ ] Function is well-documented with selection logic

## Dependencies
- Requires: ea22d177-create-shape-palette-system.md

## Testing
- Create foes with identical stats, verify same shape
- Create foes with varying stats, verify different shapes
- Create 100 random foes, verify shape distribution is reasonable

## Notes
- Prioritize determinism over perfect aesthetic matching
- Can refine selection criteria based on gameplay testing
