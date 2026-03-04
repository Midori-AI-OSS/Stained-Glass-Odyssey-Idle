"""Shape palette system for foe rendering.

Provides 25 predefined shape templates for visual variety in foe representation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ShapeTemplate:
    """Template defining a shape for foe rendering.
    
    Attributes:
        shape_id: Unique identifier for this shape
        name: Human-readable name
        geometry_fn: Function that creates the shape geometry
        base_width: Base width in pixels
        base_height: Base height in pixels
        fill_direction: How health fill is visualized ("bottom_up", "left_right", "center_out")
    """
    shape_id: str
    name: str
    geometry_fn: Callable | None  # Placeholder - will be QPainterPath function
    base_width: float
    base_height: float
    fill_direction: str


# Define all 25 shape templates
SHAPE_TEMPLATES: list[ShapeTemplate] = [
    # Basic Polygons (6)
    ShapeTemplate("circle", "Circle", None, 50.0, 50.0, "center_out"),
    ShapeTemplate("square", "Square", None, 50.0, 50.0, "bottom_up"),
    ShapeTemplate("triangle", "Triangle", None, 50.0, 50.0, "bottom_up"),
    ShapeTemplate("pentagon", "Pentagon", None, 50.0, 50.0, "bottom_up"),
    ShapeTemplate("hexagon", "Hexagon", None, 50.0, 50.0, "bottom_up"),
    ShapeTemplate("octagon", "Octagon", None, 50.0, 50.0, "bottom_up"),
    
    # Stars (5)
    ShapeTemplate("star_4", "4-Point Star", None, 55.0, 55.0, "center_out"),
    ShapeTemplate("star_5", "5-Point Star", None, 55.0, 55.0, "center_out"),
    ShapeTemplate("star_6", "6-Point Star", None, 55.0, 55.0, "center_out"),
    ShapeTemplate("star_8", "8-Point Star", None, 55.0, 55.0, "center_out"),
    ShapeTemplate("star_burst", "Star Burst", None, 60.0, 60.0, "center_out"),
    
    # Complex Geometric (7)
    ShapeTemplate("diamond", "Diamond", None, 50.0, 60.0, "bottom_up"),
    ShapeTemplate("cross", "Cross", None, 50.0, 50.0, "center_out"),
    ShapeTemplate("x_cross", "X Cross", None, 50.0, 50.0, "center_out"),
    ShapeTemplate("crescent", "Crescent", None, 45.0, 50.0, "left_right"),
    ShapeTemplate("heart", "Heart", None, 50.0, 50.0, "bottom_up"),
    ShapeTemplate("teardrop", "Teardrop", None, 45.0, 55.0, "bottom_up"),
    ShapeTemplate("ring", "Ring", None, 50.0, 50.0, "center_out"),
    
    # Organic/Irregular (4)
    ShapeTemplate("blob", "Blob", None, 55.0, 50.0, "center_out"),
    ShapeTemplate("cloud", "Cloud", None, 60.0, 45.0, "center_out"),
    ShapeTemplate("wave", "Wave", None, 60.0, 40.0, "left_right"),
    ShapeTemplate("splat", "Splat", None, 55.0, 55.0, "center_out"),
    
    # Angular/Arrows (3)
    ShapeTemplate("chevron", "Chevron", None, 50.0, 40.0, "bottom_up"),
    ShapeTemplate("arrow_up", "Arrow Up", None, 45.0, 55.0, "bottom_up"),
    ShapeTemplate("trapezoid", "Trapezoid", None, 50.0, 45.0, "bottom_up"),
]


# Create lookup dictionary for fast access
_SHAPE_LOOKUP: dict[str, ShapeTemplate] = {
    template.shape_id: template for template in SHAPE_TEMPLATES
}


def get_shape_template(shape_id: str) -> ShapeTemplate:
    """Get a shape template by its ID.
    
    Args:
        shape_id: Unique identifier for the shape
        
    Returns:
        ShapeTemplate with the requested ID
        
    Raises:
        KeyError: If shape_id is not found
    """
    return _SHAPE_LOOKUP[shape_id]


def get_all_shape_ids() -> list[str]:
    """Get list of all available shape IDs.
    
    Returns:
        List of shape IDs in order
    """
    return [template.shape_id for template in SHAPE_TEMPLATES]


def get_shape_count() -> int:
    """Get the total number of shapes in the palette.
    
    Returns:
        Number of available shapes (should be 25)
    """
    return len(SHAPE_TEMPLATES)
