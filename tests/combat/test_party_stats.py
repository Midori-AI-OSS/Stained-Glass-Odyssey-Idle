"""Tests for party_stats module."""
import math


from endless_idler.combat.party_stats import (
    apply_soft_cap_to_level_bonus,
    apply_soft_cap_to_rebirth_bonus,
    calculate_atk_speed_bonus,
)


class TestApplySoftCapToLevelBonus:
    """Test the soft cap implementation for level bonuses."""
    
    def test_no_levels_returns_zero(self):
        """Test that level 0 gives 0 bonus."""
        result = apply_soft_cap_to_level_bonus(0)
        assert result == 0.0
    
    def test_level_100_at_threshold(self):
        """Test that level 100 gives exactly 0.1 (at threshold)."""
        result = apply_soft_cap_to_level_bonus(100)
        assert result == 0.1
    
    def test_level_50_linear_below_threshold(self):
        """Test that level 50 gives linear value below threshold."""
        result = apply_soft_cap_to_level_bonus(50)
        expected = 50 * 0.001
        assert result == expected
        assert result == 0.05
    
    def test_level_150_shows_soft_cap(self):
        """Test that level 150 shows diminishing returns above threshold."""
        result = apply_soft_cap_to_level_bonus(150)
        # Raw linear would be 0.15, but soft cap should reduce it
        assert result > 0.1  # More than threshold
        assert result < 0.15  # Less than raw linear
        # Actual value with soft cap formula (STEP_SIZE = 0.005)
        assert abs(result - 0.1173) < 0.001
    
    def test_level_200_continued_diminishing(self):
        """Test that level 200 shows continued diminishing returns."""
        result = apply_soft_cap_to_level_bonus(200)
        # Raw linear would be 0.2, but soft cap should reduce it significantly
        assert result > 0.1  # More than threshold
        assert result < 0.2  # Less than raw linear
        # Actual value with soft cap formula (STEP_SIZE = 0.005)
        assert abs(result - 0.1220) < 0.001
    
    def test_level_300_extreme_diminishing(self):
        """Test that level 300 shows extreme diminishing returns."""
        result = apply_soft_cap_to_level_bonus(300)
        # Raw linear would be 0.3, but soft cap should reduce it significantly
        assert result > 0.1  # More than threshold
        assert result < 0.3  # Much less than raw linear
        # Actual value with soft cap formula (STEP_SIZE = 0.005)
        assert abs(result - 0.1268) < 0.001
    
    def test_level_500_very_high_diminishing(self):
        """Test that level 500 shows very high diminishing returns."""
        result = apply_soft_cap_to_level_bonus(500)
        # Raw linear would be 0.5, but soft cap should reduce it significantly
        assert result > 0.1  # More than threshold
        assert result < 0.5  # Much less than raw linear
        # Actual value with soft cap formula (STEP_SIZE = 0.005)
        assert abs(result - 0.1317) < 0.001
    
    def test_continuous_growth_no_plateau(self):
        """Test that bonuses continuously increase (no plateau)."""
        values = [apply_soft_cap_to_level_bonus(level) for level in [100, 150, 200, 250, 300, 350, 400, 450, 500]]
        # Each value should be strictly greater than the previous
        for i in range(1, len(values)):
            assert values[i] > values[i-1], f"Bonus should increase: {values[i-1]} < {values[i]}"
    
    def test_soft_cap_formula_correctness(self):
        """Test the soft cap formula implementation matches specification."""
        # For level beyond 100, the formula should be:
        # THRESHOLD + STEP_SIZE * log2(1 + (excess / STEP_SIZE))
        level = 250
        raw_value = level * 0.001  # 0.25
        threshold = 0.1
        step_size = 0.005  # 5% of threshold as per task spec
        excess = raw_value - threshold  # 0.15
        
        expected = threshold + step_size * math.log2(1 + (excess / step_size))
        result = apply_soft_cap_to_level_bonus(level)
        
        assert abs(result - expected) < 1e-10  # Very close (floating point tolerance)


class TestApplySoftCapToRebirthBonus:
    """Test the soft cap implementation for rebirth bonuses."""
    
    def test_no_rebirths_returns_zero(self):
        """Test that 0 rebirths gives 0 bonus."""
        result = apply_soft_cap_to_rebirth_bonus(0)
        assert result == 0.0
    
    def test_rebirth_100_at_threshold(self):
        """Test that rebirth 100 gives exactly 0.2 (at threshold)."""
        result = apply_soft_cap_to_rebirth_bonus(100)
        assert result == 0.2
    
    def test_rebirth_50_linear_below_threshold(self):
        """Test that rebirth 50 gives linear value below threshold."""
        result = apply_soft_cap_to_rebirth_bonus(50)
        expected = 50 * 0.002
        assert result == expected
        assert result == 0.1
    
    def test_rebirth_150_shows_soft_cap(self):
        """Test that rebirth 150 shows diminishing returns above threshold."""
        result = apply_soft_cap_to_rebirth_bonus(150)
        # Raw linear would be 0.3, but soft cap should reduce it
        assert result > 0.2  # More than threshold
        assert result < 0.3  # Less than raw linear
        # Actual value with soft cap formula (STEP_SIZE = 0.01)
        assert abs(result - 0.2346) < 0.001
    
    def test_rebirth_200_continued_diminishing(self):
        """Test that rebirth 200 shows continued diminishing returns."""
        result = apply_soft_cap_to_rebirth_bonus(200)
        # Raw linear would be 0.4, but soft cap should reduce it significantly
        assert result > 0.2  # More than threshold
        assert result < 0.4  # Less than raw linear
        # Actual value with soft cap formula (STEP_SIZE = 0.01)
        assert abs(result - 0.2439) < 0.001
    
    def test_rebirth_300_extreme_diminishing(self):
        """Test that rebirth 300 shows extreme diminishing returns."""
        result = apply_soft_cap_to_rebirth_bonus(300)
        # Raw linear would be 0.6, but soft cap should reduce it significantly
        assert result > 0.2  # More than threshold
        assert result < 0.6  # Much less than raw linear
        # Actual value with soft cap formula (STEP_SIZE = 0.01)
        assert abs(result - 0.2536) < 0.001
    
    def test_rebirth_500_very_high_diminishing(self):
        """Test that rebirth 500 shows very high diminishing returns."""
        result = apply_soft_cap_to_rebirth_bonus(500)
        # Raw linear would be 1.0, but soft cap should reduce it significantly
        assert result > 0.2  # More than threshold
        assert result < 1.0  # Much less than raw linear
        # Actual value with soft cap formula (STEP_SIZE = 0.01)
        assert abs(result - 0.2634) < 0.001
    
    def test_continuous_growth_no_plateau(self):
        """Test that bonuses continuously increase (no plateau)."""
        values = [apply_soft_cap_to_rebirth_bonus(r) for r in [100, 150, 200, 250, 300, 350, 400, 450, 500]]
        # Each value should be strictly greater than the previous
        for i in range(1, len(values)):
            assert values[i] > values[i-1], f"Bonus should increase: {values[i-1]} < {values[i]}"
    
    def test_soft_cap_formula_correctness(self):
        """Test the soft cap formula implementation matches specification."""
        # For rebirth beyond 100, the formula should be:
        # THRESHOLD + STEP_SIZE * log2(1 + (excess / STEP_SIZE))
        rebirths = 250
        raw_value = rebirths * 0.002  # 0.5
        threshold = 0.2
        step_size = 0.01  # 5% of threshold as per task spec
        excess = raw_value - threshold  # 0.3
        
        expected = threshold + step_size * math.log2(1 + (excess / step_size))
        result = apply_soft_cap_to_rebirth_bonus(rebirths)
        
        assert abs(result - expected) < 1e-10  # Very close (floating point tolerance)


class TestCalculateAtkSpeedBonus:
    """Test the combined atk_speed bonus calculation."""
    
    def test_level_0_rebirth_0_returns_zero(self):
        """Test that level 0, rebirth 0 gives 0 bonus."""
        result = calculate_atk_speed_bonus(0, 0)
        assert result == 0.0
    
    def test_level_bonus_linear_up_to_100(self):
        """Test that level bonus is linear up to level 100."""
        result_50 = calculate_atk_speed_bonus(50, 0)
        assert result_50 == 0.05
        
        result_100 = calculate_atk_speed_bonus(100, 0)
        assert result_100 == 0.1
    
    def test_level_bonus_uses_soft_cap(self):
        """Test that level bonus uses soft cap function."""
        # At level 100, should be at threshold
        result_100 = calculate_atk_speed_bonus(100, 0)
        assert result_100 == 0.1
        
        # At level 150, should show soft cap
        result_150 = calculate_atk_speed_bonus(150, 0)
        assert result_150 > 0.1  # More than threshold
        assert result_150 < 0.15  # Less than raw linear
        assert abs(result_150 - 0.1173) < 0.001
    
    def test_rebirth_bonus_uses_soft_cap(self):
        """Test that rebirth bonus uses soft cap function."""
        # At rebirth 100, should be at threshold
        result_100 = calculate_atk_speed_bonus(0, 100)
        assert result_100 == 0.2
        
        # At rebirth 150, should show soft cap
        result_150 = calculate_atk_speed_bonus(0, 150)
        assert result_150 > 0.2
        assert result_150 < 0.3
    
    def test_combined_bonuses(self):
        """Test that level and rebirth bonuses combine correctly."""
        level_bonus = calculate_atk_speed_bonus(100, 0)
        rebirth_bonus = calculate_atk_speed_bonus(0, 100)
        combined = calculate_atk_speed_bonus(100, 100)
        
        assert combined == level_bonus + rebirth_bonus
        assert abs(combined - 0.3) < 1e-10  # 0.1 from level + 0.2 from rebirth
    
    def test_combined_with_soft_cap(self):
        """Test combined bonuses with soft cap active."""
        result = calculate_atk_speed_bonus(100, 150)
        # Level gives 0.1, rebirth ~0.2346
        assert result > 0.3  # More than threshold (0.1 + 0.2)
        assert abs(result - 0.3346) < 0.001  # ~0.1 + 0.2346
    
    def test_combined_with_both_soft_caps(self):
        """Test combined bonuses with both soft caps active."""
        result = calculate_atk_speed_bonus(150, 150)
        # Level ~0.1173, rebirth ~0.2346
        assert result > 0.3  # More than thresholds (0.1 + 0.2)
        assert abs(result - 0.3519) < 0.001  # ~0.1173 + 0.2346
    
    def test_negative_inputs_clamped(self):
        """Test that negative inputs are clamped to 0."""
        result = calculate_atk_speed_bonus(-10, -10)
        assert result == 0.0
