# Tarot Oracle

A comprehensive tarot divination system with AI-powered interpretation and
semantic analysis. Features custom deck loading, multiple spread configurations,
and integration with various AI providers for guided readings.

This project was my first project with OpenCode, intended mostly as an opportunity
to learn the newest addition to my dev tools. It is still necessary to understand
fundamental software development paradigms and be competent with a code editor in
my experience, but the tools can be pushed pretty far if you can provide solid
guardrails, good prompts, and a bit of occasional manual intervention.

## Status

Issues are tracked in the project repository. Historical changes can be found in the changelog.

## Features

### Core Functionality
- Custom tarot deck creation and loading
- Multiple built-in spread configurations (Celtic Cross, Three Card, etc.)
- Semantic analysis with position-based interpretation guidance
- AI-powered reading interpretations

### AI Provider Integration
- Google Gemini
- Ollama (local models)
- OpenRouter (wide variety of models)
- Custom model configuration and fallback logic

### Custom Content System
- Custom invocations for different traditions
- Custom spreads with semantic hints
- User-created deck configurations
- Guidance rules for focused/relevant interpretations

## Usage

Install with `pip install tarot-oracle`, then configure your preferred AI
provider. The project provides both CLI tools and Python APIs.

### Basic Reading

```bash
# Generate a Celtic Cross reading
tarot "What guidance do you seek?" --spread celtic

# Use a specific deck
tarot "Question about career" --deck rider-waite

# Get AI interpretation
oracle "Life path question" --provider gemini --interpret
```

### Custom Decks

```python
from tarot_oracle.tarot import DeckLoader, TarotDivination

# Load a custom deck by name (searches local and config directories)
loader = DeckLoader()
deck = loader.load_deck("my-custom-deck")

# Or load by file path
from tarot_oracle.tarot import Deck
deck = Deck(deck_path="my-custom-deck.json")

# Use in reading
divination = TarotDivination(deck_config=None)
```

### AI Integration

```python
from tarot_oracle.oracle import Oracle

# Use Gemini for interpretation
oracle = Oracle(provider="gemini", api_key="your-api-key")
result = oracle.perform_divinatory_reading(
    question="Your question",
    spread_type="3-card",
    interpret=True
)

print(result["spread_display"])
print(result["legend_display"])
if "interpretation" in result:
    print(result["interpretation"])
```

## Configuration

Manage oracle settings via CLI commands:

```bash
# Display current configuration
oracle --config

# Set configuration values
oracle --set-config provider ollama
oracle --set-config ollama_model qwen3:0.6b
oracle --set-config interpret true

# Remove configuration values
oracle --unset-config openrouter_api_key
```

### Configuration Keys

| Key                  | Description                              | Default         |
|----------------------|------------------------------------------|-----------------|
| `provider`           | AI provider (gemini, ollama, openrouter) | ollama          |
| `google_ai_api_key`  | Gemini API key                           | -               |
| `openrouter_api_key` | OpenRouter API key                       | -               |
| `ollama_host`        | Ollama server host                       | localhost:11434 |
| `autosave_sessions`  | Auto-save readings                       | true            |
| `autosave_location`  | Save location                            | ~/oracles       |
| `gemini_model`       | Gemini model                             | gemini-3-flash  |
| `openrouter_model`   | OpenRouter model                         | openrouter/free |
| `ollama_model`       | Ollama model                             | qwen3:0.6b      |
| `interpret`          | Default interpretation behavior          | false           |

### Environment Variables

- `ORACLE_PROVIDER` - AI provider to use (gemini, ollama, openrouter)
- `GOOGLE_AI_API_KEY` - Gemini API key
- `OPENROUTER_API_KEY` - OpenRouter API key
- `OLLAMA_HOST` - Ollama server host (default: localhost:11434)
- `TAROT_ORACLE_AUTOSAVE` - Enable session autosaving (default: true)
- `TAROT_ORACLE_AUTOSAVE_LOCATION` - Directory for saving sessions (default: ~/oracles)
- `TAROT_ORACLE_INTERPRET` - Enable AI interpretation by default (default: false)

### Python API

```python
from tarot_oracle import TarotDivination, SpreadRenderer
from tarot_oracle.data_loader import BundledDataLoader
from time import time

# Create a reading
divination = TarotDivination()
question = "What guidance do you seek?"
timestamp = str(int(time()))
spread_config = BundledDataLoader.load_spread("celtic")
layout = spread_config['layout']

# Draw cards
seed = divination.create_seed(timestamp, question)
drawn_cards = divination.draw_cards_for_reading(seed, layout)

# Render the spread
output = SpreadRenderer.render_spread(drawn_cards, layout)
print(output)
```

## LLM Interpretation Configuration

The `oracle` CLI supports three AI providers for interpreting tarot readings. Each provider has different configuration options and model considerations.

### Quick Start (Ollama - Recommended for Privacy)

Ollama is the default provider and runs locally on your machine. No API keys required.

```bash
# Install Ollama and pull a recommended model
ollama pull qwen3:0.6b

# Run a reading with interpretation
oracle "What guidance do you seek?" --interpret

# If you want to always use interpretation, configure it
oracle --set-config interpret true
```

### Local Model Recommendations (Ollama)

The following small models have been tested and are verified to work:

- qwen3:0.6b
- granite4:1b-h

Note that larger models may require adjusting the timeout.

I recommend avoiding the following models:

- `graphite4:350-h`: it refused to interpret
- `tinyllama:latest`: fairly unintelligent model with somewhat unintelligible
output and worse performance than qwen3:0.6b

### Configuration Examples

```bash
# Configure Ollama with recommended model
oracle --set-config provider ollama
oracle --set-config ollama_model qwen3:0.6b

# Configure OpenRouter (requires API key)
oracle --set-config provider openrouter
oracle --set-config openrouter_api_key your-api-key-here
oracle --set-config openrouter_model google/gemini-flash-1.5

# Configure Gemini (requires API key)
oracle --set-config provider gemini
oracle --set-config google_ai_api_key your-api-key-here

# Enable interpretation by default
oracle --set-config interpret true
```

### Troubleshooting Model Issues

**"Interpretation was not available" message:**
- Check that model is installed (Ollama): `ollama list`
- Verify API key is valid (cloud providers): `oracle --config`
- Try a different model if current one refuses tarot interpretation

**Model fails to interpret spreads:**
- Some models have safety filters or lack sufficient intelligence
- Switch to a recommended model

**Slow interpretation:**
- Use smaller/faster models (qwen3:0.6b is very fast)
- Reduce spread size (single or 3-card instead of Celtic Cross)
- For Ollama, ensure your machine has adequate RAM

## CLI Reference

Run `tarot --help` or `oracle --help` for complete option details.

### Common Options

Both tools support these options:
- `--spread TYPE` - Spread layout (default: 3-card)
- `--deck NAME` - Use specific deck (tarot only)
- `--reversed` - Allow reversed cards
- `--random N` - Add N random bytes to seed

### Oracle-Specific Options

- `--provider TYPE` - AI provider (gemini, ollama, openrouter)
- `--interpret` / `--no-interpret` - Generate AI interpretation
- `--model NAME` - Specific model to use
- `--invocation TEXT` - Custom invocation text
- `--invocation_name NAME` - Use named invocation
- `--save` / `--no-save` - Force save or skip saving session
- `--config` - Display current configuration
- `--list-models` - List available models
- `--set-config KEY VALUE` - Set configuration
- `--unset-config KEY` - Remove configuration

### Tarot-Specific Options

- `--lookup CODES` - Look up card codes (CSV format)
- `--list-decks` - List available decks
- `--list-spreads` - List available spreads
- `--export-deck NAME` - Export bundled deck to stdout
- `--export-spread NAME` - Export bundled spread to stdout
- `--json` - Output in JSON format
- `--no-keywords` - Hide card keywords
- `--invoke` - Use default invocation

## Custom Content

### Custom Invocations

Custom invocations can be created as text files (.txt or .md) and placed in:
- `~/.tarot-oracle/invocations/`
- Current working directory

Example invocation file:
```
By the wisdom of ancient guides,
and through the language of symbols,
I seek clarity and understanding.
May the cards reveal the truth.
```

Use custom invocations:
```bash
oracle "What guidance do you seek?" --invocation_name my-invocation

oracle "Question" --invocation "By ancient powers, I seek wisdom"

tarot "Question" --invoke  # Uses default invocation
```

### Custom Decks

Custom deck configurations are JSON files placed in:
- `~/.tarot-oracle/decks/`
- Current working directory

Example deck configuration:
```json
{
  "name": "My Custom Deck",
  "description": "A custom tarot deck",
  "cards": [
    {
      "name": "The Fool",
      "card_type": "major",
      "suit": null,
      "value": "0",
      "keywords": "Beginnings, innocence, spontaneity",
      "reversed_keywords": "Recklessness, risk, naivety"
    }
  ]
}
```

List available decks:
```bash
tarot --list-decks
```

Use custom deck:
```bash
tarot "Question" --deck my-custom-deck
```

## Spreads and Semantics

The system includes comprehensive semantic analysis for each card position:

### Built-in Spreads
- **single** - Single Card: The simplest possible spread, good for quick/simple readings
- **3-card** - Three Card: Past, Present, Future (default)
- **cross** - Five Card Cross: Extended situation analysis
- **celtic** - Celtic Cross: 10 cards for comprehensive readings
- **crowley** - Golden Dawn Spread: An extensive, 15-card, general purpose spread
- **zodiac** - Zodiac Spread: A 12-card spread with one for each astrological house
- **zodiac_plus** - Zodiac Plus Spread: Same as the Zodiac spread with one additional central card

### Semantic Features
- Position-based card meanings
- Suit and element interactions
- Major/Minor Arcana balance analysis
- Reversed card interpretations
- Custom guidance rules

### Custom Spread Syntax

Custom spreads can be defined with json files specifying the name, description,
and layout matrix, and optionally semantic groupings, per-card semantics, and
interpretation guidance principles.

This is the structure of the "crowley" spread bundled with the library:

```json
{
  "name": "Golden Dawn",
  "description": "15-card Golden Dawn spread",
  "layout": [
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
python -m unittest discover -s tests
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
