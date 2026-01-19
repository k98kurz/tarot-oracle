"""Test configuration management for Tarot Oracle."""

import unittest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.config import Config


class TestConfig(unittest.TestCase):
    def test_config_initialization(self):
        """Test that Config initializes with proper defaults."""
        config = Config()

        assert config.provider == "gemini", f"Expected 'gemini', got {config.provider}"
        assert config.ollama_host == "localhost:11434", f"Expected 'localhost:11434', got {config.ollama_host}"
        assert config.autosave_sessions is True, f"Expected True, got {config.autosave_sessions}"
        assert config.default_spread == "celtic_cross", f"Expected 'celtic_cross', got {config.default_spread}"
        assert config.max_file_size == 1024 * 1024, f"Expected {1024 * 1024}, got {config.max_file_size}"

    def test_config_directory_structure(self):
        """Test that required directories are created."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {'HOME': temp_dir}):
                config = Config()

                # Check that directories were created
                assert config.home_dir.exists(), "Home directory should exist"
                assert config.decks_dir.exists(), "Decks directory should exist"
                assert config.invocations_dir.exists(), "Invocations directory should exist"
                assert config.spreads_dir.exists(), "Spreads directory should exist"

    def test_config_file_loading(self):
        """Test that config.json file is loaded properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {'HOME': temp_dir}):
                # Create config file
                config_dir = Path(temp_dir) / ".tarot-oracle"
                config_dir.mkdir()
                config_file = config_dir / "config.json"

                test_config = {
                    "provider": "ollama",
                    "ollama_host": "custom-host:11434",
                    "default_spread": "three_card"
                }

                with open(config_file, 'w') as f:
                    json.dump(test_config, f)

                config = Config()

                assert config.provider == "ollama", f"Expected 'ollama', got {config.provider}"
                assert config.ollama_host == "custom-host:11434", f"Expected 'custom-host:11434', got {config.ollama_host}"
                assert config.default_spread == "three_card", f"Expected 'three_card', got {config.default_spread}"

    def test_environment_variable_override(self):
        """Test that environment variables override config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {
                'HOME': temp_dir,
                'ORACLE_PROVIDER': 'openrouter',
                'OLLAMA_HOST': 'env-host:11434'
            }):
                config = Config()

                assert config.provider == "openrouter", f"Expected 'openrouter', got {config.provider}"
                assert config.ollama_host == "env-host:11434", f"Expected 'env-host:11434', got {config.ollama_host}"

    def test_config_save(self):
        """Test that configuration can be saved."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {'HOME': temp_dir}):
                config = Config()
                config.set('test_key', 'test_value')
                config.save()

                # Load new instance to verify persistence
                config2 = Config()
                assert config2.get('test_key') == 'test_value', "Test key should persist after save"


if __name__ == "__main__":
    unittest.main()
