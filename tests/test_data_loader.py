from pathlib import Path
from unittest.mock import patch, MagicMock

import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.data_loader import BundledDataLoader


class TestBundledDataLoader(unittest.TestCase):
    def test_load_deck_existing(self):
        """Test loading existing bundled deck."""
        deck = BundledDataLoader.load_deck("rider-waite")
        assert deck is not None, "Should load rider-waite deck"
        assert "name" in deck, "Deck should have 'name' field"
        assert "description" in deck, "Deck should have 'description' field"
        assert "cards" in deck, "Deck should have 'cards' field"

    def test_load_spread_existing(self):
        """Test loading existing bundled spread."""
        spread = BundledDataLoader.load_spread("celtic")
        assert spread is not None, "Should load celtic spread"
        assert "name" in spread, "Spread should have 'name' field"
        assert "description" in spread, "Spread should have 'description' field"
        assert "layout" in spread, "Spread should have 'layout' field"

    def test_load_all_bundled_spreads(self):
        """Test loading all bundled spreads are valid."""
        expected_spreads = ["cross", "celtic", "single", "zodiac", "crowley", "3-card", "zodiac_plus"]
        for spread_name in expected_spreads:
            spread = BundledDataLoader.load_spread(spread_name)
            assert spread is not None, f"Should load {spread_name} spread"
            assert "name" in spread, f"{spread_name} should have 'name' field"
            assert "layout" in spread, f"{spread_name} should have 'layout' field"

    def test_load_spread_with_semantics(self):
        """Test loading spread with semantic configuration."""
        spread = BundledDataLoader.load_spread("celtic")
        assert spread is not None, "Should load celtic spread"
        assert "semantics" in spread, "Spread should have 'semantics' field"
        assert isinstance(spread["semantics"], list), "Semantics should be a list"

    def test_load_simple_spread(self):
        """Test loading minimal spread configuration."""
        spread = BundledDataLoader.load_spread("single")
        assert spread is not None, "Should load single spread"
        assert spread["layout"] == [[1]], "Single spread should have [[1]] layout"

    def test_list_decks(self):
        """Test listing all bundled decks."""
        decks = BundledDataLoader.list_decks()
        assert isinstance(decks, list), "Should return a list"
        assert "rider-waite" in decks, "Should include rider-waite deck"

    def test_list_spreads(self):
        """Test listing all bundled spreads."""
        spreads = BundledDataLoader.list_spreads()
        assert isinstance(spreads, list), "Should return a list"
        expected_count = 7
        assert len(spreads) == expected_count, f"Should have {expected_count} spreads"

    def test_list_no_json_extension(self):
        """Verify listed names don't include .json extension."""
        spreads = BundledDataLoader.list_spreads()
        for spread_name in spreads:
            assert not spread_name.endswith(".json"), f"Spread name '{spread_name}' should not end with .json"

    def test_export_deck(self):
        """Test exporting deck as JSON string."""
        deck_json = BundledDataLoader.export_deck("rider-waite")
        assert deck_json is not None, "Should export rider-waite deck"
        parsed = json.loads(deck_json)
        assert "name" in parsed, "Exported JSON should have 'name' field"
        assert parsed["name"] == "Rider-Waite", "Deck name should be Rider-Waite"

    def test_export_spread(self):
        """Test exporting spread as JSON string."""
        spread_json = BundledDataLoader.export_spread("celtic")
        assert spread_json is not None, "Should export celtic spread"
        parsed = json.loads(spread_json)
        assert "name" in parsed, "Exported JSON should have 'name' field"
        assert parsed["name"] == "celtic", "Spread name should be celtic"

    @patch('importlib.resources.files')
    def test_load_deck_nonexistent(self, mock_files):
        """Test loading non-existent deck returns None."""
        mock_files.return_value.joinpath.return_value.open.side_effect = FileNotFoundError()
        deck = BundledDataLoader.load_deck("nonexistent-deck")
        assert deck is None, "Should return None for non-existent deck"

    @patch('importlib.resources.files')
    def test_load_spread_nonexistent(self, mock_files):
        """Test loading non-existent spread returns None."""
        mock_files.return_value.joinpath.return_value.open.side_effect = FileNotFoundError()
        spread = BundledDataLoader.load_spread("nonexistent-spread")
        assert spread is None, "Should return None for non-existent spread"

    @patch('importlib.resources.files')
    def test_export_deck_nonexistent(self, mock_files):
        """Test exporting non-existent deck returns None."""
        mock_files.return_value.joinpath.return_value.open.side_effect = FileNotFoundError()
        deck_json = BundledDataLoader.export_deck("nonexistent-deck")
        assert deck_json is None, "Should return None for non-existent deck"

    @patch('importlib.resources.files')
    def test_export_spread_nonexistent(self, mock_files):
        """Test exporting non-existent spread returns None."""
        mock_files.return_value.joinpath.return_value.open.side_effect = FileNotFoundError()
        spread_json = BundledDataLoader.export_spread("nonexistent-spread")
        assert spread_json is None, "Should return None for non-existent spread"

    def test_deck_structure_valid(self):
        """Validate deck data structure is correct."""
        deck = BundledDataLoader.load_deck("rider-waite")
        assert deck is not None, "Should load rider-waite deck"
        assert "cards" in deck, "Deck should have cards"
        cards = deck["cards"]
        assert isinstance(cards, list), "Cards should be a list"
        assert len(cards) > 0, "Should have at least one card"
        card = cards[0]
        assert "name" in card, "Card should have name"
        assert "card_type" in card, "Card should have card_type"

    def test_spread_structure_valid(self):
        """Validate spread data structure is correct."""
        spread = BundledDataLoader.load_spread("3-card")
        assert spread is not None, "Should load 3-card spread"
        assert "layout" in spread, "Spread should have layout"
        layout = spread["layout"]
        assert isinstance(layout, list), "Layout should be a list"
        assert isinstance(layout[0], list), "Layout row should be a list"
        assert isinstance(layout[0][0], int), "Layout cell should be an integer"

    def test_export_format_indented(self):
        """Verify exported JSON is properly indented."""
        deck_json = BundledDataLoader.export_deck("rider-waite")
        assert deck_json is not None, "Should export deck"
        assert "  " in deck_json, "JSON should be indented with 2 spaces"
        parsed = json.loads(deck_json)
        assert isinstance(parsed, dict), "Exported data should parse as dict"


if __name__ == "__main__":
    unittest.main()
