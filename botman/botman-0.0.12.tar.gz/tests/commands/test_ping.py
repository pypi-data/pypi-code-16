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

    async def test_command_output(self):
        """
        Tests that the command runs properly and outputs pong
        """

        mock_bot = self.get_mock_bot()
        mock_message = self.get_mock_message(
            f'{mock_bot.user.mention} ping',
            mentions=[mock_bot.user],
        )

        await botman.commands.ping(mock_bot, mock_message, '')

        mock_bot.send_message.assert_called_with(mock_message.channel, 'pong!')

