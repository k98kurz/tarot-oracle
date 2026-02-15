"""Test CLI entry points for tarot and oracle commands."""

import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from tarot_oracle import tarot, oracle
from tarot_oracle.helpers import config


class TestTarotCLI(unittest.TestCase):
    def setUp(self):
        """Set up common tarot test mocks."""
        self.divination_patcher = patch('tarot_oracle.tarot.TarotDivination')
        self.mock_divination_class = self.divination_patcher.start()
        self.mock_instance = MagicMock()
        self.mock_instance.perform_reading.return_value = ("Spread", "Legend")
        self.mock_instance.perform_reading_json.return_value = {
            "question": "Test",
            "spread_type": "3-card",
            "cards": []
        }
        self.mock_divination_class.return_value = self.mock_instance

    def tearDown(self):
        """Clean up patches."""
        self.divination_patcher.stop()

    def test_tarot_parser_has_required_arguments(self):
        """Verify parser has core arguments."""
        parser = tarot.create_parser()

        args = parser.parse_args(['test question'])
        assert args.question == 'test question'
        assert args.lookup is None
        assert args.spread == '3-card'
        assert args.random == 8
        assert args.no_keywords is False
        assert args.reversed is False
        assert args.json is False

    def test_tarot_basic_reading(self):
        """Test basic reading with question only."""
        self.mock_instance.perform_reading.return_value = ("Test Spread\nLayout", "Test Legend")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = tarot.main(['What does the future hold?'])
            output = mock_stdout.getvalue()

            assert result == 0
            assert 'Question: What does the future hold?' in output
            assert 'Spread: 3-card' in output
            assert 'Test Spread\nLayout' in output
            assert 'Test Legend' in output
            self.mock_instance.perform_reading.assert_called_once()

    def test_tarot_json_output(self):
        """Test reading with --json flag."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = tarot.main(['Test question', '--json'])
            output = mock_stdout.getvalue()

            assert result == 0
            assert '"question": "Test"' in output
            assert '"spread_type": "3-card"' in output
            self.mock_instance.perform_reading_json.assert_called_once()

    def test_tarot_lookup_mode(self):
        """Test --lookup with valid card codes."""
        with patch('tarot_oracle.tarot.resolve_card_codes') as mock_resolve:
            mock_resolve.return_value = []

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = tarot.main(['--lookup', 'I,W3,C_Q'])
                output = mock_stdout.getvalue()

                assert result == 0
                mock_resolve.assert_called_once_with('I,W3,C_Q')

    def test_tarot_list_decks(self):
        """Test --list-decks output."""
        with patch('tarot_oracle.tarot.DeckLoader') as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader.list_available_decks.return_value = [
                {'filename': 'test.json', 'name': 'Test Deck', 'description': 'Test'}
            ]
            mock_loader_class.return_value = mock_loader

            with patch('tarot_oracle.tarot.BundledDataLoader') as mock_bundled:
                mock_bundled.list_decks.return_value = ['rider-waite-smith']

                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = tarot.main(['--list-decks'])
                    output = mock_stdout.getvalue()

                    assert result == 0
                    assert 'Bundled decks:' in output
                    assert 'rider-waite-smith' in output
                    assert 'User decks:' in output

    def test_tarot_list_spreads(self):
        """Test --list-spreads output."""
        with patch('tarot_oracle.tarot.SpreadLoader') as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader.list_spreads.return_value = []
            mock_loader_class.return_value = mock_loader

            with patch('tarot_oracle.tarot.BundledDataLoader') as mock_bundled:
                mock_bundled.list_spreads.return_value = ['3-card', 'celtic-cross']

                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = tarot.main(['--list-spreads'])
                    output = mock_stdout.getvalue()

                    assert result == 0
                    assert 'Bundled spreads:' in output
                    assert '3-card' in output
                    assert 'celtic-cross' in output

    def test_tarot_missing_question(self):
        """Test returns 1 and prints error for missing question."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = tarot.main([])
            output = mock_stdout.getvalue()

            assert result == 1
            assert 'Error: Question is required' in output

    def test_tarot_invalid_deck(self):
        """Test returns 1 and prints error for invalid deck."""
        with patch('tarot_oracle.tarot.Deck.load_deck_by_name') as mock_load:
            mock_load.side_effect = ValueError(f"Deck 'nonexistent' not found.")

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = tarot.main(['--deck', 'nonexistent', 'test question'])
                output = mock_stdout.getvalue()

                assert result == 1
                assert "Error: Deck 'nonexistent' not found" in output

    def test_tarot_invalid_spread(self):
        """Test returns 1 and prints error for invalid spread."""
        with patch('tarot_oracle.tarot.resolve_spread') as mock_resolve:
            mock_resolve.side_effect = ValueError("Invalid spread")

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = tarot.main(['--spread', 'invalid-spread', 'test question'])
                output = mock_stdout.getvalue()

                assert result == 1
                assert 'Error: Invalid spread' in output

    def test_tarot_invalid_card_codes(self):
        """Test --lookup with invalid card codes returns 1."""
        with patch('tarot_oracle.tarot.resolve_card_codes') as mock_resolve:
            mock_resolve.side_effect = ValueError("Invalid card code: XYZ")

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = tarot.main(['--lookup', 'XYZ,ABC'])
                output = mock_stdout.getvalue()

                assert result == 1
                assert 'Error: Invalid card code' in output

    def test_tarot_export_success(self):
        """Test export commands successfully export bundled resources."""
        test_cases = [
            ('deck', 'rider-waite-smith', 'export_deck', '{"name": "Test"}'),
            ('spread', '3-card', 'export_spread', '{"name": "Test Spread"}'),
        ]

        for resource_type, name, export_method, expected_output in test_cases:
            with self.subTest(resource=resource_type, name=name):
                with patch('tarot_oracle.tarot.BundledDataLoader') as mock_bundled:
                    getattr(mock_bundled, export_method).return_value = expected_output

                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        result = tarot.main([f'--export-{resource_type}', name])
                        output = mock_stdout.getvalue()

                        assert result == 0
                        assert expected_output in output
                        getattr(mock_bundled, export_method).assert_called_once_with(name)

    def test_tarot_export_not_found(self):
        """Test export commands handle non-existent resources."""
        test_cases = [
            ('deck', 'nonexistent', 'export_deck', "Error: Deck 'nonexistent' not found"),
            ('spread', 'nonexistent', 'export_spread', "Error: Spread 'nonexistent' not found"),
        ]

        for resource_type, name, export_method, expected_error in test_cases:
            with self.subTest(resource=resource_type, name=name):
                with patch('tarot_oracle.tarot.BundledDataLoader') as mock_bundled:
                    getattr(mock_bundled, export_method).return_value = None

                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        result = tarot.main([f'--export-{resource_type}', name])
                        output = mock_stdout.getvalue()

                        assert result == 1
                        assert expected_error in output
                        getattr(mock_bundled, export_method).assert_called_once_with(name)

    def test_tarot_parameter_flags(self):
        """Test flags that pass parameters to reading."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = tarot.main(['--random', '16', '--reversed', 'test question'])
            output = mock_stdout.getvalue()

            assert result == 0
            assert 'Question: test question' in output
            assert 'Spread: 3-card' in output
            assert 'Spread' in output
            assert 'Legend' in output

    def test_tarot_invocation_flags(self):
        """Test invocation-related flags."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = tarot.main(['--invoke', 'test question'])
            output = mock_stdout.getvalue()

            assert result == 0
            assert 'Reading influenced by divine invocation' in output

    def test_tarot_custom_invocation_text(self):
        """Test --invocation flag with custom invocation text."""
        custom_invocation = "By ancient powers, I seek wisdom through the cards"
        self.mock_instance.perform_reading.return_value = ("Spread", "Legend")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = tarot.main(['--invocation', custom_invocation, 'test question'])
            output = mock_stdout.getvalue()

            assert result == 0
            assert 'Question: test question' in output
            assert 'Reading influenced by divine invocation' in output
            self.mock_instance.perform_reading.assert_called_once()
            call_args = self.mock_instance.perform_reading.call_args
            assert call_args[0][2] == custom_invocation

    def test_tarot_no_keywords(self):
        """Test --no-keywords hides keyword descriptions."""
        self.mock_instance.perform_reading.return_value = ("Spread", "Legend without keywords")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = tarot.main(['--no-keywords', 'test question'])
            output = mock_stdout.getvalue()

            assert result == 0
            assert 'Question: test question' in output
            assert 'Legend without keywords' in output

    def test_tarot_custom_spread_matrix(self):
        """Test --spread with custom matrix format."""
        custom_matrix = "[[1,2,3],[4,5,6]]"
        self.mock_instance.perform_reading.return_value = ("Spread", "Legend")

        with patch('tarot_oracle.tarot.resolve_spread') as mock_resolve:
            mock_resolve.return_value = ([[1, 2, 3], [4, 5, 6]], None)

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = tarot.main(['--spread', custom_matrix, 'test question'])
                output = mock_stdout.getvalue()

                assert result == 0
                assert 'Question: test question' in output
                assert 'Spread:' in output
                mock_resolve.assert_called_once_with(custom_matrix)


class TestOracleCLI(unittest.TestCase):
    def setUp(self):
        """Set up common oracle test mocks."""
        self.oracle_patcher = patch('tarot_oracle.oracle.Oracle')
        self.mock_oracle_class = self.oracle_patcher.start()
        self.mock_instance = MagicMock()
        self.mock_instance.perform_divinatory_reading.return_value = {
            'question': 'Test',
            'spread_type': '3-card',
            'spread_display': 'Spread',
            'legend_display': 'Legend',
            'interpretation_requested': False,
            'interpretation': None
        }
        self.mock_oracle_class.return_value = self.mock_instance

        # Save current autosave_sessions config value and disable for tests
        conf = config()
        self.original_autosave = conf.get('autosave_sessions')
        conf.set('autosave_sessions', False)

    def tearDown(self):
        """Clean up patches and restore config."""
        self.oracle_patcher.stop()

        # Restore original autosave_sessions config value
        conf = config()
        if self.original_autosave is None:
            conf.unset('autosave_sessions')
        else:
            conf.set('autosave_sessions', self.original_autosave)

    def test_oracle_parser_provider_choices(self):
        """Verify parser has correct provider choices."""
        parser = oracle.create_oracle_parser()

        args = parser.parse_args(['test'])
        assert args.provider == 'ollama'
        assert args.interpret is None

        args = parser.parse_args(['--provider', 'openrouter', 'test'])
        assert args.provider == 'openrouter'

        args = parser.parse_args(['--provider', 'ollama', 'test'])
        assert args.provider == 'ollama'

    def test_oracle_parser_session_options(self):
        """Verify session save options."""
        parser = oracle.create_oracle_parser()

        args = parser.parse_args(['test'])
        assert args.save is False
        assert args.no_save is False
        assert args.save_path is None

        args = parser.parse_args(['--save', 'test'])
        assert args.save is True

        args = parser.parse_args(['--no-save', 'test'])
        assert args.no_save is True

        args = parser.parse_args(['--save-path', '/tmp/sessions', 'test'])
        assert args.save_path == '/tmp/sessions'

    def test_oracle_basic_divination(self):
        """Test basic reading without interpretation."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = oracle.main(['What should I do?'])
            output = mock_stdout.getvalue()

            assert result == 0
            assert '=== Invocation ===' in output
            assert '=== Tarot Reading ===' in output

    def test_oracle_with_interpretation(self):
        """Test reading with --interpret flag."""
        self.mock_instance.perform_divinatory_reading.return_value = {
            'question': 'Test',
            'spread_type': '3-card',
            'spread_display': 'Spread',
            'legend_display': 'Legend',
            'interpretation_requested': True,
            'interpretation': 'The cards suggest...'
        }
        mock_client = MagicMock()
        self.mock_instance.get_client.return_value = mock_client

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = oracle.main(['--interpret', 'Test question'])
            output = mock_stdout.getvalue()

            assert result == 0
            assert '=== Interpretation ===' in output

    def test_oracle_save_session(self):
        """Test reading with --save flag."""
        with patch('tarot_oracle.oracle.save_oracle_session') as mock_save:
            mock_save.return_value = True

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['--save', 'Test question'])

                assert result == 0
                mock_save.assert_called_once()

    def test_oracle_custom_invocation(self):
        """Test reading with custom invocation."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = oracle.main(['--invocation', 'By ancient powers', 'Test question'])
            output = mock_stdout.getvalue()

            assert result == 0
            assert '=== Invocation ===' in output

    def test_oracle_missing_question(self):
        """Test returns 1 for missing question."""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            parser = oracle.create_oracle_parser()
            try:
                args = parser.parse_args([])
            except SystemExit:
                pass

    def test_oracle_provider_error(self):
        """Test handling of Oracle errors."""
        self.mock_instance.perform_divinatory_reading.return_value = {
            'error': 'Provider unavailable'
        }

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = oracle.main(['Test question'])
            output = mock_stdout.getvalue()

            assert result == 1
            assert 'Error: Provider unavailable' in output

    def test_oracle_provider_validation(self):
        """Test provider-specific validation checks."""
        self.mock_instance.perform_divinatory_reading.return_value = {
            'question': 'Test',
            'spread_type': '3-card',
            'spread_display': 'Spread',
            'legend_display': 'Legend',
            'interpretation_requested': True,
            'interpretation': None
        }

        test_cases = [
            ('openrouter', 'check_api_key', False, 'API key validation failed'),
            ('ollama', 'check_model_available', False, f"Model '{oracle.ORACLE_CONFIG_DEFAULTS['ollama_model']}' not found in Ollama"),
        ]

        for provider, check_method, check_result, expected_message in test_cases:
            with self.subTest(provider=provider):
                mock_client = MagicMock()
                getattr(mock_client, check_method).return_value = check_result
                self.mock_instance.get_client.return_value = mock_client

                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = oracle.main(['--provider', provider, '--interpret', 'Test'])
                    output = mock_stdout.getvalue()

                    assert result == 0
                    assert expected_message in output

    def test_oracle_flag_combinations(self):
        """Test various oracle flag combinations."""
        test_cases = [
            (
                ['--model', 'gpt-4', '--api-key', 'test-key', '--ollama-host', 'localhost:11434', '--timeout', '60', 'Test'],
                'provider flags'
            ),
            (
                ['--random', '16', '--reversed', 'Test'],
                'tarot flags'
            ),
        ]

        for flags, case_name in test_cases:
            with self.subTest(case=case_name):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = oracle.main(flags)
                    output = mock_stdout.getvalue()

                    assert result == 0
                    assert '=== Invocation ===' in output
                    assert '=== Tarot Reading ===' in output

        with self.subTest(case='save flags'):
            conf = config()
            conf.set('autosave_sessions', True)

            with patch('tarot_oracle.oracle.save_oracle_session') as mock_save:
                mock_save.return_value = True

                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = oracle.main(['--no-save', 'Test'])
                    output = mock_stdout.getvalue()

                    assert result == 0
                    assert '=== Invocation ===' in output
                    mock_save.assert_not_called()

            conf.set('autosave_sessions', False)

    def test_oracle_custom_spreads(self):
        """Test multiple built-in spread types."""
        spreads = ['cross', 'celtic', 'single', 'crowley']

        for spread in spreads:
            with self.subTest(spread=spread):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = oracle.main(['--spread', spread, 'Test question'])
                    output = mock_stdout.getvalue()

                    assert result == 0
                    assert '=== Invocation ===' in output
                    assert '=== Tarot Reading ===' in output

    def test_oracle_save_override(self):
        """Test --save flag override when autosave_sessions is False."""
        with patch('tarot_oracle.oracle.save_oracle_session') as mock_save:
            mock_save.return_value = True

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['--save', 'Test question'])
                output = mock_stdout.getvalue()

                assert result == 0
                assert '=== Invocation ===' in output
                mock_save.assert_called_once()

    def test_oracle_config_display(self):
        """Test --config displays all 6 configuration keys."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = oracle.main(['--config'])
            output = mock_stdout.getvalue()

            assert result == 0
            assert 'Oracle Configuration:' in output
            assert 'autosave_location' in output
            assert 'autosave_sessions' in output
            assert 'google_ai_api_key' in output
            assert 'ollama_host' in output
            assert 'openrouter_api_key' in output
            assert 'provider' in output

    def test_oracle_set_config_string_key(self):
        """Test --set-config with valid string keys."""
        with patch('tarot_oracle.oracle.config') as mock_config:
            mock_config.return_value.get.return_value = None
            mock_config.return_value.list.return_value = []

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['--set-config', 'provider', 'ollama'])
                output = mock_stdout.getvalue()

                assert result == 0
                assert 'Configuration set: provider = ollama' in output
                mock_config.return_value.set.assert_called_once_with('provider', 'ollama')
                mock_config.return_value.save.assert_called_once()

    def test_oracle_set_config_boolean_true(self):
        """Test --set-config with boolean true values for autosave_sessions."""
        test_values = ['true', '1', 'yes']

        for value in test_values:
            with self.subTest(value=value):
                with patch('tarot_oracle.oracle.config') as mock_config:
                    mock_config.return_value.get.return_value = None
                    mock_config.return_value.list.return_value = []

                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        result = oracle.main(['--set-config', 'autosave_sessions', value])
                        output = mock_stdout.getvalue()

                        assert result == 0
                        assert 'Configuration set: autosave_sessions' in output
                        mock_config.return_value.set.assert_called_once_with('autosave_sessions', True)
                        mock_config.return_value.save.assert_called_once()

    def test_oracle_set_config_boolean_false(self):
        """Test --set-config with boolean false values for autosave_sessions."""
        test_values = ['false', '0', 'no']

        for value in test_values:
            with self.subTest(value=value):
                with patch('tarot_oracle.oracle.config') as mock_config:
                    mock_config.return_value.get.return_value = None
                    mock_config.return_value.list.return_value = []

                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        result = oracle.main(['--set-config', 'autosave_sessions', value])
                        output = mock_stdout.getvalue()

                        assert result == 0
                        assert 'Configuration set: autosave_sessions' in output
                        mock_config.return_value.set.assert_called_once_with('autosave_sessions', False)
                        mock_config.return_value.save.assert_called_once()

    def test_oracle_set_config_invalid_key(self):
        """Test --set-config rejects invalid keys."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = oracle.main(['--set-config', 'invalid_key', 'value'])
            output = mock_stdout.getvalue()

            assert result == 1
            assert 'Error: Invalid configuration key' in output
            assert 'Valid keys:' in output

    def test_oracle_set_config_invalid_boolean(self):
        """Test --set-config rejects invalid boolean values for autosave_sessions."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = oracle.main(['--set-config', 'autosave_sessions', 'maybe'])
            output = mock_stdout.getvalue()

            assert result == 1
            assert 'Error: Invalid value' in output
            assert 'Use: true, false, 1, 0, yes, no' in output

    def test_oracle_unset_config_valid_key(self):
        """Test --unset-config removes valid keys."""
        with patch('tarot_oracle.oracle.config') as mock_config:
            mock_config.return_value.get.return_value = 'some_value'
            mock_config.return_value.list.return_value = ['provider']

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['--unset-config', 'provider'])
                output = mock_stdout.getvalue()

                assert result == 0
                assert 'Configuration unset: provider' in output
                mock_config.return_value.unset.assert_called_once_with('provider')
                mock_config.return_value.save.assert_called_once()

    def test_oracle_unset_config_invalid_key(self):
        """Test --unset-config rejects invalid keys."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = oracle.main(['--unset-config', 'invalid_key'])
            output = mock_stdout.getvalue()

            assert result == 1
            assert 'Error: Invalid configuration key' in output
            assert 'Valid keys:' in output

    def test_oracle_config_display_with_defaults(self):
        """Test --config displays default values for unset keys."""
        with patch('tarot_oracle.oracle.config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.get.return_value = None
            mock_config.list.return_value = []
            mock_config_func.return_value = mock_config

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['--config'])
                output = mock_stdout.getvalue()

                assert result == 0
                assert 'Oracle Configuration:' in output
                assert f"(default: {oracle.ORACLE_CONFIG_DEFAULTS['provider']})" in output
                assert f"(default: {oracle.ORACLE_CONFIG_DEFAULTS['ollama_model']})" in output
                assert f"(default: {oracle.ORACLE_CONFIG_DEFAULTS['gemini_model']})" in output
                assert f"(default: {oracle.ORACLE_CONFIG_DEFAULTS['openrouter_model']})" in output
                assert f"(default: {oracle.ORACLE_CONFIG_DEFAULTS['ollama_host']})" in output
                assert f"(default: {oracle.ORACLE_CONFIG_DEFAULTS['autosave_sessions']})" in output
                assert f"(default: {oracle.ORACLE_CONFIG_DEFAULTS['autosave_location']})" in output
                assert f"(default: {oracle.ORACLE_CONFIG_DEFAULTS['interpret']})" in output

    def test_oracle_set_config_provider_valid(self):
        """Test --set-config with valid provider values."""
        valid_providers = ['gemini', 'openrouter', 'ollama']

        for provider in valid_providers:
            with self.subTest(provider=provider):
                with patch('tarot_oracle.oracle.config') as mock_config:
                    mock_config.return_value.get.return_value = None
                    mock_config.return_value.list.return_value = []

                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        result = oracle.main(['--set-config', 'provider', provider])
                        output = mock_stdout.getvalue()

                        assert result == 0
                        assert 'Configuration set: provider' in output
                        mock_config.return_value.set.assert_called_once_with('provider', provider)
                        mock_config.return_value.save.assert_called_once()

    def test_oracle_set_config_provider_invalid(self):
        """Test --set-config rejects invalid provider values."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = oracle.main(['--set-config', 'provider', 'invalid_provider'])
            output = mock_stdout.getvalue()

            assert result == 1
            assert 'Error: Invalid provider' in output
            assert 'Valid providers: gemini, openrouter, ollama' in output

    def test_oracle_set_config_gemini_model(self):
        """Test --set-config with gemini_model."""
        with patch('tarot_oracle.oracle.config') as mock_config:
            mock_config.return_value.get.return_value = None
            mock_config.return_value.list.return_value = []

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['--set-config', 'gemini_model', 'gemini-pro'])
                output = mock_stdout.getvalue()

                assert result == 0
                assert 'Configuration set: gemini_model = gemini-pro' in output
                mock_config.return_value.set.assert_called_once_with('gemini_model', 'gemini-pro')
                mock_config.return_value.save.assert_called_once()

    def test_oracle_set_config_openrouter_model(self):
        """Test --set-config with openrouter_model."""
        with patch('tarot_oracle.oracle.config') as mock_config:
            mock_config.return_value.get.return_value = None
            mock_config.return_value.list.return_value = []

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['--set-config', 'openrouter_model', 'gpt-4'])
                output = mock_stdout.getvalue()

                assert result == 0
                assert 'Configuration set: openrouter_model = gpt-4' in output
                mock_config.return_value.set.assert_called_once_with('openrouter_model', 'gpt-4')
                mock_config.return_value.save.assert_called_once()

    def test_oracle_set_config_ollama_model(self):
        """Test --set-config with ollama_model."""
        with patch('tarot_oracle.oracle.config') as mock_config:
            mock_config.return_value.get.return_value = None
            mock_config.return_value.list.return_value = []

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['--set-config', 'ollama_model', 'llama2'])
                output = mock_stdout.getvalue()

                assert result == 0
                assert 'Configuration set: ollama_model = llama2' in output
                mock_config.return_value.set.assert_called_once_with('ollama_model', 'llama2')
                mock_config.return_value.save.assert_called_once()

    def test_oracle_config_uses_model_defaults(self):
        """Test Oracle uses config model defaults when --model not provided."""
        config_values = {
            'provider': 'ollama',
            'ollama_model': 'custom-llama',
            'ollama_host': 'localhost:11434'
        }

        with patch('tarot_oracle.oracle.OllamaClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            with patch('tarot_oracle.oracle.config') as mock_config_func:
                mock_config = MagicMock()
                mock_config.get.side_effect = lambda key, default=None: config_values.get(key, default)
                mock_config.list.return_value = ['provider', 'ollama_model']
                mock_config_func.return_value = mock_config

                self.oracle_patcher.stop()
                try:
                    oracle_instance = oracle.Oracle()

                    assert oracle_instance.default_model == 'custom-llama'

                    mock_config.get.assert_any_call('ollama_model', oracle.ORACLE_CONFIG_DEFAULTS['ollama_model'])
                finally:
                    self.oracle_patcher.start()

    def test_oracle_set_config_interpret_valid(self):
        """Test --set-config with interpret boolean values."""
        valid_values = ['true', '1', 'yes', 'false', '0', 'no']

        for value in valid_values:
            with self.subTest(value=value):
                with patch('tarot_oracle.oracle.config') as mock_config:
                    mock_config.return_value.get.return_value = None
                    mock_config.return_value.list.return_value = []

                    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                        result = oracle.main(['--set-config', 'interpret', value])
                        output = mock_stdout.getvalue()

                        assert result == 0
                        assert 'Configuration set: interpret' in output

    def test_oracle_set_config_interpret_invalid(self):
        """Test --set-config rejects invalid interpret values."""
        invalid_values = ['maybe', '2', 'invalid']

        for value in invalid_values:
            with self.subTest(value=value):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    result = oracle.main(['--set-config', 'interpret', value])
                    output = mock_stdout.getvalue()

                    assert result == 1
                    assert 'Error: Invalid value' in output

    def test_oracle_interpret_flag_overrides_config(self):
        """Test --interpret flag overrides config setting."""
        config_values = {
            'provider': 'ollama',
            'ollama_model': 'test-model',
            'ollama_host': 'localhost:11434',
            'autosave_sessions': False,
            'interpret': False
        }

        with patch('tarot_oracle.oracle.config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.get.side_effect = lambda key, default=None: config_values.get(key, default)
            mock_config.list.return_value = ['provider', 'ollama_model', 'interpret']
            mock_config_func.return_value = mock_config

            self.mock_instance.perform_divinatory_reading.return_value = {
                'question': 'Test',
                'spread_type': '3-card',
                'spread_display': 'Spread',
                'legend_display': 'Legend',
                'interpretation_requested': True,
                'interpretation': 'Interpretation'
            }

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['--interpret', 'Test question'])
                output = mock_stdout.getvalue()

                assert result == 0

    def test_oracle_no_interpret_flag_overrides_config(self):
        """Test --no-interpret flag overrides config setting."""
        config_values = {
            'provider': 'ollama',
            'ollama_model': 'test-model',
            'ollama_host': 'localhost:11434',
            'autosave_sessions': False,
            'interpret': True
        }

        with patch('tarot_oracle.oracle.config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.get.side_effect = lambda key, default=None: config_values.get(key, default)
            mock_config.list.return_value = ['provider', 'ollama_model', 'interpret']
            mock_config_func.return_value = mock_config

            self.mock_instance.perform_divinatory_reading.return_value = {
                'question': 'Test',
                'spread_type': '3-card',
                'spread_display': 'Spread',
                'legend_display': 'Legend',
                'interpretation_requested': False,
                'interpretation': None
            }

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['--no-interpret', 'Test question'])
                output = mock_stdout.getvalue()

                assert result == 0

    def test_oracle_interpret_respects_config_default(self):
        """Test interpret respects config default when no flag provided."""
        config_values = {
            'provider': 'ollama',
            'ollama_model': 'test-model',
            'ollama_host': 'localhost:11434',
            'autosave_sessions': False,
            'interpret': False
        }

        with patch('tarot_oracle.oracle.config') as mock_config_func:
            mock_config = MagicMock()
            mock_config.get.side_effect = lambda key, default=None: config_values.get(key, default)
            mock_config.list.return_value = ['provider', 'ollama_model', 'interpret']
            mock_config_func.return_value = mock_config

            self.mock_instance.perform_divinatory_reading.return_value = {
                'question': 'Test',
                'spread_type': '3-card',
                'spread_display': 'Spread',
                'legend_display': 'Legend',
                'interpretation_requested': False,
                'interpretation': None
            }

            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                result = oracle.main(['Test question'])
                output = mock_stdout.getvalue()

                assert result == 0


if __name__ == "__main__":
    unittest.main()
