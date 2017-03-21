# coding: utf-8

import click

from hedgehog import SteamCMD
from bsconf import BSConfCache
from bscache.cache import BSCache


key_config = click.option('--config', help='path to a config file')


@click.group()
def cli():
    pass


@cli.command()
@key_config
@click.option(
    '--steam', help='check and setup steam cmd', is_flag=True, default=False
)
@click.option('--game', help='deploy cache of game', metavar='<game>')
def steamcmd(game, steam, config):
    if steam:
        conf = BSConfCache(config) if config else BSConfCache()
        steam_cmd = SteamCMD(steam_cmd_dir=conf.steam_cmd_dir)

        if not steam_cmd.check_steam_cmd():
            steam_cmd.batch()

    if game:
        cache = BSCache()
        cache.define_cache(game)
        return
