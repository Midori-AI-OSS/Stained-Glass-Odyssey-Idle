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
- [ ] 25 unique shape templates defined
- [ ] Each template has complete geometry and properties
- [ ] Templates can be retrieved by ID
- [ ] Shapes are visually distinct from each other
- [ ] Fill directions are defined for all shapes

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
