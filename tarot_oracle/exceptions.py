"""
Custom exceptions for the Tarot Oracle system.

This module provides a comprehensive hierarchy of custom exceptions for better
error handling, debugging, and user experience throughout the tarot-oracle
application.
"""


class TarotOracleError(Exception):
    """Base exception for all Tarot Oracle errors.
    
    All custom exceptions in the tarot-oracle system inherit from this base
    class to provide consistent error handling and user experience.
    
    Attributes:
        message (str): Human-readable error description
        context (dict, optional): Additional context information
        suggestions (list, optional): Suggested solutions for the user
    """
    
    def __init__(self, message: str, context: dict | None = None, suggestions: list | None = None):
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.suggestions = suggestions or []
    
    def __str__(self) -> str:
        result = self.message
        if self.suggestions:
            result += f"\n\nSuggestions:\n" + "\n".join(f"  • {s}" for s in self.suggestions)
        return result


class TarotConfigurationError(TarotOracleError):
    """Base exception for configuration-related errors."""
    pass


class DeckLoadError(TarotConfigurationError):
    """Raised when deck configuration cannot be loaded or is invalid.
    
    This includes issues with JSON parsing, missing required fields,
    invalid card definitions, or incompatible deck formats.
    """
    def __init__(self, message: str, deck_path: str | None = None, **kwargs):
        context = kwargs.get('context', {})
        if deck_path:
            context['deck_path'] = deck_path
        kwargs['context'] = context
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check that the deck file is valid JSON",
                "Verify all required fields are present",
                "Ensure card codes are in correct format",
                "Check deck file permissions"
            ]
        kwargs['suggestions'] = suggestions
        
        super().__init__(message, **kwargs)


class SpreadError(TarotConfigurationError):
    """Raised when spread configuration is invalid or cannot be loaded.
    
    This includes malformed JSON, missing semantic groups,
    invalid variable placeholders, or incompatible spread dimensions.
    """
    def __init__(self, message: str, spread_name: str | None = None, **kwargs):
        context = kwargs.get('context', {})
        if spread_name:
            context['spread_name'] = spread_name
        kwargs['context'] = context
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check that the spread file is valid JSON",
                "Verify semantic_groups are properly defined",
                "Ensure variable placeholders use correct format: ${element}",
                "Check spread layout dimensions"
            ]
        kwargs['suggestions'] = suggestions
        
        super().__init__(message, **kwargs)


class InvocationError(TarotConfigurationError):
    """Raised when invocation configuration is invalid or cannot be loaded.
    
    This includes missing invocation files, invalid file formats,
    or path-related security issues.
    """
    def __init__(self, message: str, invocation_name: str | None = None, **kwargs):
        context = kwargs.get('context', {})
        if invocation_name:
            context['invocation_name'] = invocation_name
        kwargs['context'] = context
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check that invocation files exist in the correct directory",
                "Verify file format is .txt or .md",
                "Check file permissions and accessibility",
                "Ensure invocation name is valid"
            ]
        kwargs['suggestions'] = suggestions
        
        super().__init__(message, **kwargs)


class ConfigError(TarotConfigurationError):
    """Raised when system configuration is invalid or cannot be loaded.
    
    This includes issues with config.json parsing, environment variable
    handling, or directory creation problems.
    """
    def __init__(self, message: str, config_path: str | None = None, **kwargs):
        context = kwargs.get('context', {})
        if config_path:
            context['config_path'] = config_path
        kwargs['context'] = context
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check that config.json is valid JSON",
                "Verify configuration directory exists and is writable",
                "Check environment variable names and values",
                "Reset configuration with default values if needed"
            ]
        kwargs['suggestions'] = suggestions
        
        super().__init__(message, **kwargs)


class ProviderError(TarotOracleError):
    """Base exception for AI provider-related errors."""
    
    def __init__(self, message: str, provider: str | None = None, **kwargs):
        context = kwargs.get('context', {})
        if provider:
            context['provider'] = provider
        kwargs['context'] = context
        super().__init__(message, **kwargs)


class AuthenticationError(ProviderError):
    """Raised when API authentication fails.
    
    This includes invalid API keys, missing authentication headers,
    or expired credentials.
    """
    
    def __init__(self, message: str, provider: str | None = None, **kwargs):
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check that API key is correct and valid",
                "Verify API key is set in environment variable or config",
                "Ensure API key has not expired",
                "Check provider-specific authentication requirements"
            ]
        kwargs['suggestions'] = suggestions
        super().__init__(message, provider, **kwargs)


class NetworkError(ProviderError):
    """Raised when network connectivity issues occur.
    
    This includes timeouts, connection refused, DNS resolution failures,
    and other network-related problems.
    """
    
    def __init__(self, message: str, provider: str | None = None, timeout: int | None = None, **kwargs):
        context = kwargs.get('context', {})
        if timeout:
            context['timeout'] = timeout
        kwargs['context'] = context
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check internet connection",
                "Verify firewall settings allow API access",
                "Try again after a brief delay",
                "Check if provider service is operational"
            ]
        kwargs['suggestions'] = suggestions
        super().__init__(message, provider, **kwargs)


class RateLimitError(ProviderError):
    """Raised when API rate limits are exceeded.
    
    This includes HTTP 429 responses and provider-specific rate limiting.
    """
    
    def __init__(self, message: str, provider: str | None = None, retry_after: int | None = None, **kwargs):
        context = kwargs.get('context', {})
        if retry_after:
            context['retry_after'] = retry_after
        kwargs['context'] = context
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                f"Wait {retry_after or 'a few'} seconds before retrying",
                "Upgrade API plan for higher rate limits",
                "Implement request batching to reduce calls",
                "Use cached responses when possible"
            ]
        kwargs['suggestions'] = suggestions
        super().__init__(message, provider, **kwargs)


class ValidationError(TarotOracleError):
    """Base exception for data validation errors."""
    pass


class CardCodeError(ValidationError):
    """Raised when card codes or notations are invalid.
    
    This includes malformed card codes, invalid card positions,
    or incompatible card formats.
    """
    
    def __init__(self, message: str, card_code: str | None = None, **kwargs):
        context = kwargs.get('context', {})
        if card_code:
            context['card_code'] = card_code
        kwargs['context'] = context
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Use card codes in format: rank-suit (e.g., 'ace-cups')",
                "Check deck-specific card code requirements",
                "Verify card exists in the selected deck",
                "Use --list-cards to see available cards"
            ]
        kwargs['suggestions'] = suggestions
        super().__init__(message, **kwargs)


class SemanticValidationError(ValidationError):
    """Raised when semantic validation fails.
    
    This includes dimension mismatches, invalid semantic groups,
    or malformed variable placeholders.
    """
    
    def __init__(self, message: str, **kwargs):
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Check spread dimensions match deck requirements",
                "Verify semantic variables use ${element} format",
                "Ensure all semantic groups are properly defined",
                "Check that placeholder elements are valid"
            ]
        kwargs['suggestions'] = suggestions
        super().__init__(message, **kwargs)


class FileOperationError(TarotOracleError):
    """Base exception for file operation errors."""
    pass


class PathTraversalError(FileOperationError):
    """Raised when path traversal security violations are detected.
    
    This is raised when file paths attempt to access directories outside
    the intended safe paths.
    """
    
    def __init__(self, message: str, attempted_path: str | None = None, **kwargs):
        context = kwargs.get('context', {})
        if attempted_path:
            context['attempted_path'] = attempted_path
        kwargs['context'] = context
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Use only relative paths within allowed directories",
                "Avoid '..' directory traversal patterns",
                "Use file names without directory components",
                "Check that file is in the correct data directory"
            ]
        kwargs['suggestions'] = suggestions
        super().__init__(message, **kwargs)


class StateError(TarotOracleError):
    """Base exception for invalid system state errors."""
    pass


class InvalidDeckStateError(StateError):
    """Raised when operations are attempted on invalid deck states.
    
    This includes drawing from unshuffled decks or invalid deck
    configurations.
    """
    
    def __init__(self, message: str, deck_state: str | None = None, **kwargs):
        context = kwargs.get('context', {})
        if deck_state:
            context['deck_state'] = deck_state
        kwargs['context'] = context
        
        suggestions = kwargs.get('suggestions', [])
        if not suggestions:
            suggestions = [
                "Shuffle the deck before drawing cards",
                "Check that deck is properly initialized",
                "Verify deck configuration is valid",
                "Reset deck to initial state"
            ]
        kwargs['suggestions'] = suggestions
        super().__init__(message, **kwargs)