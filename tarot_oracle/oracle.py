#!/usr/bin/env python3

"""Oracle system for AI-powered tarot divination readings.

Combines traditional tarot with LLM interpretation via Gemini,
OpenRouter, or Ollama. Supports custom invocations, spreads, session
saving, and both CLI and programmatic interfaces."""

from argparse import ArgumentParser
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from sys import stderr
from typing import Any, cast
from tarot_oracle.data_loader import BundledDataLoader
from tarot_oracle.helpers import config, ensure_config_directories, lstrip_lines
from tarot_oracle.loaders import InvocationLoader
from tarot_oracle.tarot import Card, SpreadRenderer, TarotDivination

try:
    from google import genai
except ImportError:
    genai = None

import json
import os
import re
import requests
import sys


ORACLE_CONFIG_KEYS = {
    "provider",
    "google_ai_api_key",
    "openrouter_api_key",
    "ollama_host",
    "autosave_sessions",
    "autosave_location",
    "gemini_model",
    "openrouter_model",
    "ollama_model",
    "interpret"
}

ORACLE_CONFIG_DEFAULTS = {
    "provider": "ollama",
    "google_ai_api_key": None,
    "openrouter_api_key": None,
    "ollama_host": "localhost:11434",
    "autosave_sessions": "true",
    "autosave_location": "~/oracles",
    "gemini_model": "gemini-3-flash",
    "openrouter_model": "openrouter/free",
    "ollama_model": "qwen3:0.6b",
    "interpret": "false"
}


class InvocationManager:
    """Manages invocations for divinatory readings. Loads and provides
        ceremonial opening texts for tarot readings. Supports built-in
        and custom user-defined invocations.
    """

    def __init__(self) -> None:
        """Initialize the invocation manager with loader."""
        self.loader = InvocationLoader()

    @staticmethod
    def get_default_invocation() -> str:
        """Returns the default invocation from bundled data. Loads
            Hermes-Thoth and Prometheus dual invocation combining wisdom
            and foresight for ceremonial readings.
        """
        bundled = BundledDataLoader.load_invocation("default-hermes-thoth-prometheus")
        if bundled:
            return bundled
        raise ValueError("Default invocation not found in bundled data")

    def get_invocation(self, name: str | None) -> str:
        """Get invocation by name or return default. Loads custom
            invocations from files via InvocationLoader. Falls back to
            default bundled invocation if custom invocation not found.
        """
        if name:
            try:
                custom_invocation = self.loader.load_invocation(name)
                if custom_invocation:
                    return custom_invocation
            except Exception as e:
                raise ValueError(f"Failed to load invocation '{name}': {e}")
        return self.get_default_invocation()

    @staticmethod
    def prepend_invocation(question: str, invocation_type: str = "default") -> str:
        """Combine invocation with question for ceremonial LLM prompt.
            Used for interpretation requests to frame the reading
            ceremonially.
        """
        if invocation_type == "default":
            invocation = InvocationManager.get_default_invocation()
            return f"{invocation}\n\nQuestion: {question}"
        else:
            return question


class GeminiClient:
    """Client for Google Gemini API integration. Requires google-genai
        package and API key. Generates tarot interpretations via Gemini
        models. Raises ImportError if google-genai package is not
        installed.
    """

    def __init__(self, api_key: str, model: str = ORACLE_CONFIG_DEFAULTS["gemini_model"]):
        """Initialize Gemini client with API key and model. Raises
            ImportError if google-genai package is not installed.
        """
        if genai is None:
            raise ImportError(
                "google-genai package not installed. Install with: pip install"
                " google-genai"
            )
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_response(
            self, prompt: str, model: str | None = None, timeout: int = 30
        ) -> str | None:
        """Send prompt to Gemini model and return generated text.
            Returns None on API errors or if response is empty.
        """
        try:
            response = self.client.models.generate_content(
                model=model or self.model,
                contents=prompt
            )
            text = response.text
            return text.strip() if text else None
        except Exception as e:
            print(f"Error generating response from Gemini: {e}", file=sys.stderr)
            return None

    def check_api_key(self) -> bool:
        """Verify API key is valid and service is accessible. Returns
            True if API key is valid, False otherwise.
        """
        try:
            test_response = self.client.models.generate_content(
                model=self.model,
                contents="Hello, please respond with 'API key is valid' to "
                "confirm the connection."
            )
            return True
        except Exception as e:
            print(f"Error validating API key: {e}", file=sys.stderr)
            return False


class OpenRouterClient:
    """Client for OpenRouter API marketplace integration. Uses
        OpenAI-compatible API for multiple models through unified
        interface. Supports configurable base URL and model selection.
    """

    def __init__(
            self, api_key: str,
            model: str = ORACLE_CONFIG_DEFAULTS["openrouter_model"]
        ):
        """Initialize OpenRouter client with API key and model."""
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"

    def generate_response(
            self, prompt: str, model: str | None = None, timeout: int = 30
        ) -> str | None:
        """Call OpenRouter chat completions endpoint with prompt. Raises
            ValueError on API errors (401 for invalid key, 429 for rate
            limit, network/timeout issues).
        """
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/k98kurz/tarot-oracle",
            "X-Title": "Tarot Oracle"
        }

        payload = {
            "model": model or self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.7
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return content.strip() if content else None
                else:
                    raise ValueError("Invalid response format from OpenRouter")
            elif response.status_code == 401:
                raise ValueError("Invalid OpenRouter API key")
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                raise ValueError(
                    f"OpenRouter API rate limit exceeded. Retry after: {retry_after}"
                )
            else:
                raise ValueError(
                    f"OpenRouter API returned status {response.status_code}: "
                    f"{response.text}"
                )

        except requests.exceptions.Timeout:
            raise ValueError(f"OpenRouter API request timed out after {timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"OpenRouter API request failed: {e}")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Unexpected error calling OpenRouter API: {e}")

    def check_api_key(self) -> bool:
        """Verify API key is valid and OpenRouter service is accessible.
            Returns True if key is valid, False otherwise with error
            printed to stderr.
        """
        try:
            # Simple test request with minimal content
            test_prompt = "Hello, please respond with 'API key is valid' to " \
                "confirm the connection."
            response = self.generate_response(test_prompt, timeout=10)
            return response is not None and "API key is valid" in response.lower()
        except Exception as e:
            print(f"Error validating OpenRouter API key: {e}", file=sys.stderr)
            return False

    def list_models(self) -> list[dict[str, Any]]:
        """List all available models from OpenRouter. Returns list of
            model dictionaries with id, name, pricing, and context_length.
            Raises ValueError on API errors.
        """
        url = f"{self.base_url}/models"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/k98kurz/tarot-oracle",
            "X-Title": "Tarot Oracle"
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get("data", [])
            elif response.status_code == 401:
                raise ValueError("Invalid OpenRouter API key")
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                raise ValueError(
                    f"OpenRouter API rate limit exceeded. Retry after: {retry_after}"
                )
            else:
                raise ValueError(
                    f"OpenRouter API returned status {response.status_code}: "
                    f"{response.text}"
                )

        except requests.exceptions.Timeout:
            raise ValueError(f"OpenRouter API request timed out")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"OpenRouter API request failed: {e}")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Unexpected error listing OpenRouter models: {e}")


class OllamaClient:
    """Client for local Ollama AI server integration. Connects to
        locally-hosted models for private readings. Default host:
        localhost:11434.
    """

    def __init__(self, host: str = ORACLE_CONFIG_DEFAULTS["ollama_host"]):
        """Initialize Ollama client with server host."""
        self.host = host

    def generate_response(
            self, prompt: str, model: str = ORACLE_CONFIG_DEFAULTS["ollama_model"],
            timeout: int = 300
        ) -> str | None:
        """Call Ollama generate endpoint with prompt. Returns stripped
            response text or None on error.
        """
        url = f"http://{self.host}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(url, json=payload, timeout=timeout)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return None
        except Exception:
            return None

    def check_model_available(self, model: str) -> bool:
        """Query Ollama server for installed models. Returns True if
            model is available (exact or versioned match).
        """
        url = f"http://{self.host}/api/tags"

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                result = response.json()
                models = [m["name"] for m in result.get("models", [])]
                return model in models or any(model.split(":")[0] in m for m in models)
            else:
                return False
        except Exception:
            return False

    def list_models(self) -> list[dict[str, Any]]:
        """List all available models from Ollama server. Returns list of
            model dictionaries with name, size, and modified date. Raises
            ValueError on connection errors.
        """
        url = f"http://{self.host}/api/tags"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result.get("models", [])
            else:
                raise ValueError(f"Ollama API returned status {response.status_code}")
        except requests.exceptions.Timeout:
            raise ValueError(f"Ollama API request timed out")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Ollama API request failed: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error listing Ollama models: {e}")


def extract_card_codes_for_filename(legend_display: str) -> list[str]:
    """Parse legend display for bracketed card codes. Converts ↓/↑ to
        'R' for reversed cards. Returns sanitized codes list.
    """
    # Find all bracketed card codes
    matches = re.findall(r'\[([^\]]+)\]', legend_display)
    # Replace arrow symbols with R for reversed cards and strip whitespace
    codes = [code.replace('↓', 'R').replace('↑', 'R').strip() for code in matches]
    return codes


def generate_session_filename(card_codes: list[str]) -> str:
    """Create timestamped filename with card codes for session saving.
        Format: YYYY-MM-DD-HHMMSS-codes.md
    """
    import re
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    # Sanitize card codes to prevent injection
    safe_codes = [re.sub(r'[^a-zA-Z0-9]', '', code) for code in card_codes if code]
    codes_str = "-".join(safe_codes) if safe_codes else "no-codes"
    return f"{timestamp}-{codes_str}.md"


def ensure_autosave_directory(save_location: str) -> bool:
    """Create autosave directory if it doesn't exist. Returns True on
        success, False with warning to stderr on failure.
    """
    try:
        os.makedirs(save_location, exist_ok=True)
        return True
    except Exception as e:
        print(
            f"Warning: Could not create save directory {save_location}: {e}",
            file=sys.stderr
        )
        return False


def save_oracle_session(
        question: str, spread_type: str, result: dict[str, Any],
        save_location: str
    ) -> bool:
    """Save reading session to markdown file with full reading details.
        Mirrors terminal output including invocation, cards, legend, and
        interpretation. Returns True on success, False with warning on
        failure.
    """
    if not ensure_autosave_directory(save_location):
        return False

    try:
        # Extract card codes from legend display
        card_codes = extract_card_codes_for_filename(result['legend_display'])
        filename = generate_session_filename(card_codes)
        filepath = os.path.join(save_location, filename)

        # Validate filepath is safe
        save_path = Path(save_location).resolve()
        full_path = Path(filepath).resolve()
        if not full_path.is_relative_to(save_path):
            raise ValueError(f"Invalid file path: {filepath}")

        # Build content by mirroring the exact print statements
        content = []

        # Mirror print_invocation()
        content.append("# === Invocation ===")
        invocation_text = InvocationManager.get_default_invocation()
        content.append(invocation_text)
        content.append("")

        # Mirror print_cards()
        content.append("# === Tarot Reading ===")
        content.append("")
        content.append(f"**Question**: {question}")
        content.append(f"**Spread**: {spread_type}")
        content.append("")
        content.append(result['spread_display'])
        content.append("")
        content.append(result['legend_display'])
        content.append("")

        # Mirror print_interpretation() if requested
        if result.get('interpretation_requested'):
            provider = result.get('provider_used', 'unknown')
            model = result.get('model_used', 'unknown')
            content.append(f"# === Interpretation ({provider} | {model}) ===")
            if result.get('interpretation'):
                content.append(result['interpretation'])
            else:
                content.append("Interpretation was not available.")

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        return True
    except Exception as e:
        print(f"Warning: Failed to save oracle session: {e}", file=sys.stderr)
        return False


class Oracle:
    """Main oracle class combining tarot readings with LLM
        interpretation. Supports Gemini, OpenRouter, and Ollama
        providers. Manages invocations and session persistence. Raises
        ValueError for missing credentials, ImportError for missing
        packages.
    """

    def __init__(
            self, provider: str | None = None, model: str | None = None,
            api_key: str | None = None, ollama_host: str | None = None
        ):
        """Initialize Oracle with provider and configuration.
            Validates API keys for cloud providers. Raises ValueError
            if required credentials missing.
        """
        self.tarot = TarotDivination()
        self.invocation_manager = InvocationManager()

        conf = config()

        # Provider selection
        self.provider = provider or conf.get(
            "provider",
            os.getenv("ORACLE_PROVIDER", ORACLE_CONFIG_DEFAULTS["provider"])
        )

        if self.provider == "gemini":
            api_key = api_key or conf.get(
                "google_ai_api_key", os.getenv("GOOGLE_AI_API_KEY")
            )
            if not api_key:
                raise ValueError(
                    "GOOGLE_AI_API_KEY environment variable must be set for "
                    "Gemini provider"
                )
            if genai is None:
                raise ImportError(
                    "google-genai package not installed. Install with: pip "
                    "install google-genai"
                )
            model_to_use = model or conf.get(
                "gemini_model", ORACLE_CONFIG_DEFAULTS["gemini_model"]
            )
            self.client = GeminiClient(str(api_key), model_to_use)
            self.default_model = model_to_use

        elif self.provider == "openrouter":
            api_key = api_key or conf.get(
                "openrouter_api_key", os.getenv("OPENROUTER_API_KEY")
            )
            if not api_key:
                raise ValueError(
                    "OPENROUTER_API_KEY environment variable must be set for "
                    "OpenRouter provider"
                )
            model_to_use = model or conf.get(
                "openrouter_model", ORACLE_CONFIG_DEFAULTS["openrouter_model"]
            )
            self.client = OpenRouterClient(str(api_key), model_to_use)
            self.default_model = model_to_use

        elif self.provider == "ollama":
            host = ollama_host or conf.get(
                "ollama_host",
                os.getenv("OLLAMA_HOST", ORACLE_CONFIG_DEFAULTS["ollama_host"])
            )
            self.client = OllamaClient(str(host))
            model_to_use = model or conf.get(
                "ollama_model", ORACLE_CONFIG_DEFAULTS["ollama_model"]
            )
            self.default_model = model_to_use
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def get_client(self) -> GeminiClient | OpenRouterClient | OllamaClient:
        """Get the current provider client instance."""
        return self.client

    def get_default_model(self) -> str:
        """Get the default model identifier for the current provider."""
        return self.default_model

    def build_interpretation_prompt(
            self, spread_display: str, legend_display: str, invocation: str,
            question: str, spread_type: str
        ) -> str:
        """Construct structured prompt for LLM interpretation.
            Includes invocation, question, spread info, and detailed
            interpretation instructions.
        """

        prompt = lstrip_lines(f"""# Role: Oracle
        You are an intuitive tarot reader channeling ancient wisdom
        and divine insight to provide an oracular service.

        ## Invocation
        {invocation}

        ## Question
        {question}

        ## Spread Type
        {spread_type}

        ## Cards Drawn by Position
        {legend_display}

        ## Directions
        Provide an intuitive interpretation covering:
        1. Overall reading narrative and theme
        2. Individual card meanings in their specific positions
        3. How the positional meanings influence the interpretation
        4. Practical guidance and actionable insight
        5. Potential outcomes and paths forward
        6. How the cards weave together to answer the question

        Pay special attention to the positional meanings and how they
        affect each card's interpretation. Speak with wisdom, clarity,
        and compassion. Blend traditional symbolism with intuitive
        insight. Be thorough but concise enough to be useful for
        practical guidance. For large spreads of more than 5 cards,
        lean toward concise summary rather than exhaustive card-by-card analyses.
        """)

        return prompt

    def get_interpretation(self, spread_display: str, legend_display: str, invocation: str, question: str, model: str | None = None, spread_type: str = "unknown") -> str | None:
        """Generate AI interpretation via configured provider.

        Returns None on errors or if interpretation is unavailable."""
        if model is None:
            model = self.default_model

        timeout = 30 if self.provider in ["gemini", "openrouter"] else 300

        try:
            prompt = self.build_interpretation_prompt(spread_display, legend_display, invocation, question, spread_type)
            response = self.client.generate_response(prompt, model, timeout)
            return response
        except Exception as e:
            # For debugging - we can remove this later
            print(f"DEBUG: Error getting interpretation: {e}", file=sys.stderr)
            return None

    def perform_divinatory_reading(
            self, question: str, spread_type: str = "3-card",
            interpret: bool = False, model: str | None = None, **kwargs
        ) -> dict[str, Any]:
        """Perform complete reading with optional interpretation.
            Returns dict with spread_display, legend_display,
            interpretation (if requested), provider_used,
            interpretation_requested/available flags, question, and spread_type.
        """
        # Get invocation text (always used for oracle)
        # Custom invocation can be passed via kwargs as either text or name
        custom_invocation = kwargs.get('invocation')
        invocation_name = kwargs.get('invocation_name')

        if invocation_name:
            invocation = self.invocation_manager.get_invocation(invocation_name)
        elif custom_invocation:
            invocation = custom_invocation
        else:
            invocation = self.invocation_manager.get_default_invocation()

        # Use direct method calls instead of JSON
        spread_display, legend_display = self.tarot.perform_reading(
            question=question,
            spread_input=spread_type,
            invocation=invocation,
            random_bytes=kwargs.get('random_bytes', 8),
            allow_reversed=kwargs.get('allow_reversed', False),
            show_descriptions=kwargs.get('show_descriptions', True)
        )

        # Get interpretation if requested
        interpretation = None
        if interpret:
            interpretation = self.get_interpretation(
                spread_display, legend_display, invocation, question,
                model, spread_type
            )

        return {
            "spread_display": spread_display,
            "legend_display": legend_display,
            "interpretation": interpretation,
            "provider_used": self.provider,
            "model_used": model or self.default_model,
            "interpretation_requested": interpret,
            "interpretation_available": interpretation is not None,
            "question": question,
            "spread_type": spread_type
        }


def create_oracle_parser() -> ArgumentParser:
    """Configure CLI argument parser for oracle. Includes provider
        selection, spread options, interpretation settings, and
        session management.
    """
    parser = ArgumentParser(description="Divinatory oracle with LLM interpretation")

    # Core question and spread
    parser.add_argument(
        "question", nargs='?',
        help="Question for the oracle (not required for config commands)"
    )
    parser.add_argument(
        "--spread", default="3-card",
        help=f"Spread layout (default: 3-card). Available: "
        f"{BundledDataLoader.list_spreads()} or custom matrix"
    )

    # Oracle-specific features
    parser.add_argument(
        "--provider", choices=["gemini", "openrouter", "ollama"],
        default=ORACLE_CONFIG_DEFAULTS["provider"],
        help="LLM provider (default: ollama)"
    )
    parser.add_argument(
        "--invocation",
        help="Custom invocation text (uses default invocation if not provided)"
    )
    interpret_group = parser.add_mutually_exclusive_group()
    interpret_group.add_argument(
        "--interpret", action="store_true", dest="interpret",
        help="Generate LLM interpretation of reading (overrides config)"
    )
    interpret_group.add_argument(
        "--no-interpret", action="store_false", dest="interpret",
        help="Do not generate LLM interpretation (overrides config)"
    )
    interpret_group.set_defaults(interpret=None)
    parser.add_argument("--model", help="Model name (provider-specific)")

    # Provider-specific options
    parser.add_argument("--api-key", help="API key (for gemini or openrouter provider)")
    parser.add_argument("--ollama-host", help="Ollama host (for ollama provider)")
    parser.add_argument(
        "--timeout", type=int,
        help="Timeout in seconds (default: 30 gemini, 300 ollama)"
    )

    # Session saving options
    save_group = parser.add_mutually_exclusive_group()
    save_group.add_argument(
        "--save", action="store_true",
        help="Force save this session (overrides environment settings)"
    )
    save_group.add_argument(
        "--no-save", action="store_true",
        help="Do not save this session (overrides environment settings)"
    )
    parser.add_argument(
        "--save-path", help="Override default save location for this session"
    )

    # Tarot options (re-using existing logic)
    parser.add_argument(
        "--random", type=int, default=8,
        help="Add N random bytes to RNG seed for entropy (default: 8)"
    )
    parser.add_argument(
        "--reversed", action="store_true",
        help="Allow cards to appear reversed"
    )

    # Configuration management
    parser.add_argument(
        "--config", action="store_true", help="Display current configuration"
    )
    parser.add_argument(
        "--list-models", action="store_true",
        help="List available models for the specified provider"
    )
    parser.add_argument(
        "--set-config", nargs=2, metavar=("KEY", "VALUE"),
        help="Set configuration key=value and save"
    )
    parser.add_argument(
        "--unset-config", metavar="KEY", help="Remove configuration key and save"
    )

    return parser


def print_invocation(invocation_text: str) -> None:
    """Print the ceremonial invocation with header."""
    print("# === Invocation ===")
    print(invocation_text)
    print()


def print_cards(
        spread_display: str, legend_display: str, question: str,
        spread_type: str
    ) -> None:
    """Print tarot reading with question, spread type, layout, and card legend."""
    print("# === Tarot Reading ===")

    print(f"Question: {question}")
    print(f"Spread: {spread_type}\n")
    print(spread_display)
    print("\n" + legend_display)
    print()


def print_interpretation(interpretation: str | None, provider: str, model: str) -> None:
    """Print AI interpretation or fallback message if unavailable."""
    print(f"# === Interpretation ({provider} | {model}) ===")
    if interpretation:
        print(interpretation)
    else:
        print("Interpretation was not available.")


def handle_config_commands(
        show_config: bool, set_config: list[str] | None, unset_config: str | None
    ) -> int:
    """Handle configuration management commands. Returns 0 on success, 1 on error."""
    conf = config()

    if show_config:
        print("Oracle Configuration:")
        for key in sorted(ORACLE_CONFIG_KEYS):
            value = conf.get(key)
            default = ORACLE_CONFIG_DEFAULTS.get(key)

            if value is None:
                if default is None:
                    provider_name = key.split("_")[0] if "_api_key" in key else None
                    if provider_name:
                        print(f"  {key}: (not set - required when using {provider_name})")
                    else:
                        print(f"  {key}: (not set)")
                else:
                    print(f"  {key}: (default: {default})")
            else:
                print(f"  {key}: {value}")
        return 0

    if set_config:
        key, value = set_config[0], set_config[1]
        if key not in ORACLE_CONFIG_KEYS:
            print(
                f"Error: Invalid configuration key '{key}'. Valid keys: "
                f"{', '.join(sorted(ORACLE_CONFIG_KEYS))}"
            )
            return 1

        if key == "provider":
            valid_providers = ["gemini", "openrouter", "ollama"]
            if value not in valid_providers:
                print(
                    f"Error: Invalid provider '{value}'. Valid providers: "
                    f"{', '.join(valid_providers)}"
                )
                return 1

        if key == "autosave_sessions" or key == "interpret":
            lower_value = value.lower()
            if lower_value in ("true", "1", "yes"):
                conf.set(key, True)
            elif lower_value in ("false", "0", "no"):
                conf.set(key, False)
            else:
                print(
                    f"Error: Invalid value '{value}' for '{key}'. Use: true, "
                    "false, 1, 0, yes, no"
                )
                return 1
        else:
            conf.set(key, value)

        conf.save()
        print(f"Configuration set: {key} = {value}")
        return 0

    if unset_config:
        if unset_config not in ORACLE_CONFIG_KEYS:
            print(
                f"Error: Invalid configuration key '{unset_config}'. Valid keys: "
                f"{', '.join(sorted(ORACLE_CONFIG_KEYS))}"
            )
            return 1

        conf.unset(unset_config)
        conf.save()
        print(f"Configuration unset: {unset_config}")
        return 0

    return 0


def handle_list_models(oracle: "Oracle", provider: str) -> int:
    """Handle listing available models for the specified provider.
        Returns 0 on success, 1 on error.
    """
    client = oracle.get_client()

    try:
        models = []

        if provider == "openrouter":
            if isinstance(client, OpenRouterClient):
                models = client.list_models()
            else:
                print(
                    "Error: OPENROUTER_API_KEY must be set to list models",
                    file=sys.stderr
                )
                return 1
        elif provider == "ollama":
            if isinstance(client, OllamaClient):
                models = client.list_models()
            else:
                print(
                    f"Error: Could not get Ollama client for provider {provider}",
                    file=sys.stderr
                )
                return 1
        else:
            print(f"Error: Unknown provider {provider}", file=sys.stderr)
            return 1

        print(f"Available Models for {provider}:")
        print("")

        if provider == "openrouter":
            max_id_len = len("ID")
            max_name_len = len("Name")
            max_price_len = len("Price/1M Tokens")

            for model in models:
                model_id = model.get("id", "unknown")
                model_name = model.get("name", "unknown")
                pricing = model.get("pricing", {})
                prompt_price = pricing.get("prompt", 0)
                completion_price = pricing.get("completion", 0)
                try:
                    if prompt_price == "-1" or completion_price == "-1":
                        price_str = "Variable"
                    elif not prompt_price or not completion_price:
                        price_str = "N/A"
                    else:
                        prompt_decimal = Decimal(str(prompt_price)) * Decimal('1000000')
                        completion_decimal = Decimal(str(completion_price)) * \
                            Decimal('1000000')
                        price_str = f"${prompt_decimal:.2f} / ${completion_decimal:.2f}"
                except (ValueError, TypeError):
                    price_str = "N/A"
                max_id_len = max(max_id_len, len(model_id))
                max_name_len = max(max_name_len, len(model_name))
                max_price_len = max(max_price_len, len(price_str))

            id_width = max_id_len
            name_width = max_name_len
            price_width = max_price_len

            print(
                f"{'ID':<{id_width}} | {'Name':<{name_width}} | "
                f"{'Price/1M Tokens':<{price_width}}"
            )
            print("-" * (id_width + 3 + name_width + 3 + price_width))

            for model in models:
                model_id = model.get("id", "unknown")
                model_name = model.get("name", "unknown")
                pricing = model.get("pricing", {})
                prompt_price = pricing.get("prompt", 0)
                completion_price = pricing.get("completion", 0)
                try:
                    if prompt_price == "-1" or completion_price == "-1":
                        price_str = "Variable"
                    elif not prompt_price or not completion_price:
                        price_str = "N/A"
                    else:
                        prompt_decimal = Decimal(str(prompt_price)) * Decimal('1000000')
                        completion_decimal = Decimal(str(completion_price)) * \
                            Decimal('1000000')
                        price_str = f"${prompt_decimal:.2f} / ${completion_decimal:.2f}"
                except (ValueError, TypeError):
                    price_str = "N/A"
                print(
                    f"{model_id:<{id_width}} | {model_name:<{name_width}} | "
                    f"{price_str:<{price_width}}"
                )
        elif provider == "ollama":
            max_name_len = len("Model Name")
            max_size_len = len("Size")
            max_modified_len = len("Modified")

            for model in models:
                model_name = model.get("name", "unknown")
                model_size = model.get("details", {}).get("parameter_size", "N/A")
                model_modified = model.get("modified_at", "N/A")
                if isinstance(model_size, (int, float)):
                    size_str = f"{model_size / (1024**3):.1f} GB"
                else:
                    size_str = str(model_size)
                max_name_len = max(max_name_len, len(model_name))
                max_size_len = max(max_size_len, len(size_str))
                max_modified_len = max(max_modified_len, len(model_modified))

            name_width = max_name_len
            size_width = max_size_len
            modified_width = max_modified_len

            print(
                f"{'Model Name':<{name_width}} | {'Size':<{size_width}} | "
                f"{'Modified':<{modified_width}}"
            )
            print("-" * (name_width + 3 + size_width + 3 + modified_width))

            for model in models:
                model_name = model.get("name", "unknown")
                model_size = model.get("details", {}).get("parameter_size", "N/A")
                model_modified = model.get("modified_at", "N/A")
                if isinstance(model_size, (int, float)):
                    size_str = f"{model_size / (1024**3):.1f} GB"
                else:
                    size_str = str(model_size)
                print(
                    f"{model_name:<{name_width}} | {size_str:<{size_width}} | "
                    f"{model_modified:<{modified_width}}"
                )

        print("")
        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def main(args=None) -> int:
    """Oracle CLI entry point. Parses arguments, runs reading,
        displays results, optionally saves session. Returns exit code 
        0 for success, non-zero for error).
    """
    parser = create_oracle_parser()

    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    ensure_config_directories()

    # Handle configuration management commands
    if args.config or args.set_config or args.unset_config:
        return handle_config_commands(args.config, args.set_config, args.unset_config)

    # Handle --list-models flag
    if args.list_models:
        if args.provider == "gemini":
            print(
                "Error: Model listing not available for Gemini provider",
                file=sys.stderr
            )
            return 1
        oracle = Oracle(
            provider=args.provider,
            model=args.model,
            api_key=args.api_key,
            ollama_host=args.ollama_host
        )
        return handle_list_models(oracle, args.provider)

    # Validate that question is provided for reading mode
    if not args.question:
        print(
            "Error: Question is required for oracle reading. Use --config to "
            "manage configuration."
        )
        return 1

    # Create oracle instance with provider-specific options
    oracle = Oracle(
        provider=args.provider,
        model=args.model,
        api_key=args.api_key,
        ollama_host=args.ollama_host
    )

    # Resolve interpret value: flag override > config > default
    conf = config()
    interpret_config = conf.get(
        "interpret",
        os.getenv("TAROT_ORACLE_INTERPRET", ORACLE_CONFIG_DEFAULTS["interpret"])
    )
    interpret = interpret_config if isinstance(interpret_config, bool) \
        else str(interpret_config).lower() in ["true", "1", "yes"]
    if args.interpret is not None:
        interpret = args.interpret

    # Check availability if interpretation requested
    if interpret:
        if args.provider == "openrouter":
            client = oracle.get_client()
            # We know this is OpenRouterClient when provider is "openrouter"
            if hasattr(client, 'check_api_key'):
                # Type assertion: we know this method exists due to hasattr check
                openrouter_client = cast(OpenRouterClient, client)
                api_key_valid = openrouter_client.check_api_key()
                if not api_key_valid:
                    print(
                        f"Warning: OpenRouter API key validation failed. "
                        "Interpretation may not be available."
                    )
        elif args.provider == "ollama":
            client = oracle.get_client()
            # We know this is OllamaClient when provider is "ollama"
            if hasattr(client, 'check_model_available'):
                # Type assertion: we know this method exists due to hasattr check
                ollama_client = cast(OllamaClient, client)
                model = args.model or ORACLE_CONFIG_DEFAULTS["ollama_model"]
                model_available = ollama_client.check_model_available(model)
                if not model_available:
                    print(
                        f"Warning: Model '{model}' not found in Ollama. "
                        "Interpretation may not be available."
                    )

    # Perform the reading
    result = oracle.perform_divinatory_reading(
        question=args.question,
        spread_type=args.spread,
        interpret=interpret,
        model=args.model,
        timeout=args.timeout,
        invocation=args.invocation,  # Pass invocation (None or custom)
        random_bytes=args.random,
        allow_reversed=args.reversed
    )

    # Handle errors
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1

    # Display results in the requested order
    invocation_text = InvocationManager.get_default_invocation()
    print_invocation(invocation_text)
    print_cards(
        result["spread_display"], result["legend_display"], result["question"],
        result["spread_type"]
    )

    if result["interpretation_requested"]:
        print_interpretation(
            result["interpretation"], result["provider_used"], result["model_used"]
        )

    # Determine save behavior
    conf = config()
    autosave = conf.get(
        "autosave_sessions",
        os.getenv("TAROT_ORACLE_AUTOSAVE", ORACLE_CONFIG_DEFAULTS["autosave_sessions"])
    )
    should_save = autosave if isinstance(autosave, bool) else \
        str(autosave).lower() in ["true", "1", "yes"]
    save_location = conf.get(
        "autosave_location",
        os.getenv(
            "TAROT_ORACLE_AUTOSAVE_LOCATION",
            os.path.expanduser(ORACLE_CONFIG_DEFAULTS["autosave_location"])
        )
    )

    if args.save:
        should_save = True
    elif args.no_save:
        should_save = False

    if args.save_path:
        save_location = os.path.expanduser(args.save_path)

    # Save session if requested
    if should_save:
        if not save_oracle_session(
            args.question, args.spread, result, str(save_location)
        ):
            # Warning already printed in save function
            pass

    return 0


if __name__ == '__main__':
    exit(main())
