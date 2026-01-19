"""Test custom exception hierarchy for Tarot Oracle."""

import pytest
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
    CardCodeError,
    SemanticValidationError,
    FileOperationError,
    PathTraversalError,
    StateError,
    InvalidDeckStateError
)


class TestTarotOracleError:
    """Test base TarotOracleError class."""
    
    def test_basic_initialization(self):
        """Test basic exception initialization."""
        error = TarotOracleError("Test message")
        assert str(error) == "Test message"
        assert error.message == "Test message"
        assert error.context == {}
        assert error.suggestions == []
    
    def test_initialization_with_context(self):
        """Test exception with context."""
        context = {"key": "value"}
        error = TarotOracleError("Test message", context=context)
        assert error.context == context
    
    def test_initialization_with_suggestions(self):
        """Test exception with suggestions."""
        suggestions = ["Try again", "Check config"]
        error = TarotOracleError("Test message", suggestions=suggestions)
        assert error.suggestions == suggestions
    
    def test_string_representation_with_suggestions(self):
        """Test string representation includes suggestions."""
        suggestions = ["Try again", "Check config"]
        error = TarotOracleError("Test message", suggestions=suggestions)
        result = str(error)
        assert "Test message" in result
        assert "Suggestions:" in result
        assert "• Try again" in result
        assert "• Check config" in result


class TestConfigurationErrors:
    """Test configuration-related exceptions."""
    
    def test_deck_load_error_basic(self):
        """Test DeckLoadError basic functionality."""
        error = DeckLoadError("Invalid deck format")
        assert "Invalid deck format" in str(error)
        assert error.context.get("deck_path") is None
        assert len(error.suggestions) > 0
        assert "Check that the deck file is valid JSON" in error.suggestions
    
    def test_deck_load_error_with_path(self):
        """Test DeckLoadError with deck path."""
        deck_path = "/path/to/deck.json"
        error = DeckLoadError("File not found", deck_path=deck_path)
        assert error.context["deck_path"] == deck_path
        assert "File not found" in str(error)
    
    def test_spread_error_basic(self):
        """Test SpreadError basic functionality."""
        error = SpreadError("Invalid spread layout")
        assert "Invalid spread layout" in str(error)
        assert len(error.suggestions) > 0
        assert "Check that the spread file is valid JSON" in error.suggestions
    
    def test_spread_error_with_name(self):
        """Test SpreadError with spread name."""
        spread_name = "custom_spread"
        error = SpreadError("Missing semantic groups", spread_name=spread_name)
        assert error.context["spread_name"] == spread_name
    
    def test_invocation_error_basic(self):
        """Test InvocationError basic functionality."""
        error = InvocationError("Invocation not found")
        assert "Invocation not found" in str(error)
        assert len(error.suggestions) > 0
        assert "Check that invocation files exist in the correct directory" in error.suggestions
    
    def test_invocation_error_with_name(self):
        """Test InvocationError with invocation name."""
        invocation_name = "morning_ritual"
        error = InvocationError("File permission denied", invocation_name=invocation_name)
        assert error.context["invocation_name"] == invocation_name
    
    def test_config_error_basic(self):
        """Test ConfigError basic functionality."""
        error = ConfigError("Invalid configuration")
        assert "Invalid configuration" in str(error)
        assert len(error.suggestions) > 0
        assert "Check that config.json is valid JSON" in error.suggestions
    
    def test_config_error_with_path(self):
        """Test ConfigError with config path."""
        config_path = "/path/to/config.json"
        error = ConfigError("Permission denied", config_path=config_path)
        assert error.context["config_path"] == config_path


class TestProviderErrors:
    """Test AI provider-related exceptions."""
    
    def test_provider_error_basic(self):
        """Test ProviderError basic functionality."""
        error = ProviderError("Provider unavailable", provider="test_provider")
        assert "Provider unavailable" in str(error)
        assert error.context["provider"] == "test_provider"
    
    def test_authentication_error_basic(self):
        """Test AuthenticationError basic functionality."""
        error = AuthenticationError("Invalid API key")
        assert "Invalid API key" in str(error)
        assert len(error.suggestions) > 0
        assert "Check that API key is correct and valid" in error.suggestions
    
    def test_authentication_error_with_provider(self):
        """Test AuthenticationError with provider."""
        provider = "openrouter"
        error = AuthenticationError("Expired token", provider=provider)
        assert error.context["provider"] == provider
    
    def test_network_error_basic(self):
        """Test NetworkError basic functionality."""
        error = NetworkError("Connection timeout")
        assert "Connection timeout" in str(error)
        assert len(error.suggestions) > 0
        assert "Check internet connection" in error.suggestions
    
    def test_network_error_with_timeout(self):
        """Test NetworkError with timeout information."""
        timeout = 30
        error = NetworkError("Timeout occurred", timeout=timeout)
        assert error.context["timeout"] == timeout
    
    def test_rate_limit_error_basic(self):
        """Test RateLimitError basic functionality."""
        error = RateLimitError("Rate limit exceeded")
        assert "Rate limit exceeded" in str(error)
        assert len(error.suggestions) > 0
        assert "Wait" in error.suggestions[0]
    
    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError with retry_after information."""
        retry_after = 60
        error = RateLimitError("Too many requests", retry_after=retry_after)
        assert error.context["retry_after"] == retry_after
        assert "60 seconds" in str(error)


class TestValidationErrors:
    """Test validation-related exceptions."""
    
    def test_card_code_error_basic(self):
        """Test CardCodeError basic functionality."""
        error = CardCodeError("Invalid card format")
        assert "Invalid card format" in str(error)
        assert len(error.suggestions) > 0
        assert "Use card codes in format" in error.suggestions[0]
    
    def test_card_code_error_with_code(self):
        """Test CardCodeError with card code."""
        card_code = "invalid-format"
        error = CardCodeError("Malformed code", card_code=card_code)
        assert error.context["card_code"] == card_code
    
    def test_semantic_validation_error_basic(self):
        """Test SemanticValidationError basic functionality."""
        error = SemanticValidationError("Dimension mismatch")
        assert "Dimension mismatch" in str(error)
        assert len(error.suggestions) > 0
        assert "Check spread dimensions" in error.suggestions[0]


class TestFileOperationErrors:
    """Test file operation-related exceptions."""
    
    def test_path_traversal_error_basic(self):
        """Test PathTraversalError basic functionality."""
        error = PathTraversalError("Dangerous path detected")
        assert "Dangerous path detected" in str(error)
        assert len(error.suggestions) > 0
        assert "Use only relative paths" in error.suggestions[0]
    
    def test_path_traversal_error_with_path(self):
        """Test PathTraversalError with attempted path."""
        attempted_path = "../../../etc/passwd"
        error = PathTraversalError("Path traversal attempt", attempted_path=attempted_path)
        assert error.context["attempted_path"] == attempted_path


class TestStateErrors:
    """Test state-related exceptions."""
    
    def test_invalid_deck_state_error_basic(self):
        """Test InvalidDeckStateError basic functionality."""
        error = InvalidDeckStateError("Deck not shuffled")
        assert "Deck not shuffled" in str(error)
        assert len(error.suggestions) > 0
        assert "Shuffle the deck" in error.suggestions[0]
    
    def test_invalid_deck_state_error_with_state(self):
        """Test InvalidDeckStateError with deck state."""
        deck_state = "uninitialized"
        error = InvalidDeckStateError("Invalid deck state", deck_state=deck_state)
        assert error.context["deck_state"] == deck_state


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""
    
    def test_configuration_error_inheritance(self):
        """Test configuration errors inherit properly."""
        assert issubclass(DeckLoadError, TarotConfigurationError)
        assert issubclass(SpreadError, TarotConfigurationError)
        assert issubclass(InvocationError, TarotConfigurationError)
        assert issubclass(ConfigError, TarotConfigurationError)
        assert issubclass(TarotConfigurationError, TarotOracleError)
    
    def test_provider_error_inheritance(self):
        """Test provider errors inherit properly."""
        assert issubclass(AuthenticationError, ProviderError)
        assert issubclass(NetworkError, ProviderError)
        assert issubclass(RateLimitError, ProviderError)
        assert issubclass(ProviderError, TarotOracleError)
    
    def test_validation_error_inheritance(self):
        """Test validation errors inherit properly."""
        assert issubclass(CardCodeError, ValidationError)
        assert issubclass(SemanticValidationError, ValidationError)
        assert issubclass(ValidationError, TarotOracleError)
    
    def test_file_operation_error_inheritance(self):
        """Test file operation errors inherit properly."""
        assert issubclass(PathTraversalError, FileOperationError)
        assert issubclass(FileOperationError, TarotOracleError)
    
    def test_state_error_inheritance(self):
        """Test state errors inherit properly."""
        assert issubclass(InvalidDeckStateError, StateError)
        assert issubclass(StateError, TarotOracleError)


class TestExceptionChaining:
    """Test exception chaining and context preservation."""
    
    def test_exception_catching(self):
        """Test that exceptions can be caught by their base types."""
        try:
            raise DeckLoadError("Deck file corrupted")
        except TarotConfigurationError as e:
            assert isinstance(e, DeckLoadError)
            assert "Deck file corrupted" in str(e)
        
        try:
            raise AuthenticationError("API key invalid")
        except ProviderError as e:
            assert isinstance(e, AuthenticationError)
            assert "API key invalid" in str(e)
        
        try:
            raise PathTraversalError("Dangerous path")
        except TarotOracleError as e:
            assert isinstance(e, PathTraversalError)
            assert "Dangerous path" in str(e)
    
    def test_custom_context_and_suggestions(self):
        """Test custom context and suggestions override defaults."""
        custom_context = {"custom": "value"}
        custom_suggestions = ["Custom suggestion 1", "Custom suggestion 2"]
        
        error = DeckLoadError(
            "Custom error",
            context=custom_context,
            suggestions=custom_suggestions
        )
        
        assert error.context == custom_context
        assert error.suggestions == custom_suggestions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])