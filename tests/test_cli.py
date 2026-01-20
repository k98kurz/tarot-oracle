"""Test CLI subcommand functionality and unified interface."""

import unittest
import sys
from unittest.mock import patch, Mock
from io import StringIO
from argparse import ArgumentParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle.cli import (
    create_unified_parser,
    main as cli_main,
    _add_reading_arguments,
    _add_deck_arguments,
    _add_invocation_arguments,
    _add_spread_arguments
)
# Custom exceptions removed - using standard TypeError and ValueError instead


class TestUnifiedParser(unittest.TestCase):
    """Test unified CLI argument parser."""

    def test_parser_creation(self):
        """Test basic parser creation."""
        parser = create_unified_parser()
        assert isinstance(parser, ArgumentParser), "Should return ArgumentParser instance"
        assert parser.prog == "tarot-oracle", f"Expected prog 'tarot-oracle', got '{parser.prog}'"

    def test_version_argument(self):
        """Test version argument handling."""
        parser = create_unified_parser()
        with self.assertRaises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['--version'])

    def test_subcommands_required(self):
        """Test that subcommands are required."""
        parser = create_unified_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([])

    def test_reading_command_parsing(self):
        """Test reading subcommand parsing."""
        parser = create_unified_parser()
        args = parser.parse_args([
            'reading',
            'What does the future hold?',
            '--provider', 'gemini',
            '--interpret',
            '--spread', 'celtic'
        ])

        assert args.command == 'reading', f"Expected command 'reading', got '{args.command}'"
        assert args.question == 'What does the future hold?', f"Expected question, got '{args.question}'"
        assert args.provider == 'gemini', f"Expected provider 'gemini', got '{args.provider}'"
        assert args.interpret is True, f"Expected interpret=True, got {args.interpret}"
        assert args.spread == 'celtic', f"Expected spread 'celtic', got '{args.spread}'"

    def test_deck_command_parsing(self):
        """Test deck subcommand parsing."""
        parser = create_unified_parser()
        args = parser.parse_args([
            'deck',
            '--list'
        ])

        assert args.command == 'deck', f"Expected command 'deck', got '{args.command}'"
        assert args.list_decks is True, f"Expected list_decks=True, got {args.list_decks}"

    def test_invocation_command_parsing(self):
        """Test invocation subcommand parsing."""
        parser = create_unified_parser()
        args = parser.parse_args([
            'invocation',
            '--list'
        ])

        assert args.command == 'invocation', f"Expected command 'invocation', got '{args.command}'"
        assert args.list_invocations is True, f"Expected list_invocations=True, got {args.list_invocations}"

    def test_spread_command_parsing(self):
        """Test spread subcommand parsing."""
        parser = create_unified_parser()
        args = parser.parse_args([
            'spread',
            '--list'
        ])

        assert args.command == 'spread', f"Expected command 'spread', got '{args.command}'"
        assert args.list_spreads is True, f"Expected list_spreads=True, got {args.list_spreads}"

    def test_reading_command_defaults(self):
        """Test reading command defaults."""
        parser = create_unified_parser()
        args = parser.parse_args([
            'reading',
            'Test question'
        ])

        assert args.provider == 'gemini', f"Expected default provider 'gemini', got '{args.provider}'"
        assert args.spread == '3-card', f"Expected default spread '3-card', got '{args.spread}'"
        assert args.interpret is False, f"Expected default interpret=False, got {args.interpret}"

    def test_provider_choices_validation(self):
        """Test provider choice validation."""
        parser = create_unified_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([
                'reading',
                'Test question',
                '--provider', 'invalid'
            ])


class TestReadingArguments(unittest.TestCase):
    """Test reading subcommand argument configuration."""

    def test_add_reading_arguments(self):
        """Test reading arguments are added correctly."""
        parser = ArgumentParser()
        _add_reading_arguments(parser)

        # Test parsing with all arguments
        args = parser.parse_args([
            'Test question',
            '--provider', 'openrouter',
            '--interpret',
            '--invocation', 'Custom invocation',
            '--invocation-name', 'custom',
            '--spread', 'celtic'
        ])

        assert args.question == 'Test question', f"Expected question 'Test question', got '{args.question}'"
        assert args.provider == 'openrouter', f"Expected provider 'openrouter', got '{args.provider}'"
        assert args.interpret is True, f"Expected interpret=True, got {args.interpret}"
        assert args.invocation == 'Custom invocation', f"Expected invocation 'Custom invocation', got '{args.invocation}'"
        assert args.invocation_name == 'custom', f"Expected invocation_name 'custom', got '{args.invocation_name}'"
        assert args.spread == 'celtic', f"Expected spread 'celtic', got '{args.spread}'"


class TestDeckArguments(unittest.TestCase):
    """Test deck subcommand argument configuration."""

    def test_add_deck_arguments(self):
        """Test deck arguments are added correctly."""
        parser = ArgumentParser()
        _add_deck_arguments(parser)

        # Test parsing with list argument
        args = parser.parse_args(['--list'])
        assert args.list_decks is True, f"Expected list_decks=True, got {args.list_decks}"


class TestInvocationArguments(unittest.TestCase):
    """Test invocation subcommand argument configuration."""

    def test_add_invocation_arguments(self):
        """Test invocation arguments are added correctly."""
        parser = ArgumentParser()
        _add_invocation_arguments(parser)

        # Test parsing with list argument
        args = parser.parse_args(['--list'])
        assert args.list_invocations is True, f"Expected list_invocations=True, got {args.list_invocations}"


class TestSpreadArguments(unittest.TestCase):
    """Test spread subcommand argument configuration."""

    def test_add_spread_arguments(self):
        """Test spread arguments are added correctly."""
        parser = ArgumentParser()
        _add_spread_arguments(parser)

        # Test parsing with list argument
        args = parser.parse_args(['--list'])
        assert args.list_spreads is True, f"Expected list_spreads=True, got {args.list_spreads}"


class TestCLIIntegration(unittest.TestCase):
    """Test CLI integration with backend modules."""

    @patch('tarot_oracle.cli.oracle_main')
    def test_reading_command_integration(self, mock_oracle_main):
        """Test reading command integration with oracle module."""
        mock_oracle_main.return_value = 0

        test_args = [
            'tarot-oracle',
            'reading',
            'What does the future hold?',
            '--provider', 'gemini',
            '--interpret'
        ]

        with patch('sys.argv', test_args):
            result = cli_main()

        assert result == 0, f"Expected return code 0, got {result}"
        mock_oracle_main.assert_called_once()

    @patch('tarot_oracle.cli.tarot_main')
    def test_deck_command_integration(self, mock_tarot_main):
        """Test deck command integration with tarot module."""
        mock_tarot_main.return_value = 0

        test_args = [
            'tarot-oracle',
            'deck',
            '--list'
        ]

        with patch('sys.argv', test_args):
            result = cli_main()

        assert result == 0, f"Expected return code 0, got {result}"
        mock_tarot_main.assert_called_once()

    def test_invocation_command_integration(self):
        """Test invocation command integration."""
        test_args = [
            'tarot-oracle',
            'invocation',
            '--list'
        ]

        with patch('sys.argv', test_args):
            result = cli_main()

        assert result == 0, f"Expected return code 0, got {result}"

    def test_spread_command_integration(self):
        """Test spread command integration."""
        test_args = [
            'tarot-oracle',
            'spread',
            '--list'
        ]

        with patch('sys.argv', test_args):
            result = cli_main()

        assert result == 0, f"Expected return code 0, got {result}"


class TestCLIErrorHandling(unittest.TestCase):
    """Test CLI error handling and user guidance."""

    @patch('tarot_oracle.cli.oracle_main')
    def test_tarot_oracle_error_handling(self, mock_oracle_main):
        """Test handling of ValueError."""
        mock_oracle_main.side_effect = ValueError(
            "Test error"
        )

        test_args = [
            'tarot-oracle',
            'reading',
            'Test question'
        ]

        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                result = cli_main()

        assert result != 0, f"Expected non-zero return code for error, got {result}"
        assert "Test error" in mock_stderr.getvalue(), "Error message should be in stderr"


    @patch('tarot_oracle.cli.oracle_main')
    def test_generic_error_handling(self, mock_oracle_main):
        """Test handling of generic exceptions."""
        mock_oracle_main.side_effect = Exception("Unexpected error")

        test_args = [
            'tarot-oracle',
            'reading',
            'Test question'
        ]

        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                result = cli_main()

        assert result != 0, f"Expected non-zero return code for error, got {result}"
        assert "Unexpected error" in mock_stderr.getvalue(), "Error message should be in stderr"


class TestCLIHelpSystem(unittest.TestCase):
    """Test CLI help system and documentation."""

    def test_main_help(self):
        """Test main help output."""
        parser = create_unified_parser()
        with self.assertRaises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['--help'])

        help_text = mock_stdout.getvalue()
        assert "Unified CLI for Tarot Oracle" in help_text, "Help should contain CLI description"
        assert "reading" in help_text, "Help should mention reading command"
        assert "deck" in help_text, "Help should mention deck command"
        assert "invocation" in help_text, "Help should mention invocation command"
        assert "spread" in help_text, "Help should mention spread command"

    def test_reading_help(self):
        """Test reading subcommand help."""
        parser = create_unified_parser()
        with self.assertRaises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['reading', '--help'])

        help_text = mock_stdout.getvalue()
        assert "oracle functionality" in help_text.lower(), "Help should mention oracle functionality"
        assert "provider" in help_text, "Help should mention provider option"
        assert "interpret" in help_text, "Help should mention interpret option"

    def test_deck_help(self):
        """Test deck subcommand help."""
        parser = create_unified_parser()
        with self.assertRaises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['deck', '--help'])

        help_text = mock_stdout.getvalue()
        assert "tarot decks" in help_text.lower(), "Help should mention tarot decks"
        assert "list" in help_text.lower(), "Help should mention list option"

    def test_invocation_help(self):
        """Test invocation subcommand help."""
        parser = create_unified_parser()
        with self.assertRaises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['invocation', '--help'])

        help_text = mock_stdout.getvalue()
        assert "invocation" in help_text.lower(), "Help should mention invocation"
        assert "custom" in help_text.lower(), "Help should mention custom invocations"

    def test_spread_help(self):
        """Test spread subcommand help."""
        parser = create_unified_parser()
        with self.assertRaises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['spread', '--help'])

        help_text = mock_stdout.getvalue()
        assert "spread" in help_text.lower(), "Help should mention spread"
        assert "custom" in help_text.lower(), "Help should mention custom spreads"


class TestCLIArguments(unittest.TestCase):
    """Test CLI argument validation and processing."""

    def test_question_argument_required(self):
        """Test that question is required for reading command."""
        parser = create_unified_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(['reading'])

    def test_provider_argument_choices(self):
        """Test provider argument limited to valid choices."""
        parser = create_unified_parser()

        # Valid providers should work
        for provider in ['gemini', 'openrouter', 'ollama']:
            args = parser.parse_args([
                'reading', 'Test question', '--provider', provider
            ])
            assert args.provider == provider, f"Expected provider {provider}, got {args.provider}"

    def test_spread_argument_processing(self):
        """Test spread argument processing."""
        parser = create_unified_parser()

        # Default spread
        args = parser.parse_args(['reading', 'Test question'])
        assert args.spread == '3-card', f"Expected default spread '3-card', got '{args.spread}'"

        # Custom spread
        args = parser.parse_args([
            'reading', 'Test question', '--spread', 'celtic'
        ])
        assert args.spread == 'celtic', f"Expected custom spread 'celtic', got '{args.spread}'"

    def test_boolean_flags(self):
        """Test boolean flag processing."""
        parser = create_unified_parser()

        # Default (False)
        args = parser.parse_args(['reading', 'Test question'])
        assert args.interpret is False, f"Expected default interpret=False, got {args.interpret}"

        # Explicit True
        args = parser.parse_args(['reading', 'Test question', '--interpret'])
        assert args.interpret is True, f"Expected interpret=True when flag set, got {args.interpret}"


class TestCLIExamples(unittest.TestCase):
    """Test CLI usage examples from documentation."""

    @patch('tarot_oracle.cli.oracle_main')
    def test_example_interpretation_reading(self, mock_oracle_main):
        """Test example: tarot-oracle reading "What does the future hold?" --interpret --provider gemini."""
        mock_oracle_main.return_value = 0

        test_args = [
            'tarot-oracle',
            'reading',
            'What does the future hold?',
            '--interpret',
            '--provider', 'gemini'
        ]

        with patch('sys.argv', test_args):
            result = cli_main()

        assert result == 0, f"Expected return code 0, got {result}"
        mock_oracle_main.assert_called_once()

    @patch('tarot_oracle.cli.tarot_main')
    def test_example_list_decks(self, mock_tarot_main):
        """Test example: tarot-oracle deck --list."""
        mock_tarot_main.return_value = 0

        test_args = [
            'tarot-oracle',
            'deck',
            '--list'
        ]

        with patch('sys.argv', test_args):
            result = cli_main()

        assert result == 0, f"Expected return code 0, got {result}"
        mock_tarot_main.assert_called_once()

    @patch('tarot_oracle.cli.oracle_main')
    def test_example_custom_invocation(self, mock_oracle_main):
        """Test example: tarot-oracle reading "Should I take this opportunity?" --invocation-name hermes-thoth."""
        mock_oracle_main.return_value = 0

        test_args = [
            'tarot-oracle',
            'reading',
            'Should I take this opportunity?',
            '--invocation-name', 'hermes-thoth'
        ]

        with patch('sys.argv', test_args):
            result = cli_main()

        assert result == 0, f"Expected return code 0, got {result}"
        mock_oracle_main.assert_called_once()


if __name__ == "__main__":
    unittest.main()
