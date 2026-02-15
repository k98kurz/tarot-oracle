# AGENTS.md - Repository Guidelines for Coding Agents

This file provides essential information for agentic coding systems working in the tarot-oracle repository.

##  Prerequisites
- **Virtual environment activation**: Always run `source venv/bin/activate` before executing any Python or pip commands
- This ensures commands use the correct Python environment and dependencies

## Build, Lint, and Test Commands

### Running Tests
- **All tests**: `python -m unittest discover -s tests`
- **Single test**: `python -m unittest tests.test_module.TestClass.test_method`
  - Example: `python -m unittest tests.test_tarot.TestTarot.test_deck_loader_security`
- **Pytest alternative**: `python -m pytest tests/` (if pytest is installed)
- Do not use tinyllama. tinyllama is retarded.

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

### Line Lengths
- Soft-max line length of 80 chars for normal code and 72 chars for docstrings
- Docstrings should look like the following:
```python
def something():
    """This is the docstring for something(). It will wrap around onto
        the next line indented in one additional tab length, then it
        will end with the closing triple quotes on a new line.
    """
    ...
```
- If a piece of code calling a function will be too long, start the args on a new line:
```python
        # some indented code
        thing = some_class.some_method(
            "this is the first thing" if some_param > some_threshold else
            "this is the alternate",
            123
        )
```
- If a print statement is too long, break apart the string:
```python
        # some indented code
        print(
            "This is a very long print statement with f-string: "
            f"{some_dict['some_key'] if 'some_key' in some_dict else 'nope'}"
        )
```
- If a conditional is too long, use a backslash to continue on the next line:
```python
        # some indented code
        if something.value < threshold and something_else in whatever \
            and one_more_condition:
            ...
```

### Type Annotations
- Use union type syntax with `|`: `str | None` instead of `Optional[str]`
- Use built-in generics: `list[str]` instead of `List[str]`, `dict[str, Any]` instead of `Dict[str, Any]`
- Import from `typing` only for special cases: `Any`, `cast`, `NoReturn`
- Annotate all function parameters and return types

Example:
```python
from crossconfig import get_config, ConfigProtocol

def config() -> ConfigProtocol:
    """Get crossconfig instance, loading config if keys not initialized."""
    conf = get_config("tarot-oracle")
    if len(conf.list()) == 0:
        conf.load()
    return conf
```

### Imports
- **All `from x import y` style imports first, alphabetized**
- **All `import x` style imports last, alphabetized**
- Group by: standard library, third-party (with fallback handling for optional deps), then local

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
from .loaders import SpreadLoader
from .tarot import Deck

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
- **Path traversal prevention**: Use `sanitize_filename()` from helpers before using filenames
- **Directory validation**: Use `validate_path_security()` from helpers to validate paths
- **Filename sanitization**: Handled by `sanitize_filename()` which removes dangerous characters

Example:
```python
from pathlib import Path
from .helpers import sanitize_filename, validate_path_security, config

# Sanitize filename
safe_filename = sanitize_filename(filename)
if safe_filename is None:
    return None

# Validate path security
resolved = path.resolve()
validate_path_security(resolved, str(path))
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
- Use `from .helpers import config`
- The `config()` function handles lazy loading automatically when `len(conf.list()) == 0`
- Access config values via `get()` method or `path()` for directories
- Config precedence: defaults → config file → environment variables → runtime

### CLI Patterns
- Use `argparse.ArgumentParser` for CLI interfaces
- Create subparsers for multi-command CLIs
- Return `int` exit codes from main functions (0 = success, non-zero = error)

## Project Structure
- `tarot_oracle/` - Main package
  - `tarot.py` - Core tarot functionality (cards, decks, spreads)
  - `oracle.py` - AI integration (Gemini, OpenRouter, Ollama)
  - `loaders.py` - Custom content loaders (invocations, spreads, decks)
  - `data_loader.py` - Bundled data loader for package resources
  - `helpers.py` - Shared helper functions (config, security, utilities)
  - `version.py` - Package version information
- `tests/` - Test modules (unittest framework)

## Important Notes
- **No comments in code** unless explicitly requested
- This project is in active development (v0.1.0 work-in-progress)
- All file operations must validate paths to prevent directory traversal (use helpers)
- Always use UTF-8 encoding for file I/O
- Use standard Python exceptions only - no custom exceptions
- Use helper functions from `helpers.py` for common patterns (config, security, directories)
