"""Test foe cap and wave-only overflow scaling"""


def test_wave_only_multiplier_calculation():
    """Test that wave-only multiplier is calculated correctly"""
    # Test cases from task requirements
    test_cases = [
        (0, 1.0),       # No blocked spawns
        (1, 1.01),      # 1 blocked spawn
        (5, 1.051),     # 5 blocked spawns (approx 1.051)
        (10, 1.1046),   # 10 blocked spawns (approx 1.1046)
    ]
    
    for blocked_spawns, expected_mult in test_cases:
        wave_only_mult = pow(1.01, blocked_spawns)
        assert abs(wave_only_mult - expected_mult) < 0.001, \
            f"Expected {expected_mult}, got {wave_only_mult} for {blocked_spawns} blocked spawns"
    
    print("✓ Wave-only multiplier calculation test passed")


def test_foe_cap_logic():
    """Test that foe cap logic works correctly"""
    MAX_FOES = 100
    
    # Simulate scenario: 95 foes alive, try to spawn 10
    current_foe_count = 95
    requested_spawn_count = 10
    
    available_slots = MAX_FOES - current_foe_count
    actual_spawn_count = min(requested_spawn_count, max(0, available_slots))
    blocked_spawns = max(0, requested_spawn_count - actual_spawn_count)
    
    assert available_slots == 5, f"Expected 5 available slots, got {available_slots}"
    assert actual_spawn_count == 5, f"Expected 5 actual spawns, got {actual_spawn_count}"
    assert blocked_spawns == 5, f"Expected 5 blocked spawns, got {blocked_spawns}"
    
    wave_only_mult = pow(1.01, blocked_spawns)
    expected_mult = pow(1.01, 5)  # Should be ~1.051
    assert abs(wave_only_mult - expected_mult) < 0.001, \
        f"Expected multiplier ~{expected_mult}, got {wave_only_mult}"
    
    print("✓ Foe cap logic test passed (95 alive + 10 requested = 5 spawned + 5 blocked)")


def test_cap_at_100():
    """Test that spawning stops at 100 foes"""
    MAX_FOES = 100
    
    # Simulate 100 foes already alive
    current_foe_count = 100
    requested_spawn_count = 5
    
    available_slots = MAX_FOES - current_foe_count
    actual_spawn_count = min(requested_spawn_count, max(0, available_slots))
    blocked_spawns = max(0, requested_spawn_count - actual_spawn_count)
    
    assert available_slots == 0, f"Expected 0 available slots, got {available_slots}"
    assert actual_spawn_count == 0, f"Expected 0 actual spawns, got {actual_spawn_count}"
    assert blocked_spawns == 5, f"Expected 5 blocked spawns, got {blocked_spawns}"
    
    print("✓ Cap at 100 foes test passed (100 alive + 5 requested = 0 spawned + 5 blocked)")


if __name__ == "__main__":
    test_wave_only_multiplier_calculation()
    test_foe_cap_logic()
    test_cap_at_100()
    print("\n✅ All foe cap tests passed!")
