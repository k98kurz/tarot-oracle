# Tarot Oracle

A comprehensive tarot divination system with AI-powered interpretation and
semantic analysis. Features custom deck loading, multiple spread configurations,
and integration with various AI providers for guided readings.

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

## Quick Start

Get started with Tarot Oracle in 5 minutes.

### Prerequisites

- Python 3.10 or higher
- For AI interpretation: Choose one option below

### Option 1: Ollama (Recommended for Privacy)

Ollama runs locally on your machine. No API keys required and your readings never leave your computer.

```bash
# Install Ollama (visit ollama.ai for instructions)
# Pull a recommended small model
ollama pull qwen3:0.6b

# Install Tarot Oracle
pip install tarot-oracle

# Run your first reading with AI interpretation
oracle "What will today bring?" --interpret

# Make interpretation default
oracle --set-config interpret true
```

### Option 2: OpenRouter

Access a wide variety of cloud-based models through OpenRouter.

```bash
# Install Tarot Oracle
pip install tarot-oracle

# Configure OpenRouter
oracle --set-config provider openrouter
oracle --set-config openrouter_model google/gemini-2.5-flash # optional; openrouter/free is default

# Get your API key from openrouter.ai
oracle --set-config openrouter_api_key your-api-key-here
# or use an environment variable (on *nix systems)
export OPENROUTER_API_KEY=your-api-key-here

# Run your first reading with interpretation
oracle "What will today bring?" --interpret
```

### Option 3: Google Gemini

Use Google's Gemini models for interpretation.

```bash
# Install Tarot Oracle with Gemini support
pip install tarot-oracle[gemini]

# Configure Gemini
oracle --set-config provider gemini

# Get your API key from ai.google.dev
oracle --set-config google_ai_api_key your-api-key-here
oracle --set-config gemini_model gemini-2.5-flash-lite # optional; gemini-3-flash is default
# or use an environment variable (on *nix systems)
export GOOGLE_AI_API_KEY=your-api-key-here

# Run your first reading with interpretation
oracle "What will today bring?" --interpret
```

### Try a Reading Without AI

You can also use Tarot Oracle without AI interpretation:

```bash
# Simple 3-card reading (no AI needed)
tarot "What will today bring?"

# Celtic Cross spread
tarot "Question about career" --spread celtic
```

If you want to use the session saving features without AI interpretation:
```bash
# Simple 3-card reading
oracle --no-interpret "What will today bring?"

# Golden Dawn spread
oracle --no-interpret --spread crowley "I seek general guidance."
```

## Usage

Tarot Oracle provides two main CLI tools: `tarot` for traditional readings and
`oracle` for AI-powered interpretations or to use the session saving features.

### Basic Reading

```bash
# Generate a 3-card reading (no AI)
tarot "What guidance do you seek?"

# Use a specific spread
tarot "Question about career" --spread celtic

# Get AI interpretation with oracle
oracle "Life path question" --interpret
```

For more CLI options, see the [CLI Reference](#cli-reference) section below.

## Choosing Your AI Provider

The `oracle` CLI supports three AI providers for interpreting tarot readings. You should have already configured one of these in the [Quick Start](#quick-start) section above.

### Ollama

Ollama is the default provider and runs locally on your machine. No API keys required and your readings remain private.

**Recommended small models:**
- qwen3:0.6b (fastest, tested)
- granite4:1b-h (good balance of speed and intelligence)

**Models to avoid:**
- `graphite4:350-h`: refused to interpret readings
- `tinyllama:latest`: unintelligible output, poor performance

For larger models, you may need to increase the timeout with the `--timeout` setting.

### OpenRouter

OpenRouter provides access to a wide variety of cloud-based models through a
unified API. Requires an API key from openrouter.ai.

Popular models include `google/gemini-3-flash-preview`, `anthropic/claude-3-haiku`,
and many others. Use `oracle --list-models` with OpenRouter configured to see all
available options. There are a variety of free models to choose from; by default,
the `openrouter/free` will route to an available free model automatically.

### Google Gemini

Gemini provides Google's AI models for interpretation. Requires an API key from
[AI Studio](https://aistudio.google.com/app/api-keys) and the optional
`google-generativeai` package.

To install with Gemini support: `pip install tarot-oracle[gemini]`

### Cloud Provider Considerations

When using cloud providers (OpenRouter or Gemini):
- Your questions and readings are sent to external servers
- Review each provider's privacy policy
- API costs may apply depending on usage
- Internet connection required

## Configuration

Manage oracle settings via CLI commands. You can view current settings with `oracle --config`.

### Configuration Commands

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

Configuration can also be set via environment variables:

- `ORACLE_PROVIDER` - AI provider to use (gemini, ollama, openrouter)
- `GOOGLE_AI_API_KEY` - Gemini API key
- `OPENROUTER_API_KEY` - OpenRouter API key
- `OLLAMA_HOST` - Ollama server host (default: localhost:11434)
- `TAROT_ORACLE_AUTOSAVE` - Enable session autosaving (default: true)
- `TAROT_ORACLE_AUTOSAVE_LOCATION` - Directory for saving sessions (default: ~/oracles)
- `TAROT_ORACLE_INTERPRET` - Enable AI interpretation by default (default: false)

Environment variables take precedence over configuration file values.

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

List and manage saved invocations:
```bash
# List all available invocations
oracle --list-invocations

# Show contents of a specific invocation
oracle --show-invocation my-invocation

# Save an invocation from a file to user directory
oracle --save-invocation path/to/invocation.txt
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

Export the default deck to use as a scaffold:
```bash
tarot --export-deck rider-waite > rider-waite.json
```

Use custom deck:
```bash
tarot "Question" --deck my-custom-deck
```

Save decks and spreads to user directory:
```bash
# Save deck from JSON file to ~/.tarot-oracle/decks/
tarot --save-deck path/to/my-deck.json

# Save spread from JSON file to ~/.tarot-oracle/spreads/
tarot --save-spread path/to/my-spread.json
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

The text output of the tarot reading includes semantic headings, grouping together
all cards in positions with the same semantic hint. Guidance text is then displayed
below.

## Advanced Usage

### Python API

The tarot_oracle package provides a Python API for programmatic access.

#### Custom Decks

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

#### AI Integration

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

#### Direct Spread Rendering

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

## CLI Reference

Run `tarot --help` or `oracle --help` for complete option details.

### Common Options

Both tools support these options:
- `--spread TYPE` - Spread layout (default: 3-card)
- `--deck NAME` - Use specific deck (tarot only)
- `--reversed` - Allow reversed cards
- `--random N` - Add N random bytes to seed

### Tarot-Specific Options

- `--lookup CODES` - Look up card codes (CSV format)
- `--list-decks` - List available decks
- `--list-spreads` - List available spreads
- `--list-invocations` - List saved invocations
- `--show-invocation NAME` - Show contents of a saved invocation
- `--export-deck NAME` - Export bundled deck to stdout
- `--export-spread NAME` - Export bundled spread to stdout
- `--save-deck SOURCE` - Save deck from JSON file to user directory
- `--save-spread SOURCE` - Save spread from JSON file to user directory
- `--json` - Output in JSON format
- `--no-keywords` - Hide card keywords
- `--invoke` - Use default invocation

### Oracle-Specific Options

- `--provider TYPE` - AI provider (gemini, ollama, openrouter)
- `--interpret` / `--no-interpret` - Generate or skip AI interpretation
- `--model NAME` - Specific model to use
- `--invocation TEXT` - Custom invocation text
- `--invocation_name NAME` - Use named invocation
- `--list-invocations` - List saved invocations
- `--show-invocation NAME` - Show contents of a saved invocation
- `--save-invocation SOURCE` - Save invocation from text file to user directory
- `--save` / `--no-save` - Force save or skip saving session
- `--config` - Display current configuration
- `--list-models` - List available models
- `--set-config KEY VALUE` - Set configuration
- `--unset-config KEY` - Remove configuration

## Troubleshooting

### Model Issues

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

### Configuration Issues

**Configuration not saving:**
- Ensure config directory exists: `~/.config/tarot-oracle/`
- Check file permissions on config directory

**Provider not working:**
- Verify provider is correctly set: `oracle --config`
- For cloud providers, check API key validity
- For Ollama, check that server is running: `curl http://localhost:11434`

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

## Devlog Note

This project was my first project with OpenCode, intended mostly as an opportunity
to learn the newest addition to my dev tools. It is still necessary to understand
fundamental software development paradigms and be competent with a code editor in
my experience, but the tools can be pushed pretty far if you can provide solid
guardrails, good prompts, and a bit of occasional manual intervention.

## Contributing

Check out the [Pycelium discord server](https://discord.gg/b2QFEJDX69). If you
experience a problem, please discuss it on the Discord server. All suggestions
for improvement are also welcome, and the best place for that is also Discord.
If you experience a bug and do not use Discord, open an issue or discussion on
Github.

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
