# Implementation Plan

## Tasks

### Task 3.2: Custom Feature Loaders

- Status: Completed ✅
- Description: Create extensible loaders for custom invocations and spreads
- Acceptance Criteria:
        - ✅ Create `InvocationLoader` class with `load_invocation(name)` and `list_invocations()` methods
        - ✅ Support plain .txt/.md files for invocations (not JSON format)
        - ✅ Create `SpreadLoader` class for custom spreads with semantic hints (JSON format)
        - ✅ Implement variable placeholder syntax validation for spreads
        - ✅ Extend existing `DeckLoader` to use centralized paths from Config
        - ✅ Add consistent error handling across all loaders
        - ✅ Test file validation (JSON structure for spreads/decks, plain text for invocations)

### Task 4.1: Enhanced Semantic System

- Status: Done ✅
- Description: Refactor semantic analysis to support custom guidance rules with variable placeholder syntax
- Acceptance Criteria:
        - ✅ Add support for semantic_groups with descriptions in spread definitions
        - ✅ Implement variable placeholder syntax like "${water}", "${fire}", "${air}", "${earth}", "${spirit}" in semantics matrix
        - ✅ Add guidance rules with markdown output formatting
        - ✅ Create `SemanticAnalyzer` class for rule-based interpretation
        - ✅ Extend SemanticAdapter to process both position semantics and general guidance
        - ✅ Test Zodiac and Zodiac Plus spread semantic integration

### Task 4.2: OpenRouter Integration

- Status: Pending
- Description: Add OpenRouter client to oracle system
- Acceptance Criteria:
        - Implement `OpenRouterClient` class with consistent interface to existing clients
        - Add OpenRouter to provider choices in CLI and initialization
        - Support OpenRouter-specific model selection
        - Add OpenRouter-specific configuration (API key, model preferences)
        - Implement proper error handling for API rate limits and authentication
        - Use "z-ai/glm-4.5-air:free" as the default model

### Task 4.3: CLI Unification

- Status: Pending
- Description: Consolidate separate CLI tools into unified interface
- Acceptance Criteria:
        - Create unified CLI with subcommands (reading, deck, invocation, spread)
        - Maintain backward compatibility with existing CLI interfaces
        - Add help system and command-specific documentation
        - Implement consistent error handling across subcommands
        - Update pyproject.toml entry points to use unified CLI

### Task 5.1: Error Handling & Custom Exceptions

- Status: Pending
- Description: Implement comprehensive error handling with custom exception hierarchy
- Acceptance Criteria:
        - Create `TarotOracleError` base class with proper inheritance
        - Add specific exceptions: `DeckLoadError`, `SpreadError`, `InvocationError`, `ConfigError`
        - Implement proper exception chaining and context preservation
        - Add user-friendly error messages with suggested solutions
        - Add logging integration for error tracking

### Task 5.2: Documentation & Type Documentation

- Status: Pending
- Description: Add comprehensive docstrings and type documentation
- Acceptance Criteria:
        - Use Google-style docstrings consistently across all modules
        - Add detailed parameter and return type documentation
        - Include usage examples in docstrings for public APIs
        - Add type annotations for all complex nested structures
        - Document configuration options and their defaults

## Dependencies

### Critical Path Dependencies
1. **Task 3.1 (Completed)** → **Task 3.2**: Configuration system provides centralized paths for loaders
2. **Task 3.2** → **Task 4.1**: Custom loaders enable semantic enhancements
3. **Task 3.2** → **Task 4.2**: Loaders support custom features for OpenRouter integration
4. **Task 4.1** → **Task 4.3**: Enhanced semantics inform unified CLI design
5. **All core tasks** → **Task 5.1**: Exception handling applied across completed features
6. **All core tasks** → **Task 5.2**: Documentation covers final implementation

### Prerequisites
- Task 3.1: Centralized Configuration (COMPLETED ✅)
- Task 2.1-2.2: Type System Modernization (COMPLETED ✅)
- Phase 1: Critical Infrastructure (COMPLETED ✅)

## Current Status & Priority

### Completed Tasks
- ✅ **Task 3.2: Custom Feature Loaders** - Create extensible loaders for custom invocations and spreads (COMPLETED - Iteration 9)
- ✅ **Task 3.1: Centralized Configuration System** - Implement unified config management with `~/.tarot-oracle/` directory structure
- ✅ **Task 2.1: Unified Type System** - Modernized type annotations throughout codebase
- ✅ **Task 2.2: Type Safety Improvements** - Removed all type ignore comments and improved type safety
- ✅ **Phase 1: Critical Infrastructure Fixes** - Package structure, import errors, and security hardening

### Next Priority Tasks (Iteration 11)
1. **Task 4.2: OpenRouter Integration** - Add OpenRouter client to oracle system
2. **Task 4.3: CLI Unification** - Consolidate separate CLI tools into unified interface
3. **Task 5.1: Error Handling & Custom Exceptions** - Add comprehensive error handling

### Implementation Priority

**Phase 3 (COMPLETED - Iteration 9)**: Task 3.2 - Build loader infrastructure for custom features
**Phase 4 (CURRENT - Iteration 11)**: Tasks 4.2, 4.3 - Enable OpenRouter integration and CLI unification
**Phase 5 (Final)**: Tasks 5.1, 5.2 - Add comprehensive error handling and documentation

Each phase should be completed and tested before proceeding to the next phase to ensure a stable foundation for subsequent development work.

### Iteration 10 Status Update
- Current iteration: 10
- Enhanced mode: Yes
- Progress: Task 3.2 COMPLETED ✅
- Custom feature loader system fully implemented with comprehensive security validation
- InvocationLoader and SpreadLoader classes complete with variable placeholder support
- Path traversal prevention and filename sanitization implemented across all loaders
- Integration with centralized config system verified
- Comprehensive test coverage for all loader functionality
- Ready to proceed with Task 4.1: Enhanced Semantic System