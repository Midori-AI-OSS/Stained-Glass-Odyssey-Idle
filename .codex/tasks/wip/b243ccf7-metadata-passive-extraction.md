# Task: Extend Metadata Extraction for Passives

**ID**: b243ccf7  
**Parent**: 7437c51e-passive-system-overview  
**Priority**: High  
**Complexity**: Low  
**Assigned Mode**: Coder  
**Dependencies**: None (can run in parallel with 1e4e2d6b)

## Objective

Extend the AST-based metadata extraction in `endless_idler/characters/metadata.py` to parse and extract passive IDs from character class definitions.

## Current State

The `extract_character_metadata()` function in `metadata.py` currently extracts:
- Character ID
- Display name
- Stars/rarity
- Placement
- Damage type
- Base stats
- Base aggro
- Damage reduction passes

But it does NOT extract the `passives: list[str]` field.

## Requirements

### 1. Extend the Return Type

Update `extract_character_metadata()` signature to include passives:

**Before**:
```python
def extract_character_metadata(
    path: Path,
) -> tuple[str, str, int, str, str, bool, dict[str, float], float | None, int | None]:
```

**After**:
```python
def extract_character_metadata(
    path: Path,
) -> tuple[str, str, int, str, str, bool, dict[str, float], float | None, int | None, list[str]]:
```

The new `list[str]` at the end contains passive IDs.

### 2. Add Passive Extraction Function

Create a new helper function to extract passives from a ClassDef AST node:

```python
def _extract_passives_from_classdef(node: ast.ClassDef) -> list[str]:
    """Extract passive IDs from a character class definition.
    
    Looks for:
    - passives: list[str] = field(default_factory=lambda: ["passive_id_1", "passive_id_2"])
    - passives: list[str] = ["passive_id"]
    """
    for stmt in node.body:
        # Check annotated assignments: passives: list[str] = ...
        if isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name) and stmt.target.id == "passives":
                return _extract_passive_list(stmt.value)
        
        # Check regular assignments: passives = ...
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "passives":
                    return _extract_passive_list(stmt.value)
    
    return []

def _extract_passive_list(node: ast.AST | None) -> list[str]:
    """Extract list of strings from various AST patterns.
    
    Handles:
    - Direct list: ["id1", "id2"]
    - field(default_factory=lambda: ["id1", "id2"])
    """
    if node is None:
        return []
    
    # Direct list literal
    if isinstance(node, ast.List):
        passives = []
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                passives.append(elt.value)
        return passives
    
    # field(default_factory=lambda: [...])
    if isinstance(node, ast.Call):
        # Check if it's a field() call
        if isinstance(node.func, ast.Name) and node.func.id == "field":
            # Look for default_factory keyword argument
            for keyword in node.keywords:
                if keyword.arg == "default_factory":
                    # Check if it's a lambda
                    if isinstance(keyword.value, ast.Lambda):
                        # Extract the lambda body
                        return _extract_passive_list(keyword.value.body)
    
    return []
```

### 3. Integrate into Main Extraction Flow

Update `extract_character_metadata()` to call the new function:

```python
def extract_character_metadata(
    path: Path,
) -> tuple[str, str, int, str, str, bool, dict[str, float], float | None, int | None, list[str]]:
    # ... existing initialization code ...
    passives: list[str] = []
    
    # ... existing parsing logic ...
    
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        
        # ... existing extraction calls ...
        found_passives = _extract_passives_from_classdef(node)
        
        if found_id or found_name:
            found_character = True
        
        # ... existing field updates ...
        
        if found_passives:
            passives = found_passives
        
        if found_id or found_name:
            break
    
    # ... existing return logic ...
    
    return (
        char_id,
        display_name,
        _sanitize_stars(stars),
        _sanitize_placement(placement),
        _sanitize_damage_type(damage_type_id),
        bool(damage_type_random),
        sanitized_base_stats,
        base_aggro,
        damage_reduction_passes,
        passives,  # New field
    )
```

### 4. Handle Edge Cases

- Empty passives list (default)
- Invalid passive ID formats (non-strings in list)
- Multiple passive declarations (use last one found)
- Passives declared at module level vs class level (focus on class level)

### 5. Update Callers (if any)

Search for code that calls `extract_character_metadata()` and update to handle the new return value:

```bash
grep -r "extract_character_metadata" endless_idler/
```

Update any callers to unpack the new passives field.

## Testing Strategy

### Manual Testing

Test with existing character files:

```python
from pathlib import Path
from endless_idler.characters.metadata import extract_character_metadata

# Test Lady Light (has passive)
path = Path("endless_idler/characters/lady_light.py")
result = extract_character_metadata(path)
passives = result[9]  # New field at index 9
assert "lady_light_radiant_aegis" in passives

# Test Lady Darkness (has passive)
path = Path("endless_idler/characters/lady_darkness.py")
result = extract_character_metadata(path)
passives = result[9]
assert "lady_darkness_eclipsing_veil" in passives

# Test a character without passives (if any)
# Should return empty list
```

### Edge Cases to Test

1. Character with no passives declaration → `[]`
2. Character with empty passives → `[]`
3. Character with multiple passives → all IDs extracted
4. Malformed passive declarations → graceful fallback to `[]`

## Technical Considerations

1. **AST Parsing**: Must handle various ways passives might be declared
2. **Backward Compatibility**: Ensure existing metadata extraction still works
3. **Error Handling**: Don't crash on malformed passive declarations
4. **Type Safety**: Return type must be `list[str]`, not `list[Any]`

## Acceptance Criteria

- [ ] `extract_character_metadata()` returns passives as 10th element in tuple
- [ ] Extracts passives from `field(default_factory=lambda: [...])`  pattern
- [ ] Extracts passives from direct list assignment
- [ ] Returns empty list when no passives found
- [ ] All existing character files parse correctly
- [ ] Passives extracted from Lady Light, Lady Darkness, Persona Light and Dark
- [ ] Code passes linting (`ruff check endless_idler/characters/metadata.py`)
- [ ] All functions have docstrings

## Example Expected Output

```python
# Lady Light
result = extract_character_metadata(Path("endless_idler/characters/lady_light.py"))
# result[9] == ["lady_light_radiant_aegis"]

# Lady Darkness
result = extract_character_metadata(Path("endless_idler/characters/lady_darkness.py"))
# result[9] == ["lady_darkness_eclipsing_veil"]

# Persona Light and Dark
result = extract_character_metadata(Path("endless_idler/characters/persona_light_and_dark.py"))
# result[9] == ["persona_light_and_dark_duality"]
```

## Notes

- This task is independent and can proceed in parallel with infrastructure creation
- Focus on the common patterns used in existing character files
- The trinity_synergy passive will be shared across multiple characters, but extraction happens per-file
- Consider adding a helper to deduplicate passive IDs if a character somehow declares the same passive multiple times

## Related Files

- `endless_idler/characters/metadata.py` - Main file to modify
- `endless_idler/characters/*.py` - Test files with passive declarations
- `endless_idler/characters/plugins.py` - May need updates if it uses metadata
