# coding: utf-8

import os

from hedgehog.base import SteamBase
from hedgehog.tools import launch_external_program


class ManageSrv(SteamBase):
    def __init__(self, steam_cmd_dir, server_dir, username=None, game=None):
        self.bin = os.path.join(steam_cmd_dir, 'steamcmd.sh')
        self.server_dir = server_dir
        self.game = game
        self.username = username or 'anonymous'

    def steam_cmd(self, validate=False):
        """Install and validationg a server (files) if `validate` is True,
        default is False."""

        if self.game is None:
            raise AttributeError('salf.game is not be None')

        if not os.path.exists(self.bin):
            raise FileNotFoundError('\'{}\' not found'.format(self.bin))

        if not os.path.exists(self.server_dir):
            os.makedirs(self.server_dir)

        cmd = '%s +login %s +force_install_dir %s +app_update %s ' \
            '%s +quit' % (
                self.bin,
                self.username,
                self.server_dir,
                self.get_game_id(self.game),
                'validate' if validate else ''
            )

        return launch_external_program(cmd.split())
