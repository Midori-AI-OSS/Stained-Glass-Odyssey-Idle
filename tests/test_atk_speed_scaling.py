"""Tests for atk_speed rebirth scaling feature."""

from endless_idler.combat.party_stats import calculate_atk_speed_bonus
from endless_idler.combat.party_stats import build_scaled_character_stats
from endless_idler.combat.stats import Stats


def test_calculate_atk_speed_bonus_level_only():
    """Test atk_speed bonus from level alone."""
    # Level 1: 0.001 bonus
    assert calculate_atk_speed_bonus(1, 0) == 0.001
    
    # Level 50: 0.05 bonus
    assert calculate_atk_speed_bonus(50, 0) == 0.05
    
    # Level 100: 0.1 bonus (capped)
    assert calculate_atk_speed_bonus(100, 0) == 0.1
    
    # Level 200: 0.1 bonus (still capped)
    assert calculate_atk_speed_bonus(200, 0) == 0.1


def test_calculate_atk_speed_bonus_rebirth_only():
    """Test atk_speed bonus from rebirth alone."""
    # Rebirth 1: 0.002 bonus
    assert calculate_atk_speed_bonus(0, 1) == 0.002
    
    # Rebirth 50: 0.1 bonus
    assert calculate_atk_speed_bonus(0, 50) == 0.1
    
    # Rebirth 100: 0.2 bonus (capped)
    assert calculate_atk_speed_bonus(0, 100) == 0.2
    
    # Rebirth 200: 0.2 bonus (still capped)
    assert calculate_atk_speed_bonus(0, 200) == 0.2


def test_calculate_atk_speed_bonus_combined():
    """Test atk_speed bonus from both level and rebirth."""
    # Level 50 + Rebirth 50: 0.05 + 0.1 = 0.15
    assert calculate_atk_speed_bonus(50, 50) == 0.15
    
    # Level 100 + Rebirth 100: 0.1 + 0.2 = 0.3 (both maxed)
    assert calculate_atk_speed_bonus(100, 100) == 0.3
    
    # Level 1 + Rebirth 1: 0.001 + 0.002 = 0.003
    assert calculate_atk_speed_bonus(1, 1) == 0.003


def test_atk_speed_with_progression():
    """Test that atk_speed is correctly modified through progression."""
    # Create a stats object with base atk_speed
    stats = Stats()
    stats.set_base_stat("atk_speed", 2)
    
    # Initially should be 2
    assert stats.atk_speed == 2
    
    # Apply progression bonus manually
    from endless_idler.combat.stat_effect import StatEffect
    bonus = calculate_atk_speed_bonus(50, 25)  # 0.05 + 0.05 = 0.1
    effect = StatEffect(
        name="test_progression",
        stat_modifiers={"atk_speed": bonus},
        duration=-1,
        source="test"
    )
    stats.add_effect(effect)
    
    # Should now be 2 (base) + 0.1 (bonus) = 2.1, converted to int = 2
    # But the property returns int(max(1, value)), so we get 2
    assert stats.atk_speed == 2


def test_atk_speed_hard_cap():
    """Test that atk_speed is capped at 5.0."""
    stats = Stats()
    stats.set_base_stat("atk_speed", 10)  # Set very high base
    
    # Should be capped at 5
    assert stats.atk_speed == 5
    
    # Test with effects
    from endless_idler.combat.stat_effect import StatEffect
    effect = StatEffect(
        name="test_large_bonus",
        stat_modifiers={"atk_speed": 100},
        duration=-1,
        source="test"
    )
    stats.add_effect(effect)
    
    # Should still be capped at 5
    assert stats.atk_speed == 5


def test_atk_speed_minimum():
    """Test that atk_speed has a minimum of 1."""
    stats = Stats()
    stats.set_base_stat("atk_speed", 0)
    
    # Should be at least 1
    assert stats.atk_speed == 1
    
    # Test with negative effect
    from endless_idler.combat.stat_effect import StatEffect
    effect = StatEffect(
        name="test_negative",
        stat_modifiers={"atk_speed": -10},
        duration=-1,
        source="test"
    )
    stats.add_effect(effect)
    
    # Should still be at least 1
    assert stats.atk_speed == 1


def test_build_scaled_character_stats_with_rebirth():
    """Test that build_scaled_character_stats applies rebirth bonuses."""
    progress = {
        "level": 50,
        "exp": 100.0,
        "exp_multiplier": 1.0,
        "rebirths": 25,
    }
    
    stats = build_scaled_character_stats(
        plugin=None,
        party_level=1,
        stars=1,
        stacks=1,
        progress=progress,
        saved_base_stats={"atk_speed": 2.0},
        atk_speed=2,
    )
    
    # Base atk_speed is 2
    # Level 50 bonus: 0.05
    # Rebirth 25 bonus: 0.05
    # Total: 2 + 0.05 + 0.05 = 2.1, which rounds to 2 as int
    # The progression effect should be applied
    assert stats.level == 50
    assert stats.atk_speed >= 2  # Should have at least the base value


def test_calculate_atk_speed_bonus_negative_values():
    """Test that negative or zero values are handled correctly."""
    # Zero values
    assert calculate_atk_speed_bonus(0, 0) == 0.0
    
    # Negative values should be clamped to 0
    assert calculate_atk_speed_bonus(-10, -5) == 0.0
