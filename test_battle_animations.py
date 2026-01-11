#!/usr/bin/env python3
"""
Test script to verify battle animation configuration.
This validates that:
1. SHOW_BATTLE_ANIMATIONS flag exists and is False
2. LineOverlay has the conditional check in paintEvent
3. MergeFxOverlay and MergeArrow are in separate files (not affected)
"""

import sys
import inspect


def test_config_flag():
    """Test that SHOW_BATTLE_ANIMATIONS flag exists and is False."""
    print("TEST 1: Checking SHOW_BATTLE_ANIMATIONS flag...")
    try:
        from endless_idler.ui.battle.widgets import SHOW_BATTLE_ANIMATIONS
        print(f"  ✓ Flag found: SHOW_BATTLE_ANIMATIONS = {SHOW_BATTLE_ANIMATIONS}")
        
        if SHOW_BATTLE_ANIMATIONS is False:
            print("  ✓ Flag is correctly set to False (animations disabled)")
            return True
        else:
            print(f"  ✗ Flag is set to {SHOW_BATTLE_ANIMATIONS}, expected False")
            return False
    except ImportError as e:
        print(f"  ✗ Failed to import flag: {e}")
        return False


def test_lineoverlay_conditional():
    """Test that LineOverlay.paintEvent checks the flag."""
    print("\nTEST 2: Checking LineOverlay.paintEvent implementation...")
    try:
        from endless_idler.ui.battle.widgets import LineOverlay
        
        # Get the source code of paintEvent
        source = inspect.getsource(LineOverlay.paintEvent)
        
        # Check for the flag check
        if "SHOW_BATTLE_ANIMATIONS" in source:
            print("  ✓ paintEvent references SHOW_BATTLE_ANIMATIONS")
        else:
            print("  ✗ paintEvent does not reference SHOW_BATTLE_ANIMATIONS")
            return False
        
        # Check for early return pattern
        if "if not SHOW_BATTLE_ANIMATIONS:" in source and "return" in source:
            print("  ✓ paintEvent has conditional return based on flag")
        else:
            print("  ✗ paintEvent missing conditional return")
            return False
        
        return True
    except Exception as e:
        print(f"  ✗ Failed to inspect LineOverlay: {e}")
        return False


def test_merge_animations_separate():
    """Test that merge animations are in a separate file."""
    print("\nTEST 3: Checking merge animation separation...")
    try:
        from endless_idler.ui.party_builder_merge_fx import MergeFxOverlay, MergeArrow
        from endless_idler.ui.battle.widgets import LineOverlay
        
        # Get file paths
        merge_file = inspect.getfile(MergeFxOverlay)
        battle_file = inspect.getfile(LineOverlay)
        
        print(f"  ✓ MergeFxOverlay located in: {merge_file}")
        print(f"  ✓ LineOverlay located in: {battle_file}")
        
        if merge_file != battle_file:
            print("  ✓ Merge and battle animations are in separate files")
            return True
        else:
            print("  ✗ Merge and battle animations are in the same file")
            return False
    except ImportError as e:
        print(f"  ✗ Failed to import animation classes: {e}")
        return False


def test_tick_unchanged():
    """Test that tick() method still exists and doesn't check the flag."""
    print("\nTEST 4: Checking LineOverlay.tick() cleanup mechanism...")
    try:
        from endless_idler.ui.battle.widgets import LineOverlay
        
        # Get the source code of tick
        source = inspect.getsource(LineOverlay.tick)
        
        # Check that tick exists
        print("  ✓ tick() method exists")
        
        # Verify tick does NOT check the flag (it should always run)
        if "SHOW_BATTLE_ANIMATIONS" in source:
            print("  ✗ tick() references SHOW_BATTLE_ANIMATIONS (should not)")
            print("     tick() must always run to prevent memory leaks")
            return False
        else:
            print("  ✓ tick() does not check flag (runs unconditionally for cleanup)")
        
        # Check that tick removes expired pulses
        if "remaining_ms" in source and ("remaining_ms > 0" in source or "remaining_ms <= 0" in source):
            print("  ✓ tick() handles pulse expiration")
            return True
        else:
            print("  ✗ tick() missing pulse expiration logic")
            return False
    except Exception as e:
        print(f"  ✗ Failed to inspect tick(): {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Battle Animation Configuration Tests")
    print("="*60)
    
    results = []
    results.append(("Config Flag", test_config_flag()))
    results.append(("LineOverlay Conditional", test_lineoverlay_conditional()))
    results.append(("Merge Separation", test_merge_animations_separate()))
    results.append(("Tick Cleanup", test_tick_unchanged()))
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "PASS ✓" if passed else "FAIL ✗"
        print(f"{name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed! Battle animations are correctly disabled.")
        print("   Stack merge animations remain unaffected.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
