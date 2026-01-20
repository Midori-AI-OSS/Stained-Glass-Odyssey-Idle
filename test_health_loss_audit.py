#!/usr/bin/env python3
"""
Audit test for task 3b475c14: Implement run health loss on defeat
Tests all acceptance criteria and edge cases.
"""

import time
from endless_idler.run_rules import apply_battle_result
from endless_idler.save import RunSave


def test_health_loss_formula():
    """Test that the health loss formula meets all requirements."""
    print("\n=== Testing Health Loss Formula ===")
    
    # Test 1: Short survival (10s) - should have ~95-97% loss
    save = RunSave(party_hp_current=100, party_hp_max=100)
    apply_battle_result(save, victory=False, survival_seconds=10.0)
    loss_10s = 100 - save.party_hp_current
    loss_10s_percent = (loss_10s / 100) * 100
    print(f"10s survival: {loss_10s}% loss (expected ~95-97%)")
    assert 94 <= loss_10s_percent <= 98, f"10s loss should be ~95-97%, got {loss_10s_percent}%"
    
    # Test 2: Medium survival (100s) - should have ~70% loss
    save = RunSave(party_hp_current=100, party_hp_max=100)
    apply_battle_result(save, victory=False, survival_seconds=100.0)
    loss_100s = 100 - save.party_hp_current
    loss_100s_percent = (loss_100s / 100) * 100
    print(f"100s survival: {loss_100s}% loss (expected ~70%)")
    assert 68 <= loss_100s_percent <= 72, f"100s loss should be ~70%, got {loss_100s_percent}%"
    
    # Test 3: Long survival (300s) - should have ~10% loss
    save = RunSave(party_hp_current=100, party_hp_max=100)
    apply_battle_result(save, victory=False, survival_seconds=300.0)
    loss_300s = 100 - save.party_hp_current
    loss_300s_percent = (loss_300s / 100) * 100
    print(f"300s survival: {loss_300s}% loss (expected ~10%)")
    assert 8 <= loss_300s_percent <= 12, f"300s loss should be ~10%, got {loss_300s_percent}%"
    
    # Test 4: Very long survival (400s) - should have minimum 5% loss
    save = RunSave(party_hp_current=100, party_hp_max=100)
    apply_battle_result(save, victory=False, survival_seconds=400.0)
    loss_400s = 100 - save.party_hp_current
    loss_400s_percent = (loss_400s / 100) * 100
    print(f"400s survival: {loss_400s}% loss (expected ~5% minimum)")
    assert 5 <= loss_400s_percent <= 7, f"400s loss should be ~5%, got {loss_400s_percent}%"
    
    print("✓ Health loss formula tests passed")


def test_monotonic_decreasing():
    """Test that longer survival always means less or equal loss."""
    print("\n=== Testing Monotonic Decreasing Property ===")
    
    test_times = [5.0, 10.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0]
    previous_loss_percent = 100.0
    
    for survival_time in test_times:
        save = RunSave(party_hp_current=100, party_hp_max=100)
        apply_battle_result(save, victory=False, survival_seconds=survival_time)
        loss = 100 - save.party_hp_current
        loss_percent = (loss / 100) * 100
        
        print(f"{survival_time:6.1f}s survival: {loss_percent:5.1f}% loss")
        assert loss_percent <= previous_loss_percent, \
            f"Loss must be monotonically decreasing: {survival_time}s has {loss_percent}%, but previous was {previous_loss_percent}%"
        
        previous_loss_percent = loss_percent
    
    print("✓ Monotonic decreasing property verified")


def test_bounds():
    """Test max 95% and min 5% loss bounds."""
    print("\n=== Testing Bounds (Max 95%, Min 5%) ===")
    
    # Test maximum loss (very short survival)
    save = RunSave(party_hp_current=100, party_hp_max=100)
    apply_battle_result(save, victory=False, survival_seconds=0.0)
    loss_0s = 100 - save.party_hp_current
    loss_0s_percent = (loss_0s / 100) * 100
    print(f"0s survival: {loss_0s}% loss (max should be ≤95%)")
    assert loss_0s_percent <= 95, f"Max loss should be ≤95%, got {loss_0s_percent}%"
    
    # Test minimum loss (very long survival)
    save = RunSave(party_hp_current=100, party_hp_max=100)
    apply_battle_result(save, victory=False, survival_seconds=1000.0)
    loss_1000s = 100 - save.party_hp_current
    loss_1000s_percent = (loss_1000s / 100) * 100
    print(f"1000s survival: {loss_1000s}% loss (min should be ≥5%)")
    assert loss_1000s_percent >= 5, f"Min loss should be ≥5%, got {loss_1000s_percent}%"
    
    print("✓ Bounds tests passed")


def test_never_below_zero():
    """Test that health never goes below 0."""
    print("\n=== Testing Health Never Goes Below 0 ===")
    
    # Test with low health
    save = RunSave(party_hp_current=10, party_hp_max=100)
    apply_battle_result(save, victory=False, survival_seconds=5.0)
    print(f"Low health test: {save.party_hp_current} (should be ≥0)")
    assert save.party_hp_current >= 0, f"Health should never be negative, got {save.party_hp_current}"
    
    # Test with very low health
    save = RunSave(party_hp_current=1, party_hp_max=100)
    apply_battle_result(save, victory=False, survival_seconds=0.0)
    print(f"Very low health test: {save.party_hp_current} (should be ≥0)")
    assert save.party_hp_current >= 0, f"Health should never be negative, got {save.party_hp_current}"
    
    print("✓ Health never below 0 verified")


def test_run_health_variable():
    """Test that correct run health variable is used."""
    print("\n=== Testing Correct Run Health Variable ===")
    
    save = RunSave(party_hp_current=100, party_hp_max=150)
    initial_hp = save.party_hp_current
    
    apply_battle_result(save, victory=False, survival_seconds=100.0)
    
    print(f"Initial: {initial_hp}, After defeat: {save.party_hp_current}")
    assert save.party_hp_current < initial_hp, "Health should decrease on defeat"
    assert save.party_hp_current <= save.party_hp_max, "Health should not exceed max"
    
    print("✓ Correct run health variable (party_hp_current) verified")


def test_partial_health_scenarios():
    """Test with various starting health levels."""
    print("\n=== Testing Partial Health Scenarios ===")
    
    # Test with 50% health
    save = RunSave(party_hp_current=50, party_hp_max=100)
    apply_battle_result(save, victory=False, survival_seconds=50.0)
    print(f"50% initial health, 50s survival: {save.party_hp_current} HP remaining")
    assert save.party_hp_current >= 0, "Health should not be negative"
    
    # Test with 25% health
    save = RunSave(party_hp_current=25, party_hp_max=100)
    apply_battle_result(save, victory=False, survival_seconds=50.0)
    print(f"25% initial health, 50s survival: {save.party_hp_current} HP remaining")
    assert save.party_hp_current >= 0, "Health should not be negative"
    
    print("✓ Partial health scenarios tested")


def test_force_reset_condition():
    """Test that run resets when health reaches 0."""
    print("\n=== Testing Force Reset Condition ===")
    
    # Test that very low health with high loss triggers reset
    save = RunSave(party_hp_current=5, party_hp_max=100)
    should_reset = apply_battle_result(save, victory=False, survival_seconds=10.0)
    print(f"Low health, short survival: should_reset={should_reset}, final_hp={save.party_hp_current}")
    
    if save.party_hp_current <= 0:
        assert should_reset is True, "Should return True when health reaches 0"
        print("✓ Force reset triggered correctly")
    else:
        print("✓ Health stayed above 0, no reset needed")


if __name__ == "__main__":
    print("=" * 60)
    print("AUDIT: Task 3b475c14 - Run Health Loss on Defeat")
    print("=" * 60)
    
    try:
        test_health_loss_formula()
        test_monotonic_decreasing()
        test_bounds()
        test_never_below_zero()
        test_run_health_variable()
        test_partial_health_scenarios()
        test_force_reset_condition()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nConclusion: Implementation meets all acceptance criteria.")
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"TEST FAILED ✗")
        print("=" * 60)
        print(f"\nError: {e}")
        exit(1)
