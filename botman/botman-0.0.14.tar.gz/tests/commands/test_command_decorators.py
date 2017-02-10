#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the command decorators
"""

import unittest
import unittest.mock

import asynctest

import botman.commands.base
import botman.errors

import tests.mixins

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

        await wrapped(mock_bot, message, '')

        mock_handler.assert_called_with(mock_bot, message)

class TestDescriptionDecorator(unittest.TestCase):
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

class TestParametersDecorator(unittest.TestCase):
    """
    Tests for the parameters decorator
    """

    def test_decorator_non_command(self):
        """
        Tests that the decorator only works on command instances
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')

        expected = 'test must have the chat_command decorator'
        with self.assertRaises(botman.errors.ConfigurationError, msg=expected):
            botman.commands.base.parameters()(mock_handler)

    def test_sets_parameters(self):
        """
        Tests that the decorator actually sets the parameters
        """

        params = {
            'one': botman.commands.base.StringArg(),
            'two': botman.commands.base.StringArg(),
        }

        mock_handler = asynctest.CoroutineMock(__name__='test')
        wrapped = botman.commands.base.chat_command('test')(mock_handler)
        wrapped = botman.commands.base.parameters(**params)(wrapped)

        self.assertDictEqual(
            params,
            wrapped.parameters,
            'The parameters were set',
        )

