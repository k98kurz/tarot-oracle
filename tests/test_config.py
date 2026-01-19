"""Test configuration management for Tarot Oracle."""

import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.config import Config


def test_config_initialization():
    """Test that Config initializes with proper defaults."""
    config = Config()
    
    assert config.provider == "gemini"
    assert config.ollama_host == "localhost:11434"
    assert config.autosave_sessions is True
    assert config.default_spread == "celtic_cross"
    assert config.max_file_size == 1024 * 1024


def test_config_directory_structure():
    """Test that required directories are created."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {'HOME': temp_dir}):
            config = Config()
            
            # Check that directories were created
            assert config.home_dir.exists()
            assert config.decks_dir.exists()
            assert config.invocations_dir.exists()
            assert config.spreads_dir.exists()


def test_config_file_loading():
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
            
            assert config.provider == "ollama"
            assert config.ollama_host == "custom-host:11434"
            assert config.default_spread == "three_card"


def test_environment_variable_override():
    """Test that environment variables override config file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {
            'HOME': temp_dir,
            'ORACLE_PROVIDER': 'openrouter',
            'OLLAMA_HOST': 'env-host:11434'
        }):
            config = Config()
            
            assert config.provider == "openrouter"
            assert config.ollama_host == "env-host:11434"


def test_config_save():
    """Test that configuration can be saved."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch.dict(os.environ, {'HOME': temp_dir}):
            config = Config()
            config.set('test_key', 'test_value')
            config.save()
            
            # Load new instance to verify persistence
            config2 = Config()
            assert config2.get('test_key') == 'test_value'


if __name__ == "__main__":
    test_config_initialization()
    test_config_directory_structure()
    test_config_file_loading()
    test_environment_variable_override()
    test_config_save()
    print("All configuration tests passed!")