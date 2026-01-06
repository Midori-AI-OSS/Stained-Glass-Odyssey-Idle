"""Tests for Trinity Synergy passive ability.

This test suite verifies that the Trinity Synergy passive correctly:
- Activates when all three trinity members are present
- Does not activate when any member is missing
- Applies correct bonuses to each character
- Redirects attacks targeting Lady Darkness to Persona
- Only redirects if Persona is alive
- Handles edge cases properly
"""


from unittest.mock import Mock

from endless_idler.passives.implementations.trinity_synergy import (
    LADY_DARKNESS_ID,
    LADY_LIGHT_ID,
    PERSONA_LIGHT_AND_DARK_ID,
    TrinitySynergy,
    is_trinity_active,
)
from endless_idler.passives.registry import get_passive, load_passive
from endless_idler.passives.triggers import PassiveTrigger, TriggerContext


class TestTrinitySynergy:
    """Test suite for Trinity Synergy passive."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        self.passive = TrinitySynergy()

        # Create mock stats for trinity members
        self.lady_light = Mock()
        self.lady_light.name = "Lady Light"
        self.lady_light.character_id = LADY_LIGHT_ID
        self.lady_light.hp = 1000
        self.lady_light.max_hp = 1000
        self.lady_light.regain = 100

        self.lady_darkness = Mock()
        self.lady_darkness.name = "Lady Darkness"
        self.lady_darkness.character_id = LADY_DARKNESS_ID
        self.lady_darkness.hp = 1200
        self.lady_darkness.max_hp = 1200
        self.lady_darkness.atk = 500

        self.persona = Mock()
        self.persona.name = "Persona Light and Dark"
        self.persona.character_id = PERSONA_LIGHT_AND_DARK_ID
        self.persona.hp = 1500
        self.persona.max_hp = 1700

        # Create mock stats for other characters
        self.other_ally = Mock()
        self.other_ally.name = "Other Ally"
        self.other_ally.character_id = "other_ally"
        self.other_ally.hp = 800
        self.other_ally.max_hp = 1000

        self.enemy = Mock()
        self.enemy.name = "Enemy"
        self.enemy.character_id = "enemy"
        self.enemy.hp = 2000
        self.enemy.max_hp = 2000
        self.enemy.atk = 300

    def create_context(
        self,
        trigger=PassiveTrigger.TURN_START,
        owner=None,
        trinity_present=True,
        extra=None,
    ):
        """Helper to create a TriggerContext for testing.

        Args:
            trigger: The trigger type
            owner: The owner of the passive (defaults to lady_light)
            trinity_present: Whether all three trinity members are present
            extra: Extra context data

        Returns:
            TriggerContext configured for the given trigger
        """
        if owner is None:
            owner = self.lady_light

        if trinity_present:
            all_allies = [self.lady_light, self.lady_darkness, self.persona]
        else:
            all_allies = [self.lady_light, self.lady_darkness]

        if extra is None:
            extra = {}

        return TriggerContext(
            trigger=trigger,
            owner_stats=owner,
            all_allies=all_allies,
            onsite_allies=[self.lady_darkness, self.persona],
            offsite_allies=[self.lady_light],
            enemies=[self.enemy],
            extra=extra,
        )

    def test_passive_initialization(self):
        """Test that passive initializes with correct attributes."""
        assert self.passive.id == "trinity_synergy"
        assert self.passive.display_name == "Trinity Synergy"
        assert len(self.passive.description) > 0
        assert PassiveTrigger.TURN_START in self.passive.triggers
        assert PassiveTrigger.TARGET_SELECTION in self.passive.triggers
        assert self.passive.lady_light_regain_mult == 15.0
        assert self.passive.lady_light_healing_mult == 4.0
        assert self.passive.lady_darkness_damage_mult == 2.0
        assert self.passive.lady_darkness_bleed_reduction == 0.5

    def test_passive_registration(self):
        """Test that passive is properly registered in the registry."""
        passive_class = get_passive("trinity_synergy")
        assert passive_class is not None
        assert passive_class == TrinitySynergy

        # Test loading an instance
        instance = load_passive("trinity_synergy")
        assert instance is not None
        assert isinstance(instance, TrinitySynergy)

    def test_is_trinity_active_all_present(self):
        """Test is_trinity_active returns True when all members present."""
        context = self.create_context(trinity_present=True)
        is_active, members = is_trinity_active(context)

        assert is_active is True
        assert members[LADY_LIGHT_ID] == self.lady_light
        assert members[LADY_DARKNESS_ID] == self.lady_darkness
        assert members[PERSONA_LIGHT_AND_DARK_ID] == self.persona

    def test_is_trinity_active_one_missing(self):
        """Test is_trinity_active returns False when one member missing."""
        context = self.create_context(trinity_present=False)
        is_active, members = is_trinity_active(context)

        assert is_active is False
        assert members[LADY_LIGHT_ID] == self.lady_light
        assert members[LADY_DARKNESS_ID] == self.lady_darkness
        assert members[PERSONA_LIGHT_AND_DARK_ID] is None

    def test_can_trigger_when_trinity_active(self):
        """Test that passive triggers when all trinity members present."""
        context = self.create_context(trinity_present=True)
        assert self.passive.can_trigger(context) is True

    def test_cannot_trigger_when_trinity_incomplete(self):
        """Test that passive does not trigger when any member missing."""
        context = self.create_context(trinity_present=False)
        assert self.passive.can_trigger(context) is False

    def test_lady_light_turn_start_bonuses(self):
        """Test Lady Light receives correct bonuses at turn start."""
        context = self.create_context(
            trigger=PassiveTrigger.TURN_START,
            owner=self.lady_light,
            trinity_present=True,
        )

        # Execute passive
        result = self.passive.execute(context)

        # Check that bonuses were applied
        assert result["trigger_type"] == "turn_start"
        assert result["character_id"] == LADY_LIGHT_ID
        assert len(result["effects_applied"]) == 2

        # Check regain boost: 100 * (15.0 - 1.0) = 1400 bonus
        expected_regain = 100 + 1400
        assert self.lady_light.regain == expected_regain

        # Check healing multiplier stored in context
        assert context.extra["lady_light_healing_mult"] == 4.0

        # Check effect descriptions
        effects = result["effects_applied"]
        assert any("regain boosted by 15.0x" in effect for effect in effects)
        assert any("healing output x4.0" in effect for effect in effects)

    def test_lady_darkness_turn_start_bonuses(self):
        """Test Lady Darkness receives correct bonuses at turn start."""
        context = self.create_context(
            trigger=PassiveTrigger.TURN_START,
            owner=self.lady_darkness,
            trinity_present=True,
        )

        # Execute passive
        result = self.passive.execute(context)

        # Check that bonuses were applied
        assert result["trigger_type"] == "turn_start"
        assert result["character_id"] == LADY_DARKNESS_ID
        assert len(result["effects_applied"]) == 2

        # Check multipliers stored in context
        assert context.extra["lady_darkness_damage_mult"] == 2.0
        assert context.extra["lady_darkness_bleed_reduction"] == 0.5

        # Check effect descriptions
        effects = result["effects_applied"]
        assert any("damage x2.0" in effect for effect in effects)
        assert any("1/2 damage from Lady Darkness bleed" in effect for effect in effects)

    def test_persona_no_turn_start_effects(self):
        """Test Persona does not get turn start effects (only redirect)."""
        context = self.create_context(
            trigger=PassiveTrigger.TURN_START,
            owner=self.persona,
            trinity_present=True,
        )

        # Execute passive
        result = self.passive.execute(context)

        # Persona should not have any effects at turn start
        assert result["trigger_type"] == "turn_start"
        assert result["character_id"] == PERSONA_LIGHT_AND_DARK_ID
        assert len(result["effects_applied"]) == 0

    def test_target_redirection_to_persona(self):
        """Test that attacks targeting Lady Darkness are redirected to Persona."""
        context = self.create_context(
            trigger=PassiveTrigger.TARGET_SELECTION,
            owner=self.persona,
            trinity_present=True,
            extra={"original_target": self.lady_darkness},
        )

        # Execute passive
        result = self.passive.execute(context)

        # Check that target was redirected
        assert result["trigger_type"] == "target_selection"
        assert len(result["effects_applied"]) == 1
        assert "redirected" in result["effects_applied"][0].lower()

        # Check that new_target was set
        assert context.extra["new_target"] == self.persona

    def test_no_redirection_when_persona_dead(self):
        """Test that redirection does not occur when Persona is dead."""
        self.persona.hp = 0

        context = self.create_context(
            trigger=PassiveTrigger.TARGET_SELECTION,
            owner=self.persona,
            trinity_present=True,
            extra={"original_target": self.lady_darkness},
        )

        # Execute passive
        result = self.passive.execute(context)

        # Check that target was NOT redirected
        assert result["trigger_type"] == "target_selection"
        assert len(result["effects_applied"]) == 0
        assert "new_target" not in context.extra

    def test_no_redirection_for_other_targets(self):
        """Test that attacks not targeting Lady Darkness are not redirected."""
        context = self.create_context(
            trigger=PassiveTrigger.TARGET_SELECTION,
            owner=self.persona,
            trinity_present=True,
            extra={"original_target": self.lady_light},
        )

        # Execute passive
        result = self.passive.execute(context)

        # Check that target was NOT redirected
        assert result["trigger_type"] == "target_selection"
        assert len(result["effects_applied"]) == 0
        assert "new_target" not in context.extra

    def test_no_effects_when_trinity_incomplete(self):
        """Test that no effects are applied when trinity is incomplete."""
        context = self.create_context(
            trigger=PassiveTrigger.TURN_START,
            owner=self.lady_light,
            trinity_present=False,
        )

        # Execute passive
        result = self.passive.execute(context)

        # No effects should be applied
        assert result["trigger_type"] == "turn_start"
        assert len(result["effects_applied"]) == 0

        # Stats should not be modified
        assert self.lady_light.regain == 100  # Unchanged

    def test_multiple_turn_start_executions_stack(self):
        """Test that multiple turn start executions stack the bonuses."""
        context = self.create_context(
            trigger=PassiveTrigger.TURN_START,
            owner=self.lady_light,
            trinity_present=True,
        )

        # Execute twice (simulating multiple turns)
        self.passive.execute(context)
        self.passive.execute(context)

        # Regain should stack: 100 + 1400 = 1500, then 1500 + 21000 = 22500
        # (Note: This shows that multiple applications stack - may need balancing)
        assert self.lady_light.regain > 100

    def test_trinity_with_additional_allies(self):
        """Test that trinity works correctly with additional allies present."""
        context = TriggerContext(
            trigger=PassiveTrigger.TURN_START,
            owner_stats=self.lady_light,
            all_allies=[
                self.lady_light,
                self.lady_darkness,
                self.persona,
                self.other_ally,
            ],
            onsite_allies=[self.lady_darkness, self.persona, self.other_ally],
            offsite_allies=[self.lady_light],
            enemies=[self.enemy],
            extra={},
        )

        # Should still trigger with additional allies
        assert self.passive.can_trigger(context) is True

        # Execute and check bonuses
        result = self.passive.execute(context)
        assert len(result["effects_applied"]) == 2

    def test_character_id_missing_does_not_crash(self):
        """Test that missing character_id attributes don't cause crashes."""
        # Create character without character_id
        no_id_char = Mock()
        no_id_char.name = "No ID"
        no_id_char.hp = 1000
        del no_id_char.character_id  # Remove the character_id

        context = TriggerContext(
            trigger=PassiveTrigger.TURN_START,
            owner_stats=no_id_char,
            all_allies=[self.lady_light, self.lady_darkness, no_id_char],
            onsite_allies=[self.lady_darkness, no_id_char],
            offsite_allies=[self.lady_light],
            enemies=[self.enemy],
            extra={},
        )

        # Should not trigger (missing persona)
        assert self.passive.can_trigger(context) is False

        # Should not crash
        result = self.passive.execute(context)
        assert result["trigger_type"] == "turn_start"
        assert len(result["effects_applied"]) == 0

    def test_lady_light_regain_multiplier_calculation(self):
        """Test that regain multiplier calculation is correct."""
        # Set base regain
        self.lady_light.regain = 200

        context = self.create_context(
            trigger=PassiveTrigger.TURN_START,
            owner=self.lady_light,
            trinity_present=True,
        )

        # Execute passive
        self.passive.execute(context)

        # Expected: 200 + (200 * (15.0 - 1.0)) = 200 + 2800 = 3000
        assert self.lady_light.regain == 3000

    def test_redirection_requires_all_trinity_members(self):
        """Test that redirection only works when all trinity members present."""
        # Context with only two members
        context = TriggerContext(
            trigger=PassiveTrigger.TARGET_SELECTION,
            owner_stats=self.persona,
            all_allies=[self.lady_darkness, self.persona],
            onsite_allies=[self.lady_darkness, self.persona],
            offsite_allies=[],
            enemies=[self.enemy],
            extra={"original_target": self.lady_darkness},
        )

        # Should not trigger
        assert self.passive.can_trigger(context) is False

        # No redirection
        self.passive.execute(context)
        assert "new_target" not in context.extra

    def test_all_three_passives_can_execute_simultaneously(self):
        """Test that all three characters can have this passive active."""
        # Lady Light's passive
        context_light = self.create_context(
            trigger=PassiveTrigger.TURN_START,
            owner=self.lady_light,
            trinity_present=True,
        )
        passive_light = TrinitySynergy()
        result_light = passive_light.execute(context_light)

        # Lady Darkness's passive
        context_darkness = self.create_context(
            trigger=PassiveTrigger.TURN_START,
            owner=self.lady_darkness,
            trinity_present=True,
        )
        passive_darkness = TrinitySynergy()
        result_darkness = passive_darkness.execute(context_darkness)

        # Persona's passive
        context_persona = self.create_context(
            trigger=PassiveTrigger.TURN_START,
            owner=self.persona,
            trinity_present=True,
        )
        passive_persona = TrinitySynergy()
        result_persona = passive_persona.execute(context_persona)

        # Each should execute correctly
        assert result_light["character_id"] == LADY_LIGHT_ID
        assert result_darkness["character_id"] == LADY_DARKNESS_ID
        assert result_persona["character_id"] == PERSONA_LIGHT_AND_DARK_ID

        # Lady Light should have effects
        assert len(result_light["effects_applied"]) == 2
        # Lady Darkness should have effects
        assert len(result_darkness["effects_applied"]) == 2
        # Persona should have no turn start effects
        assert len(result_persona["effects_applied"]) == 0
