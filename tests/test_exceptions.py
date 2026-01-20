"""Test custom exception hierarchy for Tarot Oracle."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.exceptions import (
    TarotOracleError,
    TarotConfigurationError,
    DeckLoadError,
    SpreadError,
    InvocationError,
    ConfigError,
    ProviderError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ValidationError,
    FileOperationError,
    PathTraversalError,
    StateError,
)


class TestTarotOracleError(unittest.TestCase):
    """Test base TarotOracleError class."""

    def test_basic_initialization(self):
        """Test basic exception initialization."""
        error = TarotOracleError("Test message")
        assert str(error) == "Test message", f"Expected 'Test message', got '{str(error)}'"
        assert error.message == "Test message", f"Expected 'Test message', got '{error.message}'"
        assert error.context == {}, f"Expected empty context, got {error.context}"
        assert error.suggestions == [], f"Expected empty suggestions, got {error.suggestions}"

    def test_initialization_with_context(self):
        """Test exception with context."""
        context = {"key": "value"}
        error = TarotOracleError("Test message", context=context)
        assert error.context == context, f"Expected {context}, got {error.context}"

    def test_initialization_with_suggestions(self):
        """Test exception with suggestions."""
        suggestions = ["Try again", "Check config"]
        error = TarotOracleError("Test message", suggestions=suggestions)
        assert error.suggestions == suggestions, f"Expected {suggestions}, got {error.suggestions}"

    def test_string_representation_with_suggestions(self):
        """Test string representation includes suggestions."""
        suggestions = ["Try again", "Check config"]
        error = TarotOracleError("Test message", suggestions=suggestions)
        result = str(error)
        assert "Test message" in result, "Message should be in string representation"
        assert "Suggestions:" in result, "Suggestions header should be in string representation"
        assert "• Try again" in result, "First suggestion should be in string representation"
        assert "• Check config" in result, "Second suggestion should be in string representation"


class TestConfigurationErrors(unittest.TestCase):
    """Test configuration-related exceptions."""

    def test_deck_load_error_basic(self):
        """Test DeckLoadError basic functionality."""
        error = DeckLoadError("Invalid deck format")
        assert "Invalid deck format" in str(error), "Error message should be in string representation"
        assert error.context.get("deck_path") is None, "Deck path should not be set by default"
        assert len(error.suggestions) > 0, "Should have default suggestions"
        assert "Check that the deck file is valid JSON" in error.suggestions, "Should have JSON suggestion"

    def test_deck_load_error_with_path(self):
        """Test DeckLoadError with deck path."""
        deck_path = "/path/to/deck.json"
        error = DeckLoadError("File not found", deck_path=deck_path)
        assert error.context["deck_path"] == deck_path, f"Expected {deck_path}, got {error.context['deck_path']}"
        assert "File not found" in str(error), "Error message should be in string representation"

    def test_spread_error_basic(self):
        """Test SpreadError basic functionality."""
        error = SpreadError("Invalid spread layout")
        assert "Invalid spread layout" in str(error), "Error message should be in string representation"
        assert len(error.suggestions) > 0, "Should have default suggestions"
        assert "Check that the spread file is valid JSON" in error.suggestions, "Should have JSON suggestion"

    def test_spread_error_with_name(self):
        """Test SpreadError with spread name."""
        spread_name = "custom_spread"
        error = SpreadError("Missing semantic groups", spread_name=spread_name)
        assert error.context["spread_name"] == spread_name, f"Expected {spread_name}, got {error.context['spread_name']}"

    def test_invocation_error_basic(self):
        """Test InvocationError basic functionality."""
        error = InvocationError("Invocation not found")
        assert "Invocation not found" in str(error), "Error message should be in string representation"
        assert len(error.suggestions) > 0, "Should have default suggestions"
        assert "Check that invocation files exist in the correct directory" in error.suggestions, "Should have directory suggestion"

    def test_invocation_error_with_name(self):
        """Test InvocationError with invocation name."""
        invocation_name = "morning_ritual"
        error = InvocationError("File permission denied", invocation_name=invocation_name)
        assert error.context["invocation_name"] == invocation_name, f"Expected {invocation_name}, got {error.context['invocation_name']}"

    def test_config_error_basic(self):
        """Test ConfigError basic functionality."""
        error = ConfigError("Invalid configuration")
        assert "Invalid configuration" in str(error), "Error message should be in string representation"
        assert len(error.suggestions) > 0, "Should have default suggestions"
        assert "Check that config.json is valid JSON" in error.suggestions, "Should have JSON suggestion"

    def test_config_error_with_path(self):
        """Test ConfigError with config path."""
        config_path = "/path/to/config.json"
        error = ConfigError("Permission denied", config_path=config_path)
        assert error.context["config_path"] == config_path, f"Expected {config_path}, got {error.context['config_path']}"


class TestProviderErrors(unittest.TestCase):
    """Test AI provider-related exceptions."""

    def test_provider_error_basic(self):
        """Test ProviderError basic functionality."""
        error = ProviderError("Provider unavailable", provider="test_provider")
        assert "Provider unavailable" in str(error), "Error message should be in string representation"
        assert error.context["provider"] == "test_provider", f"Expected 'test_provider', got {error.context['provider']}"

    def test_authentication_error_basic(self):
        """Test AuthenticationError basic functionality."""
        error = AuthenticationError("Invalid API key")
        assert "Invalid API key" in str(error), "Error message should be in string representation"
        assert len(error.suggestions) > 0, "Should have default suggestions"
        assert "Check that API key is correct and valid" in error.suggestions, "Should have API key suggestion"

    def test_authentication_error_with_provider(self):
        """Test AuthenticationError with provider."""
        provider = "openrouter"
        error = AuthenticationError("Expired token", provider=provider)
        assert error.context["provider"] == provider, f"Expected {provider}, got {error.context['provider']}"

    def test_network_error_basic(self):
        """Test NetworkError basic functionality."""
        error = NetworkError("Connection timeout")
        assert "Connection timeout" in str(error), "Error message should be in string representation"
        assert len(error.suggestions) > 0, "Should have default suggestions"
        assert "Check internet connection" in error.suggestions, "Should have internet connection suggestion"

    def test_network_error_with_timeout(self):
        """Test NetworkError with timeout information."""
        timeout = 30
        error = NetworkError("Timeout occurred", timeout=timeout)
        assert error.context["timeout"] == timeout, f"Expected {timeout}, got {error.context['timeout']}"

    def test_rate_limit_error_basic(self):
        """Test RateLimitError basic functionality."""
        error = RateLimitError("Rate limit exceeded")
        assert "Rate limit exceeded" in str(error), "Error message should be in string representation"
        assert len(error.suggestions) > 0, "Should have default suggestions"
        assert "Wait" in error.suggestions[0], "Should suggest waiting"

    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError with retry_after information."""
        retry_after = 60
        error = RateLimitError("Too many requests", retry_after=retry_after)
        assert error.context["retry_after"] == retry_after, f"Expected {retry_after}, got {error.context['retry_after']}"
        assert "60 seconds" in str(error), "Should include retry time in string representation"


class TestFileOperationErrors(unittest.TestCase):
    """Test file operation-related exceptions."""

    def test_path_traversal_error_basic(self):
        """Test PathTraversalError basic functionality."""
        error = PathTraversalError("Dangerous path detected")
        assert "Dangerous path detected" in str(error), "Error message should be in string representation"
        assert len(error.suggestions) > 0, "Should have default suggestions"
        assert "Use only relative paths" in error.suggestions[0], "Should have path suggestion"

    def test_path_traversal_error_with_path(self):
        """Test PathTraversalError with attempted path."""
        attempted_path = "../../../etc/passwd"
        error = PathTraversalError("Path traversal attempt", attempted_path=attempted_path)
        assert error.context["attempted_path"] == attempted_path, f"Expected {attempted_path}, got {error.context['attempted_path']}"


class TestExceptionInheritance(unittest.TestCase):
    """Test exception inheritance hierarchy."""

    def test_configuration_error_inheritance(self):
        """Test configuration errors inherit properly."""
        assert issubclass(DeckLoadError, TarotConfigurationError), "DeckLoadError should inherit from TarotConfigurationError"
        assert issubclass(SpreadError, TarotConfigurationError), "SpreadError should inherit from TarotConfigurationError"
        assert issubclass(InvocationError, TarotConfigurationError), "InvocationError should inherit from TarotConfigurationError"
        assert issubclass(ConfigError, TarotConfigurationError), "ConfigError should inherit from TarotConfigurationError"
        assert issubclass(TarotConfigurationError, TarotOracleError), "TarotConfigurationError should inherit from TarotOracleError"

    def test_provider_error_inheritance(self):
        """Test provider errors inherit properly."""
        assert issubclass(AuthenticationError, ProviderError), "AuthenticationError should inherit from ProviderError"
        assert issubclass(NetworkError, ProviderError), "NetworkError should inherit from ProviderError"
        assert issubclass(RateLimitError, ProviderError), "RateLimitError should inherit from ProviderError"
        assert issubclass(ProviderError, TarotOracleError), "ProviderError should inherit from TarotOracleError"

    def test_validation_error_inheritance(self):
        """Test validation errors inherit properly."""
        assert issubclass(ValidationError, TarotOracleError), "ValidationError should inherit from TarotOracleError"

    def test_file_operation_error_inheritance(self):
        """Test file operation errors inherit properly."""
        assert issubclass(PathTraversalError, FileOperationError), "PathTraversalError should inherit from FileOperationError"
        assert issubclass(FileOperationError, TarotOracleError), "FileOperationError should inherit from TarotOracleError"

    def test_state_error_inheritance(self):
        """Test state errors inherit properly."""
        assert issubclass(StateError, TarotOracleError), "StateError should inherit from TarotOracleError"


class TestExceptionChaining(unittest.TestCase):
    """Test exception chaining and context preservation."""

    def test_exception_catching(self):
        """Test that exceptions can be caught by their base types."""
        try:
            raise DeckLoadError("Deck file corrupted")
        except TarotConfigurationError as e:
            assert isinstance(e, DeckLoadError), "Should be DeckLoadError instance"
            assert "Deck file corrupted" in str(e), "Error message should be preserved"

        try:
            raise AuthenticationError("API key invalid")
        except ProviderError as e:
            assert isinstance(e, AuthenticationError), "Should be AuthenticationError instance"
            assert "API key invalid" in str(e), "Error message should be preserved"

        try:
            raise PathTraversalError("Dangerous path")
        except TarotOracleError as e:
            assert isinstance(e, PathTraversalError), "Should be PathTraversalError instance"
            assert "Dangerous path" in str(e), "Error message should be preserved"

    def test_custom_context_and_suggestions(self):
        """Test custom context and suggestions override defaults."""
        custom_context = {"custom": "value"}
        custom_suggestions = ["Custom suggestion 1", "Custom suggestion 2"]

        error = DeckLoadError(
            "Custom error",
            context=custom_context,
            suggestions=custom_suggestions
        )

        assert error.context == custom_context, f"Expected {custom_context}, got {error.context}"
        assert error.suggestions == custom_suggestions, f"Expected {custom_suggestions}, got {error.suggestions}"


if __name__ == "__main__":
    unittest.main()
