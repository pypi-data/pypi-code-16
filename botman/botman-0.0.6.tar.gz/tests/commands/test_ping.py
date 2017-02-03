#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the ping command
"""

import asynctest

import botman.commands.ping

import tests.mixins

class TestPingCommand(tests.mixins.DiscordMockMixin, asynctest.TestCase):
    """
    Tests for the ping command
    """

    async def test_command_no_mention(self):
        """
        Tests that the message doesn't fire when we don't mention the bot
        """

        mock_bot = self.get_mock_bot()
        mock_message = self.get_mock_message('ping')

        await botman.commands.ping(mock_bot, mock_message)

        mock_bot.send_message.assert_not_called()

    async def test_command_output(self):
        """
        Tests that the command runs properly and outputs pong
        """

        mock_bot = self.get_mock_bot()
        mock_message = self.get_mock_message(
            f'{mock_bot.user.mention} ping',
            mentions=[mock_bot.user],
        )

        await botman.commands.ping(mock_bot, mock_message)

        mock_bot.send_message.assert_called_with(mock_message.channel, 'pong!')

