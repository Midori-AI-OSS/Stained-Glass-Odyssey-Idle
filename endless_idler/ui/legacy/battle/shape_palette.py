"""
Shape palette system for rendering foes.

This module defines 25 predefined shape templates with geometry, sizing,
and fill behavior for visualizing foes in battle.
"""

from __future__ import annotations

import math

from dataclasses import dataclass
from typing import Callable

from PySide6.QtGui import QPainterPath


@dataclass
class ShapeTemplate:
    """Template defining a shape's geometry and properties."""

    shape_id: str
    name: str
    geometry_fn: Callable[[float, float], QPainterPath]
    base_width: float
    base_height: float
    fill_direction: str  # "bottom_up", "left_right", "center_out"


def _create_circle(width: float, height: float) -> QPainterPath:
    """Create a circle path."""
    path = QPainterPath()
    path.addEllipse(0, 0, width, height)
    return path


def _create_square(width: float, height: float) -> QPainterPath:
    """Create a square path."""
    path = QPainterPath()
    path.addRect(0, 0, width, height)
    return path


def _create_triangle(width: float, height: float) -> QPainterPath:
    """Create an equilateral triangle pointing up."""
    path = QPainterPath()
    path.moveTo(width / 2, 0)  # Top point
    path.lineTo(width, height)  # Bottom right
    path.lineTo(0, height)  # Bottom left
    path.closeSubpath()
    return path


def _create_pentagon(width: float, height: float) -> QPainterPath:
    """Create a regular pentagon."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    radius = min(width, height) / 2
    for i in range(5):
        angle = math.radians(i * 72 - 90)  # Start at top
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    return path


def _create_hexagon(width: float, height: float) -> QPainterPath:
    """Create a regular hexagon."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    radius = min(width, height) / 2
    for i in range(6):
        angle = math.radians(i * 60 - 90)  # Start at top
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    return path


def _create_octagon(width: float, height: float) -> QPainterPath:
    """Create a regular octagon."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    radius = min(width, height) / 2
    for i in range(8):
        angle = math.radians(i * 45 - 90)  # Start at top
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    return path


def _create_star_4(width: float, height: float) -> QPainterPath:
    """Create a 4-pointed star."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    outer = min(width, height) / 2
    inner = outer * 0.4
    for i in range(8):
        angle = math.radians(i * 45 - 90)
        radius = outer if i % 2 == 0 else inner
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    return path


def _create_star_5(width: float, height: float) -> QPainterPath:
    """Create a 5-pointed star."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    outer = min(width, height) / 2
    inner = outer * 0.38
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        radius = outer if i % 2 == 0 else inner
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    return path


def _create_star_6(width: float, height: float) -> QPainterPath:
    """Create a 6-pointed star."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    outer = min(width, height) / 2
    inner = outer * 0.5
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        radius = outer if i % 2 == 0 else inner
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    return path


def _create_star_8(width: float, height: float) -> QPainterPath:
    """Create an 8-pointed star."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    outer = min(width, height) / 2
    inner = outer * 0.5
    for i in range(16):
        angle = math.radians(i * 22.5 - 90)
        radius = outer if i % 2 == 0 else inner
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    return path


def _create_star_burst(width: float, height: float) -> QPainterPath:
    """Create an irregular spiky star."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    outer = min(width, height) / 2
    inner = outer * 0.3
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        # Alternate between outer and inner, with some irregularity
        if i % 2 == 0:
            radius = outer * (0.9 + 0.1 * (i % 3))
        else:
            radius = inner * (0.8 + 0.2 * ((i + 1) % 3))
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    return path


def _create_diamond(width: float, height: float) -> QPainterPath:
    """Create a diamond (rotated square)."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    path.moveTo(cx, 0)  # Top
    path.lineTo(width, cy)  # Right
    path.lineTo(cx, height)  # Bottom
    path.lineTo(0, cy)  # Left
    path.closeSubpath()
    return path


def _create_cross(width: float, height: float) -> QPainterPath:
    """Create a plus sign cross."""
    path = QPainterPath()
    thickness = min(width, height) * 0.3
    cx, cy = width / 2, height / 2
    # Horizontal bar
    path.addRect(0, cy - thickness / 2, width, thickness)
    # Vertical bar
    path.addRect(cx - thickness / 2, 0, thickness, height)
    return path


def _create_x_cross(width: float, height: float) -> QPainterPath:
    """Create an X shape."""
    path = QPainterPath()
    thickness = min(width, height) * 0.25
    # Two diagonal bars
    path.moveTo(thickness, 0)
    path.lineTo(width, height - thickness)
    path.lineTo(width - thickness, height)
    path.lineTo(0, thickness)
    path.closeSubpath()
    
    path.moveTo(width - thickness, 0)
    path.lineTo(width, thickness)
    path.lineTo(thickness, height)
    path.lineTo(0, height - thickness)
    path.closeSubpath()
    return path


def _create_crescent(width: float, height: float) -> QPainterPath:
    """Create a crescent moon shape."""
    path = QPainterPath()
    # Outer circle
    path.addEllipse(0, 0, width, height)
    # Inner circle offset to create crescent
    offset = width * 0.25
    inner_path = QPainterPath()
    inner_path.addEllipse(offset, 0, width * 0.8, height)
    path = path.subtracted(inner_path)
    return path


def _create_heart(width: float, height: float) -> QPainterPath:
    """Create a heart shape."""
    path = QPainterPath()
    # Two circles at top and triangle at bottom
    r = width / 4
    path.addEllipse(r / 2, 0, r * 2, r * 2)
    path.addEllipse(width - r * 2.5, 0, r * 2, r * 2)
    # Bottom triangle point
    path.moveTo(0, r)
    path.lineTo(width / 2, height)
    path.lineTo(width, r)
    return path


def _create_teardrop(width: float, height: float) -> QPainterPath:
    """Create a teardrop shape."""
    path = QPainterPath()
    cx = width / 2
    # Circle at bottom
    r = width / 2
    path.addEllipse(0, height - width, width, width)
    # Point at top
    path.moveTo(cx, 0)
    path.lineTo(0, height - r)
    path.moveTo(cx, 0)
    path.lineTo(width, height - r)
    return path


def _create_ring(width: float, height: float) -> QPainterPath:
    """Create a ring (circle with hole)."""
    path = QPainterPath()
    path.addEllipse(0, 0, width, height)
    # Inner hole
    margin = min(width, height) * 0.3
    inner_path = QPainterPath()
    inner_path.addEllipse(margin, margin, width - 2 * margin, height - 2 * margin)
    path = path.subtracted(inner_path)
    return path


def _create_blob(width: float, height: float) -> QPainterPath:
    """Create an irregular rounded blob."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    radius = min(width, height) / 2
    # Create irregular blob with varying radii
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    radii = [0.9, 1.0, 0.8, 1.1, 0.85, 0.95, 1.05, 0.9]
    for i, (angle, r_factor) in enumerate(zip(angles, radii)):
        angle_rad = math.radians(angle - 90)
        r = radius * r_factor
        x = cx + r * math.cos(angle_rad)
        y = cy + r * math.sin(angle_rad)
        if i == 0:
            path.moveTo(x, y)
        else:
            # Use quadratic curves for smoothness
            ctrl_angle = math.radians((angles[i - 1] + angle) / 2 - 90)
            ctrl_r = radius * (radii[i - 1] + r_factor) / 2
            ctrl_x = cx + ctrl_r * math.cos(ctrl_angle)
            ctrl_y = cy + ctrl_r * math.sin(ctrl_angle)
            path.quadTo(ctrl_x, ctrl_y, x, y)
    path.closeSubpath()
    return path


def _create_cloud(width: float, height: float) -> QPainterPath:
    """Create a puffy cloud shape."""
    path = QPainterPath()
    # Multiple overlapping circles
    r1 = width * 0.3
    r2 = width * 0.25
    r3 = width * 0.28
    path.addEllipse(0, height * 0.3, r1 * 2, r1 * 2)
    path.addEllipse(width * 0.3, 0, r2 * 2, r2 * 2)
    path.addEllipse(width * 0.5, height * 0.2, r3 * 2, r3 * 2)
    return path


def _create_wave(width: float, height: float) -> QPainterPath:
    """Create a sine wave shape."""
    path = QPainterPath()
    amplitude = height / 4
    cy = height / 2
    path.moveTo(0, cy)
    # Create sine wave
    steps = 20
    for i in range(steps + 1):
        x = (i / steps) * width
        y = cy + amplitude * math.sin((i / steps) * 4 * math.pi)
        path.lineTo(x, y)
    # Close the path
    path.lineTo(width, height)
    path.lineTo(0, height)
    path.closeSubpath()
    return path


def _create_splat(width: float, height: float) -> QPainterPath:
    """Create an irregular splat shape."""
    path = QPainterPath()
    cx, cy = width / 2, height / 2
    radius = min(width, height) / 2
    # Create irregular star-like splat
    angles = list(range(0, 360, 30))
    for i, angle in enumerate(angles):
        angle_rad = math.radians(angle - 90)
        # Vary radius irregularly
        r = radius * (0.6 + 0.4 * ((i * 7) % 10) / 10)
        x = cx + r * math.cos(angle_rad)
        y = cy + r * math.sin(angle_rad)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    return path


def _create_chevron(width: float, height: float) -> QPainterPath:
    """Create a chevron (V pointing down)."""
    path = QPainterPath()
    thickness = min(width, height) * 0.2
    cx = width / 2
    # V shape
    path.moveTo(0, 0)
    path.lineTo(cx, height - thickness)
    path.lineTo(width, 0)
    path.lineTo(width - thickness, 0)
    path.lineTo(cx, height - thickness * 2)
    path.lineTo(thickness, 0)
    path.closeSubpath()
    return path


def _create_arrow_up(width: float, height: float) -> QPainterPath:
    """Create an arrow pointing up."""
    path = QPainterPath()
    cx = width / 2
    shaft_width = width * 0.3
    head_height = height * 0.4
    # Arrow head (triangle)
    path.moveTo(cx, 0)
    path.lineTo(0, head_height)
    path.lineTo(cx - shaft_width / 2, head_height)
    # Shaft
    path.lineTo(cx - shaft_width / 2, height)
    path.lineTo(cx + shaft_width / 2, height)
    path.lineTo(cx + shaft_width / 2, head_height)
    # Complete head
    path.lineTo(width, head_height)
    path.closeSubpath()
    return path


def _create_trapezoid(width: float, height: float) -> QPainterPath:
    """Create a trapezoid (wider at top)."""
    path = QPainterPath()
    inset = width * 0.2
    path.moveTo(0, 0)
    path.lineTo(width, 0)
    path.lineTo(width - inset, height)
    path.lineTo(inset, height)
    path.closeSubpath()
    return path


# Shape palette - 25 unique templates
_SHAPE_TEMPLATES = [
    # Basic Polygons (6)
    ShapeTemplate("circle", "Circle", _create_circle, 50, 50, "bottom_up"),
    ShapeTemplate("square", "Square", _create_square, 50, 50, "bottom_up"),
    ShapeTemplate("triangle", "Triangle", _create_triangle, 50, 50, "bottom_up"),
    ShapeTemplate("pentagon", "Pentagon", _create_pentagon, 50, 50, "bottom_up"),
    ShapeTemplate("hexagon", "Hexagon", _create_hexagon, 50, 50, "bottom_up"),
    ShapeTemplate("octagon", "Octagon", _create_octagon, 50, 50, "bottom_up"),
    # Stars (5)
    ShapeTemplate("star_4", "4-Point Star", _create_star_4, 50, 50, "center_out"),
    ShapeTemplate("star_5", "5-Point Star", _create_star_5, 50, 50, "center_out"),
    ShapeTemplate("star_6", "6-Point Star", _create_star_6, 50, 50, "center_out"),
    ShapeTemplate("star_8", "8-Point Star", _create_star_8, 50, 50, "center_out"),
    ShapeTemplate("star_burst", "Burst Star", _create_star_burst, 50, 50, "center_out"),
    # Complex Geometric (7)
    ShapeTemplate("diamond", "Diamond", _create_diamond, 50, 50, "bottom_up"),
    ShapeTemplate("cross", "Cross", _create_cross, 50, 50, "center_out"),
    ShapeTemplate("x_cross", "X Cross", _create_x_cross, 50, 50, "center_out"),
    ShapeTemplate("crescent", "Crescent", _create_crescent, 50, 50, "left_right"),
    ShapeTemplate("heart", "Heart", _create_heart, 50, 50, "bottom_up"),
    ShapeTemplate("teardrop", "Teardrop", _create_teardrop, 50, 60, "bottom_up"),
    ShapeTemplate("ring", "Ring", _create_ring, 50, 50, "center_out"),
    # Organic/Irregular (4)
    ShapeTemplate("blob", "Blob", _create_blob, 50, 50, "center_out"),
    ShapeTemplate("cloud", "Cloud", _create_cloud, 60, 40, "bottom_up"),
    ShapeTemplate("wave", "Wave", _create_wave, 60, 40, "left_right"),
    ShapeTemplate("splat", "Splat", _create_splat, 50, 50, "center_out"),
    # Angular/Arrows (3)
    ShapeTemplate("chevron", "Chevron", _create_chevron, 50, 40, "bottom_up"),
    ShapeTemplate("arrow_up", "Arrow Up", _create_arrow_up, 40, 60, "bottom_up"),
    ShapeTemplate("trapezoid", "Trapezoid", _create_trapezoid, 50, 40, "bottom_up"),
]

# Create lookup dictionary
_SHAPE_LOOKUP = {template.shape_id: template for template in _SHAPE_TEMPLATES}


def get_shape_template(shape_id: str) -> ShapeTemplate:
    """
    Get a shape template by its ID.

    Args:
        shape_id: Unique identifier for the shape

    Returns:
        The ShapeTemplate for the given ID

    Raises:
        KeyError: If the shape_id is not found
    """
    if shape_id not in _SHAPE_LOOKUP:
        raise KeyError(f"Unknown shape_id: {shape_id}")
    return _SHAPE_LOOKUP[shape_id]


def get_all_shape_ids() -> list[str]:
    """
    Get a list of all available shape IDs.

    Returns:
        List of all shape IDs in the palette
    """
    return list(_SHAPE_LOOKUP.keys())


def get_all_shape_templates() -> list[ShapeTemplate]:
    """
    Get a list of all shape templates.

    Returns:
        List of all ShapeTemplate objects
    """
    return _SHAPE_TEMPLATES.copy()
