# -*- coding: utf-8 -*-

"""
Command line interface for the bot
"""

import click

import botman.bot
import botman.commands

@click.command()
@click.argument('auth_token', type=str, envvar='BOTMAN_AUTH_TOKEN')
def main(auth_token):
    """
    Botman, not the bot we need but not the bot we deserve
    """

    commands = ', '.join(botman.bot.BotmanBot.command_handlers.keys())
    click.echo(f'Commands: {commands}')

    bot = botman.bot.BotmanBot(auth_token)
    bot.run()

