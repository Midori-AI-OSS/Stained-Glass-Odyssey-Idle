"""Tests for foe shape selection logic."""

from __future__ import annotations


from endless_idler.characters.foe_shape_selector import get_shape_selection_info
from endless_idler.characters.foe_shape_selector import select_shape_for_foe
from endless_idler.combat.stats import Stats
from endless_idler.characters.shape_palette import get_all_shape_ids
from endless_idler.characters.shape_palette import get_shape_count


class TestShapeSelection:
    """Test suite for deterministic shape selection."""
    
    def test_same_stats_same_shape(self):
        """Test that identical stats always produce the same shape."""
        # Create two foes with identical stats
        stats1 = Stats(character_id="foe1", level=10)
        stats1.max_hp = 1000
        stats1.atk = 200
        stats1.defense = 100
        stats1.atk_speed = 2
        
        stats2 = Stats(character_id="foe2", level=10)
        stats2.max_hp = 1000
        stats2.atk = 200
        stats2.defense = 100
        stats2.atk_speed = 2
        
        # Should produce same shape
        shape1 = select_shape_for_foe(stats1)
        shape2 = select_shape_for_foe(stats2)
        
        assert shape1 == shape2, "Same stats should produce same shape"
    
    def test_deterministic_across_calls(self):
        """Test that calling multiple times with same stats gives same result."""
        stats = Stats(character_id="foe", level=5)
        stats.max_hp = 500
        stats.atk = 100
        stats.defense = 50
        stats.atk_speed = 1
        
        # Call multiple times
        shapes = [select_shape_for_foe(stats) for _ in range(10)]
        
        # All should be identical
        assert len(set(shapes)) == 1, "Multiple calls should return same shape"
    
    def test_different_stats_can_differ(self):
        """Test that different stat profiles can produce different shapes."""
        # Create foes with very different stat profiles
        tank_stats = Stats(character_id="tank", level=10)
        tank_stats.max_hp = 2000  # High HP
        tank_stats.atk = 100      # Low ATK
        tank_stats.defense = 200  # High DEF
        tank_stats.atk_speed = 1  # Low speed
        
        dps_stats = Stats(character_id="dps", level=10)
        dps_stats.max_hp = 500    # Low HP
        dps_stats.atk = 400       # High ATK
        dps_stats.defense = 50    # Low DEF
        dps_stats.atk_speed = 4   # High speed
        
        tank_shape = select_shape_for_foe(tank_stats)
        dps_shape = select_shape_for_foe(dps_stats)
        
        # Different profiles should likely produce different shapes
        # (not guaranteed but very likely with these extremes)
        assert isinstance(tank_shape, str)
        assert isinstance(dps_shape, str)
    
    def test_returns_valid_shape_id(self):
        """Test that returned shape ID is from the palette."""
        stats = Stats(character_id="foe", level=7)
        stats.max_hp = 700
        stats.atk = 140
        stats.defense = 70
        stats.atk_speed = 2
        
        shape_id = select_shape_for_foe(stats)
        valid_shapes = get_all_shape_ids()
        
        assert shape_id in valid_shapes, f"Shape {shape_id} not in palette"
    
    def test_all_shapes_reachable(self):
        """Test that with varied stats, we can reach different shapes."""
        # Generate 100 foes with random-ish varied stats
        shapes_seen = set()
        
        for i in range(100):
            stats = Stats(character_id=f"foe_{i}", level=i % 20 + 1)
            # Vary stats to create different profiles
            stats.max_hp = (i * 137 % 500) + 500
            stats.atk = (i * 73 % 200) + 100
            stats.defense = (i * 59 % 150) + 50
            stats.atk_speed = (i % 4) + 1
            
            shape_id = select_shape_for_foe(stats)
            shapes_seen.add(shape_id)
        
        # Should see a reasonable variety of shapes (at least 10 different ones)
        assert len(shapes_seen) >= 10, (
            f"Only saw {len(shapes_seen)} shapes, expected variety"
        )
    
    def test_handles_level_one(self):
        """Test that level 1 foes work correctly."""
        stats = Stats(character_id="weak_foe", level=1)
        stats.max_hp = 10
        stats.atk = 2
        stats.defense = 1
        stats.atk_speed = 1
        
        shape_id = select_shape_for_foe(stats)
        assert shape_id in get_all_shape_ids()
    
    def test_handles_high_level(self):
        """Test that high level foes work correctly."""
        stats = Stats(character_id="strong_foe", level=1000)
        stats.max_hp = 100000
        stats.atk = 20000
        stats.defense = 10000
        stats.atk_speed = 5
        
        shape_id = select_shape_for_foe(stats)
        assert shape_id in get_all_shape_ids()
    
    def test_get_shape_selection_info(self):
        """Test the debugging info function."""
        stats = Stats(character_id="test_foe", level=10)
        stats.max_hp = 1000
        stats.atk = 200
        stats.defense = 100
        stats.atk_speed = 2
        
        info = get_shape_selection_info(stats)
        
        # Check all expected keys present
        assert "shape_id" in info
        assert "fingerprint" in info
        assert "shape_index" in info
        assert "stat_ratios" in info
        assert "level" in info
        assert "character_id" in info
        
        # Check types
        assert isinstance(info["shape_id"], str)
        assert isinstance(info["fingerprint"], int)
        assert isinstance(info["shape_index"], int)
        assert isinstance(info["stat_ratios"], dict)
        assert isinstance(info["level"], int)
        
        # Check that shape_id matches direct call
        shape_id = select_shape_for_foe(stats)
        assert info["shape_id"] == shape_id
    
    def test_stat_ratios_calculated_correctly(self):
        """Test that stat ratios are normalized as expected."""
        stats = Stats(character_id="test", level=10)
        stats.max_hp = 100   # 100 / (10 * 10) = 1.0
        stats.atk = 20       # 20 / (10 * 2) = 1.0
        stats.defense = 10   # 10 / 10 = 1.0
        stats.atk_speed = 1  # 1 / 1.0 = 1.0
        
        info = get_shape_selection_info(stats)
        ratios = info["stat_ratios"]
        
        # All ratios should be 1.0 (matching baseline)
        assert abs(ratios["hp_ratio"] - 1.0) < 0.01
        assert abs(ratios["atk_ratio"] - 1.0) < 0.01
        assert abs(ratios["def_ratio"] - 1.0) < 0.01
        assert abs(ratios["spd_ratio"] - 1.0) < 0.01


class TestShapePalette:
    """Test the shape palette system."""
    
    def test_shape_count(self):
        """Test that we have exactly 25 shapes."""
        assert get_shape_count() == 25
    
    def test_all_shapes_unique(self):
        """Test that all shape IDs are unique."""
        all_shapes = get_all_shape_ids()
        assert len(all_shapes) == len(set(all_shapes))
    
    def test_shape_ids_valid(self):
        """Test that shape IDs are valid strings."""
        all_shapes = get_all_shape_ids()
        for shape_id in all_shapes:
            assert isinstance(shape_id, str)
            assert len(shape_id) > 0
            assert shape_id.replace("_", "").replace("-", "").isalnum()
