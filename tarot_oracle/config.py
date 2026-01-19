"""Centralized configuration management for Tarot Oracle."""

import json
import os
from pathlib import Path
from typing import Any
from tarot_oracle.exceptions import ConfigError


class Config:
    """Centralized configuration for Tarot Oracle."""

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
                raise ConfigError(f"Unexpected error loading configuration: {e}", config_path=str(self.config_file))

    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            "ORACLE_PROVIDER": "provider",
            "GOOGLE_AI_API_KEY": "google_ai_api_key",
            "OPENROUTER_API_KEY": "openrouter_api_key",
            "OLLAMA_HOST": "ollama_host",
            "AUTOSAVE_SESSIONS": "autosave_sessions",
            "AUTOSAVE_LOCATION": "autosave_location",
        }

        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string boolean to actual boolean
                if config_key == "autosave_sessions":
                    self.config[config_key] = value.lower() in ("true", "1", "yes")
                else:
                    self.config[config_key] = value

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
                raise ConfigError(f"Unexpected error creating directory {directory}: {e}", config_path=str(self.config_file))

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
            raise ConfigError(f"Error saving config file: {e}", config_path=str(self.config_file))
        except Exception as e:
            raise ConfigError(f"Unexpected error saving configuration: {e}", config_path=str(self.config_file))

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
