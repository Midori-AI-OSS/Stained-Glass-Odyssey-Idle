"""
Crit Mod System

This module provides utilities for calculating crit chance and crit damage
based on a single unified stat called "crit mod".

Formulas:
- Crit Chance: Every 100 points of crit mod adds 1% crit chance, but it takes
  2x more points for each additional 1% (100 for 1%, 300 for 2%, 700 for 3%, etc.)
  
- Crit Damage: Every 20 points of crit mod adds 0.05x to crit damage multiplier
  (starting at 1.0x base, so 20 points = 1.05x, 40 points = 1.10x, 60 points = 1.15x).
  Every 200 points doubles the points needed per buff (so after 200 points, it takes
  40 points per 0.05x increase, after 400 cumulative it takes 80 points, etc.)
"""

from __future__ import annotations


def calculate_crit_chance(crit_mod: float) -> float:
    """
    Calculate crit chance percentage from crit mod.
    
    Formula: Each 1% crit chance requires 2x more points than the previous 1%.
    - 0-100 points: 1st percent (0-1%)
    - 100-300 points: 2nd percent (1-2%) - needs 200 more
    - 300-700 points: 3rd percent (2-3%) - needs 400 more
    - 700-1500 points: 4th percent (3-4%) - needs 800 more
    
    General formula: For nth percent, need sum of (100 * 2^(i-1)) for i=1 to n
    Which equals: 100 * (2^n - 1)
    
    Args:
        crit_mod: The crit mod stat value
        
    Returns:
        Crit chance as a decimal (0.0 to 1.0)
    """
    if crit_mod <= 0:
        return 0.0
    
    # Binary search to find which percent tier we're in
    percent = 0
    cumulative_needed = 0.0
    
    while True:
        # Calculate points needed for the next percent
        points_for_next = 100.0 * (2 ** percent)
        next_threshold = cumulative_needed + points_for_next
        
        if crit_mod < next_threshold:
            # We're in this tier, calculate partial progress
            progress_in_tier = crit_mod - cumulative_needed
            partial_percent = progress_in_tier / points_for_next
            total_percent = percent + partial_percent
            return min(1.0, total_percent / 100.0)  # Cap at 100%
        
        # Move to next tier
        cumulative_needed = next_threshold
        percent += 1
        
        if percent >= 100:  # Safety cap
            return 1.0


def calculate_crit_damage(crit_mod: float) -> float:
    """
    Calculate crit damage multiplier from crit mod.
    
    Formula: Base 1.0x, every 20 points adds 0.05x to multiplier.
    Every 200 points doubles the points needed per 0.05x increase.
    
    Tiers:
    - 0-200 points: 20 points per 0.05x (10 increases = 1.0x + 0.5x = 1.5x at 200)
    - 200-400 points: 40 points per 0.05x (5 increases = 1.5x + 0.25x = 1.75x at 400)
    - 400-600 points: 80 points per 0.05x (2.5 increases = 1.75x + 0.125x = 1.875x at 600)
    
    Args:
        crit_mod: The crit mod stat value
        
    Returns:
        Crit damage multiplier (minimum 1.0x)
    """
    if crit_mod <= 0:
        return 1.0
    
    multiplier = 1.0
    remaining_points = crit_mod
    tier = 0
    
    while remaining_points > 0:
        # Points needed per 0.05x increase in this tier
        points_per_increase = 20.0 * (2 ** tier)
        
        # Points in this tier (200 points per tier)
        tier_size = 200.0
        
        if remaining_points >= tier_size:
            # Complete this entire tier
            increases_in_tier = tier_size / points_per_increase
            multiplier += increases_in_tier * 0.05
            remaining_points -= tier_size
            tier += 1
        else:
            # Partial tier
            increases_in_tier = remaining_points / points_per_increase
            multiplier += increases_in_tier * 0.05
            break
    
    return multiplier
