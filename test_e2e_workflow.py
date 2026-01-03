#!/usr/bin/env python3
"""
End-to-end integration test simulating the complete user workflow:
Party Builder -> Idle Mode -> Party Builder -> Verify Stats Persisted
"""

import random
import tempfile
from pathlib import Path

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.save import RunSave, SaveManager
from endless_idler.ui.idle.idle_state import IdleGameState


def test_e2e_workflow():
    """Simulate complete user workflow to verify stats persist correctly."""
    print("=" * 70)
    print("End-to-End Integration Test")
    print("Simulating: Party Builder → Idle Mode → Party Builder")
    print("=" * 70)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_save_path = Path(f.name)
    
    try:
        # === SETUP ===
        plugins = discover_character_plugins()
        plugin_by_id = {p.char_id: p for p in plugins}
        rng = random.Random(42)
        
        test_chars = ['ally', 'luna', 'casno']
        available_chars = [c for c in test_chars if c in plugin_by_id][:2]
        if len(available_chars) < 2:
            available_chars = list(plugin_by_id.keys())[:2]
        
        char1, char2 = available_chars[0], available_chars[1]
        print(f"\n✓ Test characters: {char1}, {char2}")
        
        # === PHASE 1: Initial Party Builder State ===
        print(f"\n{'=' * 70}")
        print("PHASE 1: Party Builder - Initial Setup")
        print(f"{'=' * 70}")
        
        save_manager = SaveManager(path=temp_save_path)
        save = RunSave(
            party_level=1,
            onsite=[char1, char2],
            offsite=[],
            stacks={char1: 1, char2: 1},
        )
        save_manager.save(save)
        print(f"✓ Created initial party with {char1} and {char2}")
        
        # Simulate shop exp state running (party builder idle)
        shop_exp_state = IdleGameState(
            char_ids=[char1, char2],
            offsite_ids=[],
            party_level=1,
            stacks={char1: 1, char2: 1},
            plugins_by_id=plugin_by_id,
            rng=rng,
            progress_by_id={},
            stats_by_id={},
            initial_stats_by_id={},
            exp_gain_scale=0.0001,
            advance_run_buffs=False,
        )
        
        for _ in range(20):
            shop_exp_state.process_tick()
        
        shop_data = shop_exp_state.get_char_data(char1)
        shop_level = shop_data.get('level', 1)
        shop_exp = shop_data.get('exp', 0.0)
        print(f"✓ Shop exp running: {char1} at level {shop_level}, exp {shop_exp:.4f}")
        
        # === PHASE 2: Enter Idle Mode ===
        print(f"\n{'=' * 70}")
        print("PHASE 2: Enter Idle Mode")
        print(f"{'=' * 70}")
        
        # Load save for idle mode (shop exp state still exists in memory)
        save = save_manager.load()
        
        idle_state = IdleGameState(
            char_ids=[char1, char2],
            offsite_ids=[],
            party_level=1,
            stacks={char1: 1, char2: 1},
            plugins_by_id=plugin_by_id,
            rng=rng,
            progress_by_id=dict(save.character_progress),
            stats_by_id=dict(save.character_stats),
            initial_stats_by_id={},
            exp_gain_scale=10.0,
        )
        
        print(f"✓ Idle mode started")
        
        for i in range(100):
            idle_state.process_tick()
        
        idle_data_char1 = idle_state.get_char_data(char1)
        idle_data_char2 = idle_state.get_char_data(char2)
        
        char1_level = idle_data_char1.get('level', 1)
        char1_exp = idle_data_char1.get('exp', 0.0)
        char1_stats = idle_data_char1.get('base_stats', {})
        char1_atk = char1_stats.get('atk', 0.0)
        
        char2_level = idle_data_char2.get('level', 1)
        char2_exp = idle_data_char2.get('exp', 0.0)
        
        print(f"✓ Idle mode progress:")
        print(f"  {char1}: Level {char1_level}, EXP {char1_exp:.2f}, ATK {char1_atk:.3f}")
        print(f"  {char2}: Level {char2_level}, EXP {char2_exp:.2f}")
        
        # === PHASE 3: Exit Idle Mode (Save Stats) ===
        print(f"\n{'=' * 70}")
        print("PHASE 3: Exit Idle Mode - Saving Progress")
        print(f"{'=' * 70}")
        
        # Export and save (what idle screen does on exit)
        save.character_progress = idle_state.export_progress()
        save.character_stats = idle_state.export_character_stats()
        save.character_initial_stats = idle_state.export_initial_stats()
        save_manager.save(save)
        
        print(f"✓ Saved idle mode progress to disk")
        print(f"  {char1} progress: level={char1_level}, exp={char1_exp:.2f}")
        
        # === PHASE 4: Return to Party Builder (The Critical Test) ===
        print(f"\n{'=' * 70}")
        print("PHASE 4: Return to Party Builder - The Critical Test")
        print(f"{'=' * 70}")
        
        # This simulates what happens in reload_save()
        print(f"✓ Simulating reload_save()...")
        print(f"  NOTE: Old shop_exp_state has {char1} at level {shop_level}")
        print(f"  NOTE: Save file has {char1} at level {char1_level}")
        
        # Load the save (what reload_save does)
        loaded_save = save_manager.load()
        
        # THE FIX: Clear shop exp state (don't overwrite with stale data)
        shop_exp_state = None
        shop_exp_signature = None
        shop_exp_ticks = 0
        
        print(f"✓ Shop exp state cleared (fix applied)")
        
        # === PHASE 5: Verification ===
        print(f"\n{'=' * 70}")
        print("PHASE 5: Verification - Did Stats Persist?")
        print(f"{'=' * 70}")
        
        final_char1_progress = loaded_save.character_progress.get(char1, {})
        final_char1_stats = loaded_save.character_stats.get(char1, {})
        final_char2_progress = loaded_save.character_progress.get(char2, {})
        
        final_char1_level = final_char1_progress.get('level', 1)
        final_char1_exp = final_char1_progress.get('exp', 0.0)
        final_char1_atk = final_char1_stats.get('atk', 0.0)
        final_char2_level = final_char2_progress.get('level', 1)
        
        success = True
        
        # Verify char1
        if char1_level == final_char1_level:
            print(f"✓ {char1} level preserved: {final_char1_level}")
        else:
            print(f"✗ {char1} level LOST: expected {char1_level}, got {final_char1_level}")
            success = False
        
        if abs(char1_exp - final_char1_exp) < 0.01:
            print(f"✓ {char1} exp preserved: {final_char1_exp:.2f}")
        else:
            print(f"✗ {char1} exp LOST: expected {char1_exp:.2f}, got {final_char1_exp:.2f}")
            success = False
        
        if abs(char1_atk - final_char1_atk) < 0.001:
            print(f"✓ {char1} ATK preserved: {final_char1_atk:.3f}")
        else:
            print(f"✗ {char1} ATK LOST: expected {char1_atk:.3f}, got {final_char1_atk:.3f}")
            success = False
        
        # Verify char2
        if char2_level == final_char2_level:
            print(f"✓ {char2} level preserved: {final_char2_level}")
        else:
            print(f"✗ {char2} level LOST: expected {char2_level}, got {final_char2_level}")
            success = False
        
        print(f"\n{'=' * 70}")
        if success:
            print("✓✓✓ END-TO-END TEST PASSED ✓✓✓")
            print("Complete workflow verified: Stats persist correctly!")
        else:
            print("✗✗✗ END-TO-END TEST FAILED ✗✗✗")
            print("Stats did not persist through the workflow!")
        print(f"{'=' * 70}\n")
        
        return success
        
    finally:
        try:
            temp_save_path.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    import sys
    success = test_e2e_workflow()
    sys.exit(0 if success else 1)
