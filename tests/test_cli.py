"""Test CLI subcommand functionality and unified interface."""

import pytest
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
from tarot_oracle.exceptions import TarotOracleError


class TestUnifiedParser:
    """Test unified CLI argument parser."""
    
    def test_parser_creation(self):
        """Test basic parser creation."""
        parser = create_unified_parser()
        assert isinstance(parser, ArgumentParser)
        assert parser.prog == "tarot-oracle"
    
    def test_version_argument(self):
        """Test version argument handling."""
        parser = create_unified_parser()
        with pytest.raises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['--version'])
    
    def test_subcommands_required(self):
        """Test that subcommands are required."""
        parser = create_unified_parser()
        with pytest.raises(SystemExit):
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
        
        assert args.command == 'reading'
        assert args.question == 'What does the future hold?'
        assert args.provider == 'gemini'
        assert args.interpret is True
        assert args.spread == 'celtic'
    
    def test_deck_command_parsing(self):
        """Test deck subcommand parsing."""
        parser = create_unified_parser()
        args = parser.parse_args([
            'deck',
            '--list'
        ])
        
        assert args.command == 'deck'
        assert args.list_decks is True
    
    def test_invocation_command_parsing(self):
        """Test invocation subcommand parsing."""
        parser = create_unified_parser()
        args = parser.parse_args([
            'invocation',
            '--list'
        ])
        
        assert args.command == 'invocation'
        assert args.list_invocations is True
    
    def test_spread_command_parsing(self):
        """Test spread subcommand parsing."""
        parser = create_unified_parser()
        args = parser.parse_args([
            'spread',
            '--list'
        ])
        
        assert args.command == 'spread'
        assert args.list_spreads is True
    
    def test_reading_command_defaults(self):
        """Test reading command defaults."""
        parser = create_unified_parser()
        args = parser.parse_args([
            'reading',
            'Test question'
        ])
        
        assert args.provider == 'gemini'
        assert args.spread == '3-card'
        assert args.interpret is False
    
    def test_provider_choices_validation(self):
        """Test provider choice validation."""
        parser = create_unified_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([
                'reading',
                'Test question',
                '--provider', 'invalid'
            ])


class TestReadingArguments:
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
        
        assert args.question == 'Test question'
        assert args.provider == 'openrouter'
        assert args.interpret is True
        assert args.invocation == 'Custom invocation'
        assert args.invocation_name == 'custom'
        assert args.spread == 'celtic'


class TestDeckArguments:
    """Test deck subcommand argument configuration."""
    
    def test_add_deck_arguments(self):
        """Test deck arguments are added correctly."""
        parser = ArgumentParser()
        _add_deck_arguments(parser)
        
        # Test parsing with list argument
        args = parser.parse_args(['--list'])
        assert args.list_decks is True


class TestInvocationArguments:
    """Test invocation subcommand argument configuration."""
    
    def test_add_invocation_arguments(self):
        """Test invocation arguments are added correctly."""
        parser = ArgumentParser()
        _add_invocation_arguments(parser)
        
        # Test parsing with list argument
        args = parser.parse_args(['--list'])
        assert args.list_invocations is True


class TestSpreadArguments:
    """Test spread subcommand argument configuration."""
    
    def test_add_spread_arguments(self):
        """Test spread arguments are added correctly."""
        parser = ArgumentParser()
        _add_spread_arguments(parser)
        
        # Test parsing with list argument
        args = parser.parse_args(['--list'])
        assert args.list_spreads is True


class TestCLIIntegration:
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
        
        assert result == 0
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
        
        assert result == 0
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
        
        assert result == 0
    
    def test_spread_command_integration(self):
        """Test spread command integration."""
        test_args = [
            'tarot-oracle',
            'spread',
            '--list'
        ]
        
        with patch('sys.argv', test_args):
            result = cli_main()
        
        assert result == 0


class TestCLIErrorHandling:
    """Test CLI error handling and user guidance."""
    
    @patch('tarot_oracle.cli.oracle_main')
    def test_tarot_oracle_error_handling(self, mock_oracle_main):
        """Test handling of TarotOracleError."""
        mock_oracle_main.side_effect = TarotOracleError(
            "Test error",
            suggestions=["Try again", "Check config"]
        )
        
        test_args = [
            'tarot-oracle',
            'reading',
            'Test question'
        ]
        
        with patch('sys.argv', test_args):
            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                result = cli_main()
        
        assert result != 0
        assert "Test error" in mock_stderr.getvalue()
        assert "Suggestions:" in mock_stderr.getvalue()
    
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
        
        assert result != 0
        assert "Unexpected error" in mock_stderr.getvalue()


class TestCLIHelpSystem:
    """Test CLI help system and documentation."""
    
    def test_main_help(self):
        """Test main help output."""
        parser = create_unified_parser()
        with pytest.raises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['--help'])
        
        help_text = mock_stdout.getvalue()
        assert "Unified CLI for Tarot Oracle" in help_text
        assert "reading" in help_text
        assert "deck" in help_text
        assert "invocation" in help_text
        assert "spread" in help_text
    
    def test_reading_help(self):
        """Test reading subcommand help."""
        parser = create_unified_parser()
        with pytest.raises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['reading', '--help'])
        
        help_text = mock_stdout.getvalue()
        assert "oracle functionality" in help_text.lower()
        assert "provider" in help_text
        assert "interpret" in help_text
    
    def test_deck_help(self):
        """Test deck subcommand help."""
        parser = create_unified_parser()
        with pytest.raises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['deck', '--help'])
        
        help_text = mock_stdout.getvalue()
        assert "tarot decks" in help_text.lower()
        assert "list" in help_text.lower()
    
    def test_invocation_help(self):
        """Test invocation subcommand help."""
        parser = create_unified_parser()
        with pytest.raises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['invocation', '--help'])
        
        help_text = mock_stdout.getvalue()
        assert "invocation" in help_text.lower()
        assert "custom" in help_text.lower()
    
    def test_spread_help(self):
        """Test spread subcommand help."""
        parser = create_unified_parser()
        with pytest.raises(SystemExit):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                parser.parse_args(['spread', '--help'])
        
        help_text = mock_stdout.getvalue()
        assert "spread" in help_text.lower()
        assert "custom" in help_text.lower()


class TestCLIArguments:
    """Test CLI argument validation and processing."""
    
    def test_question_argument_required(self):
        """Test that question is required for reading command."""
        parser = create_unified_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(['reading'])
    
    def test_provider_argument_choices(self):
        """Test provider argument limited to valid choices."""
        parser = create_unified_parser()
        
        # Valid providers should work
        for provider in ['gemini', 'openrouter', 'ollama']:
            args = parser.parse_args([
                'reading', 'Test question', '--provider', provider
            ])
            assert args.provider == provider
    
    def test_spread_argument_processing(self):
        """Test spread argument processing."""
        parser = create_unified_parser()
        
        # Default spread
        args = parser.parse_args(['reading', 'Test question'])
        assert args.spread == '3-card'
        
        # Custom spread
        args = parser.parse_args([
            'reading', 'Test question', '--spread', 'celtic'
        ])
        assert args.spread == 'celtic'
    
    def test_boolean_flags(self):
        """Test boolean flag processing."""
        parser = create_unified_parser()
        
        # Default (False)
        args = parser.parse_args(['reading', 'Test question'])
        assert args.interpret is False
        
        # Explicit True
        args = parser.parse_args(['reading', 'Test question', '--interpret'])
        assert args.interpret is True


class TestCLIExamples:
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
        
        assert result == 0
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
        
        assert result == 0
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
        
        assert result == 0
        mock_oracle_main.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])