# -*- coding: utf-8 -*-

"""
Botman bot implementation
"""

import random
import re

import discord

import botman.errors

class BotmanBot(discord.Client):
    """
    Botman bot implementation
    """

    bad_command_responses = [
        'I\'m sorry Dave, I\'m afraid I can\'t do that',
        'I really don\'t know what you were trying to do',
        'That\'s definitely not something I know how to do',
        'You wish!',
        'Maybe try again in a few minutes (ha!)',
        'That doesn\'t look like anything to me',
    ]

    command_handlers = {}

    def __init__(self, auth_token):
        """
        Create an instance of Botman with the given auth token
        """

        super().__init__()

        self.auth_token = auth_token
        self.command_regex = None

    async def on_ready(self):
        """
        Called when the client is connected and ready
        """

        self.command_regex = re.compile(
            fr'^{self.user.mention}\s+(?P<command>[^ ]+)\s*(?P<arguments>.*)$',
        )

        print(f'Logged in as {self.user.name}')

    async def on_message(self, message: discord.Message):
        """
        Called when the client sees a message
        """

        if not self.user in message.mentions:
            return

        match = self.command_regex.match(message.content)
        if not match:
            await self._send_unknown_command_message(message.channel)
            return

        if message.author == self.user:
            return

        match_results = match.groupdict()
        command = match_results['command']
        arguments = match_results['arguments']

        if command in BotmanBot.command_handlers:
            command_handler = BotmanBot.command_handlers[command]

            await command_handler(self, message, arguments)
        else:
            await self._send_unknown_command_message(message.channel)

    # pylint: disable=arguments-differ
    def run(self):
        """
        Run Botman, run!
        """

        super().run(self.auth_token)
    # pylint: enable=arguments-differ

    async def _send_unknown_command_message(self, channel):
        await self.send_message(
            channel,
            random.choice(BotmanBot.bad_command_responses),
        )

    @classmethod
    def register(cls, command):
        """
        Chatbot command handler
        """

        # Need to do the import here to prevent a circular dependency
        from .commands.base import Command

        if not isinstance(command, Command):
            raise botman.errors.ConfigurationError(
                'Only Command instances can be registered as commands',
            )

        if command.name in cls.command_handlers:
            raise botman.errors.ConfigurationError(
                f'Cannot have duplicate command names: {command.name}'
            )

        cls.command_handlers[command.name] = command

        return command

