"""Test script to verify passive extraction from character files."""

from pathlib import Path
from endless_idler.characters.metadata import extract_character_metadata

def test_character_passives():
    """Test passive extraction for characters with known passives."""
    
    characters_dir = Path("endless_idler/characters")
    path = characters_dir / "lady_light.py"
    
    result = extract_character_metadata(path)
    print(f"Result type: {type(result)}")
    print(f"Result length: {len(result)}")
    print(f"Result: {result}")

if __name__ == "__main__":
    test_character_passives()
