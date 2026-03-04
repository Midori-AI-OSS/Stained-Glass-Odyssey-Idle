"""
Tests for the shape palette system.
"""

import pytest

from endless_idler.ui.legacy.battle.shape_palette import get_all_shape_ids
from endless_idler.ui.legacy.battle.shape_palette import get_all_shape_templates
from endless_idler.ui.legacy.battle.shape_palette import get_shape_template
from endless_idler.ui.legacy.battle.shape_palette import ShapeTemplate


def test_get_all_shape_ids():
    """Test that we can retrieve all shape IDs."""
    shape_ids = get_all_shape_ids()
    assert len(shape_ids) == 25, f"Expected 25 shapes, got {len(shape_ids)}"
    assert len(set(shape_ids)) == 25, "Shape IDs should be unique"


def test_get_all_shape_templates():
    """Test that we can retrieve all shape templates."""
    templates = get_all_shape_templates()
    assert len(templates) == 25, f"Expected 25 templates, got {len(templates)}"


def test_get_shape_template_valid():
    """Test that we can retrieve a template by ID."""
    template = get_shape_template("circle")
    assert isinstance(template, ShapeTemplate)
    assert template.shape_id == "circle"
    assert template.name == "Circle"
    assert callable(template.geometry_fn)
    assert template.base_width > 0
    assert template.base_height > 0
    assert template.fill_direction in ["bottom_up", "left_right", "center_out"]


def test_get_shape_template_invalid():
    """Test that invalid shape IDs raise KeyError."""
    with pytest.raises(KeyError):
        get_shape_template("nonexistent_shape")


def test_all_shape_ids_retrievable():
    """Test that every shape ID can be retrieved."""
    shape_ids = get_all_shape_ids()
    for shape_id in shape_ids:
        template = get_shape_template(shape_id)
        assert template.shape_id == shape_id


def test_all_shapes_have_valid_properties():
    """Test that all shapes have complete and valid properties."""
    templates = get_all_shape_templates()
    valid_fill_directions = ["bottom_up", "left_right", "center_out"]
    
    for template in templates:
        # Check required properties exist
        assert template.shape_id, "Shape ID should not be empty"
        assert template.name, "Shape name should not be empty"
        assert callable(template.geometry_fn), "geometry_fn should be callable"
        assert template.base_width > 0, f"base_width should be positive for {template.shape_id}"
        assert template.base_height > 0, f"base_height should be positive for {template.shape_id}"
        assert template.fill_direction in valid_fill_directions, \
            f"Invalid fill_direction for {template.shape_id}: {template.fill_direction}"


def test_all_geometry_functions_callable():
    """Test that all geometry functions can be called and return a path."""
    from PySide6.QtGui import QPainterPath
    
    templates = get_all_shape_templates()
    for template in templates:
        # Call geometry function with base dimensions
        path = template.geometry_fn(template.base_width, template.base_height)
        assert isinstance(path, QPainterPath), \
            f"geometry_fn for {template.shape_id} should return QPainterPath"
        assert not path.isEmpty(), \
            f"Path for {template.shape_id} should not be empty"


def test_shape_categories():
    """Test that all required shape categories are present."""
    shape_ids = get_all_shape_ids()
    
    # Basic Polygons (6)
    basic = ["circle", "square", "triangle", "pentagon", "hexagon", "octagon"]
    for shape in basic:
        assert shape in shape_ids, f"Missing basic polygon: {shape}"
    
    # Stars (5)
    stars = ["star_4", "star_5", "star_6", "star_8", "star_burst"]
    for shape in stars:
        assert shape in shape_ids, f"Missing star: {shape}"
    
    # Complex Geometric (7)
    complex_geo = ["diamond", "cross", "x_cross", "crescent", "heart", "teardrop", "ring"]
    for shape in complex_geo:
        assert shape in shape_ids, f"Missing complex geometric shape: {shape}"
    
    # Organic/Irregular (4)
    organic = ["blob", "cloud", "wave", "splat"]
    for shape in organic:
        assert shape in shape_ids, f"Missing organic shape: {shape}"
    
    # Angular/Arrows (3)
    angular = ["chevron", "arrow_up", "trapezoid"]
    for shape in angular:
        assert shape in shape_ids, f"Missing angular shape: {shape}"


def test_shape_templates_immutable():
    """Test that getting all templates returns a copy."""
    templates1 = get_all_shape_templates()
    templates2 = get_all_shape_templates()
    assert templates1 is not templates2, "Should return a copy, not the same list"
    assert len(templates1) == len(templates2), "Both lists should have same length"


def test_shape_ids_distinct():
    """Test that all shapes are visually distinct by checking they don't all use same geometry."""
    templates = get_all_shape_templates()
    geometry_functions = [template.geometry_fn for template in templates]
    # All geometry functions should be unique (different functions)
    assert len(set(geometry_functions)) == 25, "All shapes should have unique geometry functions"


def test_fill_directions_appropriate():
    """Test that fill directions are appropriately assigned."""
    templates = get_all_shape_templates()
    
    # Count each fill direction
    fill_counts = {
        "bottom_up": 0,
        "left_right": 0,
        "center_out": 0,
    }
    
    for template in templates:
        fill_counts[template.fill_direction] += 1
    
    # All three fill directions should be used
    for direction, count in fill_counts.items():
        assert count > 0, f"Fill direction '{direction}' is not used by any shape"
