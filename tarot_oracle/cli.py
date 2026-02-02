#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from typing import cast

from tarot_oracle.oracle import main as oracle_main
from tarot_oracle.tarot import main as tarot_main

import sys

# Custom exceptions removed - using standard TypeError and ValueError instead


def create_unified_parser() -> ArgumentParser:
    """Create the main unified CLI argument parser with support for multiple
        subcommands including reading, deck management, and spread
        configuration.
    """
    parser = ArgumentParser(
        prog="tarot-oracle",
        description="Unified CLI for Tarot Oracle - AI-powered tarot divination system",
    )

    # Add version argument
    parser.add_argument("--version", action="version", version="tarot-oracle 0.1.0")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command",
        title="Available commands",
        description="Choose a command to execute",
        help="Use 'tarot-oracle <command> --help' for command-specific help",
        required=True,
    )

    # Reading subcommand (oracle functionality)
    reading_parser = subparsers.add_parser(
        "reading",
        help="Perform divinatory tarot readings with optional AI interpretation",
        description="Complete oracle functionality with AI-powered interpretation using Gemini, OpenRouter, or Ollama",
    )
    _add_reading_arguments(reading_parser)

    # Deck subcommand (tarot deck functionality)
    deck_parser = subparsers.add_parser(
        "deck",
        help="Manage tarot decks and perform basic readings",
        description="Work with tarot decks, list available decks, and perform basic card readings",
    )
    _add_deck_arguments(deck_parser)

    # Invocation subcommand
    invocation_parser = subparsers.add_parser(
        "invocation",
        help="Manage custom invocations for readings",
        description="List and manage custom invocation texts",
    )
    _add_invocation_arguments(invocation_parser)

    # Spread subcommand
    spread_parser = subparsers.add_parser(
        "spread",
        help="Manage custom spread layouts",
        description="List and manage custom tarot spread configurations",
    )
    _add_spread_arguments(spread_parser)

    return parser


def _add_reading_arguments(parser: ArgumentParser) -> None:
    """Add arguments for the reading subcommand including AI provider,
        interpretation options, and spread types.
    """
    # Core question and spread
    parser.add_argument("question", help="Question for the oracle")
    parser.add_argument(
        "--spread",
        default="3-card",
        help="Spread layout (default: 3-card). Available: 3-card, cross, celtic, single, crowley or custom",
    )

    # Oracle-specific features
    parser.add_argument(
        "--provider",
        choices=["gemini", "openrouter", "ollama"],
        default="gemini",
        help="LLM provider (default: gemini)",
    )
    parser.add_argument(
        "--invocation",
        help="Custom invocation text (defaults to Hermes-Thoth/Prometheus if not provided)",
    )
    parser.add_argument("--invocation-name", help="Name of custom invocation to load")
    parser.add_argument(
        "--interpret",
        action="store_true",
        help="Generate LLM interpretation of reading",
    )
    parser.add_argument("--model", help="Model name (provider-specific)")

    # Provider-specific options
    parser.add_argument("--api-key", help="API key (for gemini or openrouter provider)")
    parser.add_argument("--ollama-host", help="Ollama host (for ollama provider)")
    parser.add_argument(
        "--timeout",
        type=int,
        help="Timeout in seconds (default: 30 gemini, 300 ollama)",
    )

    # Session saving options
    save_group = parser.add_mutually_exclusive_group()
    save_group.add_argument(
        "--save",
        action="store_true",
        help="Force save this session (overrides environment settings)",
    )
    save_group.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save this session (overrides environment settings)",
    )
    parser.add_argument(
        "--save-path", help="Override default save location for this session"
    )

    # Tarot options
    parser.add_argument(
        "--random",
        type=int,
        default=8,
        help="Add N random bytes to RNG seed for entropy (default: 8)",
    )
    parser.add_argument(
        "--reversed", action="store_true", help="Allow cards to appear reversed"
    )


def _add_deck_arguments(parser: ArgumentParser) -> None:
    """Add arguments for the deck subcommand including listing decks and
        performing basic readings.
    """
    # Create mutually exclusive group for main operations
    operation_group = parser.add_mutually_exclusive_group(required=True)

    operation_group.add_argument(
        "--list",
        action="store_true",
        dest="list_decks",
        help="List available deck configurations",
    )
    operation_group.add_argument(
        "--lookup",
        metavar="CODES",
        help="Look up card codes (e.g., '0,I,W_A,C_K'). Format: comma-separated notation",
    )
    operation_group.add_argument(
        "question",
        nargs="?",
        help="Question for tarot reading (required for reading mode)",
    )

    # General options
    parser.add_argument(
        "--spread", default="3-card", help="Spread layout (default: 3-card)"
    )
    parser.add_argument(
        "--deck", metavar="FILENAME", help="Use custom deck configuration"
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--reversed", action="store_true", help="Allow reversed cards")
    parser.add_argument(
        "--random",
        type=int,
        default=8,
        help="Add N random bytes to RNG seed for entropy (default: 8)",
    )


def _add_invocation_arguments(parser: ArgumentParser) -> None:
    """Add arguments for the invocation subcommand including listing
        available custom invocations.
    """

    operation_group = parser.add_mutually_exclusive_group(required=True)

    operation_group.add_argument(
        "--list",
        action="store_true",
        dest="list_invocations",
        help="List available custom invocations",
    )
    operation_group.add_argument(
        "--show", metavar="NAME", help="Display content of a specific invocation"
    )


def _add_spread_arguments(parser: ArgumentParser) -> None:
    """Add arguments for the spread subcommand including listing available
        custom spreads.
    """
    operation_group = parser.add_mutually_exclusive_group(required=True)

    operation_group.add_argument(
        "--list",
        action="store_true",
        dest="list_spreads",
        help="List available custom spreads",
    )
    operation_group.add_argument(
        "--show", metavar="NAME", help="Display configuration of a specific spread"
    )


def handle_reading_command(args: Namespace) -> int:
    """Handle the reading subcommand using existing oracle functionality,
        converting unified CLI arguments to oracle format and returning
        exit code.
    """
    # Convert unified args to oracle args format
    oracle_args = [args.question, "--spread", args.spread, "--provider", args.provider]

    if args.invocation:
        oracle_args.extend(["--invocation", args.invocation])
    if args.invocation_name:
        oracle_args.extend(["--invocation-name", args.invocation_name])
    if args.interpret:
        oracle_args.append("--interpret")
    if args.model:
        oracle_args.extend(["--model", args.model])
    if args.api_key:
        oracle_args.extend(["--api-key", args.api_key])
    if args.ollama_host:
        oracle_args.extend(["--ollama-host", args.ollama_host])
    if args.timeout:
        oracle_args.extend(["--timeout", str(args.timeout)])
    if args.save:
        oracle_args.append("--save")
    if args.no_save:
        oracle_args.append("--no-save")
    if args.save_path:
        oracle_args.extend(["--save-path", args.save_path])
    if args.random != 8:
        oracle_args.extend(["--random", str(args.random)])
    if args.reversed:
        oracle_args.append("--reversed")

    return cast(int, oracle_main(oracle_args))


def handle_deck_command(args: Namespace) -> int:
    """Handle the deck subcommand using existing tarot functionality.
    
    Processes deck management requests by converting unified CLI arguments
    to format expected by the tarot module. Supports listing decks,
    card lookup, and basic deck readings.
    
    Args:
        args (Namespace): Parsed command-line arguments for deck command
            Includes list_decks, lookup, and reading-related options
            
    Returns:
        int: Exit code from tarot execution (0 for success, non-zero for error)
        
    Raises:
        ValueError: For any deck-related errors during execution
        
    Example:
        >>> from argparse import Namespace
        >>> args = Namespace(list_decks=True, lookup=None, reading=False)
        >>> exit_code = handle_deck_command(args)
        >>> 
        >>> # Card lookup
        >>> args = Namespace(list_decks=False, lookup="fool", reading=False)
        >>> exit_code = handle_deck_command(args)
    """
    # Convert unified args to tarot args format
    tarot_args = []

    if args.list_decks:
        tarot_args.extend(["--list-decks"])
    elif args.lookup:
        tarot_args.extend(["--lookup", args.lookup])
    else:
        # Reading mode
        tarot_args.append(args.question)
        tarot_args.extend(["--spread", args.spread])

    if args.deck:
        tarot_args.extend(["--deck", args.deck])
    if args.json:
        tarot_args.append("--json")
    if args.reversed:
        tarot_args.append("--reversed")
    if args.random != 8:
        tarot_args.extend(["--random", str(args.random)])

    return cast(int, tarot_main(tarot_args))


def handle_invocation_command(args: Namespace) -> int:
    """Handle invocation subcommand using InvocationLoader to list and manage
        invocation files, returning exit code.
    """
    from tarot_oracle.loaders import InvocationLoader

    loader = InvocationLoader()

    if args.list_invocations:
        invocations = loader.list_invocations()
        if not invocations:
            print("No custom invocations found.")
            return 0

        print("Available custom invocations:")
        for invocation in invocations:
            print(f"  {invocation['name']:<20} - {invocation['description']}")
        return 0

    elif args.show:
        invocation_text = loader.load_invocation(args.show)
        if invocation_text:
            print(f"=== Invocation: {args.show} ===")
            print(invocation_text)
            return 0
        else:
            print(f"Invocation '{args.show}' not found.")
            return 1

    return 0


def handle_spread_command(args: Namespace) -> int:
    """Handle the spread subcommand using SpreadLoader to list and manage
        spread configurations, returning exit code.
    """
    from tarot_oracle.loaders import SpreadLoader

    loader = SpreadLoader()

    if args.list_spreads:
        spreads = loader.list_spreads()
        if not spreads:
            print("No custom spreads found.")
            return 0

        print("Available custom spreads:")
        for spread in spreads:
            print(f"  {spread['name']:<20} - {spread['description']}")
        return 0

    elif args.show:
        spread_config = loader.load_spread(args.show)
        if spread_config:
            import json
            print(f"=== Spread: {args.show} ===")
            print(json.dumps(spread_config, indent=2, ensure_ascii=False))
            return 0
        else:
            print(f"Spread '{args.show}' not found.")
            return 1

    return 0


def main(args: list[str] | None = None) -> int:
    """Main entry point for unified CLI, processing command-line arguments
        and dispatching to appropriate command handlers, returning exit code.
    """
    parser = create_unified_parser()

    if args is None:
        parsed_args = parser.parse_args()
    else:
        parsed_args = parser.parse_args(args)

    try:
        if parsed_args.command == "reading":
            return handle_reading_command(parsed_args)
        elif parsed_args.command == "deck":
            return handle_deck_command(parsed_args)
        elif parsed_args.command == "invocation":
            return handle_invocation_command(parsed_args)
        elif parsed_args.command == "spread":
            return handle_spread_command(parsed_args)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())
