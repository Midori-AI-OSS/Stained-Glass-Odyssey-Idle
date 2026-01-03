#!/usr/bin/env python3
"""Test script to verify character stats persist correctly across idle mode transitions."""

import json
import random
import tempfile
import time
from pathlib import Path

from endless_idler.characters.plugins import discover_character_plugins
from endless_idler.save import RunSave, SaveManager
from endless_idler.ui.idle.idle_state import IdleGameState


def test_idle_stat_persistence():
    """Test that character stats are properly saved and loaded when exiting idle mode."""
    print("=" * 70)
    print("Testing Idle Mode Character Stat Persistence")
    print("=" * 70)
    
    # Create a temporary save file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_save_path = Path(f.name)
    
    try:
        # Setup
        plugins = discover_character_plugins()
        plugin_by_id = {p.char_id: p for p in plugins}
        
        # Pick a test character (preferably one that exists)
        test_chars = ['ally', 'luna', 'casno']
        available_chars = [c for c in test_chars if c in plugin_by_id]
        if not available_chars:
            available_chars = [list(plugin_by_id.keys())[0]]
        
        char_id = available_chars[0]
        print(f"\n✓ Using test character: {char_id}")
        
        # Create initial save
        save_manager = SaveManager(path=temp_save_path)
        initial_save = RunSave(
            party_level=1,
            onsite=[char_id],
            offsite=[],
            stacks={char_id: 1},
        )
        save_manager.save(initial_save)
        print(f"✓ Created initial save at: {temp_save_path}")
        
        # Load save and check initial state
        loaded_save = save_manager.load()
        initial_progress = loaded_save.character_progress.get(char_id, {})
        initial_stats = loaded_save.character_stats.get(char_id, {})
        
        print(f"\nInitial state:")
        print(f"  Level: {initial_progress.get('level', 1)}")
        print(f"  EXP: {initial_progress.get('exp', 0.0):.2f}")
        print(f"  Stats keys: {list(initial_stats.keys())[:5] if initial_stats else []}")
        
        # Simulate idle mode
        print(f"\n{'=' * 70}")
        print("Simulating Idle Mode...")
        print(f"{'=' * 70}")
        
        rng = random.Random(42)
        idle_state = IdleGameState(
            char_ids=[char_id],
            offsite_ids=[],
            party_level=1,
            stacks={char_id: 1},
            plugins_by_id=plugin_by_id,
            rng=rng,
            progress_by_id=dict(loaded_save.character_progress),
            stats_by_id=dict(loaded_save.character_stats),
            initial_stats_by_id={},
            exp_gain_scale=10.0,  # Speed up for testing
        )
        
        # Process multiple ticks to level up
        ticks = 100
        print(f"\n✓ Processing {ticks} idle ticks...")
        for i in range(ticks):
            idle_state.process_tick()
            if i % 20 == 0:
                char_data = idle_state.get_char_data(char_id)
                print(f"  Tick {i}: Level {char_data.get('level', 1)}, "
                      f"EXP {char_data.get('exp', 0.0):.2f}/{char_data.get('next_exp', 30.0):.2f}")
        
        # Export state (simulating what happens on exit)
        final_progress = idle_state.export_progress()
        final_stats = idle_state.export_character_stats()
        
        print(f"\nAfter idle mode:")
        print(f"  Level: {final_progress[char_id].get('level', 1)}")
        print(f"  EXP: {final_progress[char_id].get('exp', 0.0):.2f}")
        print(f"  Stats keys: {list(final_stats[char_id].keys())[:5] if char_id in final_stats else []}")
        
        # Save the updated state (simulating idle screen _finish method)
        loaded_save.character_progress = final_progress
        loaded_save.character_stats = final_stats
        save_manager.save(loaded_save)
        print(f"\n✓ Saved idle mode progress to disk")
        
        # Simulate returning to party builder by reloading
        print(f"\n{'=' * 70}")
        print("Simulating Return to Party Builder...")
        print(f"{'=' * 70}")
        
        # Clear the save from memory to force a fresh load
        del loaded_save
        time.sleep(0.1)  # Ensure file system sync
        
        # Reload save (simulating what party_builder.reload_save() does)
        reloaded_save = save_manager.load()
        reloaded_progress = reloaded_save.character_progress.get(char_id, {})
        reloaded_stats = reloaded_save.character_stats.get(char_id, {})
        
        print(f"\n✓ Reloaded save from disk")
        print(f"\nReloaded state:")
        print(f"  Level: {reloaded_progress.get('level', 1)}")
        print(f"  EXP: {reloaded_progress.get('exp', 0.0):.2f}")
        print(f"  Stats keys: {list(reloaded_stats.keys())[:5] if reloaded_stats else []}")
        
        # Verify stats match
        print(f"\n{'=' * 70}")
        print("Verification Results")
        print(f"{'=' * 70}")
        
        success = True
        
        # Check level
        expected_level = final_progress[char_id].get('level', 1)
        actual_level = reloaded_progress.get('level', 1)
        if expected_level == actual_level:
            print(f"✓ Level preserved: {actual_level}")
        else:
            print(f"✗ Level MISMATCH: expected {expected_level}, got {actual_level}")
            success = False
        
        # Check EXP
        expected_exp = final_progress[char_id].get('exp', 0.0)
        actual_exp = reloaded_progress.get('exp', 0.0)
        if abs(expected_exp - actual_exp) < 0.01:
            print(f"✓ EXP preserved: {actual_exp:.2f}")
        else:
            print(f"✗ EXP MISMATCH: expected {expected_exp:.2f}, got {actual_exp:.2f}")
            success = False
        
        # Check stats
        if char_id in final_stats and char_id in reloaded_save.character_stats:
            final_stat_keys = set(final_stats[char_id].keys())
            reloaded_stat_keys = set(reloaded_save.character_stats[char_id].keys())
            if final_stat_keys == reloaded_stat_keys:
                print(f"✓ Stats structure preserved ({len(final_stat_keys)} keys)")
                
                # Check a few key stats
                for stat_key in ['atk', 'defense', 'max_hp']:
                    if stat_key in final_stats[char_id]:
                        expected = final_stats[char_id][stat_key]
                        actual = reloaded_save.character_stats[char_id].get(stat_key, 0.0)
                        if abs(expected - actual) < 0.001:
                            print(f"  ✓ {stat_key}: {actual:.3f}")
                        else:
                            print(f"  ✗ {stat_key} MISMATCH: expected {expected:.3f}, got {actual:.3f}")
                            success = False
            else:
                print(f"✗ Stats structure MISMATCH")
                success = False
        elif char_id in final_stats:
            print(f"✗ Stats LOST during reload")
            success = False
        else:
            print(f"  (No custom stats to verify)")
        
        print(f"\n{'=' * 70}")
        if success:
            print("✓✓✓ ALL TESTS PASSED ✓✓✓")
            print("Character stats correctly persist across idle mode transitions!")
        else:
            print("✗✗✗ TESTS FAILED ✗✗✗")
            print("Character stats are NOT persisting correctly!")
        print(f"{'=' * 70}\n")
        
        return success
        
    finally:
        # Cleanup
        try:
            temp_save_path.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    import sys
    success = test_idle_stat_persistence()
    sys.exit(0 if success else 1)
