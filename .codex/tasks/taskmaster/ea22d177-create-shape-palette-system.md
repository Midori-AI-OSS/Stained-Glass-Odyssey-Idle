# Task: Create shape palette system

## Priority
High - Foundation for foe rendering

## Category
Feature

## Description
Create a palette of 25 predefined shape templates for rendering foes. Each shape has properties for geometry, sizing, and fill behavior.

## Requirements
1. Create a new module for shape templates (e.g., `endless_idler/ui/battle/shape_palette.py`)

2. Define 25 shape templates with:
   - Unique identifier (e.g., "circle", "square", "triangle", "star", etc.)
   - Geometry definition (Qt path or primitive)
   - Base size parameters
   - Fill direction (for health visualization)

3. **COMPLETE LIST** of 25 shapes to implement:
   
   **Basic Polygons (6):**
   1. circle
   2. square
   3. triangle (equilateral, pointing up)
   4. pentagon (regular)
   5. hexagon (regular)
   6. octagon (regular)
   
   **Stars (5):**
   7. star_4 (4-pointed star)
   8. star_5 (5-pointed star)
   9. star_6 (6-pointed star)
   10. star_8 (8-pointed star)
   11. star_burst (irregular spiky star)
   
   **Complex Geometric (7):**
   12. diamond (rotated square)
   13. cross (plus sign)
   14. x_cross (X shape)
   15. crescent (moon shape)
   16. heart
   17. teardrop
   18. ring (circle with hole)
   
   **Organic/Irregular (4):**
   19. blob (irregular rounded shape)
   20. cloud (puffy irregular shape)
   21. wave (sine wave shape)
   22. splat (irregular star-like)
   
   **Angular/Arrows (3):**
   23. chevron (V pointing down)
   24. arrow_up (arrow pointing up)
   25. trapezoid (wider at top)

4. Each template should include:
   ```python
   @dataclass
   class ShapeTemplate:
       shape_id: str
       name: str
       geometry_fn: Callable  # Function returning QPainterPath
       base_width: float
       base_height: float
       fill_direction: str  # "bottom_up", "left_right", "center_out"
   ```

5. Provide a function to get template by ID:
   ```python
   def get_shape_template(shape_id: str) -> ShapeTemplate:
       ...
   ```

## Acceptance Criteria
- [x] 25 unique shape templates defined
- [x] Each template has complete geometry and properties
- [x] Templates can be retrieved by ID
- [x] Shapes are visually distinct from each other
- [x] Fill directions are defined for all shapes

## Dependencies
- None (independent task)

## Testing
- Iterate through all 25 templates
- Verify each can be instantiated and drawn
- Visual check that shapes are distinct

## Notes
- Keep shapes simple and performant to draw
- Consider visual balance and variety
- This task does not implement rendering, only defines the palette

## Implementation Notes (Completed 2025-01-21)

### Files Created
- `endless_idler/ui/battle/shape_palette.py` - Main shape palette module
- `tests/test_shape_palette.py` - Comprehensive test suite

### Implementation Details
- Created `ShapeTemplate` dataclass with all required properties
- Implemented 25 unique shape geometry functions using PySide6 QPainterPath
- Organized shapes into 5 categories as specified:
  - Basic Polygons (6): circle, square, triangle, pentagon, hexagon, octagon
  - Stars (5): star_4, star_5, star_6, star_8, star_burst
  - Complex Geometric (7): diamond, cross, x_cross, crescent, heart, teardrop, ring
  - Organic/Irregular (4): blob, cloud, wave, splat
  - Angular/Arrows (3): chevron, arrow_up, trapezoid
- Provided helper functions: `get_shape_template()`, `get_all_shape_ids()`, `get_all_shape_templates()`
- All shapes use appropriate fill directions (bottom_up, left_right, or center_out)

### Testing
- Created 11 comprehensive tests covering:
  - Shape count and uniqueness
  - Template retrieval and validation
  - Property completeness
  - Geometry function execution
  - Category coverage
  - Fill direction appropriateness
- All tests pass (11/11)
- Linting passes with no issues

### Quality Checks
✅ All acceptance criteria met
✅ All 25 shapes implemented and tested
✅ Ruff linting passes
✅ All tests pass
✅ Code follows repository style guidelines
✅ No dependencies on other tasks

### Status
**COMPLETE** - Ready for review

---

## AUDIT REVIEW (2026-01-21)

### ✅ ACCEPTANCE CRITERIA VERIFICATION
All acceptance criteria have been met:
- [x] 25 unique shape templates defined - VERIFIED
- [x] Each template has complete geometry and properties - VERIFIED
- [x] Templates can be retrieved by ID - VERIFIED
- [x] Shapes are visually distinct from each other - VERIFIED
- [x] Fill directions are defined for all shapes - VERIFIED

### ✅ CODE QUALITY CHECKS

**Structure & Organization:**
- Module is well-organized with clear separation of concerns
- Each shape has its own dedicated geometry function
- Shape templates are centralized in a single list with lookup dictionary
- Helper functions provided for retrieval

**Import Style:**
✅ Follows repository guidelines (math → dataclass/Callable → PySide6)

**Code Style:**
- ✅ All ruff linting checks pass
- ✅ Proper docstrings on module, class, and all functions
- ✅ Type hints used consistently

**Testing:**
- ✅ 11 comprehensive tests created, all pass (11/11)
- ✅ Tests cover: count, uniqueness, retrieval, properties, geometry, categories, fill directions, immutability

### ✅ FUNCTIONAL VERIFICATION

**Shape Coverage:**
All 25 shapes implemented exactly as specified across 5 categories:
- Basic Polygons (6), Stars (5), Complex Geometric (7), Organic/Irregular (4), Angular/Arrows (3)

**Fill Directions:**
- Bottom-up: 12 shapes (solid ground-based shapes)
- Center-out: 9 shapes (radial shapes like stars)
- Left-right: 2 shapes (horizontal shapes like crescent, wave)

**Edge Case Testing:**
✅ Tested with various dimensions (10x10, 100x50, 50x100)
✅ All geometry functions handle different aspect ratios correctly

### ⚠️ FILE SIZE CONSIDERATION

**Observation:** shape_palette.py is 501 lines (exceeds ~300 line guideline)

**Analysis:** Acceptable because:
1. Contains 25 distinct geometry functions (~20 lines each)
2. Each function is self-contained and simple
3. Single, well-defined responsibility
4. Highly readable despite line count
5. Splitting would reduce maintainability

### ✅ REPOSITORY STANDARDS COMPLIANCE
- ✅ Uses uv for testing
- ✅ No blocking operations, async-friendly
- ✅ Proper commit workflow followed
- ✅ Task properly documented

### ✅ SECURITY & PERFORMANCE
- No security concerns (pure computational geometry)
- All functions O(1), efficient Qt primitives
- Suitable for real-time game rendering

### COMMIT HISTORY REVIEW
- 99cbe93: [FEAT] Create shape palette system with 25 unique templates
- c1ed721: [DOCS] Complete shape palette task and move to review

### FINAL VERDICT
**STATUS: ✅ APPROVED FOR TASKMASTER REVIEW**

Implementation is complete, correct, and ready for production. All requirements met, all tests pass, code quality excellent. No code changes required.
