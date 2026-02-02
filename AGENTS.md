# AGENTS.md - Repository Guidelines for Coding Agents

This file provides essential information for agentic coding systems working in the tarot-oracle repository.

## Build, Lint, and Test Commands

### Running Tests
- **All tests**: `python -m unittest discover -s tests`
- **Single test**: `python -m unittest tests.test_module.TestClass.test_method`
  - Example: `python -m unittest tests.test_tarot.TestTarot.test_deck_loader_security`
- **Pytest alternative**: `python -m pytest tests/` (if pytest is installed)

### Build Commands
- No build commands required - uses Python packaging with pyproject.toml
- Install with: `pip install -e .` for development mode

### Linting/Type Checking
- **No linting tools currently configured** (no ruff, mypy, black, etc.)
- If adding linting, check pyproject.toml for existing configurations first

## Code Style Guidelines

### Python Version
- Minimum: Python 3.10+
- Use Python 3.10+ built-in types (PEP 604 style)

### Type Annotations
- Use union type syntax with `|`: `str | None` instead of `Optional[str]`
- Use built-in generics: `list[str]` instead of `List[str]`, `dict[str, Any]` instead of `Dict[str, Any]`
- Import from `typing` only for special cases: `Any`, `cast`, `NoReturn`
- Annotate all function parameters and return types

Example:
```python
from typing import Any, cast

def load_deck(name: str) -> dict[str, Any] | None:
    """Load deck by name."""
    result = process_deck(name)
    return cast(dict[str, Any], result) if result else None
```

### Imports
- **All `from x import y` style imports first, alphabetized**
- **All `import x` style imports last, alphabetized**
- Group by: standard library, third-party (with fallback handling for optional deps), then local
- At package level, import config instance: `from tarot_oracle.config import config`

Example:
```python
# From imports (alphabetized)
from argparse import ArgumentParser
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from secrets import token_bytes
from sys import argv, stdin
from time import time
from typing import Any, cast

# Optional third-party with fallback
try:
    from google import genai
except ImportError:
    genai = None

# Local from imports (alphabetized)
from tarot_oracle.config import config
from tarot_oracle.loaders import SpreadLoader
from tarot_oracle.tarot import Deck

# Bare imports (alphabetized)
import ast
import json
import os
import re
```

### Naming Conventions
- **Classes**: PascalCase (`DeckLoader`, `SpreadRenderer`, `TarotDivination`)
- **Functions/Methods**: snake_case (`load_deck`, `resolve_spread`, `perform_reading`)
- **Constants**: UPPER_SNAKE_CASE (`MAJOR_ARCANA`, `SPREADS`, `SEMANTICS`)
- **Private methods**: `_leading_underscore` (`_load_config`, `_ensure_directories`)
- **Instance variables**: snake_case (`self.cards`, `self.deck`)

### Error Handling
- **Use standard exceptions only**: `ValueError`, `TypeError`, `ImportError`, `OSError`
- **No custom exception classes** (intentionally removed - see comments in codebase)
- Always include context in error messages: file paths, invalid values, expected types

Example:
```python
# Good - standard exception with context
if 'name' not in config:
    raise ValueError(f"Deck configuration must include 'name' field: {path}")

if not api_key:
    raise ValueError("GOOGLE_AI_API_KEY environment variable must be set for Gemini provider")

# Bad - don't create custom exceptions
class TarotError(Exception):  # AVOID THIS
    pass
```

### Security Best Practices
- **Path traversal prevention**: Sanitize filenames with regex before use
- **Directory validation**: Ensure resolved paths are within allowed directories
- **Filename sanitization**: Remove dangerous characters (`..`, `/`, `\`, etc.)

Example:
```python
import re
from pathlib import Path

safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
safe_filename = safe_filename.lstrip('.-')

resolved = path.resolve()
if not (resolved.is_relative_to(Path.cwd()) or resolved.is_relative_to(config.home_dir)):
    raise ValueError(f"Attempted to access file outside allowed directories: {path}")
```

### File I/O
- Always specify `encoding='utf-8'` when opening text files
- Use `Path` objects from pathlib for file operations
- Use context managers (`with open(...)`)

Example:
```python
with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)
```

### Documentation Style
- **Concise docstrings only** - maximum 4 lines, paragraph format
- Describe purpose and critical details only
- **No** line-by-line parameter descriptions (Args:, Returns:, Raises: sections)
- **No** lengthy usage examples or novels
- Just 1-4 lines (soft-max 72 chars per line) with most important information
- Lines beyond the first are indented
- The final triple quote goes on its own line

Example:
```python
def load_deck(self, deck_name: str) -> "Deck":
    """Load deck by name using search order. Returns loaded deck instance,
        raises ValueError if not found.
    """
```

Example (multi-line paragraph):
```python
def load_deck(self, deck_name: str) -> "Deck":
    """Load deck by name using search order. Searches current directory
        then ~/.tarot-oracle/decks. Returns loaded deck instance, raises
        ValueError if file not found or invalid.
    """
```

### Data Structures
- Use `dataclass` for simple data containers
- Use typed dictionaries for configuration data
- Prefer `dict[str, Any]` over untyped dicts

### Testing Conventions
- Use `unittest.TestCase` for test classes
- Use `assert` for assertions (not self.assertEqual unless needed)
- Create temp directories with `tempfile.TemporaryDirectory()` context manager
- Clean up created files in `finally` blocks

Example:
```python
import unittest
import tempfile

class TestLoaders(unittest.TestCase):
    def test_path_traversal_prevention(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test logic here
            try:
                # Create test files
                ...
            finally:
                # Cleanup
                ...
```

### Configuration
- Use centralized config: `from tarot_oracle.config import config`
- Access config values via properties or `get()` method
- Config precedence: defaults → config file → environment variables → runtime

### CLI Patterns
- Use `argparse.ArgumentParser` for CLI interfaces
- Create subparsers for multi-command CLIs
- Return `int` exit codes from main functions (0 = success, non-zero = error)

## Project Structure
- `tarot_oracle/` - Main package
  - `tarot.py` - Core tarot functionality (cards, decks, spreads)
  - `oracle.py` - AI integration (Gemini, OpenRouter, Ollama)
  - `config.py` - Centralized configuration management
  - `loaders.py` - Custom content loaders (invocations, spreads, decks)
  - `cli.py` - Unified CLI entry point
  - `data_loader.py` - Bundled data loader for package resources
- `tests/` - Test modules (unittest framework)

## Important Notes
- **No comments in code** unless explicitly requested
- This project is in active development (v0.1.0 work-in-progress)
- All file operations must validate paths to prevent directory traversal
- Always use UTF-8 encoding for file I/O
- Use standard Python exceptions only - no custom exceptions
