"""Test time-based wave spawn count scaling.

Tests the formula: time_mult = 1 + 0.15 * floor(t / 25) + 0.05 * floor(t / 30)
"""
import math


def calculate_time_multiplier(survival_time: float) -> float:
    """Calculate time multiplier for spawn count.
    
    Args:
        survival_time: Seconds survived in current battle
        
    Returns:
        Time multiplier value
    """
    return 1.0 + 0.15 * int(survival_time / 25) + 0.05 * int(survival_time / 30)


def calculate_spawn_count(base_spawn_count: int, time_mult: float) -> int:
    """Calculate spawn count with time multiplier applied.
    
    Args:
        base_spawn_count: Baseline spawn count
        time_mult: Time multiplier
        
    Returns:
        Spawn count (ceiling applied)
    """
    return math.ceil(base_spawn_count * time_mult)


def test_time_multiplier_at_zero_seconds():
    """Test time_mult at t=0s should be 1.0"""
    time_mult = calculate_time_multiplier(0)
    assert time_mult == 1.0, f"Expected 1.0, got {time_mult}"
    print(f"✓ t=0s: time_mult = {time_mult}")


def test_time_multiplier_at_25_seconds():
    """Test time_mult at t=25s should be 1.15"""
    time_mult = calculate_time_multiplier(25)
    expected = 1.15
    assert time_mult == expected, f"Expected {expected}, got {time_mult}"
    print(f"✓ t=25s: time_mult = {time_mult}")


def test_time_multiplier_at_50_seconds():
    """Test time_mult at t=50s should be 1.35"""
    time_mult = calculate_time_multiplier(50)
    expected = 1.35
    assert time_mult == expected, f"Expected {expected}, got {time_mult}"
    print(f"✓ t=50s: time_mult = {time_mult}")


def test_time_multiplier_at_75_seconds():
    """Test time_mult at t=75s should be 1.55"""
    time_mult = calculate_time_multiplier(75)
    expected = 1.55
    assert time_mult == expected, f"Expected {expected}, got {time_mult}"
    print(f"✓ t=75s: time_mult = {time_mult}")


def test_time_multiplier_at_120_seconds():
    """Test time_mult at t=120s should be 1.80"""
    time_mult = calculate_time_multiplier(120)
    expected = 1.80
    assert time_mult == expected, f"Expected {expected}, got {time_mult}"
    print(f"✓ t=120s: time_mult = {time_mult}")


def test_spawn_count_with_base_5():
    """Test spawn counts with base_spawn_count = 5"""
    base = 5
    
    # t=0s: 5 * 1.0 = 5
    count = calculate_spawn_count(base, 1.0)
    assert count == 5, f"Expected 5, got {count}"
    print(f"✓ base=5, mult=1.0: spawn_count = {count}")
    
    # t=25s: 5 * 1.15 = 5.75 -> ceil = 6
    count = calculate_spawn_count(base, 1.15)
    assert count == 6, f"Expected 6, got {count}"
    print(f"✓ base=5, mult=1.15: spawn_count = {count}")
    
    # t=50s: 5 * 1.35 = 6.75 -> ceil = 7
    count = calculate_spawn_count(base, 1.35)
    assert count == 7, f"Expected 7, got {count}"
    print(f"✓ base=5, mult=1.35: spawn_count = {count}")
    
    # t=75s: 5 * 1.55 = 7.75 -> ceil = 8
    count = calculate_spawn_count(base, 1.55)
    assert count == 8, f"Expected 8, got {count}"
    print(f"✓ base=5, mult=1.55: spawn_count = {count}")
    
    # t=120s: 5 * 1.80 = 9.0 -> ceil = 9
    count = calculate_spawn_count(base, 1.80)
    assert count == 9, f"Expected 9, got {count}"
    print(f"✓ base=5, mult=1.80: spawn_count = {count}")


def test_formula_breakdown():
    """Test the formula components at various times"""
    test_cases = [
        (0, 0, 0, 1.0),
        (25, 1, 0, 1.15),
        (30, 1, 1, 1.20),
        (50, 2, 1, 1.35),
        (60, 2, 2, 1.40),
        (75, 3, 2, 1.55),
        (120, 4, 4, 1.80),
    ]
    
    for t, expected_floor_25, expected_floor_30, expected_mult in test_cases:
        floor_25 = int(t / 25)
        floor_30 = int(t / 30)
        mult = 1.0 + 0.15 * floor_25 + 0.05 * floor_30
        
        assert floor_25 == expected_floor_25, f"t={t}: floor(t/25) expected {expected_floor_25}, got {floor_25}"
        assert floor_30 == expected_floor_30, f"t={t}: floor(t/30) expected {expected_floor_30}, got {floor_30}"
        assert math.isclose(mult, expected_mult), f"t={t}: time_mult expected {expected_mult}, got {mult}"
        
        print(f"✓ t={t}s: floor(t/25)={floor_25}, floor(t/30)={floor_30}, mult={mult}")


def test_ceiling_function():
    """Test that ceiling function works correctly"""
    # Test cases where ceiling matters
    assert math.ceil(5.1) == 6
    assert math.ceil(5.9) == 6
    assert math.ceil(5.0) == 5
    assert math.ceil(6.75) == 7
    print("✓ Ceiling function works correctly")


if __name__ == "__main__":
    print("Testing time-based wave spawn count scaling...")
    print("=" * 60)
    
    test_time_multiplier_at_zero_seconds()
    test_time_multiplier_at_25_seconds()
    test_time_multiplier_at_50_seconds()
    test_time_multiplier_at_75_seconds()
    test_time_multiplier_at_120_seconds()
    
    print()
    test_spawn_count_with_base_5()
    
    print()
    test_formula_breakdown()
    
    print()
    test_ceiling_function()
    
    print("=" * 60)
    print("✅ All tests passed!")
