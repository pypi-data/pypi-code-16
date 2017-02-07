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
            command.matches(mock_bot, mock_message),
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
            command.matches(mock_bot, mock_message),
            'Matches returned the correct value',
        )

        mock_validator.assert_called_with(mock_bot, mock_message)

    def test_call_not_matches(self):
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
            command.matches(mock_bot, mock_message),
            'Matches returned the correct value',
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

        await command(mock_bot, message)

        mock_handler.assert_called_with(mock_bot, message)

@asynctest.fail_on(unused_loop=False)
class TestChatCommandDecorator(tests.mixins.DiscordMockMixin, asynctest.TestCase):
    """
    Tests for the chat_command decorator
    """

    def test_not_callable(self):
        """
        Tests that we can't decorate a non-callable object
        """

        expected = 'Cannot use a non-callable as a command'
        with self.assertRaises(botman.errors.ConfigurationError, msg=expected):
            botman.commands.base.chat_command('test')({})

    def test_not_coroutine(self):
        """
        Tests that we can't decorate a non-coroutine function
        """

        mock_handler = unittest.mock.Mock(__name__='test')

        expected = 'Cannot use a non-coroutine as a command'
        with self.assertRaises(botman.errors.ConfigurationError, msg=expected):
            botman.commands.base.chat_command('test')(mock_handler)

    def test_decorator_returns_command(self):
        """
        Tests that the decorator returns a Command instance
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        wrapped = botman.commands.base.chat_command('test')(mock_handler)

        self.assertIsInstance(
            wrapped,
            botman.commands.base.Command,
            'The function became a command instance',
        )

    def test_wrapper_has_name(self):
        """
        Tests that the decorator adds the correct name
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        wrapped = botman.commands.base.chat_command('test')(mock_handler)

        self.assertEqual(
            'test',
            wrapped.name,
            'The command had the correct name',
        )

    async def test_wrapper_calls_handler(self):
        """
        Tests that the Command instance calls the handler
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        wrapped = botman.commands.base.chat_command('test')(mock_handler)

        message = self.get_mock_message('test')
        wrapped.pattern = 'test'

        mock_bot = self.get_mock_bot()

        await wrapped(mock_bot, message)

        mock_handler.assert_called_with(mock_bot, message)

@asynctest.fail_on(unused_loop=False)
class TestDescriptionDecorator(tests.mixins.DiscordMockMixin, asynctest.TestCase):
    """
    Tests for the description deorator
    """

    def test_decorator_non_command(self):
        """
        Tests that the decorator only works on command instances
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')

        expected = 'test must have the chat_command decorator'
        with self.assertRaises(botman.errors.ConfigurationError, msg=expected):
            botman.commands.base.description('Descriptive')(mock_handler)

    def test_sets_description(self):
        """
        Tests that the decorator actually sets the description
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        wrapped = botman.commands.base.chat_command('test')(mock_handler)
        wrapped = botman.commands.base.description('Descriptive')(wrapped)

        self.assertEqual(
            'Descriptive',
            wrapped.description,
            'The description was set',
        )

@asynctest.fail_on(unused_loop=False)
class TestCommandPatternDecorator(tests.mixins.DiscordMockMixin, asynctest.TestCase):
    """
    Tests for the command_pattern decorator
    """

    def test_decorator_non_command(self):
        """
        Tests that the decorator only works on command instances
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')

        expected = 'test must have the chat_command decorator'
        with self.assertRaises(botman.errors.ConfigurationError, msg=expected):
            botman.commands.base.command_pattern(r'testification')(mock_handler)

    def test_decorator_invalid_pattern(self):
        """
        Tests that the decorator requires a valid pattern
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        wrapped = botman.commands.base.chat_command('test')(mock_handler)

        expected = 'first argument must be string or compiled pattern'
        with self.assertRaises(TypeError, msg=expected):
            botman.commands.base.command_pattern(1000)(wrapped)

    async def test_decorator_pattern_matches(self):
        """
        Tests that the command pattern matches
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')

        wrapped = botman.commands.base.chat_command('test')(mock_handler)
        wrapped = botman.commands.base.command_pattern(r'testification')(wrapped)

        mock_bot = self.get_mock_bot()

        message = self.get_mock_message('test')
        await wrapped(mock_bot, message)

        mock_handler.assert_not_called()

        message = self.get_mock_message('testification')
        await wrapped(mock_bot, message)

        mock_handler.assert_called_with(mock_bot, message)

@asynctest.fail_on(unused_loop=False)
class TestMentionsBotDecorator(tests.mixins.DiscordMockMixin, asynctest.TestCase):
    """
    Tests for the mentions_bot decorator
    """

    def test_decorator_non_command(self):
        """
        Tests that the decorator only works on command instances
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')

        expected = 'test must have the chat_command decorator'
        with self.assertRaises(botman.errors.ConfigurationError, msg=expected):
            botman.commands.base.mentions_bot()(mock_handler)

    async def test_matches_mention(self):
        """
        Tests that the validator matches when a message mentions the bot
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')

        wrapped = botman.commands.base.chat_command('test')(mock_handler)
        wrapped = botman.commands.base.mentions_bot()(wrapped)

        mock_bot = self.get_mock_bot()

        for text in ['hey!', '@bot hey!', '<@bot> hey!']:
            message = self.get_mock_message(text)
            await wrapped(mock_bot, message)

            mock_handler.assert_not_called()

        mock_user = self.get_mock_user()

        message = self.get_mock_message(
            f'{mock_user.mention} hey!',
            mentions=[mock_user],
        )

        await wrapped(mock_bot, message)

        mock_handler.assert_not_called()

        message = self.get_mock_message(
            f'{mock_bot.user.mention} hey!',
            mentions=[mock_bot.user],
        )

        await wrapped(mock_bot, message)

        mock_handler.assert_called_with(mock_bot, message)

