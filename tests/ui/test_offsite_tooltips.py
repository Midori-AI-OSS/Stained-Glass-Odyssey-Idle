"""Test that offsite character cards generate tooltips correctly."""

from __future__ import annotations

import random

from PySide6.QtWidgets import QApplication

from endless_idler.combat.stats import Stats
from endless_idler.ui.battle.sim import Combatant
from endless_idler.ui.battle.widgets import CombatantCard


def test_offsite_card_generates_tooltip():
    """Verify that offsite character cards have tooltips."""
    app = QApplication.instance() or QApplication([])
    
    # Create a simple combatant with default stats
    stats = Stats()
    stats.hp = 100
    combatant = Combatant(char_id="test_char", name="Test Character", stats=stats, max_hp=100)
    
    # Create an offsite card (variant="offsite", compact=False)
    card = CombatantCard(
        combatant=combatant,
        plugin=None,
        rng=random.Random(42),
        team_side="left",
        stack_count=1,
        variant="offsite",
        compact=False,  # Explicitly not compact
    )
    
    # Verify tooltip is generated
    assert card._tooltip_html, "Offsite card should have a tooltip"
    assert "Test Character" in card._tooltip_html, "Tooltip should contain character name"
    assert "Level" in card._tooltip_html or "level" in card._tooltip_html, "Tooltip should contain level info"


def test_offsite_card_tooltip_vs_compact():
    """Verify that offsite cards have tooltips but compact cards don't."""
    app = QApplication.instance() or QApplication([])
    
    # Create a simple combatant with default stats
    stats = Stats()
    stats.hp = 100
    combatant = Combatant(char_id="test_char", name="Test Character", stats=stats, max_hp=100)
    
    # Create an offsite card
    offsite_card = CombatantCard(
        combatant=combatant,
        plugin=None,
        rng=random.Random(42),
        team_side="left",
        stack_count=1,
        variant="offsite",
        compact=False,
    )
    
    # Create a compact card
    compact_card = CombatantCard(
        combatant=combatant,
        plugin=None,
        rng=random.Random(42),
        team_side="left",
        stack_count=1,
        variant="onsite",
        compact=True,
    )
    
    # Verify offsite has tooltip, compact doesn't
    assert offsite_card._tooltip_html, "Offsite card should have a tooltip"
    assert not compact_card._tooltip_html, "Compact card should NOT have a tooltip"


def test_onsite_card_generates_tooltip():
    """Verify that onsite character cards have tooltips too (baseline check)."""
    app = QApplication.instance() or QApplication([])
    
    # Create a simple combatant with default stats
    stats = Stats()
    stats.hp = 100
    combatant = Combatant(char_id="test_char", name="Test Character", stats=stats, max_hp=100)
    
    # Create an onsite card (variant="onsite", compact=False)
    card = CombatantCard(
        combatant=combatant,
        plugin=None,
        rng=random.Random(42),
        team_side="left",
        stack_count=1,
        variant="onsite",
        compact=False,
    )
    
    # Verify tooltip is generated
    assert card._tooltip_html, "Onsite card should have a tooltip"
    assert "Test Character" in card._tooltip_html, "Tooltip should contain character name"
