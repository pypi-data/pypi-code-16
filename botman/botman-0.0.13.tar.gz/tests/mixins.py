# -*- coding: utf-8 -*-

"""
TestCase mixins
"""

import random
import unittest.mock

import asynctest
import discord

import botman.bot

class DiscordMockMixin(object):
    """
    TestCase mixin for generating mock Discord data
    """

    sample_names = [
        'botman',
        'jarvis',
        'joe',
        'the_bottler',
    ]

    def get_mock_message(self, content, author=None, mentions=None):
        """
        Gets a mock message with the given text content
        """

        if author is None:
            author = self.get_mock_user()

        if mentions is None:
            mentions = []

        return unittest.mock.MagicMock(
            spec=discord.Message,
            author=author,
            content=content,
            mentions=mentions,
        )

    def get_mock_user(self, user_id=None, name=None, bot=False):
        """
        Gets a mock user instance
        """

        if user_id is None:
            user_id = f'{random.randint(0, 99999999999999999):#018}'

        if name is None:
            name = random.choice(self.sample_names)

        return unittest.mock.MagicMock(
            spec=discord.User,
            id=user_id,
            name=name,
            bot=bot,
            mention=f'<@{user_id}>',
        )

    def get_mock_bot(self, user=None):
        """
        Gets a mock bot instance
        """

        if user is None:
            user = self.get_mock_user(bot=True)

        return asynctest.MagicMock(
            spec=botman.bot.BotmanBot,
            user=user,
        )

