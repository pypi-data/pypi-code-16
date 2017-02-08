#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the Botman bot implementation
"""

import copy
import unittest
import unittest.mock

import asynctest

import botman.bot
import botman.commands.base
import botman.errors

import tests.mixins

@asynctest.fail_on(unused_loop=False)
class TestBotmanBot(tests.mixins.DiscordMockMixin, asynctest.TestCase):
    """
    Tests for the Botman bot implementation
    """

    def setUp(self):
        self.initial_commands = copy.copy(botman.bot.BotmanBot.command_handlers)

        self.auth_token = 'deadbeef'
        self.bot = botman.bot.BotmanBot(self.auth_token)
        self.bot.user = self.get_mock_user(bot=True)

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

    async def test_on_message(self):
        """
        Tests that when a message comes in we pass it off to command handlers
        """

        mock_handler_0 = TestBotmanBot._add_mock_command('test')
        mock_handler_1 = TestBotmanBot._add_mock_command('test1')

        message = self.get_mock_message(
            f'{self.bot.user.mention} test',
            mentions=[self.bot.user],
        )

        await self.bot.on_ready()
        await self.bot.on_message(message)

        mock_handler_0.assert_called_with(self.bot, message, '')
        mock_handler_1.assert_not_called()

    async def test_on_message_trigger(self):
        """
        Tests that we only trigger on messages that could be commands
        """

        mock_handler = TestBotmanBot._add_mock_command('test')

        mock_user = self.get_mock_user()

        mock_messages = [
            self.get_mock_message('This is a test'),
            self.get_mock_message('This is a message'),
            self.get_mock_message(
                f'{mock_user.mention} test message',
                mentions=[mock_user],
            ),
            self.get_mock_message(
                f'{self.bot.user.mention} test message',
                author=self.bot.user,
                mentions=[self.bot.user],
            ),
            self.get_mock_message(
                f'{self.bot.user.mention} test message',
                mentions=[self.bot.user],
            ),
        ]

        with asynctest.patch.object(self.bot, 'send_message'):
            await self.bot.on_ready()

            for mock_message in mock_messages:
                await self.bot.on_message(mock_message)

        mock_handler.assert_called_once_with(
            self.bot,
            mock_messages[-1],
            'message',
        )

    async def test_on_message_invalid(self):
        """
        Tests that we handle invalid commands properly
        """

        mock_message = self.get_mock_message(
            f'{self.bot.user.mention} asdfjkl',
            mentions=[self.bot.user],
        )
        with asynctest.patch.object(self.bot, 'send_message') as mock_send:
            await self.bot.on_ready()
            await self.bot.on_message(mock_message)

            mock_send.assert_called_once()

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
        command = botman.bot.BotmanBot.register(command)

        expected = 'Cannot have duplicate command names: test'
        with self.assertRaises(botman.errors.ConfigurationError, msg=expected):
            botman.bot.BotmanBot.register(command)

    @staticmethod
    def _add_mock_command(name):
        mock_handler = asynctest.CoroutineMock(__name__='test')
        command = botman.commands.base.chat_command(name)(mock_handler)
        botman.bot.BotmanBot.register(command)

        return mock_handler

