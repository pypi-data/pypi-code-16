# coding: utf-8

import os

from bsconf import BSConfCache
from hedgehog import ManageSrv, SteamCMD


class BSCache:
    def __init__(self, config_file=None):
        self.conf = BSConfCache(path=config_file)
        self.check_steam_cmd = True

    def define_cache(self, game):
        supports = ['dod', 'css']

        if game not in supports:
            raise NotImplementedError('Game \'{}\' not supports'.format(
                game
            ))

        if self.check_steam_cmd:
            """Checking that SteamCMD is work."""
            steam_cmd = SteamCMD(steam_cmd_dir=self.conf.steam_cmd_dir)

            if not steam_cmd.check_steam_cmd():
                steam_cmd.batch()

        cache_game_dir = os.path.join(self.conf.cache_dir, game)

        deploy = ManageSrv(
            steam_cmd_dir=self.conf.steam_cmd_dir,
            server_dir=cache_game_dir,
            game=game
        )
        deploy.steam_cmd()

    def steam_cmd_run(self):
        steam_cmd = SteamCMD(steam_cmd_dir=self.conf.steam_cmd_dir)
        steam_cmd.batch()
