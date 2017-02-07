#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the Botman bot implementation
"""

import asyncio
import copy
import unittest
import unittest.mock

import asynctest
import discord

import botman.bot
import botman.commands.base
import botman.errors

class TestBotmanBot(unittest.TestCase):
    """
    Tests for the Botman bot implementation
    """

    def setUp(self):
        self.initial_commands = copy.copy(botman.bot.BotmanBot.command_handlers)

        self.auth_token = 'deadbeef'
        self.bot = botman.bot.BotmanBot(self.auth_token)

        self.run_patch = unittest.mock.patch('discord.Client.run')
        self.mock_run = self.run_patch.start()

    def tearDown(self):
        self.run_patch.stop()

        botman.bot.BotmanBot.command_handlers = self.initial_commands

    def test_run_uses_auth_token(self):
        """
        Tests that the run command uses our auth token
        """

        self.bot.run()

        self.mock_run.assert_called_once_with(self.auth_token)

    def test_on_message(self):
        """
        Tests that when a message comes in we pass it off to command handlers
        """

        mock_handler_0 = TestBotmanBot._add_mock_command('test0', r'test')
        mock_handler_1 = TestBotmanBot._add_mock_command('test1', r'test')

        message = unittest.mock.MagicMock(
            spec=discord.Message,
            content='test',
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.bot.on_message(message))
        loop.close()

        mock_handler_0.assert_called_with(self.bot, message)
        mock_handler_1.assert_called_with(self.bot, message)

    def test_register_non_command(self):
        """
        Tests that we don't allow wrapping of non-command types
        """

        mock_handler = unittest.mock.Mock()
        expected = 'Only Command instances can be registered as commands'
        with self.assertRaises(botman.errors.ConfigurationError, msg=expected):
            botman.bot.BotmanBot.register(mock_handler)

    def test_register_save_handler(self):
        """
        Tests that we save the handler when a command is registered
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.chat_command('test')(mock_handler)
        command = botman.commands.base.command_pattern(r'testification')(command)
        command = botman.bot.BotmanBot.register(command)

        self.assertIn(
            'test',
            botman.bot.BotmanBot.command_handlers,
            'Command was registered to the handler set',
        )

    def test_register_duplicates(self):
        """
        Tests that we don't allow duplicate commands
        """

        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.chat_command('test')(mock_handler)
        command = botman.commands.base.command_pattern(r'testification')(command)
        command = botman.bot.BotmanBot.register(command)

        expected = 'Cannot have duplicate command names: test'
        with self.assertRaises(botman.errors.ConfigurationError, msg=expected):
            botman.bot.BotmanBot.register(command)

    @staticmethod
    def _add_mock_command(name, pattern):
        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.chat_command(name)(mock_handler)
        command = botman.commands.base.command_pattern(pattern)(command)
        botman.bot.BotmanBot.register(command)

        return mock_handler

