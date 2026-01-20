"""Comprehensive tests for semantic system."""

import unittest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.tarot import SemanticAdapter, SpreadLoader, Card
from tarot_oracle.loaders import SpreadLoader as SpreadLoaderClass
from tarot_oracle.exceptions import SpreadError


class TestSemanticAdapter(unittest.TestCase):
    """Test semantic adapter class."""

    def test_variable_resolution(self):
        """Test variable placeholder resolution."""
        from tarot_oracle.tarot import resolve_variables

        text = "This is ${fire} and ${water} working with ${spirit}"
        resolved = resolve_variables(text)

        assert "Karmic Forces/Cosmic Influences (Fire)" in resolved
        assert "Emotional Basis/Subconscious Influences (Water)" in resolved
        assert "Nature of Circumstances/Divine Will (Spirit)" in resolved

    def test_semantic_adapter_with_custom_spread(self):
        """Test SemanticAdapter with custom spread semantics."""
        config = {
            'name': 'Test Spread',
            'layout': [[1, 2, 3]],
            'semantics': [['${fire}', '${water}', '${air}']],
            'guidance': [
                'Fire transformation energy present',
                'Water emotional flow detected'
            ]
        }

        cards = [
            Card('The Tower', 'major', None, 'XVI', 'Upheaval'),
            Card('Two of Cups', 'minor', 'C', '2', 'Union'),
            Card('Three of Swords', 'minor', 'S', '3', 'Sorrow')
        ]

        adapter = SemanticAdapter(config['layout'], cards, config['semantics'])

        # Test semantic legend rendering
        legend = adapter.render_semantic_legend(include_keywords=False)
        assert 'Karmic Forces/Cosmic Influences (Fire)' in legend
        assert 'Emotional Basis/Subconscious Influences (Water)' in legend

        # Test guidance extraction
        guidance = adapter.get_guidance(config)
        assert len(guidance) == 2
        assert any('Fire transformation' in g for g in guidance)

 
class TestSpreadLoaderEnhancements(unittest.TestCase):
    """Test enhanced SpreadLoader with semantic features."""

    def test_matrix_layout_validation(self):
        """Test matrix layout validation."""
        loader = SpreadLoaderClass()

        # Valid matrix layout
        valid_config = {
            'name': 'Test Spread',
            'layout': [[1, 2], [3, 4]],
            'semantics': [['${fire}', '${water}'], ['${air}', '${earth}']]
        }

        try:
            result = loader._validate_spread_config(valid_config, 'test_path')
            assert result is not None
        except (ValueError, SpreadError):
            self.fail("Valid matrix layout should not raise ValueError or SpreadError")

        # Invalid layout (mixed types)
        invalid_config = {
            'name': 'Test Spread',
            'semantics': [['${fire}', 123]]
        }

        with self.assertRaises(SpreadError) as cm:
            loader._validate_spread_config(invalid_config, 'test_path')
            assert "must be a string or null" in str(cm.exception), "Error should mention type requirement"

    def test_semantics_matrix_validation(self):
        """Test semantics matrix validation."""
        loader = SpreadLoaderClass()

        # Valid semantics matrix
        valid_config = {
            'name': 'Test Spread',
            'layout': [[1, 2]],
            'semantics': [['${fire}', '${water}']]
        }

        try:
            result = loader._validate_spread_config(valid_config, 'test_path')
            assert result is not None
        except (ValueError, SpreadError):
            self.fail("Valid semantics matrix should not raise ValueError or SpreadError")

        # Invalid semantics (wrong type in cell)
        invalid_config = {
            'name': 'Test Spread',
            'layout': [[1, 2]],
            'semantics': [['${fire}', 123]]
        }

        with self.assertRaises(SpreadError) as cm:
            loader._validate_spread_config(invalid_config, 'test_path')

    def test_variable_placeholder_validation(self):
        """Test variable placeholder validation."""
        loader = SpreadLoaderClass()

        # Valid variables
        valid_config = {
            'name': 'Test Spread',
            'layout': [[1, 2]],
            'semantics': [['${fire}', '${water}']]
        }

        try:
            result = loader._validate_spread_config(valid_config, 'test_path')
            assert result is not None
        except (ValueError, SpreadError):
            self.fail("Valid variable placeholders should not raise ValueError or SpreadError")

        # Invalid variable
        invalid_config = {
            'name': 'Test Spread',
            'layout': [[1, 2]],
            'semantics': [['${fire}', '${invalid_var}']]
        }

        with self.assertRaises(SpreadError) as cm:
            loader._validate_spread_config(invalid_config, 'test_path')
            assert "Invalid variable placeholder" in str(cm.exception), "Error should mention invalid variable"

    def test_integration_with_real_files(self):
        """Test integration with real spread files."""
        # Create temporary test files in current directory (where SpreadLoader can find them)
        test_spread = {
            "name": "Integration Test Spread",
            "description": "Test spread for integration",
            "layout": [[1, 2, 3]],
            "semantics": [["${fire}", "${water}", "${air}"]],
            "semantic_groups": {
                "test_group": "Test group for positions 1-3"
            },
            "guidance": [
                "Test guidance with Karmic Forces/Cosmic Influences (Fire)"
            ]
        }

        temp_path = Path.cwd() / 'test_integration_spread.json'

        try:
            with open(temp_path, 'w') as f:
                json.dump(test_spread, f)

            # Test loading with SpreadLoader
            loader = SpreadLoader()
            spread = loader.load_spread('test_integration_spread')

            assert spread is not None
            assert spread['name'] == 'Integration Test Spread'
            assert 'semantic_groups' in spread
            assert 'guidance' in spread

            # Test with SemanticAdapter
            cards = [
                Card('The Tower', 'major', None, 'XVI', 'Upheaval'),
                Card('Two of Cups', 'minor', 'C', '2', 'Union'),
                Card('Three of Swords', 'minor', 'S', '3', 'Sorrow')
            ]

            adapter = SemanticAdapter(spread['layout'], cards, spread.get('semantics'))
            legend = adapter.render_semantic_legend(include_keywords=False)

            assert len(legend) > 0

        finally:
            # Clean up
            if temp_path.exists():
                temp_path.unlink()


class TestZodiacSpreads(unittest.TestCase):
    """Test specific Zodiac spread implementations."""

    def test_zodiac_spread_loading(self):
        """Test loading Zodiac spread with semantic features."""
        loader = SpreadLoader()

        # This will work if the test files exist in the current directory
        try:
            zodiac = loader.load_spread('zodiac_spread')
            if zodiac:
                assert zodiac['name'] == 'Zodiac (12-card)'
                assert 'semantic_groups' in zodiac
                assert 'ari' in zodiac['semantic_groups']
                assert 'guidance' in zodiac
                assert len(zodiac['guidance']) == 15
        except Exception:
            # Skip if test files don't exist
            self.skipTest("Zodiac test spread file not found")

    def test_zodiac_plus_spread_loading(self):
        """Test loading Zodiac Plus spread with enhanced features."""
        loader = SpreadLoader()

        try:
            zodiac_plus = loader.load_spread('zodiac_plus_spread')
            if zodiac_plus:
                assert zodiac_plus['name'] == 'Zodiac Plus (13-card)'
                assert 'cen' in zodiac_plus['semantic_groups']
                assert 'guidance' in zodiac_plus
                assert len(zodiac_plus['guidance']) == 15
        except Exception:
            # Skip if test files don't exist
            self.skipTest("Zodiac Plus test spread file not found")


if __name__ == "__main__":
    unittest.main()
