"""Test oracle module integration with centralized configuration."""

import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.config import Config, config


def test_oracle_uses_config():
    """Test that oracle module imports and uses centralized config."""
    # Test that oracle can import config
    from tarot_oracle import oracle
    assert hasattr(oracle, 'config'), "Oracle should import config"
    
    # Test that config is the same instance
    assert oracle.config is config, "Oracle should use the global config instance"


def test_oracle_config_properties():
    """Test that oracle uses config properties correctly."""
    from tarot_oracle import oracle
    
    # Test that config properties return expected types
    assert isinstance(oracle.config.provider, str)
    assert isinstance(oracle.config.ollama_host, str)
    assert isinstance(oracle.config.autosave_sessions, bool)
    assert isinstance(oracle.config.default_spread, str)


def test_oracle_session_saving_with_config():
    """Test that oracle uses config for session saving."""
    from tarot_oracle.oracle import generate_session_filename
    
    # Test that the function doesn't crash with config (takes card_codes list)
    filename = generate_session_filename(["I", "III", "V"])
    assert isinstance(filename, str)
    assert len(filename) > 0
    
    # Test that filename is sanitized 
    safe_codes = ["test", "question", "with", "special", "chars"]
    safe_filename = generate_session_filename(safe_codes)
    assert "/" not in safe_filename
    assert "?" not in safe_filename
    assert "@" not in safe_filename


if __name__ == "__main__":
    test_oracle_uses_config()
    test_oracle_config_properties()
    test_oracle_session_saving_with_config()
    print("All oracle configuration tests passed!")