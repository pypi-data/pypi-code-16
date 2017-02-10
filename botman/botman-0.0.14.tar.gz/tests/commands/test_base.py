"""
Tests for the base command implementation
"""

import unittest
import unittest.mock

import asynctest

import botman.bot
import botman.commands.base
import botman.errors

import tests.mixins

@asynctest.fail_on(unused_loop=False)
class TestCommand(tests.mixins.DiscordMockMixin, asynctest.TestCase):
    """
    Tests for the base command implementation
    """

    def test_description_default(self):
        """
        Tests that the description defaults to pydocs
        """

        mock_handler = asynctest.CoroutineMock(
            __name__='test',
            __doc__='This is a description',
        )

        command = botman.commands.base.Command('test', mock_handler)

        self.assertEqual(
            'This is a description',
            command.description,
            'Description defaulted to pydocs',
        )

    def test_matches_default(self):
        """
        Tests that matches defaults to True with no validators
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.Command('test', mock_handler)

        mock_bot = self.get_mock_bot()
        mock_message = self.get_mock_message('test')

        self.assertTrue(
            command.matches(mock_bot, mock_message, ''),
            'Mathces defaults to true',
        )

    def test_matches_calls_validators(self):
        """
        Tests that matches calls the validators
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.Command('test', mock_handler)

        mock_validator = unittest.mock.Mock()
        mock_validator.return_value = False

        command.validators.append(mock_validator)

        mock_bot = self.get_mock_bot()
        mock_message = self.get_mock_message('test')

        self.assertFalse(
            command.matches(mock_bot, mock_message, ''),
            'Matches returned the correct value',
        )

        mock_validator.assert_called_with(mock_bot, mock_message, '')

    def test_parse_arguments(self):
        """
        Tests that we can parse command line arguments
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.Command('test', mock_handler)
        command.parameters = {
            'req_val': botman.commands.base.StringArg(required=True),
            'opt_val': botman.commands.base.StringArg(default='test'),
        }

        self.assertDictEqual(
            {
                'req_val': 'my_val',
                'opt_val': 'test',
            },
            command.parse_arguments('my_val'),
            'Arguments were correctly parsed',
        )

    def test_parse_arguments_whitespace(self):
        """
        Tests that whitespace is ignored when parsing
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.Command('test', mock_handler)
        command.parameters = {
            'val_1': botman.commands.base.StringArg(required=True),
            'val_2': botman.commands.base.StringArg(required=True),
        }

        self.assertDictEqual(
            {
                'val_1': 'one',
                'val_2': 'two',
            },
            command.parse_arguments('one     two '),
            'Parser ignored whitespace',
        )

    def test_parse_arguments_quotes(self):
        """
        Tests that quotes are respected when parsing
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.Command('test', mock_handler)
        command.parameters = {
            'val_1': botman.commands.base.StringArg(required=True),
            'val_2': botman.commands.base.StringArg(required=True),
        }

        self.assertDictEqual(
            {
                'val_1': 'one two',
                'val_2': 'three',
            },
            command.parse_arguments('"one two"  three'),
            'Parser respected quotes',
        )

    def test_parse_arguments_rest(self):
        """
        Tests that the extra arguments are put in the last argument
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.Command('test', mock_handler)
        command.parameters = {
            'val_1': botman.commands.base.StringArg(required=True),
            'val_2': botman.commands.base.StringArg(required=True),
        }

        self.assertDictEqual(
            {
                'val_1': 'one',
                'val_2': 'two three',
            },
            command.parse_arguments('one two   three'),
            'Parser respected quotes',
        )

    def test_parse_arguments_rest_str(self):
        """
        Tests that the extra arguments are ignored if the last arg isnt a string
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.Command('test', mock_handler)
        command.parameters = {
            'val_1': botman.commands.base.StringArg(required=True),
            'val_2': botman.commands.base.IntArg(required=True),
        }

        self.assertDictEqual(
            {
                'val_1': 'one',
                'val_2': 2,
            },
            command.parse_arguments('one 2   three'),
            'Parser respected quotes',
        )

    async def test_call_not_matches(self):
        """
        Tests that the handler is not called when the message doesn't match
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.Command('test', mock_handler)

        mock_validator = unittest.mock.Mock()
        mock_validator.return_value = False

        command.validators.append(mock_validator)

        mock_bot = self.get_mock_bot()
        mock_message = self.get_mock_message('test')

        self.assertFalse(
            await command(mock_bot, mock_message, ''),
            'Command returned false since it was not handled',
        )

        mock_handler.assert_not_called()

    async def test_call_matches(self):
        """
        Tests that the handler is called when the message matches
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.Command('test', mock_handler)

        message = self.get_mock_message('testification')

        mock_bot = self.get_mock_bot()

        self.assertTrue(
            await command(mock_bot, message, ''),
            'Command returned true since it was handled',
        )

        mock_handler.assert_called_with(mock_bot, message)

