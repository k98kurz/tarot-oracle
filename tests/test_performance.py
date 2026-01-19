"""Performance benchmarks for Tarot Oracle components."""

import pytest
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.config import Config
from tarot_oracle.tarot import DeckLoader, Deck, SemanticAdapter
from tarot_oracle.loaders import SpreadLoader, InvocationLoader
from tarot_oracle.oracle import OpenRouterClient


class TestConfigPerformance:
    """Test configuration system performance."""
    
    def test_config_initialization_performance(self, benchmark):
        """Benchmark config initialization."""
        result = benchmark(Config)
        assert result.provider == "gemini"
    
    def test_config_loading_performance(self, benchmark):
        """Benchmark config loading operations."""
        config = Config()
        
        def load_operations():
            config.get('provider')
            config.get('default_spread')
            config.get('autosave_sessions')
        
        benchmark(load_operations)


class TestDeckPerformance:
    """Test deck loading and manipulation performance."""
    
    def test_deck_loading_performance(self, benchmark):
        """Benchmark deck loading."""
        def load_deck():
            loader = DeckLoader()
            return loader.load_deck('rider-waite-smith')
        
        deck = benchmark(load_deck)
        assert len(deck.cards) > 0
    
    def test_deck_shuffling_performance(self, benchmark):
        """Benchmark deck shuffling."""
        loader = DeckLoader()
        deck = loader.load_deck('rider-waite-smith')
        
        def shuffle_deck():
            deck.shuffle()
        
        benchmark(shuffle_deck)
    
    def test_card_drawing_performance(self, benchmark):
        """Benchmark card drawing operations."""
        loader = DeckLoader()
        deck = loader.load_deck('rider-waite-smith')
        deck.shuffle()
        
        def draw_cards():
            deck.draw_card(5)
            deck.reset()
            deck.shuffle()
        
        benchmark(draw_cards)


class TestSemanticAnalysisPerformance:
    """Test semantic analysis performance."""
    
    def test_semantic_adapter_performance(self, benchmark):
        """Benchmark semantic adapter operations."""
        from tarot_oracle.tarot import Card
        
        cards = [
            Card('The Tower', 'major', None, 'XVI', 'Upheaval'),
            Card('Two of Cups', 'minor', 'C', '2', 'Union'),
            Card('Three of Swords', 'minor', 'S', '3', 'Sorrow')
        ]
        
        config = {
            'name': 'Test Spread',
            'layout': [[1, 2, 3]],
            'semantics': [['${fire}', '${water}', '${air}']]
        }
        
        def semantic_analysis():
            adapter = SemanticAdapter([[1, 2, 3]], cards, None, config)
            return adapter.get_semantic_groups()
        
        result = benchmark(semantic_analysis)
        assert isinstance(result, list)
    
    def test_guidance_generation_performance(self, benchmark):
        """Benchmark guidance generation."""
        from tarot_oracle.tarot import Card
        
        cards = [
            Card('The Tower', 'major', None, 'XVI', 'Upheaval'),
            Card('Two of Cups', 'minor', 'C', '2', 'Union'),
            Card('Three of Swords', 'minor', 'S', '3', 'Sorrow')
        ]
        
        config = {
            'name': 'Test Spread',
            'layout': [[1, 2, 3]],
            'semantics': [['${fire}', '${water}', '${air}']],
            'guidance_rules': [
                {
                    'conditions': {
                        'major_arcana_min': 1
                    },
                    'guidance': 'Spiritual forces at work'
                }
            ]
        }
        
        def generate_guidance():
            adapter = SemanticAdapter([[1, 2, 3]], cards, None, config)
            return adapter.generate_guidance()
        
        result = benchmark(generate_guidance)
        assert isinstance(result, list)


class TestLoaderPerformance:
    """Test loader performance."""
    
    def test_spread_loading_performance(self, benchmark):
        """Benchmark spread loading."""
        def load_spreads():
            loader = SpreadLoader()
            return loader.list_spreads()
        
        result = benchmark(load_spreads)
        assert isinstance(result, list)
    
    def test_invocation_loading_performance(self, benchmark):
        """Benchmark invocation loading."""
        def load_invocations():
            loader = InvocationLoader()
            return loader.list_invocations()
        
        result = benchmark(load_invocations)
        assert isinstance(result, list)


class TestOpenRouterPerformance:
    """Test OpenRouter client performance."""
    
    def test_client_initialization_performance(self, benchmark):
        """Benchmark OpenRouter client initialization."""
        def create_client():
            return OpenRouterClient(api_key="test-key", model="z-ai/glm-4.5-air:free")
        
        client = benchmark(create_client)
        assert client.api_key == "test-key"
        assert client.model == "z-ai/glm-4.5-air:free"
    
    def test_request_preparation_performance(self, benchmark):
        """Benchmark request preparation overhead."""
        client = OpenRouterClient(api_key="test-key")
        
        def prepare_request():
            # Simulate request preparation
            headers = {
                "Authorization": f"Bearer {client.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/tarot-oracle/tarot-oracle",
                "X-Title": "Tarot Oracle"
            }
            payload = {
                "model": client.model,
                "messages": [{"role": "user", "content": "Test prompt"}],
                "max_tokens": 2048,
                "temperature": 0.7
            }
            return headers, payload
        
        headers, payload = benchmark(prepare_request)
        assert "Authorization" in headers
        assert "model" in payload


class TestMemoryUsage:
    """Test memory usage patterns."""
    
    def test_multiple_deck_instances_memory(self):
        """Test memory usage with multiple deck instances."""
        loader = DeckLoader()
        decks = []
        
        # Create multiple deck instances
        for _ in range(10):
            deck = loader.load_deck('rider-waite-smith')
            decks.append(deck)
        
        # Verify all decks have cards
        for deck in decks:
            assert len(deck.cards) > 0
        
        # Clean up
        del decks
    
    def test_large_config_handling(self):
        """Test handling of large configuration objects."""
        config = Config()
        
        # Add many configuration items
        for i in range(1000):
            config.set(f'test_key_{i}', f'test_value_{i}')
        
        # Verify retrieval
        for i in range(1000):
            value = config.get(f'test_key_{i}')
            assert value == f'test_value_{i}'


if __name__ == "__main__":
    # Run basic performance tests without pytest-benchmark
    config_perf = TestConfigPerformance()
    
    print("Running basic performance tests...")
    
    # Test config initialization
    start = time.time()
    for _ in range(100):
        config_perf.test_config_initialization_performance(lambda x: x())
    config_time = time.time() - start
    print(f"Config initialization (100 iterations): {config_time:.3f}s")
    
    # Test deck loading
    deck_perf = TestDeckPerformance()
    start = time.time()
    for _ in range(10):
        deck_perf.test_deck_loading_performance(lambda x: x())
    deck_time = time.time() - start
    print(f"Deck loading (10 iterations): {deck_time:.3f}s")
    
    print("Basic performance tests completed.")