# Tarot Oracle Remediation Plan

## Overview

This plan addresses critical blocking issues and prepares the codebase for planned feature updates including custom invocations, semantic spreads, and OpenRouter integration. The project will be modernized to use Python 3.10+ built-in types and structured as a publishable PyPI package.

## Phase 1: Critical Infrastructure Fixes

- Status: In Progress

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

- Status: Pending

### Task 2.1: Unified Type System
**Description**: Standardize on built-in generic types throughout the codebase
**Files to Modify**:
- `tarot_oracle/tarot.py` - Replace `typing` imports with built-in types
- `tarot_oracle/oracle.py` - Modernize type annotations  
- `tarot_oracle/roman_numerals.py` - Convert to modern syntax
- `tarot_oracle/config.py` - Update imports and property methods
**Status**: Completed

**Key Changes Completed**:
- ✅ Remove all `from typing import List, Dict, Optional, Tuple` imports
- ✅ Replace `List[str]` → `list[str]`, `Dict[str, int]` → `dict[str, int]`
- ✅ Replace `Optional[str]` → `str|None`
- ✅ Replace `Tuple[int, str]` → `tuple[int, str]`
- ✅ Keep `Any` only where essential for flexible API responses
- ✅ Update function signatures and variable annotations consistently
- ✅ Fixed CLI argument parsing with proper type safety
- ✅ Added explicit type coercion in config properties

**Requirements for Basic Unit Testing**:
- ✅ Run mypy type checking on all files
- ✅ Verify no type warnings or errors after changes
- ✅ Test that all function signatures still work correctly
- ✅ Validate complex nested types like `list[list[str]]` work as expected

### Task 2.2: Type Safety Improvements
- Status: Completed ✅
- Description: Remove type ignore comments and improve type inference
- Files to Modify:
  - `tarot_oracle/tarot.py` - Address type ignore comments (lines 423, 431, 433, 434, 444, 446, 455, 463)
  - Add Protocol types for client interfaces
  - Fix function signatures missing type annotations

**Key Changes Completed**:
- ✅ Added proper type hints for complex matrix operations in `SpreadRenderer`
- ✅ Fixed type casting issues in `_normalize_spread_layout` using `cast()` from typing
- ✅ Improved return type annotations in `render_json` method
- ✅ Added proper type assertions for client method calls in oracle.py
- ✅ Replaced all `# type: ignore` comments with proper type annotations
- ✅ Added `cast` import to both tarot.py and oracle.py for proper type handling
- ✅ Verified all function signatures have appropriate return type annotations

**Requirements for Basic Unit Testing**:
- ✅ Verified all type ignore comments have been removed
- ✅ Test proper type casting works with matrix operations
- ✅ Validated client method calls handle type checking correctly
- ✅ Ran comprehensive functionality tests to ensure no regressions

## Phase 3: Configuration Architecture

- Status: Pending

### Task 3.1: Centralized Configuration System
- Status: Pending
- Description: Implement unified configuration management with `~/.tarot-oracle/` directory structure
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
- Status: Pending
- Description: Create extensible loaders for custom invocations and spreads
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

- Status: Pending

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
- Use "z-ai/glm-4.5-air:free" as the default model

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

- Status: Pending

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

## Current Status & Priority

### Completed Tasks
- ✅ **Task 2.1: Unified Type System** - Successfully modernized type annotations throughout codebase (Iteration 2)
- ✅ **Task 2.2: Type Safety Improvements** - Removed all type ignore comments and improved type safety (Iteration 4)
- ✅ **Phase 1** - Critical infrastructure fixes completed in previous iteration

### Next Priority Tasks (Iteration 4)
1. ✅ **Task 2.2: Type Safety Improvements** - Remove remaining type ignore comments and fix function signatures (COMPLETED)
2. **Task 3.1: Centralized Configuration System** - Implement unified config management with `~/.tarot-oracle/` directory (NEXT)
3. **Task 3.2: Custom Feature Loaders** - Create loaders for custom invocations and spreads

### Implementation Priority

**Phase 2 (COMPLETED - Iteration 4)**: Tasks 2.1, 2.2 - Type system modernization and type safety improvements complete
**Phase 3 (NEXT - Iteration 5)**: Tasks 3.1, 3.2 - Build configuration and loader infrastructure for custom features
**Phase 4 (Iteration 6)**: Tasks 4.1, 4.2, 4.3 - Enable semantic enhancements, OpenRouter integration, and CLI unification
**Phase 5 (Final)**: Tasks 5.1, 5.2 - Add comprehensive error handling and documentation

Each phase should be completed and tested before proceeding to the next phase to ensure a stable foundation for subsequent development work.

### Blockers & Dependencies
- ✅ Task 2.2 completed - type safety blockers resolved
- Task 3.1 (Configuration) is prerequisite for Task 3.2 (Custom Loaders)  
- All subsequent phases depend on successful completion of Phase 2 (COMPLETED) and 3

### Iteration 4 Status Update
- Current iteration: 4
- Enhanced mode: Yes
- Progress: Task 2.1 completed, Task 2.2 COMPLETED ✅
- All type ignore comments successfully removed
- All function signatures now have proper type annotations
- Type safety improvements provide clean foundation for next development phase
