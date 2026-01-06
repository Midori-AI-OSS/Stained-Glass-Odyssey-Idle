"""Integration tests for the passive system with combat.

Tests that passives are properly loaded and triggered during combat.
"""

import random
import importlib.util
import sys
from pathlib import Path

import pytest

from endless_idler.characters.plugins import CharacterPlugin
from endless_idler.combat.stats import Stats
from endless_idler.passives.registry import load_passive

# Directly import sim.py to avoid PySide6 dependency from screen.py
sim_path = Path(__file__).parent.parent / "endless_idler" / "ui" / "battle" / "sim.py"
spec = importlib.util.spec_from_file_location("sim", sim_path)
sim = importlib.util.module_from_spec(spec)
sys.modules['sim'] = sim
spec.loader.exec_module(sim)


def test_load_passives_for_character():
    """Test that passives are loaded and attached to stats."""
    plugin = CharacterPlugin(
        char_id="lady_light",
        display_name="Lady Light",
        passives=["lady_light_radiant_aegis"],
    )
    
    stats = Stats()
    sim.load_passives_for_character(stats, plugin, "lady_light")
    
    assert stats.character_id == "lady_light"
    assert len(stats._passive_instances) == 1
    assert stats._passive_instances[0].id == "lady_light_radiant_aegis"


def test_load_passives_with_invalid_id():
    """Test that invalid passive IDs are gracefully skipped."""
    plugin = CharacterPlugin(
        char_id="test_char",
        display_name="Test",
        passives=["invalid_passive_id", "lady_light_radiant_aegis"],
    )
    
    stats = Stats()
    sim.load_passives_for_character(stats, plugin, "test_char")
    
    # Should only load the valid passive
    assert len(stats._passive_instances) == 1
    assert stats._passive_instances[0].id == "lady_light_radiant_aegis"


def test_build_party_loads_passives():
    """Test that build_party loads passives for characters."""
    rng = random.Random(42)
    plugins_by_id = {
        "lady_light": CharacterPlugin(
            char_id="lady_light",
            display_name="Lady Light",
            passives=["lady_light_radiant_aegis"],
        ),
        "lady_darkness": CharacterPlugin(
            char_id="lady_darkness",
            display_name="Lady Darkness",
            passives=["lady_darkness_eclipsing_veil"],
        ),
    }
    
    party = sim.build_party(
        onsite=["lady_light", "lady_darkness"],
        party_level=1,
        stacks={},
        plugins_by_id=plugins_by_id,
        rng=rng,
    )
    
    assert len(party) == 2
    
    # Check Lady Light has her passive
    lady_light = party[0]
    assert lady_light.char_id == "lady_light"
    assert lady_light.stats.character_id == "lady_light"
    assert len(lady_light.stats._passive_instances) == 1
    assert lady_light.stats._passive_instances[0].id == "lady_light_radiant_aegis"
    
    # Check Lady Darkness has her passive
    lady_darkness = party[1]
    assert lady_darkness.char_id == "lady_darkness"
    assert lady_darkness.stats.character_id == "lady_darkness"
    assert len(lady_darkness.stats._passive_instances) == 1
    assert lady_darkness.stats._passive_instances[0].id == "lady_darkness_eclipsing_veil"


def test_build_reserves_loads_passives():
    """Test that build_reserves loads passives for characters."""
    rng = random.Random(42)
    plugins_by_id = {
        "lady_light": CharacterPlugin(
            char_id="lady_light",
            display_name="Lady Light",
            passives=["lady_light_radiant_aegis"],
        ),
    }
    
    reserves = sim.build_reserves(
        char_ids=["lady_light"],
        party_level=1,
        stacks={},
        plugins_by_id=plugins_by_id,
        rng=rng,
    )
    
    assert len(reserves) == 1
    assert reserves[0].stats.character_id == "lady_light"
    assert len(reserves[0].stats._passive_instances) == 1


def test_calculate_damage_with_passives():
    """Test that damage calculation works with passive context."""
    rng = random.Random(42)
    
    attacker = Stats()
    attacker.character_id = "lady_darkness"
    attacker._base_atk = 200
    
    # Load Lady Darkness passive
    passive = load_passive("lady_darkness_eclipsing_veil")
    if passive:
        attacker._passive_instances = [passive]
    
    target = Stats()
    target._base_defense = 200
    target._base_max_hp = 1000
    target.hp = 1000
    
    all_allies = [attacker]
    onsite_allies = [attacker]
    offsite_allies = []
    enemies = [target]
    
    # Calculate damage with passive context
    damage, crit, dodged = sim.calculate_damage(
        attacker,
        target,
        rng,
        damage_multiplier=1.0,
        all_allies=all_allies,
        onsite_allies=onsite_allies,
        offsite_allies=offsite_allies,
        enemies=enemies,
    )
    
    # Should deal damage (exact amount depends on passive and calculations)
    assert damage > 0
    assert not dodged


def test_calculate_damage_without_passive_context():
    """Test that damage calculation still works without passive context."""
    rng = random.Random(42)
    
    attacker = Stats()
    attacker._base_atk = 200
    
    target = Stats()
    target._base_defense = 200
    
    # Calculate damage without passive context (backwards compatibility)
    damage, crit, dodged = sim.calculate_damage(
        attacker,
        target,
        rng,
        damage_multiplier=1.0,
    )
    
    assert damage > 0
    assert not dodged


def test_trinity_synergy_integration():
    """Test that Trinity Synergy passive loads correctly for all three characters."""
    rng = random.Random(42)
    plugins_by_id = {
        "lady_light": CharacterPlugin(
            char_id="lady_light",
            display_name="Lady Light",
            passives=["lady_light_radiant_aegis", "trinity_synergy"],
        ),
        "lady_darkness": CharacterPlugin(
            char_id="lady_darkness",
            display_name="Lady Darkness",
            passives=["lady_darkness_eclipsing_veil", "trinity_synergy"],
        ),
        "persona_light_and_dark": CharacterPlugin(
            char_id="persona_light_and_dark",
            display_name="Persona: Light and Dark",
            passives=["trinity_synergy"],
        ),
    }
    
    party = sim.build_party(
        onsite=["lady_light", "lady_darkness", "persona_light_and_dark"],
        party_level=1,
        stacks={},
        plugins_by_id=plugins_by_id,
        rng=rng,
    )
    
    # Check that all three have Trinity Synergy
    for combatant in party:
        has_trinity = any(
            p.id == "trinity_synergy" for p in combatant.stats._passive_instances
        )
        assert has_trinity, f"{combatant.char_id} should have Trinity Synergy"


def test_multiple_passives_per_character():
    """Test that a character can have multiple passives loaded."""
    plugin = CharacterPlugin(
        char_id="lady_light",
        display_name="Lady Light",
        passives=["lady_light_radiant_aegis", "trinity_synergy"],
    )
    
    stats = Stats()
    sim.load_passives_for_character(stats, plugin, "lady_light")
    
    assert len(stats._passive_instances) == 2
    passive_ids = [p.id for p in stats._passive_instances]
    assert "lady_light_radiant_aegis" in passive_ids
    assert "trinity_synergy" in passive_ids


def test_character_without_passives():
    """Test that characters without passives work correctly."""
    plugin = CharacterPlugin(
        char_id="bubbles",
        display_name="Bubbles",
        passives=[],
    )
    
    stats = Stats()
    sim.load_passives_for_character(stats, plugin, "bubbles")
    
    assert stats.character_id == "bubbles"
    assert len(stats._passive_instances) == 0


def test_target_selection_passives_integration():
    """Test that TARGET_SELECTION passives can redirect attacks.
    
    This test verifies that the apply_target_selection_passives function
    works correctly when integrated with the combat system, particularly
    for Trinity Synergy's attack redirection to Persona.
    """
    from endless_idler.passives.execution import apply_target_selection_passives
    
    # Create Trinity members
    lady_light = Stats()
    lady_light.character_id = "lady_light"
    lady_light.hp = 100
    lady_light.max_hp = 100
    lady_light._passive_instances = [load_passive("trinity_synergy")]
    
    lady_darkness = Stats()
    lady_darkness.character_id = "lady_darkness"
    lady_darkness.hp = 100
    lady_darkness.max_hp = 100
    lady_darkness._passive_instances = [load_passive("trinity_synergy")]
    
    persona = Stats()
    persona.character_id = "persona_light_and_dark"
    persona.hp = 100
    persona.max_hp = 100
    persona._passive_instances = [load_passive("trinity_synergy")]
    
    # Create enemies
    enemy1 = Stats()
    enemy1.character_id = "enemy1"
    enemy1.hp = 50
    enemy1.max_hp = 50
    
    enemy2 = Stats()
    enemy2.character_id = "enemy2"
    enemy2.hp = 50
    enemy2.max_hp = 50
    
    # Setup attack: enemy targets Lady Darkness (Trinity redirects Darkness -> Persona)
    attacker = enemy1
    original_target = lady_darkness
    all_allies = [lady_light, lady_darkness, persona]
    enemies = [enemy1, enemy2]
    
    # Apply target selection passives
    final_target = apply_target_selection_passives(
        attacker=attacker,
        original_target=original_target,
        available_targets=all_allies,
        all_allies=all_allies,
        onsite_allies=all_allies,
        offsite_allies=[],
        enemies=enemies,
    )
    
    # Trinity Synergy should redirect attacks from Lady Darkness to Persona
    assert final_target is persona, "Attack on Lady Darkness should be redirected to Persona by Trinity Synergy"
    
    # Test attack on Lady Light - should NOT redirect (Trinity only redirects Lady Darkness)
    final_target_light = apply_target_selection_passives(
        attacker=attacker,
        original_target=lady_light,
        available_targets=all_allies,
        all_allies=all_allies,
        onsite_allies=all_allies,
        offsite_allies=[],
        enemies=enemies,
    )
    
    assert final_target_light is lady_light, "Attack on Lady Light should not redirect"
    
    # Test with Persona dead - should not redirect
    persona.hp = 0
    final_target_dead = apply_target_selection_passives(
        attacker=attacker,
        original_target=lady_darkness,
        available_targets=all_allies,
        all_allies=all_allies,
        onsite_allies=all_allies,
        offsite_allies=[],
        enemies=enemies,
    )
    
    assert final_target_dead is lady_darkness, "Attack should not redirect when Persona is dead"
    
    # Test without Trinity (missing a member)
    incomplete_allies = [lady_light, lady_darkness]
    final_target_incomplete = apply_target_selection_passives(
        attacker=attacker,
        original_target=lady_darkness,
        available_targets=incomplete_allies,
        all_allies=incomplete_allies,
        onsite_allies=incomplete_allies,
        offsite_allies=[],
        enemies=enemies,
    )
    
    assert final_target_incomplete is lady_darkness, "Attack should not redirect when Trinity is incomplete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
