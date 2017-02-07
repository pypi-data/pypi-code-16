#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the help command
"""

import asynctest

import tabulate

import botman.commands.base
import botman.commands

import tests.mixins

class TestHelpCommand(tests.mixins.DiscordMockMixin, asynctest.TestCase):
    """
    Tests for the help command
    """

    async def test_command(self):
        """
        Tests that the command finds commands and outputs their info
        """

        commands = {
            'cmd': 'This is a command',
            'more': 'This is another command',
            'moar': 'I need moar commands',
        }

        mock_bot = self.get_mock_bot()
        mock_bot.command_handlers = {
            name: TestHelpCommand._get_mock_command(name, description)
            for name, description in commands.items()
        }

        mock_bot.command_handlers['help'] = botman.commands.help_command

        message_table = tabulate.tabulate(
            [
                {'Name': cmd.name, 'Description': cmd.description}
                for cmd in mock_bot.command_handlers.values()
            ],
            headers='keys',
        )

        expected_message = f'Commands:\n{message_table}'
        mock_message = self.get_mock_message(
            f'{mock_bot.user.mention} help',
            mentions=[mock_bot.user],
        )

        await botman.commands.help_command(mock_bot, mock_message)

        mock_bot.send_message.assert_called_with(
            mock_message.channel,
            expected_message,
        )

    @staticmethod
    def _get_mock_command(name, description):
        mock_handler = asynctest.CoroutineMock(__name__=name, __doc__=description)
        wrapped = botman.commands.base.chat_command(name)(mock_handler)

        return wrapped

