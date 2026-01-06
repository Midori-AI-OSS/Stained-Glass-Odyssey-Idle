"""Tests for Lady Darkness's Eclipsing Veil passive ability.

This test suite verifies that the Eclipsing Veil passive correctly:
- Amplifies damage by 2x
- Ignores 50% of target defense
- Triggers only when Lady Darkness attacks
- Handles edge cases properly
"""

import pytest

from unittest.mock import Mock

from endless_idler.passives.implementations.lady_darkness_eclipsing_veil import (
    LadyDarknessEclipsingVeil,
)
from endless_idler.passives.registry import get_passive, load_passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext


class TestLadyDarknessEclipsingVeil:
    """Test suite for Lady Darkness's Eclipsing Veil passive."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.passive = LadyDarknessEclipsingVeil()
        
        # Create mock stats objects
        self.lady_darkness = Mock()
        self.lady_darkness.name = "Lady Darkness"
        self.lady_darkness.atk = 1000
        self.lady_darkness.defense = 300
        self.lady_darkness.hp = 2000
        
        self.enemy = Mock()
        self.enemy.name = "Enemy"
        self.enemy.defense = 200
        self.enemy.hp = 1000
        
        self.other_character = Mock()
        self.other_character.name = "Other Character"
        self.other_character.atk = 500
        self.other_character.defense = 150
        self.other_character.hp = 1500
    
    def create_context(self, attacker, target):
        """Helper to create a TriggerContext for testing.
        
        Args:
            attacker: The attacking character
            target: The target of the attack
            
        Returns:
            TriggerContext configured for PRE_DAMAGE trigger
        """
        return TriggerContext(
            trigger=PassiveTrigger.PRE_DAMAGE,
            owner_stats=self.lady_darkness,
            all_allies=[self.lady_darkness],
            onsite_allies=[self.lady_darkness],
            offsite_allies=[],
            enemies=[target],
            extra={
                "attacker": attacker,
                "target": target,
            },
        )
    
    def test_passive_initialization(self):
        """Test that passive initializes with correct attributes."""
        assert self.passive.id == "lady_darkness_eclipsing_veil"
        assert self.passive.display_name == "Eclipsing Veil"
        assert len(self.passive.description) > 0
        assert PassiveTrigger.PRE_DAMAGE in self.passive.triggers
        assert self.passive.damage_multiplier == 2.0
        assert self.passive.defense_ignore == 0.50
    
    def test_passive_registration(self):
        """Test that passive is properly registered in the registry."""
        # Import the module to trigger registration
        
        passive_class = get_passive("lady_darkness_eclipsing_veil")
        assert passive_class is not None
        assert passive_class == LadyDarknessEclipsingVeil
        
        # Test loading an instance
        instance = load_passive("lady_darkness_eclipsing_veil")
        assert instance is not None
        assert isinstance(instance, LadyDarknessEclipsingVeil)
    
    def test_can_trigger_when_lady_darkness_attacks(self):
        """Test that passive triggers when Lady Darkness attacks."""
        context = self.create_context(self.lady_darkness, self.enemy)
        assert self.passive.can_trigger(context) is True
    
    def test_cannot_trigger_when_other_attacks(self):
        """Test that passive does not trigger when another character attacks."""
        context = self.create_context(self.other_character, self.enemy)
        assert self.passive.can_trigger(context) is False
    
    def test_cannot_trigger_without_attacker(self):
        """Test that passive does not trigger when attacker is missing."""
        context = TriggerContext(
            trigger=PassiveTrigger.PRE_DAMAGE,
            owner_stats=self.lady_darkness,
            all_allies=[self.lady_darkness],
            onsite_allies=[self.lady_darkness],
            offsite_allies=[],
            enemies=[self.enemy],
            extra={"target": self.enemy},  # No attacker
        )
        assert self.passive.can_trigger(context) is False
    
    def test_execute_basic_damage_amplification(self):
        """Test basic damage amplification and defense ignore."""
        context = self.create_context(self.lady_darkness, self.enemy)
        result = self.passive.execute(context)
        
        assert result["damage_multiplier"] == 2.0
        assert result["defense_ignore"] == 0.50
        assert result["original_defense"] == 200
        assert result["effective_defense"] == 100  # 200 * 0.50
    
    def test_execute_high_defense_enemy(self):
        """Test that defense ignore is effective against high-defense enemies."""
        high_defense_enemy = Mock()
        high_defense_enemy.defense = 800
        high_defense_enemy.hp = 3000
        
        context = self.create_context(self.lady_darkness, high_defense_enemy)
        result = self.passive.execute(context)
        
        assert result["original_defense"] == 800
        assert result["effective_defense"] == 400  # 800 * 0.50
        assert result["damage_multiplier"] == 2.0
    
    def test_execute_zero_defense_enemy(self):
        """Test passive still applies damage multiplier against zero defense."""
        zero_defense_enemy = Mock()
        zero_defense_enemy.defense = 0
        zero_defense_enemy.hp = 500
        
        context = self.create_context(self.lady_darkness, zero_defense_enemy)
        result = self.passive.execute(context)
        
        assert result["original_defense"] == 0
        assert result["effective_defense"] == 0
        assert result["damage_multiplier"] == 2.0
    
    def test_execute_without_target(self):
        """Test execute returns neutral modifiers when target is missing."""
        context = TriggerContext(
            trigger=PassiveTrigger.PRE_DAMAGE,
            owner_stats=self.lady_darkness,
            all_allies=[self.lady_darkness],
            onsite_allies=[self.lady_darkness],
            offsite_allies=[],
            enemies=[],
            extra={"attacker": self.lady_darkness},  # No target
        )
        
        result = self.passive.execute(context)
        
        assert result["damage_multiplier"] == 1.0
        assert result["defense_ignore"] == 0.0
    
    def test_damage_calculation_example(self):
        """Test complete damage calculation example.
        
        This test demonstrates the expected damage calculation flow:
        1. Start with base attack - effective defense
        2. Apply damage multiplier
        
        Example: Lady Darkness (1000 ATK) vs Enemy (200 DEF, 1000 HP)
        - Effective defense: 200 * 0.50 = 100
        - Base damage: 1000 - 100 = 900
        - Final damage: 900 * 2.0 = 1800
        """
        context = self.create_context(self.lady_darkness, self.enemy)
        
        # Verify passive can trigger
        assert self.passive.can_trigger(context) is True
        
        # Get passive modifiers
        result = self.passive.execute(context)
        
        # Calculate damage using passive modifiers
        effective_defense = result["effective_defense"]
        damage_multiplier = result["damage_multiplier"]
        
        base_damage = self.lady_darkness.atk - effective_defense
        final_damage = base_damage * damage_multiplier
        
        # Verify calculations
        assert effective_defense == 100
        assert base_damage == 900
        assert final_damage == 1800
    
    def test_damage_calculation_high_defense(self):
        """Test damage calculation against high-defense enemy.
        
        Example: Lady Darkness (1000 ATK) vs Tank (800 DEF, 3000 HP)
        - Effective defense: 800 * 0.50 = 400
        - Base damage: 1000 - 400 = 600
        - Final damage: 600 * 2.0 = 1200
        """
        tank = Mock()
        tank.defense = 800
        tank.hp = 3000
        
        context = self.create_context(self.lady_darkness, tank)
        result = self.passive.execute(context)
        
        effective_defense = result["effective_defense"]
        damage_multiplier = result["damage_multiplier"]
        
        base_damage = self.lady_darkness.atk - effective_defense
        final_damage = base_damage * damage_multiplier
        
        assert effective_defense == 400
        assert base_damage == 600
        assert final_damage == 1200
    
    def test_passive_always_active(self):
        """Test that passive is always active when Lady Darkness attacks.
        
        Unlike conditional passives, Eclipsing Veil has no HP threshold,
        position requirement, or other conditions. It should always work.
        """
        # Test at full HP
        self.lady_darkness.hp = 2000
        context = self.create_context(self.lady_darkness, self.enemy)
        assert self.passive.can_trigger(context) is True
        
        # Test at low HP
        self.lady_darkness.hp = 100
        context = self.create_context(self.lady_darkness, self.enemy)
        assert self.passive.can_trigger(context) is True
        
        # Test with different enemy types
        boss = Mock()
        boss.defense = 1500
        context = self.create_context(self.lady_darkness, boss)
        assert self.passive.can_trigger(context) is True


@pytest.mark.parametrize(
    "enemy_defense,expected_effective",
    [
        (0, 0),
        (100, 50),
        (200, 100),
        (500, 250),
        (1000, 500),
        (2000, 1000),
    ],
)
def test_defense_ignore_calculation(enemy_defense, expected_effective):
    """Test defense ignore calculation with various defense values.
    
    Args:
        enemy_defense: The enemy's original defense stat
        expected_effective: The expected effective defense after ignore
    """
    passive = LadyDarknessEclipsingVeil()
    
    lady_darkness = Mock()
    lady_darkness.atk = 1000
    
    enemy = Mock()
    enemy.defense = enemy_defense
    
    context = TriggerContext(
        trigger=PassiveTrigger.PRE_DAMAGE,
        owner_stats=lady_darkness,
        all_allies=[lady_darkness],
        onsite_allies=[lady_darkness],
        offsite_allies=[],
        enemies=[enemy],
        extra={
            "attacker": lady_darkness,
            "target": enemy,
        },
    )
    
    result = passive.execute(context)
    assert result["effective_defense"] == expected_effective
    assert result["damage_multiplier"] == 2.0
