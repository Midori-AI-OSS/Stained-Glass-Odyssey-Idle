"""
Test party builder character stats loading.

This test verifies that character progression (level, exp, exp_multiplier)
is correctly loaded and displayed in the party builder tooltips.
"""
from __future__ import annotations

from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.save import RunSave


def test_character_stats_load_with_progress():
    """
    Test that character stats correctly apply progress data.
    
    Verifies that when progress data is provided, the built stats
    reflect the level, exp, and exp_multiplier from the progress dict.
    """
    # Create a mock plugin with base stats
    class MockPlugin:
        id = "test_character"
        name = "Test Character"
        stars = 3
        base_stats = {
            "max_hp": 1000.0,
            "atk": 200.0,
            "defense": 200.0,
            "regain": 100.0,
        }
    
    plugin = MockPlugin()
    
    # Test with no progress (should default to level 1)
    stats_no_progress = build_scaled_character_stats(
        plugin=plugin,
        party_level=5,
        stars=3,
        stacks=1,
        progress=None,
        saved_base_stats=None,
    )
    
    assert stats_no_progress.level == 1, "Should default to level 1 with no progress"
    assert stats_no_progress.exp == 0, "Should default to 0 exp with no progress"
    assert stats_no_progress.exp_multiplier == 1.0, "Should default to 1.0 exp_multiplier with no progress"
    
    # Test with progress data (level 25, some exp, 1.5x multiplier)
    progress_data = {
        "level": 25,
        "exp": 12345,
        "exp_multiplier": 1.5,
        "rebirths": 0,
    }
    
    stats_with_progress = build_scaled_character_stats(
        plugin=plugin,
        party_level=5,
        stars=3,
        stacks=1,
        progress=progress_data,
        saved_base_stats=None,
    )
    
    assert stats_with_progress.level == 25, f"Should be level 25, got {stats_with_progress.level}"
    assert stats_with_progress.exp == 12345, f"Should have 12345 exp, got {stats_with_progress.exp}"
    assert stats_with_progress.exp_multiplier == 1.5, f"Should have 1.5 exp_multiplier, got {stats_with_progress.exp_multiplier}"


def test_party_builder_uses_saved_progress():
    """
    Test that the party builder's tooltip stats loading uses saved progress.
    
    This simulates what happens in party_builder.py's _tooltip_stats_for_character method.
    """
    # Create a save with character progress
    save = RunSave()
    save.party_level = 10
    
    # Simulate a character that has been leveled up
    char_id = "knight"
    save.character_progress[char_id] = {
        "level": 42,
        "exp": 98765,
        "exp_multiplier": 2.0,
        "rebirths": 0,
    }
    save.stacks[char_id] = 3
    
    # Simulate building stats the same way party_builder does
    class MockPlugin:
        id = char_id
        name = "Knight"
        stars = 5
        base_stats = {
            "max_hp": 1200.0,
            "atk": 250.0,
            "defense": 300.0,
            "regain": 120.0,
        }
    
    plugin = MockPlugin()
    
    # Build stats using saved progress
    stats = build_scaled_character_stats(
        plugin=plugin,
        party_level=save.party_level,
        stars=plugin.stars,
        stacks=save.stacks.get(char_id, 1),
        progress=save.character_progress.get(char_id),
        saved_base_stats=save.character_stats.get(char_id),
    )
    
    # Verify the stats reflect the saved progress
    assert stats.level == 42, f"Tooltip should show level 42, got {stats.level}"
    assert stats.exp == 98765, f"Tooltip should show 98765 exp, got {stats.exp}"
    assert stats.exp_multiplier == 2.0, f"Tooltip should show 2.0 exp_multiplier, got {stats.exp_multiplier}"


if __name__ == "__main__":
    test_character_stats_load_with_progress()
    test_party_builder_uses_saved_progress()
    print("All tests passed!")
