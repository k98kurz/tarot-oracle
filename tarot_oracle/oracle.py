#!/usr/bin/env python3

"""Oracle system for AI-powered tarot divination readings.

This module provides the core Oracle functionality that combines traditional tarot
readings with AI interpretation through multiple providers (Gemini, OpenRouter,
Ollama). It includes client classes for each provider, session management,
and a unified interface for performing divinatory readings.

Example:
    >>> oracle = Oracle(provider="gemini", api_key="your-key")
    >>> result = oracle.perform_divinatory_reading(
    ...     "What does the future hold?", 
    ...     spread_type="3-card", 
    ...     interpret=True
    ... )
    >>> print(result["interpretation"])

The module supports:
- Multiple AI providers (Gemini, OpenRouter, Ollama)
- Custom invocations and spreads
- Session saving and management
- Comprehensive error handling
- CLI and programmatic interfaces
"""

import json
import sys
import os
from argparse import ArgumentParser
from typing import Any, cast
import requests
from datetime import datetime
import re
from pathlib import Path

from tarot_oracle.tarot import (
    TarotDivination,
    SpreadRenderer,
    SPREADS,
    resolve_spread,
    Card,
    MAJOR_ARCANA,
    MINOR_ARCANA,
    SEMANTICS
)

# Import configuration
from tarot_oracle.config import config
from tarot_oracle.loaders import InvocationLoader
# Custom exceptions removed - using standard TypeError and ValueError instead

# Import Gemini SDK when available
try:
    from google import genai
except ImportError:
    genai = None


class InvocationManager:
    """Manages invocations for divinatory readings.
    
    Handles loading and management of invocation texts that provide the
    ceremonial opening for tarot readings. Supports both built-in invocations
    and custom user-defined invocations.
    
    Attributes:
        loader (InvocationLoader): Loads custom invocation files from disk.
    """

    def __init__(self) -> None:
        """Initialize the invocation manager with loader."""
        self.loader = InvocationLoader()

    @staticmethod
    def get_hermes_thoth_prometheus_invocation() -> str:
        """Returns the default Hermes-Thoth and Prometheus dual invocation.
        
        This invocation combines the wisdom of Hermes-Thoth (guide of souls
        and keeper of sacred knowledge) with the foresight of Prometheus
        (bringer of fire and divine insight).
        
        Returns:
            The complete invocation text for ceremonial reading openings.
        """
        return """By the wisdom of Hermes-Thoth, guide of souls and keeper of sacred knowledge,
and by the foresight of Prometheus, bringer of fire and divine insight,
I seek understanding through the ancient art of tarot.
May these cards reveal the patterns woven by fate and free will,
and may the oracle speak with clarity and truth."""

    def get_invocation(self, name: str | None) -> str:
        """Get invocation by name or return default.
        
        Attempts to load a custom invocation by name using the InvocationLoader.
        If the custom invocation cannot be found or loaded, falls back to the
        default Hermes-Thoth-Prometheus invocation.
        
        Args:
            name: Name of custom invocation, or None for default invocation
            
        Returns:
            The invocation text to be used for the reading.
            
        Raises:
            ValueError: If custom invocation fails to load (but still
                returns default invocation).
                
        Example:
            >>> manager = InvocationManager()
            >>> default = manager.get_invocation(None)
            >>> custom = manager.get_invocation("my-custom-invocation")
        """
        if name:
            try:
                custom_invocation = self.loader.load_invocation(name)
                if custom_invocation:
                    return custom_invocation
            except Exception as e:
                raise ValueError(f"Failed to load invocation '{name}': {e}")
        # Fall back to default
        return self.get_hermes_thoth_prometheus_invocation()

    @staticmethod
    def prepend_invocation(question: str, invocation_type: str = "hermes-thoth-prometheus") -> str:
        """Prepend invocation to the question for ceremonial reading.
        
        Combines an invocation with the user's question to create the complete
        ceremonial prompt for the tarot reading.
        
        Args:
            question: The user's question for the oracle.
            invocation_type: Type of invocation to use (currently only
                "hermes-thoth-prometheus" is supported).
                
        Returns:
            The complete ceremonial text including invocation and question.
            
        Example:
            >>> text = InvocationManager.prepend_invocation(
            ...     "What does the future hold?"
            ... )
            >>> print(text)
        """
        if invocation_type == "hermes-thoth-prometheus":
            invocation = InvocationManager.get_hermes_thoth_prometheus_invocation()
            return f"{invocation}\n\nQuestion: {question}"
        else:
            return question


class GeminiClient:
    """Client for Google Gemini API integration.
    
    Provides interface to Google's Gemini AI models for tarot interpretation.
    Requires the google-genai package to be installed.
    
    Attributes:
        client: The Gemini client instance from google-genai package.
        model (str): Default model name for requests.
        
    Example:
        >>> client = GeminiClient(api_key="your-key", model="gemini-3-flash")
        >>> response = client.generate_response("Interpret these tarot cards...")
        >>> print(response)
    """

    def __init__(self, api_key: str, model: str = "gemini-3-flash"):
        """Initialize the Gemini client.
        
        Args:
            api_key: Google AI API key for authentication.
            model: Default Gemini model to use (default: "gemini-3-flash").
            
        Raises:
            ImportError: If google-genai package is not installed.
        """
        if genai is None:
            raise ImportError("google-genai package not installed. Install with: pip install google-genai")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_response(self, prompt: str, model: str | None = None, timeout: int = 30) -> str | None:
        """Generate response from Gemini model.
        
        Sends a prompt to the specified Gemini model and returns the generated
        text response. Handles API errors gracefully.
        
        Args:
            prompt: The text prompt to send to the model.
            model: Optional model override (uses default if None).
            timeout: Request timeout in seconds (currently unused by genai client).
            
        Returns:
            Generated text response, or None if generation failed.
            
        Example:
            >>> client = GeminiClient(api_key="key")
            >>> response = client.generate_response("Hello, how are you?")
            >>> print(response)
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
        """Check if API key is valid.
        
        Performs a simple test request to verify that the API key is valid
        and the service is accessible.
        
        Returns:
            True if API key is valid and service is accessible, False otherwise.
            
        Example:
            >>> client = GeminiClient(api_key="key")
            >>> if client.check_api_key():
            ...     print("API key is valid")
        """
        try:
            test_response = self.client.models.generate_content(
                model=self.model,
                contents="Hello, please respond with 'API key is valid' to confirm the connection."
            )
            return True
        except Exception as e:
            print(f"Error validating API key: {e}", file=sys.stderr)
            return False


class OpenRouterClient:
    """Client for OpenRouter API integration.
    
    Provides interface to OpenRouter's model marketplace for tarot interpretation.
    Supports multiple AI models through a unified OpenAI-compatible API.
    
    Attributes:
        api_key (str): OpenRouter API key for authentication.
        model (str): Default model identifier for requests.
        base_url (str): Base URL for OpenRouter API endpoints.
        
    Example:
        >>> client = OpenRouterClient(
        ...     api_key="your-key", 
        ...     model="z-ai/glm-4.5-air:free"
        ... )
        >>> response = client.generate_response("Interpret these tarot cards...")
        >>> print(response)
    """

    def __init__(self, api_key: str, model: str = "z-ai/glm-4.5-air:free"):
        """Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key for authentication.
            model: Default model identifier (default: "z-ai/glm-4.5-air:free").
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"

    def generate_response(self, prompt: str, model: str | None = None, timeout: int = 30) -> str | None:
        """Generate response from OpenRouter model.
        
        Sends a prompt to the specified OpenRouter model and returns the
        generated text response. Handles various API errors and provides
        detailed exception information.
        
        Args:
            prompt: The text prompt to send to the model.
            model: Optional model override (uses default if None).
            timeout: Request timeout in seconds.
            
        Returns:
            Generated text response, or None if generation failed.
            
        Raises:
            ValueError: If API key is invalid (HTTP 401).
            ValueError: If rate limit is exceeded (HTTP 429).
            ValueError: For network connectivity or timeout issues.
            ValueError: For other API-related errors.
            
        Example:
            >>> client = OpenRouterClient(api_key="key")
            >>> response = client.generate_response("Hello, how are you?")
            >>> print(response)
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/tarot-oracle/tarot-oracle",
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
                raise ValueError(f"OpenRouter API rate limit exceeded. Retry after: {retry_after}")
            else:
                raise ValueError(f"OpenRouter API returned status {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            raise ValueError(f"OpenRouter API request timed out after {timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"OpenRouter API request failed: {e}")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Unexpected error calling OpenRouter API: {e}")

    def check_api_key(self) -> bool:
        """Check if API key is valid.
        
        Performs a simple test request to verify that the API key is valid
        and the OpenRouter service is accessible.
        
        Returns:
            True if API key is valid and service is accessible, False otherwise.
            
        Example:
            >>> client = OpenRouterClient(api_key="key")
            >>> if client.check_api_key():
            ...     print("API key is valid")
        """
        try:
            # Simple test request with minimal content
            test_prompt = "Hello, please respond with 'API key is valid' to confirm the connection."
            response = self.generate_response(test_prompt, timeout=10)
            return response is not None and "API key is valid" in response.lower()
        except Exception as e:
            print(f"Error validating OpenRouter API key: {e}", file=sys.stderr)
            return False


class OllamaClient:
    """Client for Ollama local AI model server.
    
    Provides interface to locally hosted Ollama server for tarot interpretation.
    Works with various open-source models that can be run locally.
    
    Attributes:
        host (str): Host and port for Ollama server (default: "localhost:11434").
        
    Example:
        >>> client = OllamaClient(host="localhost:11434")
        >>> if client.check_model_available("mistral"):
        ...     response = client.generate_response("Interpret these cards...", "mistral")
        >>> print(response)
    """

    def __init__(self, host: str = "localhost:11434"):
        """Initialize Ollama client.
        
        Args:
            host: Host and port for Ollama server (default: "localhost:11434").
        """
        self.host = host

    def generate_response(self, prompt: str, model: str = "mistral", timeout: int = 300) -> str | None:
        """Generate response from Ollama model.
        
        Sends a prompt to the specified Ollama model and returns the generated
        text response. Uses the non-streaming API endpoint.
        
        Args:
            prompt: The text prompt to send to the model.
            model: Model name to use (default: "mistral").
            timeout: Request timeout in seconds (default: 300 for local models).
            
        Returns:
            Generated text response, or None if generation failed.
            
        Example:
            >>> client = OllamaClient()
            >>> response = client.generate_response("Hello, how are you?", "mistral")
            >>> print(response)
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
        """Check if model is available in Ollama.
        
        Queries the Ollama server to verify that the specified model is
        installed and available for use.
        
        Args:
            model: Model name to check.
            
        Returns:
            True if model is available (exact match or versioned match), False otherwise.
            
        Example:
            >>> client = OllamaClient()
            >>> if client.check_model_available("llama2"):
            ...     print("Model is available")
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


def extract_card_codes_for_filename(legend_display: str) -> list[str]:
    """Extract card codes from legend_display for filename generation.
    
    Parses the legend display to find bracketed card codes and converts
    them to a safe format for filenames. Handles reversed card indicators.
    
    Args:
        legend_display: The formatted legend display containing card codes in brackets.
        
    Returns:
        List of sanitized card codes extracted from the legend display.
        
    Example:
        >>> display = "[ace-cups] [WP-X-CA↓] [king-pentacles]"
        >>> codes = extract_card_codes_for_filename(display)
        >>> print(codes)
        ['ace-cups', 'WP-X-CAR', 'king-pentacles']
    """
    # Find all bracketed card codes
    matches = re.findall(r'\[([^\]]+)\]', legend_display)
    # Replace arrow symbols with R for reversed cards and strip whitespace
    codes = [code.replace('↓', 'R').replace('↑', 'R').strip() for code in matches]
    return codes


def generate_session_filename(card_codes: list[str]) -> str:
    """Generate filename with timestamp and card codes for session saving.
    
    Creates a unique filename based on the current timestamp and the cards
    drawn in the reading. Card codes are sanitized to prevent file system issues.
    
    Args:
        card_codes: List of card codes from the reading.
        
    Returns:
        Filename in format "YYYY-MM-DD-HHMMSS-codes.md".
        
    Example:
        >>> codes = ["ace-cups", "WP-X-CAR"]
        >>> filename = generate_session_filename(codes)
        >>> print(filename)
        '2024-01-15-143022-ace-cups-WP-X-CAR.md'
    """
    import re
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    # Sanitize card codes to prevent injection
    safe_codes = [re.sub(r'[^a-zA-Z0-9]', '', code) for code in card_codes if code]
    codes_str = "-".join(safe_codes) if safe_codes else "no-codes"
    return f"{timestamp}-{codes_str}.md"


def ensure_autosave_directory(save_location: str) -> bool:
    """Ensure save directory exists for session autosaving.
    
    Creates the specified directory if it doesn't exist. Handles errors
    gracefully and reports warnings to stderr.
    
    Args:
        save_location: Path to the directory where sessions should be saved.
        
    Returns:
        True if directory exists or was created successfully, False otherwise.
        
    Example:
        >>> if ensure_autosave_directory("~/oracles"):
        ...     print("Directory ready for saving")
    """
    try:
        os.makedirs(save_location, exist_ok=True)
        return True
    except Exception as e:
        print(f"Warning: Could not create save directory {save_location}: {e}", file=sys.stderr)
        return False


def save_oracle_session(question: str, spread_type: str, result: dict[str, Any], save_location: str) -> bool:
    """Save oracle session to markdown file with full reading details.
    
    Mirrors the exact terminal output format in a markdown file, including
    the invocation, question, spread layout, card displays, and interpretation
    if available. Generates a unique filename based on timestamp and cards.
    
    Args:
        question: The user's question for the oracle.
        spread_type: The type of spread used (e.g., "3-card", "celtic-cross").
        result: Dictionary containing reading results with keys:
            - 'legend_display': Formatted card legend with codes
            - 'spread_display': Formatted spread layout
            - 'interpretation': Optional AI interpretation
            - 'interpretation_requested': Boolean flag for interpretation
        save_location: Directory path where the session should be saved.
        
    Returns:
        True if session was saved successfully, False otherwise.
        
    Example:
        >>> result = {
        ...     'legend_display': '[ace-cups] [2-cups] [3-cups]',
        ...     'spread_display': 'Past: Ace of Cups\nPresent: 2 of Cups...',
        ...     'interpretation': 'This reading suggests...',
        ...     'interpretation_requested': True
        ... }
        >>> success = save_oracle_session(
        ...     "What does love hold for me?",
        ...     "3-card",
        ...     result,
        ...     "~/oracles"
        ... )
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
        invocation_text = InvocationManager.get_hermes_thoth_prometheus_invocation()
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
            content.append("# === Interpretation ===")
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
    """Main oracle class combining tarot reading with LLM interpretation.
    
    The Oracle class provides a unified interface for performing divinatory
    tarot readings with optional AI interpretation. Supports multiple AI
    providers (Gemini, OpenRouter, Ollama), custom invocations, and session
    management.
    
    Attributes:
        tarot (TarotDivination): The underlying tarot reading engine.
        invocation_manager (InvocationManager): Manages invocation texts.
        provider (str): Current AI provider being used.
        client: Provider-specific AI client instance.
        default_model (str): Default model for the current provider.
        
    Example:
        >>> oracle = Oracle(provider="gemini", api_key="your-key")
        >>> result = oracle.perform_divinatory_reading(
        ...     "What does the future hold?",
        ...     spread_type="celtic-cross",
        ...     interpret=True
        ... )
        >>> print(result["interpretation"])
        
        >>> # Using OpenRouter
        >>> oracle = Oracle(provider="openrouter", api_key="key")
        >>> result = oracle.perform_divinatory_reading(
        ...     "Should I take this opportunity?",
        ...     spread_type="3-card",
        ...     model="meta-llama/llama-3-70b-instruct"
        ... )
    """

    def __init__(self, provider: str | None = None, model: str | None = None, api_key: str | None = None, ollama_host: str | None = None):
        """Initialize the Oracle with specified provider and configuration.
        
        Args:
            provider: AI provider to use ("gemini", "openrouter", "ollama").
                If None, uses value from config.
            model: Specific model to use. If None, uses provider default.
            api_key: API key for cloud providers. If None, uses config or env vars.
            ollama_host: Host for Ollama server. If None, uses config.
            
        Raises:
            ValueError: If required API key is missing.
            ImportError: If required packages are not installed.
            ValueError: If unsupported provider is specified.
            
        Example:
            >>> oracle = Oracle(provider="gemini", api_key="key")
            >>> oracle = Oracle(provider="ollama", ollama_host="localhost:11434")
        """
        self.tarot = TarotDivination()
        self.invocation_manager = InvocationManager()

        # Provider selection
        self.provider = provider or config.provider

        if self.provider == "gemini":
            api_key = api_key or config.google_ai_api_key
            if not api_key:
                raise ValueError("GOOGLE_AI_API_KEY environment variable must be set for Gemini provider")
            if genai is None:
                raise ImportError("google-genai package not installed. Install with: pip install google-genai")
            self.client = GeminiClient(api_key, model or "gemini-3-flash")
            self.default_model = model or "gemini-3-flash"

        elif self.provider == "openrouter":
            api_key = api_key or config.openrouter_api_key
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable must be set for OpenRouter provider")
            self.client = OpenRouterClient(api_key, model or "z-ai/glm-4.5-air:free")
            self.default_model = model or "z-ai/glm-4.5-air:free"

        elif self.provider == "ollama":
            host = ollama_host or config.ollama_host
            self.client = OllamaClient(host)
            self.default_model = model or "mistral"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def get_client(self) -> GeminiClient | OpenRouterClient | OllamaClient:
        """Get the current provider client instance.
        
        Returns:
            The provider-specific client (GeminiClient, OpenRouterClient, or OllamaClient).
        """
        return self.client

    def get_default_model(self) -> str:
        """Get the default model name for the current provider.
        
        Returns:
            The default model identifier for the current provider.
        """
        return self.default_model

    def build_interpretation_prompt(self, spread_display: str, legend_display: str, invocation: str, question: str, spread_type: str) -> str:
        """Build structured prompt for LLM interpretation using semantic groupings.
        
        Creates a comprehensive prompt that includes the ceremonial invocation,
        the user's question, spread information, and detailed instructions for
        the AI to provide an intuitive tarot interpretation.
        
        Args:
            spread_display: Formatted display of the spread layout.
            legend_display: Formatted legend showing cards and their positions.
            invocation: The ceremonial invocation text.
            question: The user's question for the oracle.
            spread_type: Type of spread being used.
            
        Returns:
            Complete prompt string ready for sending to the AI model.
            
        Example:
            >>> prompt = oracle.build_interpretation_prompt(
            ...     spread_display="Past: Ace of Cups...",
            ...     legend_display="[ace-cups] [2-cups]...",
            ...     invocation="By the wisdom of Hermes-Thoth...",
            ...     question="What does love hold for me?",
            ...     spread_type="3-card"
            ... )
        """

        prompt = f"""# Role: Oracle
You are an intuitive tarot reader channeling ancient wisdom and divine insight to provide an oracular service.

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

Pay special attention to the positional meanings and how they affect each card's interpretation. Speak with wisdom, clarity, and compassion. Blend traditional symbolism with intuitive insight. Be thorough but concise enough to be useful for practical guidance. For large spreads of more than 5 cards, lean toward concise summary rather than exhaustive card-by-card analyses."""

        return prompt

    def get_interpretation(self, spread_display: str, legend_display: str, invocation: str, question: str, model: str | None = None, spread_type: str = "unknown") -> str | None:
        """Get LLM interpretation of the reading.
        
        Generates an AI interpretation of the tarot reading using the
        configured provider. Handles errors gracefully and returns None
        if interpretation fails.
        
        Args:
            spread_display: Formatted display of the spread layout.
            legend_display: Formatted legend showing cards and positions.
            invocation: The ceremonial invocation text.
            question: The user's question for the oracle.
            model: Optional model override (uses default if None).
            spread_type: Type of spread being used for context.
            
        Returns:
            Generated interpretation text, or None if interpretation failed.
            
        Example:
            >>> interpretation = oracle.get_interpretation(
            ...     spread_display="Past: Ace of Cups...",
            ...     legend_display="[ace-cups] [2-cups]...",
            ...     invocation="By the wisdom...",
            ...     question="What does love hold for me?",
            ...     spread_type="3-card"
            ... )
            >>> print(interpretation)
        """
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

    def perform_divinatory_reading(self, question: str, spread_type: str = "3-card",
                                        interpret: bool = False, model: str | None = None, **kwargs) -> dict[str, Any]:
        """Perform complete divinatory reading with optional interpretation.
        
        Orchestrates a complete tarot reading session, including card selection,
        layout generation, and optional AI interpretation. Supports custom
        invocations, reversed cards, and various spread types.
        
        Args:
            question: The user's question for the oracle.
            spread_type: Type of spread to use (default: "3-card").
            interpret: Whether to generate AI interpretation (default: False).
            model: Optional model override for interpretation.
            **kwargs: Additional options:
                - invocation: Custom invocation text
                - invocation_name: Name of custom invocation to load
                - random_bytes: Entropy bytes for card selection (default: 8)
                - allow_reversed: Allow reversed cards (default: False)
                - show_descriptions: Show card descriptions (default: True)
                
        Returns:
            Dictionary containing reading results with keys:
                - spread_display: Formatted spread layout
                - legend_display: Formatted card legend with codes
                - interpretation: Optional AI interpretation
                - provider_used: Which provider was used
                - interpretation_requested: Boolean flag
                - interpretation_available: Whether interpretation succeeded
                - question: The original question
                - spread_type: The spread type used
                - error: Error message if reading failed
                
        Example:
            >>> result = oracle.perform_divinatory_reading(
            ...     "What does the future hold?",
            ...     spread_type="celtic-cross",
            ...     interpret=True,
            ...     allow_reversed=True,
            ...     invocation_name="my-custom"
            ... )
            >>> print(result["interpretation"])
            >>> print(result["legend_display"])
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
            invocation = self.invocation_manager.get_hermes_thoth_prometheus_invocation()

        # Generate tarot reading using existing system
        try:
            spread_layout = resolve_spread(spread_type)
        except ValueError as e:
            return {"error": str(e)}

        # Use direct method calls instead of JSON
        spread_display, legend_display = self.tarot.perform_reading(
            question=question,
            spread_layout=spread_layout,
            invocation=invocation,
            random_bytes=kwargs.get('random_bytes', 8),
            allow_reversed=kwargs.get('allow_reversed', False),
            show_descriptions=kwargs.get('show_descriptions', True),
            spread_type=spread_type
        )

        # Get interpretation if requested
        interpretation = None
        if interpret:
            interpretation = self.get_interpretation(spread_display, legend_display, invocation, question, model, spread_type)

        return {
            "spread_display": spread_display,
            "legend_display": legend_display,
            "interpretation": interpretation,
            "provider_used": self.provider,
            "interpretation_requested": interpret,
            "interpretation_available": interpretation is not None,
            "question": question,
            "spread_type": spread_type
        }


def create_oracle_parser() -> ArgumentParser:
    """Create command line argument parser for oracle functionality.
    
    Sets up argument parsing for the oracle command, including options for
    provider selection, spread types, interpretation settings, and session
    management.
    
    Returns:
        Configured ArgumentParser with all oracle-specific options.
        
    Example:
        >>> parser = create_oracle_parser()
        >>> args = parser.parse_args([
        ...     "What does the future hold?",
        ...     "--provider", "gemini",
        ...     "--interpret"
        ... ])
    """
    parser = ArgumentParser(description="Divinatory oracle with LLM interpretation")

    # Core question and spread
    parser.add_argument("question", help="Question for the oracle")
    parser.add_argument("--spread", default="3-card",
                       help=f"Spread layout (default: 3-card). Available: {list(SPREADS.keys())} or custom matrix")

    # Oracle-specific features
    parser.add_argument("--provider", choices=["gemini", "openrouter", "ollama"],
                       default="gemini", help="LLM provider (default: gemini)")
    parser.add_argument("--invocation",
                       help="Custom invocation text (defaults to Hermes-Thoth/Prometheus if not provided)")
    parser.add_argument("--interpret", action="store_true",
                       help="Generate LLM interpretation of reading")
    parser.add_argument("--model", help="Model name (provider-specific)")

    # Provider-specific options
    parser.add_argument("--api-key", help="API key (for gemini or openrouter provider)")
    parser.add_argument("--ollama-host", help="Ollama host (for ollama provider)")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds (default: 30 gemini, 300 ollama)")

    # Session saving options
    save_group = parser.add_mutually_exclusive_group()
    save_group.add_argument("--save", action="store_true",
                         help="Force save this session (overrides environment settings)")
    save_group.add_argument("--no-save", action="store_true",
                         help="Do not save this session (overrides environment settings)")
    parser.add_argument("--save-path",
                      help="Override default save location for this session")

    # Tarot options (re-using existing logic)
    parser.add_argument("--random", type=int, default=8,
                       help="Add N random bytes to RNG seed for entropy (default: 8)")
    parser.add_argument("--reversed", action="store_true",
                       help="Allow cards to appear reversed")

    return parser


def print_invocation(invocation_text: str) -> None:
    """Print the ceremonial invocation for the reading.
    
    Formats and prints the invocation text with appropriate header.
    
    Args:
        invocation_text: The invocation text to display.
    """
    print("# === Invocation ===")
    print(invocation_text)
    print()


def print_cards(spread_display: str, legend_display: str, question: str, spread_type: str) -> None:
    """Print the tarot reading using the provided displays.
    
    Formats and prints the complete tarot reading including question,
    spread type, layout, and card legend.
    
    Args:
        spread_display: Formatted display of the spread layout.
        legend_display: Formatted legend showing cards and their positions.
        question: The user's question for the oracle.
        spread_type: The type of spread used.
    """
    print("# === Tarot Reading ===")

    print(f"Question: {question}")
    print(f"Spread: {spread_type}\n")
    print(spread_display)
    print("\n" + legend_display)
    print()


def print_interpretation(interpretation: str | None) -> None:
    """Print the AI interpretation or fallback message.
    
    Formats and prints the interpretation, or a message indicating
    that interpretation was not available.
    
    Args:
        interpretation: Generated interpretation text, or None if unavailable.
    """
    print("# === Interpretation ===")
    if interpretation:
        print(interpretation)
    else:
        print("Interpretation was not available.")


def main(args=None) -> int:
    """Main oracle CLI interface.
    
    Handles command-line execution of oracle functionality, including
    argument parsing, oracle initialization, reading execution, and
    session management.
    
    Args:
        args: Optional argument list (for testing). If None, uses sys.argv.
        
    Returns:
        Exit code (0 for success, non-zero for error).
        
    Example:
        >>> # Direct call for testing
        >>> exit_code = main([
        ...     "What does the future hold?",
        ...     "--provider", "gemini",
        ...     "--spread", "3-card"
        ... ])
    """
    parser = create_oracle_parser()

    if args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(args)

    # Create oracle instance with provider-specific options
    oracle = Oracle(
        provider=args.provider,
        model=args.model,
        api_key=args.api_key,
        ollama_host=args.ollama_host
    )

    # Check availability if interpretation requested
    if args.interpret:
        if args.provider == "openrouter":
            client = oracle.get_client()
            # We know this is OpenRouterClient when provider is "openrouter"
            if hasattr(client, 'check_api_key'):
                # Type assertion: we know this method exists due to hasattr check
                openrouter_client = cast(OpenRouterClient, client)
                api_key_valid = openrouter_client.check_api_key()
                if not api_key_valid:
                    print(f"Warning: OpenRouter API key validation failed. Interpretation may not be available.")
        elif args.provider == "ollama":
            client = oracle.get_client()
            # We know this is OllamaClient when provider is "ollama"
            if hasattr(client, 'check_model_available'):
                # Type assertion: we know this method exists due to hasattr check
                ollama_client = cast(OllamaClient, client)
                model_available = ollama_client.check_model_available(args.model or "mistral")
                if not model_available:
                    print(f"Warning: Model '{args.model or 'mistral'}' not found in Ollama. Interpretation may not be available.")

    # Perform the reading
    result = oracle.perform_divinatory_reading(
        question=args.question,
        spread_type=args.spread,
        interpret=args.interpret,
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
    invocation_text = InvocationManager.get_hermes_thoth_prometheus_invocation()
    print_invocation(invocation_text)
    print_cards(result["spread_display"], result["legend_display"], result["question"], result["spread_type"])

    if result["interpretation_requested"]:
        print_interpretation(result["interpretation"])

    # Determine save behavior
    should_save = config.autosave_sessions
    save_location = config.autosave_location

    if args.save:
        should_save = True
    elif args.no_save:
        should_save = False

    if args.save_path:
        save_location = os.path.expanduser(args.save_path)

    # Save session if requested
    if should_save:
        if not save_oracle_session(args.question, args.spread, result, save_location):
            # Warning already printed in save function
            pass

    return 0


if __name__ == '__main__':
    exit(main())
