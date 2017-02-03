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

    click.echo("Replace this message by putting your code into "
               "botman.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    click.echo(f'Auth token: {auth_token}')

    bot = botman.bot.BotmanBot(auth_token)
    bot.run()

