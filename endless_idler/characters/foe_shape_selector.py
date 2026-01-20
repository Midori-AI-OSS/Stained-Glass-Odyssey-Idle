"""Shape selection logic for foes.

Deterministically maps foe stats to visual shapes from the shape palette.
Same stats always produce the same shape for visual consistency.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endless_idler.combat.stats import Stats


log = logging.getLogger(__name__)


def select_shape_for_foe(stats: Stats) -> str:
    """Select shape ID based on foe stats.
    
    Uses a deterministic algorithm to map stat profiles to shapes. The same
    stats will always produce the same shape choice, ensuring visual consistency.
    
    The selection is based on a "stat fingerprint" that normalizes stats relative
    to the foe's level, creating a profile-based hash. This ensures:
    - Same stats → same shape (deterministic)
    - Different stat profiles → different shapes (variety)
    - All 25 shapes reachable through different combinations
    
    Algorithm:
    1. Normalize stats relative to level to get stat "profile"
    2. Create weighted fingerprint from normalized ratios
    3. Map fingerprint to shape index via modulo
    
    Args:
        stats: Stats object containing foe attributes
        
    Returns:
        shape_id from the shape palette (e.g., "circle", "star_5", "hexagon")
        
    Example:
        >>> from endless_idler.combat.stats import Stats
        >>> stats = Stats(level=10, hp=1000)
        >>> stats.max_hp = 1000
        >>> stats.atk = 200
        >>> stats.defense = 100
        >>> shape_id = select_shape_for_foe(stats)
        >>> print(f"Selected shape: {shape_id}")
        Selected shape: hexagon
    """
    # Get current level (ensure it's at least 1 to avoid division by zero)
    level = max(1, stats.level)
    
    # Normalize stats relative to level baselines
    # Baseline assumptions:
    # - 10 HP per level
    # - 2 ATK per level  
    # - 1 DEF per level
    # - 1.0 ATK speed baseline
    
    hp_ratio = stats.max_hp / (level * 10)
    atk_ratio = stats.atk / (level * 2)
    def_ratio = stats.defense / level
    spd_ratio = stats.atk_speed / 1.0
    
    # Create fingerprint using weighted sum
    # Weights chosen to create good distribution across shape space
    fingerprint = int(
        hp_ratio * 1000 +
        atk_ratio * 500 +
        def_ratio * 250 +
        spd_ratio * 125
    )
    
    # Import here to avoid circular dependencies
    from endless_idler.characters.shape_palette import get_all_shape_ids
    from endless_idler.characters.shape_palette import get_shape_count
    
    # Map to shape index using modulo
    shape_count = get_shape_count()
    shape_index = fingerprint % shape_count
    
    # Get the shape ID
    all_shapes = get_all_shape_ids()
    shape_id = all_shapes[shape_index]
    
    # Log selection for debugging (can be disabled in production)
    log.debug(
        "Shape selection for %s (lvl %d): hp_ratio=%.2f, atk_ratio=%.2f, "
        "def_ratio=%.2f, spd_ratio=%.2f → fingerprint=%d → index=%d → shape=%s",
        getattr(stats, "character_id", "unknown"),
        level,
        hp_ratio,
        atk_ratio,
        def_ratio,
        spd_ratio,
        fingerprint,
        shape_index,
        shape_id,
    )
    
    return shape_id


def get_shape_selection_info(stats: Stats) -> dict[str, any]:
    """Get detailed information about why a shape was selected.
    
    Useful for debugging and testing to understand the selection process.
    
    Args:
        stats: Stats object containing foe attributes
        
    Returns:
        Dictionary with selection details including:
        - shape_id: Selected shape
        - fingerprint: Computed stat fingerprint
        - shape_index: Index in shape palette
        - stat_ratios: Normalized stat values used
        - level: Foe level
    """
    # Import here to avoid circular dependencies
    from endless_idler.characters.shape_palette import get_all_shape_ids
    from endless_idler.characters.shape_palette import get_shape_count
    
    level = max(1, stats.level)
    
    hp_ratio = stats.max_hp / (level * 10)
    atk_ratio = stats.atk / (level * 2)
    def_ratio = stats.defense / level
    spd_ratio = stats.atk_speed / 1.0
    
    fingerprint = int(
        hp_ratio * 1000 +
        atk_ratio * 500 +
        def_ratio * 250 +
        spd_ratio * 125
    )
    
    shape_count = get_shape_count()
    shape_index = fingerprint % shape_count
    shape_id = get_all_shape_ids()[shape_index]
    
    return {
        "shape_id": shape_id,
        "fingerprint": fingerprint,
        "shape_index": shape_index,
        "stat_ratios": {
            "hp_ratio": hp_ratio,
            "atk_ratio": atk_ratio,
            "def_ratio": def_ratio,
            "spd_ratio": spd_ratio,
        },
        "level": level,
        "character_id": getattr(stats, "character_id", "unknown"),
    }
