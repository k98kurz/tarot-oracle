#!/usr/bin/env python3

import json
import sys
import os
from argparse import ArgumentParser
from typing import Optional, List, Dict, Any
import requests
from datetime import datetime
import re

# Add current directory to Python path to import numinous modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from numinous.tarot import (
    TarotDivination,
    SpreadRenderer,
    SPREADS,
    resolve_spread,
    Card,
    MAJOR_ARCANA,
    MINOR_ARCANA,
    SEMANTICS
)

# Import Gemini SDK when available
try:
    from google import genai
except ImportError:
    genai = None


# Environment variables
ORACLE_PROVIDER = os.getenv("ORACLE_PROVIDER", "gemini")
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost:11434")

# Session autosaving
AUTOSAVE_SESSIONS = os.getenv("AUTOSAVE_SESSIONS", "true").lower() in ("true", "1")
AUTOSAVE_LOCATION = os.path.expanduser(os.getenv("AUTOSAVE_LOCATION", "~/oracles"))


class InvocationManager:
    """Manages invocations for divinatory readings."""

    @staticmethod
    def get_hermes_thoth_prometheus_invocation() -> str:
        """Returns the Hermes-Thoth and Prometheus dual invocation."""
        return """By the wisdom of Hermes-Thoth, guide of souls and keeper of sacred knowledge,
and by the foresight of Prometheus, bringer of fire and divine insight,
I seek understanding through the ancient art of tarot.
May these cards reveal the patterns woven by fate and free will,
and may the oracle speak with clarity and truth."""

    @staticmethod
    def prepend_invocation(question: str, invocation_type: str = "hermes-thoth-prometheus") -> str:
        """Prepend invocation to the question."""
        if invocation_type == "hermes-thoth-prometheus":
            invocation = InvocationManager.get_hermes_thoth_prometheus_invocation()
            return f"{invocation}\n\nQuestion: {question}"
        else:
            return question


class GeminiClient:
    """Client for Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-3-flash"):
        if genai is None:
            raise ImportError("google-genai package not installed. Install with: pip install google-genai")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate_response(self, prompt: str, model: str = None, timeout: int = 30) -> Optional[str]:
        """Generate response from Gemini model."""
        try:
            response = self.client.models.generate_content(
                model=model or self.model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating response from Gemini: {e}", file=sys.stderr)
            return None

    def check_api_key(self) -> bool:
        """Check if API key is valid."""
        try:
            test_response = self.client.models.generate_content(
                model=self.model,
                contents="Hello, please respond with 'API key is valid' to confirm the connection."
            )
            return True
        except Exception as e:
            print(f"Error validating API key: {e}", file=sys.stderr)
            return False


class OllamaClient:
    """Simple client for Ollama API."""

    def __init__(self, host: str = "localhost:11434"):
        self.host = host

    def generate_response(self, prompt: str, model: str = "mistral", timeout: int = 300) -> Optional[str]:
        """Generate response from Ollama model."""
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
        """Check if model is available in Ollama."""
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


def extract_card_codes_for_filename(legend_display: str) -> List[str]:
    """Extract card codes from legend_display for filename.
    Finds bracketed content like [WP-X-CA] and returns list.
    """
    # Find all bracketed card codes
    matches = re.findall(r'\[([^\]]+)\]', legend_display)
    # Replace arrow symbols with R for reversed cards and strip whitespace
    codes = [code.replace('↓', 'R').replace('↑', 'R').strip() for code in matches]
    return codes


def generate_session_filename(card_codes: List[str]) -> str:
    """Generate filename with timestamp and card codes."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    codes_str = "-".join(card_codes) if card_codes else "no-cards"
    return f"{timestamp}-{codes_str}.md"


def ensure_autosave_directory(save_location: str) -> bool:
    """Ensure save directory exists, return True if successful."""
    try:
        os.makedirs(save_location, exist_ok=True)
        return True
    except Exception as e:
        print(f"Warning: Could not create save directory {save_location}: {e}", file=sys.stderr)
        return False


def save_oracle_session(question: str, spread_type: str, result: dict, save_location: str) -> bool:
    """Save oracle session by mirroring terminal output exactly."""
    if not ensure_autosave_directory(save_location):
        return False

    try:
        # Extract card codes from legend display
        card_codes = extract_card_codes_for_filename(result['legend_display'])
        filename = generate_session_filename(card_codes)
        filepath = os.path.join(save_location, filename)

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
    """Main oracle class combining tarot reading with LLM interpretation."""

    def __init__(self, provider: str = None, model: str = None, api_key: str = None, ollama_host: str = None):
        self.tarot = TarotDivination()

        # Provider selection
        self.provider = provider or ORACLE_PROVIDER

        if self.provider == "gemini":
            api_key = api_key or GOOGLE_AI_API_KEY
            if not api_key:
                raise ValueError("GOOGLE_AI_API_KEY environment variable must be set for Gemini provider")
            if genai is None:
                raise ImportError("google-genai package not installed. Install with: pip install google-genai")
            self.client = GeminiClient(api_key, model)
            self.default_model = model or "gemini-3-flash"

        elif self.provider == "ollama":
            host = ollama_host or OLLAMA_HOST
            self.client = OllamaClient(host)
            self.default_model = model or "mistral"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def get_client(self):
        return self.client

    def get_default_model(self):
        return self.default_model



    def build_interpretation_prompt(self, spread_display: str, legend_display: str, invocation: str, question: str, spread_type: str) -> str:
        """Build structured prompt for LLM interpretation using semantic groupings."""

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

    def get_interpretation(self, spread_display: str, legend_display: str, invocation: str, question: str, model: Optional[str] = None, spread_type: str = "unknown") -> Optional[str]:
        """Get LLM interpretation of the reading."""
        if model is None:
            model = self.default_model

        timeout = 30 if self.provider == "gemini" else 300

        try:
            prompt = self.build_interpretation_prompt(spread_display, legend_display, invocation, question, spread_type)
            response = self.client.generate_response(prompt, model, timeout)
            return response
        except Exception as e:
            # For debugging - we can remove this later
            print(f"DEBUG: Error getting interpretation: {e}", file=sys.stderr)
            return None

    def perform_divinatory_reading(self, question: str, spread_type: str = "3-card",
                                        interpret: bool = False, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Perform complete divinatory reading with optional interpretation."""
        # Get invocation text (always used for oracle)
        # Custom invocation will be passed via kwargs, otherwise use default
        custom_invocation = kwargs.get('invocation')
        invocation = custom_invocation if custom_invocation else InvocationManager.get_hermes_thoth_prometheus_invocation()

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
    """Create command line argument parser for oracle."""
    parser = ArgumentParser(description="Divinatory oracle with LLM interpretation")

    # Core question and spread
    parser.add_argument("question", help="Question for the oracle")
    parser.add_argument("--spread", default="3-card",
                       help=f"Spread layout (default: 3-card). Available: {list(SPREADS.keys())} or custom matrix")

    # Oracle-specific features
    parser.add_argument("--provider", choices=["gemini", "ollama"],
                       default="gemini", help="LLM provider (default: gemini)")
    parser.add_argument("--invocation",
                       help="Custom invocation text (defaults to Hermes-Thoth/Prometheus if not provided)")
    parser.add_argument("--interpret", action="store_true",
                       help="Generate LLM interpretation of reading")
    parser.add_argument("--model", help="Model name (provider-specific)")

    # Provider-specific options
    parser.add_argument("--api-key", help="API key (for gemini provider)")
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


def print_invocation(invocation_text: str):
    """Print the invocation being used."""
    print("# === Invocation ===")
    print(invocation_text)
    print()


def print_cards(spread_display: str, legend_display: str, question: str, spread_type: str):
    """Print the tarot reading using the provided displays."""
    print("# === Tarot Reading ===")

    print(f"Question: {question}")
    print(f"Spread: {spread_type}\n")
    print(spread_display)
    print("\n" + legend_display)
    print()


def print_interpretation(interpretation: Optional[str]):
    """Print the interpretation or fallback message."""
    print("# === Interpretation ===")
    if interpretation:
        print(interpretation)
    else:
        print("Interpretation was not available.")


def main(args=None):
    """Main oracle CLI interface."""
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
        if args.provider == "ollama":
            model_available = oracle.get_client().check_model_available(args.model or "mistral")
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
    should_save = AUTOSAVE_SESSIONS
    save_location = AUTOSAVE_LOCATION

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
