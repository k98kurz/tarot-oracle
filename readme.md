# Tarot Oracle

A comprehensive tarot divination system with AI-powered interpretation and semantic analysis. Features custom deck loading, multiple spread configurations, and integration with various AI providers for guided readings.

## Status

This is currently a work-in-progress. Remaining work before the v0.1.0 release:

- [ ] Package structure & entry points (pyproject.toml, __init__.py)
- [ ] Import error resolution (fix numinous.tarot imports)
- [ ] Security hardening (path traversal fixes, input validation)
- [ ] Type system modernization (Python 3.10+ built-in types)
- [ ] Centralized configuration system (~/.tarot-oracle/ directory with config.json)
- [ ] Custom feature loaders (plain text invocations, semantic spreads, decks)
- [ ] Enhanced semantic system with guidance rules and variable placeholder syntax
- [ ] OpenRouter integration for additional AI providers
- [ ] CLI unification with subcommands
- [ ] Comprehensive error handling with custom exceptions
- [ ] Testing infrastructure and documentation

Issues are tracked in the project repository. Historical changes can be found in the changelog.

## Planned Features

### Core Functionality
- Custom tarot deck creation and loading
- Multiple spread configurations (Celtic Cross, Three Card, etc.)
- Semantic analysis with position-based interpretations
- AI-powered reading interpretations

### AI Provider Integration
- Google Gemini (currently implemented)
- Ollama (local models)
- OpenRouter (planned) - Access to Claude, GPT-4, and other models
- Custom model configuration and fallback logic

### Custom Content System
- Custom invocations for different traditions
- Custom spreads with semantic hints
- User-created deck configurations
- Guidance rules for focused/relevant interpretations

## Usage

Install with `pip install tarot-oracle`. The project provides both CLI tools and Python APIs.

### Basic Reading

```bash
# Generate a Celtic Cross reading
tarot-oracle reading "What guidance do you seek?" --spread celtic-cross

# Use a specific deck
tarot-oracle reading "Question about career" --deck rider-waite

# Get AI interpretation
tarot-oracle reading "Life path question" --provider gemini --interpret
```

### Python API

```python
from tarot_oracle import TarotDivination, SpreadRenderer
from tarot_oracle.tarot import SPREADS, Card

# Create a reading
divination = TarotDivination()
cards = divination.draw_cards("celtic-cross")

# Render the spread
renderer = SpreadRenderer()
output = renderer.render_spread(cards, "celtic-cross")
print(output)
```

### Custom Decks

```python
from tarot_oracle.tarot import DeckLoader

# Load a custom deck
loader = DeckLoader()
custom_deck = loader.load_deck("my-custom-deck")

# Use in reading
divination = TarotDivination(deck=custom_deck)
```

### AI Integration

```python
from tarot_oracle.oracle import OracleClient

# Use Gemini for interpretation
client = OracleClient(provider="gemini", api_key="your-api-key")
interpretation = client.interpret_reading(cards, question="Your question")
print(interpretation)
```

## Configuration

The system uses a centralized configuration in `~/.tarot-oracle/`:

```
~/.tarot-oracle/
├── config.json      # Main configuration
├── decks/          # Custom deck configurations
├── invocations/    # Custom invocation texts
└── spreads/        # Custom spread definitions
```

### Environment Variables

- `ORACLE_PROVIDER` - AI provider to use (gemini, ollama, openrouter)
- `GOOGLE_AI_API_KEY` - Gemini API key
- `OPENROUTER_API_KEY` - OpenRouter API key
- `OLLAMA_HOST` - Ollama server host (default: localhost:11434)
- `AUTOSAVE_SESSIONS` - Enable session autosaving (default: true)
- `AUTOSAVE_LOCATION` - Directory for saving sessions (default: ~/oracles)

## Spreads and Semantics

The system includes comprehensive semantic analysis for each card position:

### Built-in Spreads
- **Single Card** - The simplest possible spread, good for quick/simple readings
- **Three Card** - Past, Present, Future
- **Five Card Cross** - Extended situation analysis
- **Celtic Cross** - 10 cards for comprehensive life readings
- **Crowley/Golden Dawn Spread** - An extensive, 15-card, general purpose spread
- **Zodiac Spread** - A 12-card spread with one for each astrological house
- **Zodiac Plus Spread** - Same as the Zodiac spread with one additional central card

### Semantic Features
- Position-based card meanings
- Suit and element interactions
- Major/Minor Arcana balance analysis
- Reversed card interpretations
- Custom guidance rules

### Custom Spread Syntax

Custom spreads can be defined with json files specifying the name, description,
and positions matrix, and optionally semantic groupings, per-card semantics, and
interpretation guidance principles.

This is the structure of the "crowley" spread bundled with the library:

```json
{
  "name": "Golden Dawn",
  "description": "15-card Golden Dawn spread",
  "positions": [
     [13,  9,  5,  0,  4,  8, 12],
     [ 0,  0,  2,  1,  3,  0,  0],
     [14, 10,  6,  0,  7, 11, 15]
  ],
  "semantic_groups": {
    "earth" : "Potential Future/Natural Path (Earth)",
    "water" : "Far/Alternate Future Path (Water)",
    "air" : "Psychic Basis/Mutable Influences (Air)",
    "fire" : "Karmic Forces/Cosmic Influences (Fire)",
    "spirit" : "Nature of Circumstances (Spirit)"
  },
  "semantics": [
        ["${water}",  "${water}",  "${water}",  "",  "${earth}",  "${earth}", "${earth}"],
        [ "",  "",  "${spirit}",  "Querent/Present (Spirit)",  "${spirit}",  "",  ""],
        ["${air}", "${air}",  "${air}",  "",  "${fire}", "${fire}", "${fire}"]
   ],
  "guidance": [
    "Three cards of same suit suggests elemental consistency",
    "A majority of Major Arcana in the spread indicates a preponderance of cosmic forces",
    "Major Arcana in outcome positions indicates significant life changes"
  ]
}
```

The text output of the tarot reading includes  semantic headings, grouping together
all cards in positions with the same semantic hint. Guidance text is then displayed
below.

## Development

### Requirements
- Python 3.10+
- Dependencies listed in pyproject.toml
- Optional: Google AI SDK, Ollama for local models

### Testing

To test, clone the repo, install dependencies, and run:
```bash
python -m pytest tests/
```

Or run individual tests:
```bash
python -m unittest discover -s tests
```

### Project Structure

```
tarot_oracle/
├── __init__.py          # Package initialization
├── tarot.py            # Core tarot functionality
├── oracle.py           # AI integration and interpretation
├── config.py           # Configuration management
├── loaders.py          # Custom content loaders
├── exceptions.py       # Custom exception classes
├── cli.py              # Unified CLI interface
├── roman_numerals.py   # Utility functions
└── messages.py         # Message formatting
```

## ISC License

Copyright (c) 2026 Jonathan Voss (k98kurz) / The Pycelium Company

Permission to use, copy, modify, and/or distribute this software
for any purpose with or without fee is hereby granted, provided
that the above copyright notice and this permission notice appear in
all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
