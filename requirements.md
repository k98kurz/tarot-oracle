# Tarot Oracle Requirements

## Overview

This document outlines the requirements for the major features that the Tarot Oracle library must support. The library provides a comprehensive tarot divination system with AI-powered interpretation and semantic analysis.

## Feature Requirements

### 1. Tarot Readings ✅ Completed

**Core Functionality:**
- Multiple built-in spread configurations:
  - Single Card
  - Three Card (Past, Present, Future)
  - Five Card Cross
  - Celtic Cross (10 cards)
  - Crowley/Golden Dawn Spread (15 cards)
  - Zodiac Spread (12 cards)
  - Zodiac Plus Spread (13 cards)
- Card drawing with random selection
- Position-based card placement
- Reversed card support
- Spread rendering with semantic groupings
- Text output formatting with legends and interpretations

**Technical Requirements:**
- Support for custom deck loading
- Matrix-based card positioning system
- Semantic analysis for card positions
- Markdown-formatted output
- Configurable default spread

### 2. Oracle Integrations with AIs 🔄 Partially Done

**Current Implementation:**
- Google Gemini integration (complete)
- Ollama integration for local models (complete)

**Required Enhancements:**
- OpenRouter integration (planned)
- Support for multiple AI providers with fallback logic
- Model selection capabilities
- API key management and validation
- Error handling for rate limits and network failures
- Session management and autosave functionality

**Technical Requirements:**
- Unified client interface for all AI providers
- Provider-specific configuration options
- Custom model parameter support
- Timeout and retry logic
- Session persistence with unique identifiers

### 3. Custom Decks ✅ Completed

**Functionality:**
- JSON-based deck configuration files
- Custom card definitions with meanings
- Suit and rank customization
- Image path support for cards
- Deck validation and error handling
- Dynamic deck loading from ~/.tarot-oracle/decks/

**Technical Requirements:**
- DeckLoader class with validation
- Support for custom Major/Minor Arcana
- Reversed card meaning support
- File path security validation
- Metadata preservation (author, description, version)

### 4. Custom Spreads with Semantics and Interpretation Guidance ❌ Not Started

**Required Features:**
- JSON-based spread definition format
- Custom position matrices (rows × columns)
- Semantic group assignments for positions
- Per-card semantic hints
- Guidance rules for interpretation
- Position descriptions and meanings

**Spread Definition Structure:**
```json
{
  "name": "Custom Spread Name",
  "description": "Spread description",
  "positions": [
    [card_indices_matrix]
  ],
  "semantic_groups": {
    "group_name": "Group description"
  },
  "semantics": [
    [semantic_hints_matrix]
  ],
  "guidance": [
    "Interpretation guidance rules"
  ]
}
```

**Technical Requirements:**
- SpreadLoader class for dynamic loading
- Semantic analysis engine with rule processing
- Guidance rule matching and prioritization
- Matrix validation for position and semantic alignment
- Support for variable-sized spreads
- The semantic hints matrix will use a var placeholder syntax (see example in readme.md)

### 5. Basic Test Coverage ❌ Not Started

**Testing Infrastructure:**
- PyTest-based test framework
- Minimum 80% line coverage for core functionality
- 100% coverage for security-critical functions
- Automated testing on multiple Python versions (3.10+)

**Test Categories:**
1. **Unit Tests:**
   - Individual function and class method testing
   - Type checking with mypy
   - Exception handling validation

2. **Integration Tests:**
   - Module interaction and workflow testing
   - CLI command execution
   - File system operations

3. **Security Tests:**
   - Path traversal attack prevention
   - Input validation and sanitization
   - File permission handling

4. **Feature Tests:**
   - Tarot reading generation
   - Deck loading and validation
   - Spread configuration parsing
   - AI provider integration

**Test Data Requirements:**
- Sample deck configurations (valid/invalid)
- Test spread definitions
- Mock API responses (do not call AI providers for testing)
- Temporary directory fixtures

## Implementation Priority

### Phase 1: Foundation (Critical)
- Complete package structure and entry points
- Fix import errors and security vulnerabilities
- Modernize type system to Python 3.10+ built-in types
- Implement centralized configuration system

### Phase 2: Core Features
- Implement custom invocations system (just plain .md or .txt files)
- Implement custom spread system with semantics
- Complete OpenRouter integration
- Add comprehensive error handling with custom exceptions

### Phase 3: Quality Assurance
- Implement complete test coverage
- Add documentation and examples
- CLI unification and optimization

## Technical Constraints

### Security Requirements
- Path traversal attack prevention
- Input validation and sanitization
- Secure file handling with permission checks
- API key protection and validation
- File size limits for user uploads

### Performance Requirements
- Fast deck loading and validation
- Efficient card drawing algorithms
- Responsive AI integration with timeouts
- Minimal memory footprint for large spreads

### Compatibility Requirements
- Python 3.10+ support only
- Cross-platform compatibility (Linux, macOS, Windows)
- PyPI package distribution
- Modern dependency management with pyproject.toml

## Configuration Requirements

### Directory Structure
```
~/.tarot-oracle/
├── config.json      # Main configuration
├── decks/          # Custom deck configurations
├── invocations/    # Custom invocation texts
└── spreads/        # Custom spread definitions
```

### Environment Variables
- `ORACLE_PROVIDER` - AI provider selection
- `GOOGLE_AI_API_KEY` - Gemini API key
- `OPENROUTER_API_KEY` - OpenRouter API key
- `OLLAMA_HOST` - Ollama server host
- `AUTOSAVE_SESSIONS` - Session autosave toggle
- `AUTOSAVE_LOCATION` - Session save directory

## Success Criteria

### Functional Success
- All major features working as specified
- AI integrations functional with proper fallbacks (manual verification)
- Custom content system fully operational
- Comprehensive test coverage achieved

### Quality Success
- Zero security vulnerabilities
- Clean code with proper type annotations (using Python 3.10+ syntax; e.g. `list[str]|None` not `Optional[List[str]]`)
- Useful documentation
- User-friendly CLI interface
