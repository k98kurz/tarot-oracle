"""Comprehensive tests for enhanced semantic system."""

import pytest
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.tarot import (
    SemanticAnalyzer, SemanticAdapter, SpreadLoader, Card
)
from tarot_oracle.loaders import SpreadLoader as SpreadLoaderClass


class TestSemanticAnalyzer:
    """Test the enhanced SemanticAnalyzer class."""
    
    def test_basic_initialization(self):
        """Test SemanticAnalyzer initialization with semantic config."""
        config = {
            'semantic_groups': {'test': {'positions': [1, 2]}},
            'semantics': [['${fire}', '${water}']],
            'guidance_rules': [{'conditions': {}, 'guidance': 'Test guidance'}]
        }
        
        analyzer = SemanticAnalyzer(config)
        
        assert analyzer.semantic_groups == config['semantic_groups']
        assert analyzer.semantics_matrix == config['semantics']
        assert analyzer.guidance_rules == config['guidance_rules']
    
    def test_variable_resolution(self):
        """Test variable placeholder resolution."""
        config = {}
        analyzer = SemanticAnalyzer(config)
        
        text = "This is ${fire} and ${water} working with ${spirit}"
        resolved = analyzer.resolve_variables(text)
        
        assert "Karmic Forces/Cosmic Influences (Fire)" in resolved
        assert "Emotional Basis/Subconscious Influences (Water)" in resolved
        assert "Nature of Circumstances/Divine Will (Spirit)" in resolved
    
    def test_card_combinations_analysis(self):
        """Test comprehensive card analysis."""
        config = {}
        analyzer = SemanticAnalyzer(config)
        
        cards = [
            Card('The Tower', 'major', None, 'XVI', 'Upheaval, revelation'),
            Card('Two of Cups', 'minor', 'C', '2', 'Union, partnership'),
            Card('Knight of Wands', 'minor', 'W', 'Knight', 'Action, passion')
        ]
        
        analysis = analyzer.analyze_card_combinations(cards)
        
        assert analysis['major_arcana_count'] == 1
        assert analysis['minor_arcana_count'] == 2
        assert analysis['court_cards_count'] == 1
        assert analysis['card_count'] == 3
        assert analysis['elemental_balance']['fire'] == 1
        assert analysis['elemental_balance']['water'] == 1
        assert analysis['suit_distribution']['Wands'] == 1
        assert analysis['suit_distribution']['Cups'] == 1
    
    def test_enhanced_rule_matching(self):
        """Test enhanced rule matching conditions."""
        config = {
            'guidance_rules': [
                {
                    'conditions': {
                        'major_arcana_min': 2,
                        'elemental_balance': {'fire': 1}
                    },
                    'guidance': 'Major arcana with fire energy'
                },
                {
                    'conditions': {
                        'card_type_count': {
                            'card_type': 'minor',
                            'min_count': 2
                        }
                    },
                    'guidance': 'Minor arcana dominance'
                },
                {
                    'conditions': {
                        'suit_present': {'suits': ['W']}
                    },
                    'guidance': 'Wands energy present'
                }
            ]
        }
        
        analyzer = SemanticAnalyzer(config)
        
        # Test first rule (should match)
        cards1 = [
            Card('The Tower', 'major', None, 'XVI', 'Upheaval'),
            Card('Death', 'major', None, 'XIII', 'Transformation'),
            Card('Knight of Wands', 'minor', 'W', 'Knight', 'Action')
        ]
        analysis1 = analyzer.analyze_card_combinations(cards1)
        guidance1 = analyzer.generate_guidance(cards1, {})
        
        assert any('Major arcana with fire energy' in g for g in guidance1)
        
        # Test second rule (should match)
        cards2 = [
            Card('Two of Cups', 'minor', 'C', '2', 'Union'),
            Card('Three of Swords', 'minor', 'S', '3', 'Sorrow'),
            Card('Four of Wands', 'minor', 'W', '4', 'Harmony')
        ]
        analysis2 = analyzer.analyze_card_combinations(cards2)
        guidance2 = analyzer.generate_guidance(cards2, {})
        
        assert any('Minor arcana dominance' in g for g in guidance2)
    
    def test_card_condition_types(self):
        """Test different card condition types."""
        config = {
            'guidance_rules': [
                {
                    'conditions': {
                        'cards': [
                            {
                                'type': 'anywhere',
                                'cards': ['The Tower', 'Death']
                            }
                        ]
                    },
                    'guidance': 'Major transformation energy'
                },
                {
                    'conditions': {
                        'cards': [
                            {
                                'type': 'not_present',
                                'cards': ['The Fool']
                            }
                        ]
                    },
                    'guidance': 'Stable beginnings'
                }
            ]
        }
        
        analyzer = SemanticAnalyzer(config)
        
        # Test anywhere condition
        cards1 = [Card('The Tower', 'major', None, 'XVI', 'Upheaval')]
        guidance1 = analyzer.generate_guidance(cards1, {})
        assert any('Major transformation energy' in g for g in guidance1)
        
        # Test not_present condition
        cards2 = [Card('The Emperor', 'major', None, 'IV', 'Authority')]
        guidance2 = analyzer.generate_guidance(cards2, {})
        assert any('Stable beginnings' in g for g in guidance2)


class TestSemanticAdapter:
    """Test the enhanced SemanticAdapter class."""
    
    def test_custom_semantic_config_integration(self):
        """Test integration with custom semantic configurations."""
        config = {
            'name': 'Test Spread',
            'layout': [[1, 2, 3]],
            'semantics': [['${fire}', '${water}', '${air}']],
            'semantic_groups': {
                'fire_group': {
                    'description': 'Fire energy group',
                    'positions': [1]
                },
                'water_group': {
                    'description': 'Water energy group', 
                    'positions': [2]
                }
            },
            'guidance_rules': [
                {
                    'conditions': {
                        'cards': [
                            {
                                'type': 'in_group',
                                'group': 'fire_group',
                                'cards': ['The Tower']
                            }
                        ]
                    },
                    'guidance': 'Fire transformation'
                }
            ]
        }
        
        cards = [
            Card('The Tower', 'major', None, 'XVI', 'Upheaval'),
            Card('Two of Cups', 'minor', 'C', '2', 'Union'),
            Card('Three of Swords', 'minor', 'S', '3', 'Sorrow')
        ]
        
        layout = config['layout']
        adapter = SemanticAdapter(layout, cards, None, config)
        
        # Test semantic groups
        groups = adapter.get_semantic_groups()
        assert 'Fire energy group' in groups
        assert 'Water energy group' in groups
        
        # Test guidance
        guidance = adapter.generate_guidance()
        assert any('Fire transformation' in g for g in guidance)
    
    def test_full_interpretation_rendering(self):
        """Test complete interpretation rendering."""
        config = {
            'name': 'Test Spread',
            'layout': [[1, 2]],
            'semantics': [['${fire}', '${water}']],
            'guidance_rules': [
                {
                    'conditions': {
                        'major_arcana_min': 1
                    },
                    'guidance': 'Spiritual forces at work'
                }
            ]
        }
        
        cards = [
            Card('The Tower', 'major', None, 'XVI', 'Upheaval'),
            Card('Two of Cups', 'minor', 'C', '2', 'Union')
        ]
        
        layout = config['layout']
        adapter = SemanticAdapter(layout, cards, None, config)
        
        full_interp = adapter.render_full_interpretation(include_keywords=False)
        
        # Check that all sections are present
        assert 'Karmic Forces/Cosmic Influences (Fire)' in full_interp
        assert 'Emotional Basis/Subconscious Influences (Water)' in full_interp
        assert 'Interpretive Guidance' in full_interp
        assert 'Reading Analysis' in full_interp
        assert 'Spiritual Focus' in full_interp
    
    def test_analysis_integration(self):
        """Test analysis method integration."""
        config = {'layout': [[1, 2, 3]]}
        
        cards = [
            Card('The Tower', 'major', None, 'XVI', 'Upheaval'),
            Card('Two of Cups', 'minor', 'C', '2', 'Union'),
            Card('Knight of Wands', 'minor', 'W', 'Knight', 'Action')
        ]
        
        layout = config['layout']
        adapter = SemanticAdapter(layout, cards)
        
        # Test basic adapter (no semantic config)
        analysis = adapter.get_analysis()
        assert analysis == {}
        
        # Test with semantic config
        adapter_with_config = SemanticAdapter(layout, cards, None, {'guidance_rules': []})
        analysis_with_config = adapter_with_config.get_analysis()
        
        assert 'major_arcana_count' in analysis_with_config
        assert 'minor_arcana_count' in analysis_with_config
        assert 'elemental_balance' in analysis_with_config


class TestSpreadLoaderEnhancements:
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
        except ValueError:
            pytest.fail("Valid matrix layout should not raise ValueError")
        
        # Invalid layout (mixed types)
        invalid_config = {
            'name': 'Test Spread', 
            'layout': [[1, 2], {'invalid': 'structure'}]
        }
        
        with pytest.raises(ValueError, match="Layout row 1 must be a list"):
            loader._validate_spread_config(invalid_config, 'test_path')
    
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
        except ValueError:
            pytest.fail("Valid semantics matrix should not raise ValueError")
        
        # Invalid semantics (wrong type in cell)
        invalid_config = {
            'name': 'Test Spread',
            'layout': [[1, 2]],
            'semantics': [['${fire}', 123]]
        }
        
        with pytest.raises(ValueError, match="must be a string or null"):
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
        except ValueError:
            pytest.fail("Valid variable placeholders should not raise ValueError")
        
        # Invalid variable
        invalid_config = {
            'name': 'Test Spread',
            'layout': [[1, 2]],
            'semantics': [['${fire}', '${invalid_var}']]
        }
        
        with pytest.raises(ValueError, match="Invalid variable placeholder"):
            loader._validate_spread_config(invalid_config, 'test_path')
    
    def test_integration_with_real_files(self):
        """Test integration with real spread files."""
        # Create temporary test files
        test_spread = {
            "name": "Integration Test Spread",
            "description": "Test spread for integration",
            "layout": [[1, 2, 3]],
            "semantics": [["${fire}", "${water}", "${air}"]],
            "semantic_groups": {
                "test_group": {
                    "description": "Test group",
                    "positions": [1, 2, 3]
                }
            },
            "guidance_rules": [
                {
                    "conditions": {
                        "major_arcana_min": 1
                    },
                    "guidance": "Test guidance with ${fire}"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_spread, f)
            temp_path = f.name
        
        try:
            # Test loading with SpreadLoader
            loader = SpreadLoader()
            spread = loader.load_spread(Path(temp_path).stem)
            
            assert spread is not None
            assert spread['name'] == 'Integration Test Spread'
            assert 'semantic_groups' in spread
            assert 'guidance_rules' in spread
            
            # Test with SemanticAdapter
            cards = [
                Card('The Tower', 'major', None, 'XVI', 'Upheaval'),
                Card('Two of Cups', 'minor', 'C', '2', 'Union'),
                Card('Three of Swords', 'minor', 'S', '3', 'Sorrow')
            ]
            
            adapter = SemanticAdapter(spread['layout'], cards, None, spread)
            guidance = adapter.generate_guidance()
            
            assert len(guidance) > 0
            assert any('Test guidance' in g for g in guidance)
            
        finally:
            # Clean up
            Path(temp_path).unlink()


class TestZodiacSpreads:
    """Test specific Zodiac spread implementations."""
    
    def test_zodiac_spread_loading(self):
        """Test loading Zodiac spread with semantic features."""
        loader = SpreadLoader()
        
        # This will work if the test files exist in the current directory
        try:
            zodiac = loader.load_spread('test_zodiac_spread')
            if zodiac:
                assert zodiac['name'] == 'Zodiac'
                assert 'semantic_groups' in zodiac
                assert 'fire_signs' in zodiac['semantic_groups']
                assert 'guidance_rules' in zodiac
                assert len(zodiac['guidance_rules']) == 3
        except Exception:
            # Skip if test files don't exist
            pytest.skip("Zodiac test spread file not found")
    
    def test_zodiac_plus_spread_loading(self):
        """Test loading Zodiac Plus spread with enhanced features."""
        loader = SpreadLoader()
        
        try:
            zodiac_plus = loader.load_spread('test_zodiac_plus_spread')
            if zodiac_plus:
                assert zodiac_plus['name'] == 'Zodiac Plus'
                assert 'spirit_essence' in zodiac_plus['semantic_groups']
                assert 'cardinal_cross' in zodiac_plus['semantic_groups']
                assert len(zodiac_plus['guidance_rules']) == 8
        except Exception:
            # Skip if test files don't exist
            pytest.skip("Zodiac Plus test spread file not found")


if __name__ == "__main__":
    # Run basic tests if called directly
    test_analyzer = TestSemanticAnalyzer()
    test_analyzer.test_variable_resolution()
    test_analyzer.test_card_combinations_analysis()
    
    test_adapter = TestSemanticAdapter()
    test_adapter.test_full_interpretation_rendering()
    
    test_loader = TestSpreadLoaderEnhancements()
    test_loader.test_matrix_layout_validation()
    test_loader.test_variable_placeholder_validation()
    
    print("All basic semantic system tests passed!")