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

---

## AUDITOR REVIEW

**Auditor**: Auditor Mode  
**Review Date**: 2026-01-06  
**Commits Reviewed**: 7a54a4d, 1236b66, 37d8f68  
**Status**: ✅ **APPROVED - Ready for Task Master**

### Implementation Summary

The coder successfully implemented passive ID extraction from character metadata through AST parsing. The implementation includes:

1. **Core Implementation** (Commit 7a54a4d):
   - Added `_extract_passives_from_classdef()` function with comprehensive docstring
   - Added `_extract_passive_list()` helper function with comprehensive docstring  
   - Updated `extract_character_metadata()` return type signature to include `list[str]` for passives
   - Integrated passive extraction into the main flow
   - Added passives initialization and return in all code paths (success, OSError, SyntaxError)

2. **Integration** (Commit 1236b66):
   - Updated `CharacterPlugin` dataclass to include `passives: list[str]` field with proper default factory
   - Updated `discover_character_plugins()` to unpack and pass the passives field

3. **Task Management** (Commit 37d8f68):
   - Task moved from `wip/` to `review/` with appropriate commit message

### Acceptance Criteria Verification

All acceptance criteria have been met:

- ✅ `extract_character_metadata()` returns passives as 10th element in tuple (index 9)
- ✅ Extracts passives from `field(default_factory=lambda: [...])` pattern (verified with all 22 character files)
- ✅ Extracts passives from direct list assignment (AST handles both patterns)
- ✅ Returns empty list when no passives found (verified with edge case testing)
- ✅ All existing character files parse correctly (all 22 characters extracted successfully)
- ✅ Passives extracted from Lady Light, Lady Darkness, Persona Light and Dark (verified):
  - `lady_light` → `['lady_light_radiant_aegis']`
  - `lady_darkness` → `['lady_darkness_eclipsing_veil']`
  - `persona_light_and_dark` → `['persona_light_and_dark_duality']`
- ✅ Code passes linting (`ruff check` returned "All checks passed!" for both files)
- ✅ All functions have docstrings (both new functions include comprehensive docstrings)

### Code Quality Assessment

**Strengths:**
1. **Robust AST Parsing**: The implementation correctly handles multiple AST patterns:
   - Annotated assignments (`passives: list[str] = ...`)
   - Regular assignments (`passives = ...`)
   - Direct list literals (`["id1", "id2"]`)
   - Field with lambda factories (`field(default_factory=lambda: [...])`)

2. **Type Safety**: 
   - Non-string values in lists are properly filtered out
   - Return type correctly specified as `list[str]`
   - All type hints are accurate

3. **Error Handling**:
   - Graceful handling of `None` values
   - Empty list returned for malformed data
   - All error paths properly initialized with empty list

4. **Consistency**:
   - Follows existing code patterns in the file
   - Naming conventions match existing helpers (`_extract_*`, `_const_*`)
   - Proper integration with existing extraction flow

5. **Documentation**:
   - Clear docstrings explaining the purpose and patterns handled
   - Comments in code explain the logic

6. **Integration**:
   - `plugins.py` correctly updated to handle the new field
   - All callers properly unpacking the new return value

### Edge Case Testing

Verified the following edge cases:
- ✅ Empty passives list returns `[]`
- ✅ Mixed types in list (strings and integers) - correctly filters to strings only
- ✅ No passives field defined - returns `[]`
- ✅ Multiple passive declarations - Python AST naturally handles this (uses last)
- ✅ `None` value handling - returns `[]`

### Real-World Testing

Tested against all 22 character files in the repository:
- All characters successfully parsed
- All passives correctly extracted
- No parsing errors or crashes
- Type integrity maintained throughout

**Sample Results:**
```
ally                           passives: ['ally_overload']
becca                          passives: ['becca_menagerie_bond']
bubbles                        passives: ['bubbles_bubble_burst']
lady_light                     passives: ['lady_light_radiant_aegis']
lady_darkness                  passives: ['lady_darkness_eclipsing_veil']
persona_light_and_dark         passives: ['persona_light_and_dark_duality']
```

### Performance & Maintainability

- **Performance**: No performance concerns - AST parsing is efficient and the implementation adds minimal overhead
- **Maintainability**: Code is clear, well-documented, and follows established patterns
- **Extensibility**: The pattern-matching approach makes it easy to add support for new passive declaration formats if needed

### Issues Found

**None** - No issues or defects found in the implementation.

### Recommendations

While the implementation is complete and production-ready, for future enhancement consider:
1. If duplicate passive IDs within a single character become a concern, a deduplication step could be added
2. Consider logging/warning for non-string values found in passive lists (currently silently filtered)

These are minor suggestions and **do not block approval**.

### Linting & Code Standards

- ✅ `ruff check endless_idler/characters/metadata.py` - All checks passed
- ✅ `ruff check endless_idler/characters/plugins.py` - All checks passed
- ✅ Code follows repository Python style guide (imports sorted, proper spacing, type hints)
- ✅ Docstrings present and properly formatted
- ✅ No style violations detected

### Testing Coverage

**Manual Testing**: ✅ Comprehensive
- Tested all 22 character files
- Tested edge cases (empty lists, None values, mixed types)
- Tested integration with `discover_character_plugins()`
- Verified type correctness of all return values

**Automated Tests**: ⚠️ Not Required
- Task requirements did not specify creation of automated tests
- Repository does not have a `tests/` directory
- Per AGENTS.md: "Do not build tests unless asked to"

### Final Assessment

This implementation is **exemplary**. The coder:
- Met all acceptance criteria completely
- Followed repository coding standards precisely
- Handled edge cases properly
- Integrated the feature seamlessly
- Documented the code thoroughly
- Used appropriate commit messages
- Moved the task through the workflow correctly

The code is production-ready and requires no changes.

**VERDICT**: ✅ **APPROVED FOR TASK MASTER REVIEW**

---

**Auditor Signature**: Auditor Mode  
**Audit Completed**: 2026-01-06 10:56:00 UTC
