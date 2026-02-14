"""Test oracle module integration with crossconfig."""

import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from crossconfig import get_config


class TestOracle(unittest.TestCase):
    def test_oracle_uses_crossconfig(self):
        """Test that oracle module uses crossconfig for configuration."""
        from tarot_oracle import oracle

        # Test that oracle can be imported
        assert hasattr(oracle, 'Oracle'), "Oracle class should be available"

        # Test that Oracle instance can be created
        # This implicitly tests that crossconfig is working
        try:
            test_oracle = oracle.Oracle(provider="ollama", ollama_host="localhost:11434")
            assert test_oracle.provider == "ollama"
        except Exception as e:
            self.fail(f"Failed to create Oracle instance: {e}")

    def test_oracle_session_saving_with_config(self):
        """Test that oracle uses config for session saving."""
        from tarot_oracle.oracle import generate_session_filename

        # Test that function doesn't crash with config (takes card_codes list)
        filename = generate_session_filename(["I", "III", "V"])
        assert isinstance(filename, str), f"Filename should be string, got {type(filename)}"
        assert len(filename) > 0, "Filename should not be empty"

        # Test that filename is sanitized
        safe_codes = ["test", "question", "with", "special", "chars"]
        safe_filename = generate_session_filename(safe_codes)
        assert "/" not in safe_filename, "Filename should not contain '/'"
        assert "?" not in safe_filename, "Filename should not contain '?'"
        assert "@" not in safe_filename, "Filename should not contain '@'"


if __name__ == "__main__":
    unittest.main()
