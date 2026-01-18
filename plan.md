# Tarot Oracle Remediation Plan

## Overview

This plan addresses critical blocking issues and prepares the codebase for planned feature updates including custom invocations, semantic spreads, and OpenRouter integration. The project will be modernized to use Python 3.10+ built-in types and structured as a publishable PyPI package.

## Phase 1: Critical Infrastructure Fixes

### Task 1.1: Package Structure & Entry Points
**Description**: Create proper Python package structure with modern type annotations and PyPI-ready configuration
**Files to Create/Modify**:
- `tarot_oracle/__init__.py` - Create package initialization with proper exports
- `pyproject.toml` - Add modern Python packaging configuration
- `tarot_oracle/config.py` - Centralize configuration management

**Key Changes**:
- Use built-in generic types (`list[str]`, `dict[str, int]`, etc.) exclusively
- Define entry points for CLI tools (`tarot` and `oracle` commands)
- Centralize all hardcoded paths and configuration in Config class
- Set minimum Python version to 3.10+ in pyproject.toml
- Add project metadata: description, authors, license, dependencies

**Requirements for Basic Unit Testing**:
- Test package initialization and imports
- Verify configuration defaults and path resolution
- Validate entry point registration

### Task 1.2: Import Error Resolution
**Description**: Fix critical import errors preventing module loading
**Files to Modify**:
- `tarot_oracle/oracle.py:15-24` - Fix `numinous.tarot` import to `tarot_oracle.tarot`
- Remove `sys.path` manipulation (lines 13-14)

**Key Changes**:
- Replace `from numinous.tarot import` with `from tarot_oracle.tarot import`
- Remove unnecessary path manipulation code
- Verify all imports resolve correctly after changes

**Requirements for Basic Unit Testing**:
- Test successful import of oracle module
- Verify all imported classes and functions are accessible
- Test that both CLI entry points can import and initialize

### Task 1.3: Security Hardening
**Description**: Fix path traversal vulnerabilities and improve input validation
**Files to Modify**:
- `tarot_oracle/tarot.py:160-178` - `DeckLoader.resolve_deck_path()`
- `tarot_oracle/oracle.py:152-156` - `generate_session_filename()`
- `tarot_oracle/oracle.py:209` - File writing in `save_oracle_session()`

**Key Changes**:
- Add filename sanitization to prevent `../` attacks using regex validation
- Use `Path.resolve().is_relative_to()` for path validation
- Implement whitelist-based filename validation (alphanumeric, hyphens, underscores only)
- Add file size limits for deck configurations
- Validate JSON structure more thoroughly before processing

**Requirements for Basic Unit Testing**:
- Test path traversal attack prevention
- Verify filename sanitization works correctly
- Test that malicious filenames are rejected safely
- Validate file size limits are enforced

## Phase 2: Type System Modernization

### Task 2.1: Unified Type System
**Description**: Standardize on built-in generic types throughout the codebase
**Files to Modify**:
- `tarot_oracle/tarot.py` - Replace `typing` imports with built-in types
- `tarot_oracle/oracle.py` - Modernize type annotations  
- `tarot_oracle/roman_numerals.py` - Convert to modern syntax

**Key Changes**:
- Remove all `from typing import List, Dict, Optional, Tuple` imports
- Replace `List[str]` → `list[str]`, `Dict[str, int]` → `dict[str, int]`
- Replace `Optional[str]` → `str|None`
- Replace `Tuple[int, str]` → `tuple[int, str]`
- Keep `Any` only where essential for flexible API responses
- Update function signatures and variable annotations consistently

**Requirements for Basic Unit Testing**:
- Run mypy type checking on all files
- Verify no type warnings or errors after changes
- Test that all function signatures still work correctly
- Validate complex nested types like `list[list[str]]` work as expected

### Task 2.2: Type Safety Improvements
**Description**: Remove type ignore comments and improve type inference
**Files to Modify**:
- `tarot_oracle/tarot.py` - Address type ignore comments (lines 420, 422, 423, 433, 435, 444, 452)
- Add Protocol types for client interfaces

**Key Changes**:
- Add proper type hints for complex matrix operations in `SpreadRenderer`
- Create `APIClient` Protocol for different provider clients
- Improve generic type annotations for spread rendering
- Add explicit types for variables that need type inference help
- Replace `# type: ignore` comments with proper type annotations

**Requirements for Basic Unit Testing**:
- Verify all type ignore comments can be safely removed
- Test Protocol types work with all client implementations
- Validate matrix operation types handle edge cases correctly
- Run comprehensive type checking to ensure no regressions

## Phase 3: Configuration Architecture

### Task 3.1: Centralized Configuration System
**Description**: Implement unified configuration management with `~/.tarot-oracle/` directory structure
**Files to Create/Modify**:
- `tarot_oracle/config.py` - Create centralized configuration
- `tarot_oracle/tarot.py` - Replace hardcoded paths with Config references
- `tarot_oracle/oracle.py` - Use centralized config instead of environment variables

**Key Changes**:
- Create `Config` class with directory structure:
  ```
  ~/.tarot-oracle/
  ├── config.json      # Main configuration file
  ├── decks/          # Custom decks
  ├── invocations/    # Custom invocations  
  └── spreads/        # Custom spreads with semantics
  ```
- Add config.json file support for persistent configuration
- Integrate environment variable support (ORACLE_PROVIDER, GOOGLE_AI_API_KEY, etc.)
- Replace all hardcoded paths (`~/.tarot/`, `~/oracles/`) with Config class
- Add automatic directory creation with proper error handling
- Migrate environment variable defaults to Config class
- Add validation for directory permissions and disk space
- Support configuration precedence: config.json > environment variables > defaults

**Requirements for Basic Unit Testing**:
- Test Config class initialization and defaults
- Verify config.json file loading and parsing
- Test environment variable integration
- Verify directory creation and permission handling
- Test path resolution for all subdirectories
- Validate migration from old hardcoded paths
- Test error handling when directories cannot be created
- Test configuration precedence (config.json > env vars > defaults)

### Task 3.2: Custom Feature Loaders
**Description**: Create extensible loaders for custom invocations and spreads
**Files to Create/Modify**:
- `tarot_oracle/loaders.py` - Create unified loader system
- `tarot_oracle/tarot.py` - Integrate custom loaders and update DeckLoader
- `tarot_oracle/oracle.py` - Use custom invocations from loader system

**Key Changes**:
- Create `InvocationLoader` class with `load_invocation(name)` and `list_invocations()` methods
  - Support plain .txt/.md files (not JSON format)
  - Simple file loading and listing functionality
  - Integration with Oracle class for reading sessions
- Create `SpreadLoader` class for custom spreads with semantic hints
  - Support JSON format with semantic_groups, semantics matrix, and guidance
  - Variable placeholder syntax validation
  - Matrix validation for position and semantic alignment
- Extend existing `DeckLoader` to use centralized paths from Config
- Implement consistent error handling across all loaders
- Add file validation (JSON structure for spreads/decks, plain text for invocations)
- Support multiple file formats: `.txt/.md` (invocations) and `.json` (spreads, decks)

**Requirements for Basic Unit Testing**:
- Test loading valid invocations (plain text) and spreads (JSON)
- Test error handling for malformed files
- Verify listing functions return expected metadata
- Test file validation rejects invalid content
- Validate loader handles missing directories gracefully
- Test invocation integration with Oracle class
- Test variable placeholder syntax validation in spreads

## Phase 4: Feature Integration Preparation

### Task 4.1: Enhanced Semantic System
**Description**: Refactor semantic analysis to support custom guidance rules with variable placeholder syntax
**Files to Modify**:
- `tarot_oracle/tarot.py:588-704` - Enhance `SemanticAdapter` class
- `tarot_oracle/tarot.py:137-155` - Extend `SEMANTICS` structure

**Key Changes**:
- Add support for semantic_groups with descriptions in spread definitions
- Implement variable placeholder syntax like "${water}", "${fire}", "${air}", "${earth}", "${spirit}" in semantics matrix
- Add guidance rules with markdown output formatting
- Include support for Zodiac and Zodiac Plus spreads in semantic system
- Create `SemanticAnalyzer` class for rule-based interpretation
- Implement semantic rule processing with condition matching
- Extend `SemanticAdapter` to process both position semantics and general guidance
- Add rule prioritization and conflict resolution
- Ensure semantic system supports all built-in spreads including Zodiac and Zodiac Plus

**Requirements for Basic Unit Testing**:
- Test semantic rule matching with various card combinations
- Verify variable placeholder syntax works correctly
- Test semantic group processing and descriptions
- Verify markdown output format is correct
- Test guidance rule prioritization
- Validate that both position semantics and general rules work together
- Test edge cases like no matching rules or conflicting rules
- Test Zodiac and Zodiac Plus spread semantic integration

### Task 4.2: OpenRouter Integration
**Description**: Add OpenRouter client to oracle system
**Files to Modify**:
- `tarot_oracle/oracle.py` - Add `OpenRouterClient` class
- `tarot_oracle/oracle.py:32-40` - Update provider selection logic
- Update CLI argument parsing for OpenRouter options

**Key Changes**:
- Implement `OpenRouterClient` class with consistent interface to existing clients
- Add OpenRouter to provider choices in CLI and initialization
- Support OpenRouter-specific model selection (anthropic, openai, etc.)
- Add OpenRouter-specific configuration (API key, model preferences)
- Implement proper error handling for API rate limits and authentication
- Add model capability checking and fallback logic

**Requirements for Basic Unit Testing**:
- Test OpenRouter client initialization with valid/invalid API keys
- Verify API calls are formatted correctly
- Test error handling for network failures and API errors
- Validate model selection and fallback logic
- Test timeout handling and retry logic if implemented

### Task 4.3: CLI Unification
**Description**: Consolidate separate CLI tools into unified interface
**Files to Create/Modify**:
- `tarot_oracle/cli.py` - Create unified CLI with subcommands
- `pyproject.toml` - Update entry points to use unified CLI
- `tarot_oracle/tarot.py:837-968` - Refactor main function to be subcommand
- `tarot_oracle/oracle.py:407-478` - Refactor main function to be subcommand

**Key Changes**:
```bash
# New unified CLI structure
tarot-oracle reading "question" [options]
tarot-oracle deck list|create <name>
tarot-oracle invocation list|create <name>
tarot-oracle spread list|create <name>
```
- Create argument subparsers for different commands
- Maintain backward compatibility with existing CLI interfaces
- Add help system and command-specific documentation
- Implement consistent error handling across subcommands
- Add completion suggestions and validation

**Requirements for Basic Unit Testing**:
- Test all subcommands parse arguments correctly
- Verify backward compatibility with existing CLI calls
- Test error handling for invalid arguments and subcommands
- Validate help system works correctly
- Test that both old and new CLI entry points function

## Phase 5: Code Quality & Testing Infrastructure

### Task 5.1: Error Handling & Custom Exceptions
**Description**: Implement comprehensive error handling with custom exception hierarchy
**Files to Create/Modify**:
- `tarot_oracle/exceptions.py` - Create custom exception classes
- All existing files - Replace generic exceptions with specific ones
- `tarot_oracle/config.py` - Add config-specific exceptions

**Key Changes**:
- Create `TarotOracleError` base class with proper inheritance
- Add specific exceptions: `DeckLoadError`, `SpreadError`, `InvocationError`, `ConfigError`
- Implement proper exception chaining and context preservation
- Add user-friendly error messages with suggested solutions
- Create exception handling utilities for common patterns
- Add logging integration for error tracking

**Requirements for Basic Unit Testing**:
- Test each custom exception type is raised correctly
- Verify exception messages contain expected information
- Test exception chaining preserves context
- Validate error handling utilities work as expected
- Test logging integration captures error details

### Task 5.2: Documentation & Type Documentation
**Description**: Add comprehensive docstrings and type documentation
**Files to Modify**:
- All Python files - Standardize docstring format
- Add inline type documentation for complex return types

**Key Changes**:
- Use Google-style docstrings consistently across all modules
- Add detailed parameter and return type documentation
- Include usage examples in docstrings for public APIs
- Add type annotations for all complex nested structures
- Document configuration options and their defaults
- Add CLI help documentation with examples

**Requirements for Basic Unit Testing**:
- Test docstring examples work correctly (doctest)
- Verify all public functions have proper documentation
- Validate that help text is informative and accurate
- Test that type documentation matches actual implementations

## Testing Infrastructure Requirements

### Basic Unit Testing Framework
**Files to Create**:
- `tests/` directory structure
- `tests/__init__.py`
- `tests/test_config.py`
- `tests/test_tarot.py`
- `tests/test_oracle.py`
- `tests/test_loaders.py`
- `tests/test_exceptions.py`
- `tests/test_cli.py`
- `conftest.py` - PyTest configuration and fixtures

**Test Coverage Requirements**:
- Minimum 80% line coverage for core functionality
- 100% coverage for security-critical functions
- All custom exception types tested
- All configuration options validated
- All CLI subcommands tested

### Test Categories
1. **Unit Tests**: Individual function and class method testing
2. **Integration Tests**: Module interaction and workflow testing
3. **Security Tests**: Path traversal, input validation, file handling
4. **Type Tests**: Mypy validation and type checking
5. **CLI Tests**: Argument parsing and command execution

### Test Data and Fixtures
- Sample deck configuration files (valid and invalid)
- Test invocation texts
- Sample spread definitions
- Mock API responses for testing
- Temporary directory fixtures for file system tests

### Continuous Integration Setup
- GitHub Actions or similar CI/CD pipeline
- Automated testing on multiple Python versions (3.10+)
- Type checking with mypy
- Code formatting validation (black, ruff)
- Security scanning for dependencies

## Implementation Priority

**Phase 1 (Critical Blocking)**: Tasks 1.1, 1.2, 1.3 - Must be completed before any feature work
**Phase 2 (Foundational)**: Tasks 2.1, 2.2 - Enables proper type checking and development workflow
**Phase 3 (Structural)**: Tasks 3.1, 3.2 - Required infrastructure for new feature architecture
**Phase 4 (Feature Enablement)**: Tasks 4.1, 4.2, 4.3 - Directly enables planned features
**Phase 5 (Quality Assurance)**: Tasks 5.1, 5.2 - Improves reliability, maintainability, and testability

Each phase should be completed and tested before proceeding to the next phase to ensure a stable foundation for subsequent development work.