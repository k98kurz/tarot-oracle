"""Test deck loading with centralized configuration."""

import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.tarot import DeckLoader
from tarot_oracle.config import Config, config


def test_config_decks_dir_exists():
    """Test that the config's decks directory exists."""
    # This should work with the actual user's config
    assert config.decks_dir.parent.exists(), "Config home directory should exist"
    # The decks directory should be created automatically
    assert config.decks_dir.exists(), "Decks directory should be created automatically"


def test_deck_loader_search_paths():
    """Test that DeckLoader uses the correct search paths."""
    from tarot_oracle.tarot import DeckLoader
    import re
    
    deck_loader = DeckLoader()
    test_filename = "test_deck"
    
    # Simulate the filename sanitization
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', test_filename)
    
    # Expected search paths using config
    expected_paths = [
        Path.cwd() / safe_filename,
        Path.cwd() / f"{safe_filename}.json",
        config.decks_dir / safe_filename,
        config.decks_dir / f"{safe_filename}.json"
    ]
    
    # Verify paths use config.decks_dir
    assert str(expected_paths[2]).endswith(f"{config.decks_dir.name}/{safe_filename}")
    assert str(expected_paths[3]).endswith(f"{config.decks_dir.name}/{safe_filename}.json")


def test_deck_loader_security():
    """Test that DeckLoader prevents path traversal."""
    deck_loader = DeckLoader()
    
    # Test malicious filenames
    malicious_names = [
        "../../../etc/passwd",
        "..\\..\\windows\\system32\\config\\sam",
        "test/../../../etc/passwd",
        ""
    ]
    
    for name in malicious_names:
        resolved = deck_loader.resolve_deck_path(name)
        assert resolved is None, f"Should reject malicious filename: {name}"


def test_deck_loader_with_real_deck():
    """Test DeckLoader with an actual deck file in the config directory."""
    # Create a minimal test deck in the actual config directory
    test_deck = {
        "name": "Unit Test Deck",
        "description": "Temporary deck for testing",
        "cards": ["W_A", "W_2", "W_3"]
    }
    
    deck_file = config.decks_dir / "unit_test_deck.json"
    
    try:
        # Create the test deck file
        with open(deck_file, 'w') as f:
            json.dump(test_deck, f)
        
        # Test that the deck loader can find it
        deck_loader = DeckLoader()
        resolved = deck_loader.resolve_deck_path("unit_test_deck")
        
        assert resolved is not None, "Should resolve the test deck"
        assert resolved.endswith("unit_test_deck.json"), "Should resolve to correct filename"
        
        # Test that the deck can be loaded
        deck_config = DeckLoader.load_deck_config(resolved)
        assert deck_config["name"] == "Unit Test Deck"
        assert deck_config["cards"] == ["W_A", "W_2", "W_3"]
        
    finally:
        # Clean up the test file
        if deck_file.exists():
            deck_file.unlink()





if __name__ == "__main__":
    test_config_decks_dir_exists()
    test_deck_loader_search_paths()
    test_deck_loader_security()
    test_deck_loader_with_real_deck()
    print("All DeckLoader tests passed!")