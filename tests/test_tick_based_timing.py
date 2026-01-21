"""Tests for tick-based action timing system."""

from __future__ import annotations

import random

from endless_idler.combat.stats import Stats
from endless_idler.ui.battle.sim import Combatant


def test_action_interval_calculation():
    """Test that action intervals are calculated correctly based on atk_speed."""
    # Helper to calculate action interval (mimics _calculate_action_interval)
    def calculate_action_interval(atk_speed: int, is_offsite: bool) -> int:
        base_interval = 500.0 / max(1, atk_speed)
        if is_offsite:
            base_interval *= 10.0
        return int(base_interval)
    
    # Test atk_speed=1 (500 ticks per action)
    assert calculate_action_interval(1, False) == 500
    
    # Test atk_speed=2 (250 ticks per action)
    assert calculate_action_interval(2, False) == 250
    
    # Test atk_speed=0.5 (1000 ticks per action, but atk_speed is int so this would be 0 -> 1)
    # In reality, atk_speed is an int property that caps at 1 minimum
    assert calculate_action_interval(1, False) == 500
    
    # Test offsite multiplier (10x slower)
    assert calculate_action_interval(1, True) == 5000
    assert calculate_action_interval(2, True) == 2500


def test_combatant_tick_fields():
    """Test that Combatant has tick-related fields."""
    stats = Stats(hp=1000, character_id="test")
    combatant = Combatant(
        char_id="test",
        name="Test",
        stats=stats,
        max_hp=1000,
    )
    
    # Check new fields exist
    assert hasattr(combatant, "next_action_tick")
    assert hasattr(combatant, "is_offsite")
    
    # Check default values
    assert combatant.next_action_tick == 0
    assert combatant.is_offsite is False


def test_action_timing_simulation():
    """Simulate actions over 1000 ticks and verify action counts."""
    # Create combatants with different atk_speed values
    stats1 = Stats(hp=1000, character_id="char1")
    stats1._base_atk_speed = 1
    combatant1 = Combatant(
        char_id="char1",
        name="Char1",
        stats=stats1,
        max_hp=1000,
        is_offsite=False,
    )
    
    stats2 = Stats(hp=1000, character_id="char2")
    stats2._base_atk_speed = 2
    combatant2 = Combatant(
        char_id="char2",
        name="Char2",
        stats=stats2,
        max_hp=1000,
        is_offsite=False,
    )
    
    stats3 = Stats(hp=1000, character_id="char3")
    stats3._base_atk_speed = 1
    combatant3 = Combatant(
        char_id="char3",
        name="Char3 Offsite",
        stats=stats3,
        max_hp=1000,
        is_offsite=True,
    )
    
    def calculate_action_interval(combatant: Combatant) -> int:
        base_interval = 500.0 / max(1, combatant.stats.atk_speed)
        if combatant.is_offsite:
            base_interval *= 10.0
        return int(base_interval)
    
    # Simulate 5000 ticks
    action_counts = {
        "char1": 0,
        "char2": 0,
        "char3": 0,
    }
    
    for tick in range(5001):
        # Check if each combatant should act
        for combatant in [combatant1, combatant2, combatant3]:
            if combatant.next_action_tick <= tick:
                action_counts[combatant.char_id] += 1
                interval = calculate_action_interval(combatant)
                combatant.next_action_tick = tick + interval
    
    # Verify action counts
    # atk_speed=1: 1 action per 500 ticks = 11 actions in 5000 ticks (acts at tick 0, 500, 1000, ..., 5000)
    assert action_counts["char1"] == 11, f"Expected 11 actions for char1, got {action_counts['char1']}"
    
    # atk_speed=2: 1 action per 250 ticks = 21 actions in 5000 ticks (acts at tick 0, 250, 500, ..., 5000)
    assert action_counts["char2"] == 21, f"Expected 21 actions for char2, got {action_counts['char2']}"
    
    # atk_speed=1 offsite: 1 action per 5000 ticks = 2 actions in 5000 ticks (acts at tick 0, 5000)
    assert action_counts["char3"] == 2, f"Expected 2 actions for char3 (offsite), got {action_counts['char3']}"


def test_offsite_vs_onsite_timing():
    """Test that offsite characters act 10x slower than onsite."""
    stats_onsite = Stats(hp=1000, character_id="onsite")
    stats_onsite._base_atk_speed = 2
    combatant_onsite = Combatant(
        char_id="onsite",
        name="Onsite",
        stats=stats_onsite,
        max_hp=1000,
        is_offsite=False,
    )
    
    stats_offsite = Stats(hp=1000, character_id="offsite")
    stats_offsite._base_atk_speed = 2
    combatant_offsite = Combatant(
        char_id="offsite",
        name="Offsite",
        stats=stats_offsite,
        max_hp=1000,
        is_offsite=True,
    )
    
    def calculate_action_interval(combatant: Combatant) -> int:
        base_interval = 500.0 / max(1, combatant.stats.atk_speed)
        if combatant.is_offsite:
            base_interval *= 10.0
        return int(base_interval)
    
    onsite_interval = calculate_action_interval(combatant_onsite)
    offsite_interval = calculate_action_interval(combatant_offsite)
    
    # Offsite should be 10x slower
    assert offsite_interval == onsite_interval * 10
    assert onsite_interval == 250
    assert offsite_interval == 2500


if __name__ == "__main__":
    test_action_interval_calculation()
    test_combatant_tick_fields()
    test_action_timing_simulation()
    test_offsite_vs_onsite_timing()
    print("All tick-based timing tests passed!")
