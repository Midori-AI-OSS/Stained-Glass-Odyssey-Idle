"""Tests for Lady Light's Radiant Aegis passive ability.

This test suite verifies that the Radiant Aegis passive correctly:
- Heals all party members (onsite + offsite)
- Only triggers when Lady Light is offsite
- Respects max HP limits
- Heals based on Lady Light's regain stat
- Handles edge cases properly
"""

import pytest

from unittest.mock import Mock

from endless_idler.passives.implementations.lady_light_radiant_aegis import (
    LadyLightRadiantAegis,
)
from endless_idler.passives.registry import get_passive, load_passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext


class TestLadyLightRadiantAegis:
    """Test suite for Lady Light's Radiant Aegis passive."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        self.passive = LadyLightRadiantAegis()

        # Create mock stats objects
        self.lady_light = Mock()
        self.lady_light.name = "Lady Light"
        self.lady_light.hp = 1000
        self.lady_light.max_hp = 1000
        self.lady_light.regain = 200

        self.ally1 = Mock()
        self.ally1.name = "Ally 1"
        self.ally1.hp = 500
        self.ally1.max_hp = 1000
        self.ally1.character_id = "ally_1"

        self.ally2 = Mock()
        self.ally2.name = "Ally 2"
        self.ally2.hp = 800
        self.ally2.max_hp = 1000
        self.ally2.character_id = "ally_2"

        self.ally3 = Mock()
        self.ally3.name = "Ally 3"
        self.ally3.hp = 300
        self.ally3.max_hp = 500
        self.ally3.character_id = "ally_3"

    def create_context(self, owner_offsite=True, allies_onsite=None, allies_offsite=None):
        """Helper to create a TriggerContext for testing.

        Args:
            owner_offsite: Whether Lady Light is offsite
            allies_onsite: List of onsite allies (default: ally1, ally2)
            allies_offsite: List of offsite allies (default: lady_light)

        Returns:
            TriggerContext configured for TURN_START trigger
        """
        if allies_onsite is None:
            allies_onsite = [self.ally1, self.ally2]
        if allies_offsite is None:
            allies_offsite = [self.lady_light] if owner_offsite else []

        # If owner is not offsite, add to onsite
        if not owner_offsite and self.lady_light not in allies_onsite:
            allies_onsite = [self.lady_light] + allies_onsite
            allies_offsite = [a for a in allies_offsite if a != self.lady_light]

        all_allies = list(set(allies_onsite + allies_offsite))

        return TriggerContext(
            trigger=PassiveTrigger.TURN_START,
            owner_stats=self.lady_light,
            all_allies=all_allies,
            onsite_allies=allies_onsite,
            offsite_allies=allies_offsite,
            enemies=[],
            extra={},
        )

    def test_passive_initialization(self):
        """Test that passive initializes with correct attributes."""
        assert self.passive.id == "lady_light_radiant_aegis"
        assert self.passive.display_name == "Radiant Aegis"
        assert len(self.passive.description) > 0
        assert PassiveTrigger.TURN_START in self.passive.triggers
        assert self.passive.heal_multiplier == 0.50

    def test_passive_registration(self):
        """Test that passive is properly registered in the registry."""
        # Import the module to trigger registration

        passive_class = get_passive("lady_light_radiant_aegis")
        assert passive_class is not None
        assert passive_class == LadyLightRadiantAegis

        # Test loading an instance
        instance = load_passive("lady_light_radiant_aegis")
        assert instance is not None
        assert isinstance(instance, LadyLightRadiantAegis)

    def test_can_trigger_when_lady_light_offsite(self):
        """Test that passive triggers when Lady Light is offsite."""
        context = self.create_context(owner_offsite=True)
        assert self.passive.can_trigger(context) is True

    def test_cannot_trigger_when_lady_light_onsite(self):
        """Test that passive does not trigger when Lady Light is onsite."""
        context = self.create_context(owner_offsite=False)
        assert self.passive.can_trigger(context) is False

    def test_heal_all_allies_basic(self):
        """Test healing all allies when Lady Light is offsite."""
        # Setup: ally1 at 500/1000 HP, ally2 at 800/1000 HP
        context = self.create_context(owner_offsite=True)

        # Lady Light has 200 regain, heal_multiplier is 0.50
        # Expected heal: 200 * 0.50 = 100 per ally
        result = self.passive.execute(context)

        assert result["base_heal_amount"] == 100
        assert result["total_healing"] == 200  # 100 (ally1) + 100 (ally2), lady_light is at max
        assert self.ally1.hp == 600  # 500 + 100
        assert self.ally2.hp == 900  # 800 + 100
        assert self.lady_light.hp == 1000  # Already at max, no change
        assert len(result["healed"]) == 2  # Only ally1 and ally2 needed healing

    def test_heal_respects_max_hp(self):
        """Test that healing does not exceed max HP."""
        # Ally3 is at 980 HP with max 1000 HP
        self.ally3.hp = 980
        self.ally3.max_hp = 1000

        context = self.create_context(
            owner_offsite=True,
            allies_onsite=[self.ally3],
            allies_offsite=[self.lady_light],
        )

        # Expected heal: 100, but ally3 only needs 20 to reach max
        result = self.passive.execute(context)

        assert self.ally3.hp == 1000  # Capped at max
        assert result["total_healing"] == 20  # Only 20 was actually healed
        assert ("ally_3", 20) in result["healed"]

    def test_heal_zero_when_all_at_max_hp(self):
        """Test that no healing occurs when all allies are at max HP."""
        self.lady_light.hp = 1000
        self.ally1.hp = 1000
        self.ally2.hp = 1000

        context = self.create_context(owner_offsite=True)
        result = self.passive.execute(context)

        assert result["total_healing"] == 0
        assert len(result["healed"]) == 0
        assert result["base_heal_amount"] == 100

    def test_heal_both_onsite_and_offsite_allies(self):
        """Test that both onsite and offsite allies receive healing."""
        # ally1 onsite, ally2 offsite, both damaged
        context = self.create_context(
            owner_offsite=True,
            allies_onsite=[self.ally1],
            allies_offsite=[self.lady_light, self.ally2],
        )

        result = self.passive.execute(context)

        # Both allies should be healed
        assert self.ally1.hp == 600  # 500 + 100
        assert self.ally2.hp == 900  # 800 + 100
        assert result["total_healing"] == 200

    def test_heal_scales_with_regain_stat(self):
        """Test that heal amount scales with Lady Light's regain stat."""
        # Increase Lady Light's regain
        self.lady_light.regain = 400

        context = self.create_context(owner_offsite=True)

        # Expected heal: 400 * 0.50 = 200
        result = self.passive.execute(context)

        assert result["base_heal_amount"] == 200
        assert self.ally1.hp == 700  # 500 + 200
        assert self.ally2.hp == 1000  # 800 + 200 = 1000 (capped)

    def test_heal_with_low_regain(self):
        """Test healing with low regain stat."""
        self.lady_light.regain = 50

        context = self.create_context(owner_offsite=True)

        # Expected heal: 50 * 0.50 = 25
        result = self.passive.execute(context)

        assert result["base_heal_amount"] == 25
        assert self.ally1.hp == 525  # 500 + 25
        assert self.ally2.hp == 825  # 800 + 25

    def test_heal_with_zero_regain(self):
        """Test that no healing occurs with zero regain."""
        self.lady_light.regain = 0

        context = self.create_context(owner_offsite=True)

        result = self.passive.execute(context)

        assert result["base_heal_amount"] == 0
        assert result["total_healing"] == 0
        assert self.ally1.hp == 500  # Unchanged
        assert self.ally2.hp == 800  # Unchanged

    def test_heal_empty_party(self):
        """Test that passive handles empty party gracefully."""
        context = self.create_context(
            owner_offsite=True,
            allies_onsite=[],
            allies_offsite=[],
        )

        result = self.passive.execute(context)

        assert result["total_healing"] == 0
        assert len(result["healed"]) == 0

    def test_heal_only_lady_light_in_party(self):
        """Test healing when Lady Light is the only party member."""
        self.lady_light.hp = 500  # Damaged

        context = self.create_context(
            owner_offsite=True,
            allies_onsite=[],
            allies_offsite=[self.lady_light],
        )

        result = self.passive.execute(context)

        assert self.lady_light.hp == 600  # 500 + 100
        assert result["total_healing"] == 100

    def test_heal_multiple_allies(self):
        """Test healing with many allies."""
        allies = []
        for i in range(5):
            ally = Mock()
            ally.hp = 500
            ally.max_hp = 1000
            ally.character_id = f"ally_{i}"
            allies.append(ally)

        context = self.create_context(
            owner_offsite=True,
            allies_onsite=allies[:3],
            allies_offsite=[self.lady_light] + allies[3:],
        )

        result = self.passive.execute(context)

        # Each ally should be healed for 100
        for ally in allies:
            assert ally.hp == 600

        assert result["total_healing"] == 500  # 5 allies * 100 each

    def test_character_id_fallback(self):
        """Test that passive handles missing character_id gracefully."""
        # Create ally without character_id attribute
        ally_no_id = Mock(spec=['hp', 'max_hp'])  # Restrict to specific attributes
        ally_no_id.hp = 500
        ally_no_id.max_hp = 1000
        # Don't set character_id

        context = self.create_context(
            owner_offsite=True,
            allies_onsite=[ally_no_id],
            allies_offsite=[self.lady_light],
        )

        result = self.passive.execute(context)

        # Should still heal, just use "unknown" as character_id
        assert ally_no_id.hp == 600
        assert result["total_healing"] == 100
        assert ("unknown", 100) in result["healed"]

    def test_heal_calculation_example(self):
        """Test complete healing calculation example.

        Example: Lady Light (200 regain) is offsite
        - Heal amount: 200 * 0.50 = 100
        - Ally1: 500 HP → 600 HP (healed 100)
        - Ally2: 800 HP → 900 HP (healed 100)
        - Lady Light: 1000 HP → 1000 HP (no change, at max)
        - Total healing: 200
        """
        context = self.create_context(owner_offsite=True)

        # Verify passive can trigger
        assert self.passive.can_trigger(context) is True

        # Execute healing
        result = self.passive.execute(context)

        # Verify healing calculations
        assert result["base_heal_amount"] == 100
        assert self.ally1.hp == 600
        assert self.ally2.hp == 900
        assert self.lady_light.hp == 1000
        assert result["total_healing"] == 200


@pytest.mark.parametrize(
    "regain,heal_multiplier,expected_heal",
    [
        (100, 0.50, 50),
        (200, 0.50, 100),
        (300, 0.50, 150),
        (400, 0.50, 200),
        (500, 0.50, 250),
        (1000, 0.50, 500),
    ],
)
def test_heal_amount_calculation(regain, heal_multiplier, expected_heal):
    """Test heal amount calculation with various regain values.

    Args:
        regain: Lady Light's regain stat
        heal_multiplier: The heal multiplier (always 0.50)
        expected_heal: The expected heal amount per ally
    """
    passive = LadyLightRadiantAegis()

    lady_light = Mock()
    lady_light.regain = regain

    ally = Mock()
    ally.hp = 0
    ally.max_hp = 10000
    ally.character_id = "test_ally"

    context = TriggerContext(
        trigger=PassiveTrigger.TURN_START,
        owner_stats=lady_light,
        all_allies=[ally],
        onsite_allies=[],
        offsite_allies=[lady_light],
        enemies=[],
        extra={},
    )

    result = passive.execute(context)
    assert result["base_heal_amount"] == expected_heal
    assert ally.hp == expected_heal


@pytest.mark.parametrize(
    "current_hp,max_hp,heal_amount,expected_hp,expected_actual_heal",
    [
        (500, 1000, 100, 600, 100),  # Normal healing
        (950, 1000, 100, 1000, 50),  # Partial healing to cap
        (1000, 1000, 100, 1000, 0),  # No healing needed
        (0, 1000, 100, 100, 100),  # Healing from 0 HP
        (990, 1000, 100, 1000, 10),  # Small overheal prevention
    ],
)
def test_overheal_prevention(
    current_hp, max_hp, heal_amount, expected_hp, expected_actual_heal
):
    """Test that healing correctly prevents exceeding max HP.

    Args:
        current_hp: Starting HP
        max_hp: Maximum HP
        heal_amount: Base heal amount
        expected_hp: Expected HP after healing
        expected_actual_heal: Expected actual healing done
    """
    passive = LadyLightRadiantAegis()

    lady_light = Mock()
    lady_light.regain = heal_amount * 2  # Multiplier is 0.50

    ally = Mock()
    ally.hp = current_hp
    ally.max_hp = max_hp
    ally.character_id = "test_ally"

    context = TriggerContext(
        trigger=PassiveTrigger.TURN_START,
        owner_stats=lady_light,
        all_allies=[ally],
        onsite_allies=[],
        offsite_allies=[lady_light],
        enemies=[],
        extra={},
    )

    result = passive.execute(context)
    assert ally.hp == expected_hp
    if expected_actual_heal > 0:
        assert result["total_healing"] == expected_actual_heal
        assert ("test_ally", expected_actual_heal) in result["healed"]
    else:
        assert result["total_healing"] == 0
        assert len(result["healed"]) == 0
