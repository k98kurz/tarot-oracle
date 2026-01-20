"""Centralized configuration management for Tarot Oracle.

This module provides comprehensive configuration management with support for
environment variables, configuration files, and runtime updates. It manages
all aspects of the tarot oracle system including AI providers,
file paths, and user preferences.

The configuration system follows this precedence order:
1. Default values (hardcoded)
2. Configuration file (~/.tarot-oracle/config.json)
3. Environment variables
4. Runtime modifications

Configuration Options:
    - provider: AI provider to use ('gemini', 'openrouter', 'ollama')
    - google_ai_api_key: API key for Google Gemini provider
    - openrouter_api_key: API key for OpenRouter provider  
    - ollama_host: Host address for Ollama server (default: 'localhost:11434')
    - autosave_sessions: Whether to automatically save sessions (default: True)
    - autosave_location: Directory path for session saving (default: '~/oracles')
    - default_spread: Default spread type for readings (default: 'celtic_cross')
    - max_file_size: Maximum file size for custom configurations (default: 1MB)

Environment Variables:
    - ORACLE_PROVIDER: Override AI provider selection
    - GOOGLE_AI_API_KEY: Google Gemini API key
    - OPENROUTER_API_KEY: OpenRouter API key
    - OLLAMA_HOST: Ollama server host address
    - TAROT_ORACLE_AUTOSAVE: Enable/disable session autosaving ('true'/'false')
    - TARO_ORACLE_AUTOSAVE_LOCATION: Override session save directory

Example:
    >>> from tarot_oracle.config import config
    >>> print(config.provider)  # Get current provider
    >>> config.set("provider", "openrouter")  # Set new provider
    >>> config.save()  # Persist changes
    >>> 
    >>> # Environment variable usage
    >>> # In shell: export ORACLE_PROVIDER=openrouter
    >>> # In Python: config.provider will use environment value
"""

import json
import os
from pathlib import Path
from typing import Any
# Custom exceptions removed - using standard TypeError and ValueError instead


class Config:
    """Centralized configuration for Tarot Oracle.
    
    Manages all configuration aspects including AI provider settings,
    file paths, user preferences, and security parameters.
    Provides both property-based and dictionary-style access.
    
    Attributes:
        home_dir (Path): Main configuration directory (~/.tarot-oracle)
        config_file (Path): Path to config.json file
        decks_dir (Path): Directory for custom deck configurations
        invocations_dir (Path): Directory for custom invocation files
        spreads_dir (Path): Directory for custom spread configurations
        
    Configuration Options:
        - provider: AI provider to use (gemini, openrouter, ollama)
        - google_ai_api_key: API key for Google Gemini
        - openrouter_api_key: API key for OpenRouter
        - ollama_host: Host address for Ollama server
        - autosave_sessions: Whether to automatically save sessions
        - autosave_location: Directory path for session saving
        - default_spread: Default spread type for readings
        - max_file_size: Maximum file size for custom configurations
        
    Example:
        >>> config = Config()
        >>> provider = config.provider
        >>> api_key = config.google_ai_api_key
        >>> config.set("provider", "openrouter")
        >>> config.save()
    """

    def __init__(self) -> None:
        """Initialize configuration with defaults and load from file/environment."""
        self.home_dir = Path.home() / ".tarot-oracle"
        self.config_file = self.home_dir / "config.json"
        self.decks_dir = self.home_dir / "decks"
        self.invocations_dir = self.home_dir / "invocations"
        self.spreads_dir = self.home_dir / "spreads"

        # Default configuration
        self.config: dict[str, Any] = {
            "provider": "gemini",
            "google_ai_api_key": None,
            "openrouter_api_key": None,
            "ollama_host": "localhost:11434",
            "autosave_sessions": True,
            "autosave_location": str(Path.home() / "oracles"),
            "default_spread": "celtic_cross",
            "max_file_size": 1024 * 1024,  # 1MB
        }

        # Load configuration
        self._load_config()
        self._load_env_vars()
        self._ensure_directories()

    def _load_config(self) -> None:
        """Load configuration from config.json file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                self.config.update(file_config)
            except (json.JSONDecodeError, OSError) as e:
                # Log error but continue with defaults
                print(f"Warning: Could not load config file: {e}")
            except Exception as e:
                raise ValueError(f"Unexpected error loading configuration: {e} (config_path: {self.config_file})")

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        self.config["provider"] = os.getenv("ORACLE_PROVIDER", self.config.get("provider", None))
        self.config["google_ai_api_key"] = os.getenv("GOOGLE_AI_API_KEY", self.config.get("google_ai_api_key", None))
        self.config["openrouter_api_key"] = os.getenv("OPENROUTER_API_KEY", self.config.get("openrouter_api_key", None))
        self.config["ollama_host"] = os.getenv("OLLAMA_HOST", self.config.get("ollama_host", None))
        self.config["autosave_location"] = os.getenv("TARO_ORACLE_AUTOSAVE_LOCATION", self.config.get("autosave_location", None))
        autosave_sessions = os.getenv("TAROT_ORACLE_AUTOSAVE")
        if autosave_sessions is not None:
            self.config["autosave_sessions"] = autosave_sessions.lower() in ["true", "1", "yes"]

    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.home_dir,
            self.decks_dir,
            self.invocations_dir,
            self.spreads_dir,
        ]

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"Error creating directory {directory}: {e}")
            except Exception as e:
                raise ValueError(f"Unexpected error creating directory {directory}: {e} (config_path: {self.config_file})")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except OSError as e:
            raise ValueError(f"Error saving config file: {e} (config_path: {self.config_file})")
        except Exception as e:
            raise ValueError(f"Unexpected error saving configuration: {e} (config_path: {self.config_file})")

    @property
    def provider(self) -> str:
        """Get the AI provider."""
        result = self.get("provider", "gemini")
        return str(result) if result is not None else "gemini"

    @property
    def google_ai_api_key(self) -> str | None:
        """Get the Google AI API key."""
        result = self.get("google_ai_api_key")
        return result if result is not None else None

    @property
    def openrouter_api_key(self) -> str | None:
        """Get the OpenRouter API key."""
        result = self.get("openrouter_api_key")
        return result if result is not None else None

    @property
    def ollama_host(self) -> str:
        """Get the Ollama host."""
        result = self.get("ollama_host", "localhost:11434")
        return str(result) if result is not None else "localhost:11434"

    @property
    def autosave_sessions(self) -> bool:
        """Get whether to autosave sessions."""
        result = self.get("autosave_sessions", True)
        return bool(result) if result is not None else True

    @property
    def autosave_location(self) -> str:
        """Get the autosave location."""
        result = self.get("autosave_location", str(Path.home() / "oracles"))
        return str(result) if result is not None else str(Path.home() / "oracles")

    @property
    def default_spread(self) -> str:
        """Get the default spread."""
        result = self.get("default_spread", "celtic_cross")
        return str(result) if result is not None else "celtic_cross"

    @property
    def max_file_size(self) -> int:
        """Get the maximum file size."""
        result = self.get("max_file_size", 1024 * 1024)
        return int(result) if result is not None else 1024 * 1024


# Global configuration instance
config = Config()
