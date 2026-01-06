"""Test script to verify passive extraction from character files."""

from pathlib import Path
from endless_idler.characters.metadata import extract_character_metadata

def test_character_passives():
    """Test passive extraction for characters with known passives."""
    
    test_cases = [
        ("lady_light.py", ["lady_light_radiant_aegis"]),
        ("lady_darkness.py", ["lady_darkness_eclipsing_veil"]),
        ("persona_light_and_dark.py", ["persona_light_and_dark_duality"]),
    ]
    
    characters_dir = Path("endless_idler/characters")
    
    for filename, expected_passives in test_cases:
        path = characters_dir / filename
        if not path.exists():
            print(f"⚠️  {filename} not found")
            continue
            
        result = extract_character_metadata(path)
        passives = result[9]  # Passives are at index 9
        
        if passives == expected_passives:
            print(f"✅ {filename}: {passives}")
        else:
            print(f"❌ {filename}: Expected {expected_passives}, got {passives}")
    
    # Test a character without passives (if any)
    print("\nTesting character without passives:")
    path = characters_dir / "ally.py"
    if path.exists():
        result = extract_character_metadata(path)
        passives = result[9]
        if passives == []:
            print(f"✅ ally.py: {passives} (empty as expected)")
        else:
            print(f"⚠️  ally.py: Got {passives}, expected empty list")

if __name__ == "__main__":
    test_character_passives()
