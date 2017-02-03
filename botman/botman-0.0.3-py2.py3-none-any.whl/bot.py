# -*- coding: utf-8 -*-

"""
Botman bot implementation
"""

import discord

import botman.errors

class BotmanBot(discord.Client):
    """
    Botman bot implementation
    """

    command_handlers = {}

    def __init__(self, auth_token):
        """
        Create an instance of Botman with the given auth token
        """

        super().__init__()

        self.auth_token = auth_token

    async def on_ready(self):
        """
        Called when the client is connected and ready
        """

        print(f'Logged in as {self.user.name}')

    async def on_message(self, message: discord.Message):
        """
        Called when the client sees a message
        """

        for command in BotmanBot.command_handlers.values():
            await command(self, message)

    # pylint: disable=arguments-differ
    def run(self):
        """
        Run Botman, run!
        """

        super().run(self.auth_token)
    # pylint: enable=arguments-differ

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

