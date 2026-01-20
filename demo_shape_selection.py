#!/usr/bin/env python
"""Demonstration of foe shape selection logic.

Shows how different stat profiles map to different shapes.
"""

from endless_idler.characters.foe_shape_selector import get_shape_selection_info
from endless_idler.characters.foe_shape_selector import select_shape_for_foe
from endless_idler.combat.stats import Stats


def demo_basic_selection():
    """Demonstrate basic shape selection."""
    print("=" * 60)
    print("DEMO 1: Basic Shape Selection")
    print("=" * 60)
    
    # Create a basic foe
    foe = Stats(character_id="basic_foe", level=10)
    foe._base_max_hp = 1000
    foe._base_atk = 200
    foe._base_defense = 100
    foe._base_atk_speed = 2
    
    shape_id = select_shape_for_foe(foe)
    info = get_shape_selection_info(foe)
    
    print(f"\nFoe Stats:")
    print(f"  Level: {foe.level}")
    print(f"  HP: {foe.max_hp}")
    print(f"  ATK: {foe.atk}")
    print(f"  DEF: {foe.defense}")
    print(f"  SPD: {foe.atk_speed}")
    
    print(f"\nSelection Process:")
    print(f"  HP Ratio: {info['stat_ratios']['hp_ratio']:.2f}")
    print(f"  ATK Ratio: {info['stat_ratios']['atk_ratio']:.2f}")
    print(f"  DEF Ratio: {info['stat_ratios']['def_ratio']:.2f}")
    print(f"  SPD Ratio: {info['stat_ratios']['spd_ratio']:.2f}")
    print(f"  Fingerprint: {info['fingerprint']}")
    print(f"  Shape Index: {info['shape_index']}")
    
    print(f"\n  → Selected Shape: {shape_id}")


def demo_determinism():
    """Demonstrate that same stats always give same shape."""
    print("\n" + "=" * 60)
    print("DEMO 2: Determinism (Same Stats → Same Shape)")
    print("=" * 60)
    
    # Create two foes with identical stats
    foe1 = Stats(character_id="foe_1", level=10)
    foe1._base_max_hp = 1500
    foe1._base_atk = 250
    foe1._base_defense = 120
    foe1._base_atk_speed = 3
    
    foe2 = Stats(character_id="foe_2", level=10)
    foe2._base_max_hp = 1500
    foe2._base_atk = 250
    foe2._base_defense = 120
    foe2._base_atk_speed = 3
    
    shape1 = select_shape_for_foe(foe1)
    shape2 = select_shape_for_foe(foe2)
    
    print(f"\nFoe 1 (ID: {foe1.character_id}): {shape1}")
    print(f"Foe 2 (ID: {foe2.character_id}): {shape2}")
    print(f"\nDeterministic: {shape1 == shape2}")


def demo_archetypes():
    """Demonstrate different foe archetypes get different shapes."""
    print("\n" + "=" * 60)
    print("DEMO 3: Archetypes (Different Profiles → Different Shapes)")
    print("=" * 60)
    
    archetypes = []
    
    # Tank: High HP and Defense, low ATK and Speed
    tank = Stats(character_id="tank", level=10)
    tank._base_max_hp = 3000
    tank._base_atk = 100
    tank._base_defense = 300
    tank._base_atk_speed = 1
    archetypes.append(("Tank (High HP/DEF)", tank))
    
    # DPS: High ATK and Speed, low HP and Defense
    dps = Stats(character_id="dps", level=10)
    dps._base_max_hp = 500
    dps._base_atk = 500
    dps._base_defense = 50
    dps._base_atk_speed = 5
    archetypes.append(("DPS (High ATK/SPD)", dps))
    
    # Balanced: Average everything
    balanced = Stats(character_id="balanced", level=10)
    balanced._base_max_hp = 1000
    balanced._base_atk = 200
    balanced._base_defense = 100
    balanced._base_atk_speed = 2
    archetypes.append(("Balanced", balanced))
    
    # Glass Cannon: Very high ATK, very low defense
    glass = Stats(character_id="glass_cannon", level=10)
    glass._base_max_hp = 300
    glass._base_atk = 800
    glass._base_defense = 20
    glass._base_atk_speed = 4
    archetypes.append(("Glass Cannon", glass))
    
    # Fortress: Very high DEF, low everything else
    fortress = Stats(character_id="fortress", level=10)
    fortress._base_max_hp = 2000
    fortress._base_atk = 50
    fortress._base_defense = 500
    fortress._base_atk_speed = 1
    archetypes.append(("Fortress (Very High DEF)", fortress))
    
    print()
    for name, foe in archetypes:
        shape = select_shape_for_foe(foe)
        info = get_shape_selection_info(foe)
        print(f"{name:25} → {shape:15} (fingerprint: {info['fingerprint']:6})")


def demo_level_scaling():
    """Demonstrate that stat ratios matter more than absolute values."""
    print("\n" + "=" * 60)
    print("DEMO 4: Level Scaling (Same Profile → Same Shape)")
    print("=" * 60)
    
    print("\nFoes with same stat profile at different levels:")
    print()
    
    for level in [1, 5, 10, 50, 100]:
        foe = Stats(character_id=f"foe_lvl_{level}", level=level)
        # Keep same ratios: 10 HP/level, 2 ATK/level, 1 DEF/level, 1 SPD
        foe._base_max_hp = level * 10
        foe._base_atk = level * 2
        foe._base_defense = level * 1
        foe._base_atk_speed = 1
        
        shape = select_shape_for_foe(foe)
        print(f"  Level {level:3}: HP={foe.max_hp:4}, ATK={foe.atk:3}, DEF={foe.defense:3} → {shape}")


def demo_variety():
    """Demonstrate variety in shape selection."""
    print("\n" + "=" * 60)
    print("DEMO 5: Variety (Random Foes)")
    print("=" * 60)
    
    import random
    random.seed(42)
    
    shapes_count = {}
    
    for i in range(100):
        foe = Stats(character_id=f"random_foe_{i}", level=random.randint(1, 20))
        foe._base_max_hp = random.randint(500, 3000)
        foe._base_atk = random.randint(50, 500)
        foe._base_defense = random.randint(20, 300)
        foe._base_atk_speed = random.randint(1, 5)
        
        shape = select_shape_for_foe(foe)
        shapes_count[shape] = shapes_count.get(shape, 0) + 1
    
    print(f"\nGenerated 100 random foes:")
    print(f"Unique shapes seen: {len(shapes_count)}/25")
    print(f"\nShape distribution:")
    for shape, count in sorted(shapes_count.items(), key=lambda x: -x[1])[:10]:
        print(f"  {shape:15}: {count:2} {'█' * count}")


if __name__ == "__main__":
    demo_basic_selection()
    demo_determinism()
    demo_archetypes()
    demo_level_scaling()
    demo_variety()
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
