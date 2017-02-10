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

    async def test_command_all(self):
        """
        Tests that the command finds all commands and outputs their info
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
                {'name': cmd.name, 'description': cmd.description}
                for cmd in mock_bot.command_handlers.values()
            ],
            tablefmt='plain',
        )

        expected_message = f'Commands:\n{message_table}'
        mock_message = self.get_mock_message(
            f'{mock_bot.user.mention} help',
            mentions=[mock_bot.user],
        )

        await botman.commands.help_command(mock_bot, mock_message, '')

        mock_bot.send_message.assert_called_with(
            mock_message.channel,
            expected_message,
        )

    async def test_command_usage(self):
        """
        Tests that the command can get usage for a specific command
        """

        mock_command = TestHelpCommand._get_mock_command(
            'test',
            'This is a test command',
            parameters={
                'req_param': botman.commands.base.StringArg(
                    required=True,
                    descr='A required param',
                ),
                'opt_param': botman.commands.base.StringArg(
                    default='my_def',
                    descr='An optional param',
                ),
            },
        )

        mock_bot = self.get_mock_bot()
        mock_bot.command_handlers = {
            'help': botman.commands.help_command,
            'test': mock_command,
        }

        mock_message = self.get_mock_message(
            f'{mock_bot.user.mention} help test',
            mentions=[mock_bot.user],
        )

        expected_message = 'test - This is a test command\n' +       \
            'req_param :: String (required) :: A required param\n' + \
            'opt_param :: String (optional) :: An optional param'

        await botman.commands.help_command(mock_bot, mock_message, 'test')

        mock_bot.send_message.assert_called_with(
            mock_message.channel,
            expected_message,
        )

    async def test_command_usage_invalid(self):
        """
        Test that full usage is displayed for a command that doesn't exist
        """

        mock_bot = self.get_mock_bot()
        mock_bot.command_handlers = {
            'help': botman.commands.help_command,
        }

        mock_message = self.get_mock_message(
            f'{mock_bot.user.mention} help test',
            mentions=[mock_bot.user],
        )

        await botman.commands.help_command(mock_bot, mock_message, 'test')

        message_table = tabulate.tabulate(
            [
                {'name': cmd.name, 'description': cmd.description}
                for cmd in mock_bot.command_handlers.values()
            ],
            tablefmt='plain',
        )

        expected_message = f'Commands:\n{message_table}'

        mock_bot.send_message.assert_has_calls(
            [
                asynctest.call(
                    mock_message.channel,
                    'No such command: test',
                ),
                asynctest.call(
                    mock_message.channel,
                    expected_message,
                ),
            ],
        )

    @staticmethod
    def _get_mock_command(name, description, parameters=None):
        mock_handler = asynctest.CoroutineMock(__name__=name, __doc__=description)
        wrapped = botman.commands.base.chat_command(name)(mock_handler)

        if parameters is not None:
            wrapped = botman.commands.base.parameters(**parameters)(wrapped)

        return wrapped

