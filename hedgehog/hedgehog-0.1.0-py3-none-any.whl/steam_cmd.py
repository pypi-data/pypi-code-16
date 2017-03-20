# coding: utf-8

import os
import shutil
import tarfile

import requests

from hedgehog.tools import launch_external_program


class SteamCMD:
    """Class that download steam cmd and unpack it."""

    url = 'https://steamcdn-a.akamaihd.net/client/installer' \
          '/steamcmd_linux.tar.gz'

    def __init__(self, steam_cmd_dir=None, username=None, password=''):
        self.username = username or 'anonymous'
        self.password = password
        self.steam_cmd_dir = steam_cmd_dir or self.get_steam_cmd_dir()
        self.steam_cmd_arch = None

    def get_steam_cmd_dir(self):
        return os.path.join(
            '/tmp',
            self.url.split('/')[-1].split('.')[0]
        )

    def getting_steam_cmd(self):
        """Download steam cmd."""

        file_name = self.url.split('/')[-1]
        self.steam_cmd_arch = os.path.join('/tmp', file_name)
        req_file = requests.get(self.url, stream=True)

        with open(self.steam_cmd_arch, 'wb') as f:
            for chunk in req_file.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return True

    def unpack_bin(self):
        """Unpack steam cmd archive. If directory self.bin_dir is exists it
        will be rewriten."""

        if self.steam_cmd_arch is None:
            raise AttributeError('self.steam_cmd_arch is not be None')

        if not os.path.exists(self.steam_cmd_arch):
            raise FileNotFoundError('file \'{}\' not found'.format(
                self.steam_cmd_arch
            ))

        if os.path.exists(self.steam_cmd_dir):
            shutil.rmtree(self.steam_cmd_dir)

        try:
            os.mkdir(self.steam_cmd_dir)
        except FileExistsError:
            pass

        tar_gz = tarfile.open(self.steam_cmd_arch, 'r:gz')

        try:
            tar_gz.extractall(self.steam_cmd_dir)
        except PermissionError:
            return False
        finally:
            tar_gz.close()

        return True

    def init_steam(self):
        """Initial steamcmd."""
        command = [
            os.path.join(self.steam_cmd_dir, 'steamcmd.sh'),
            '+ login %s' % self.username,
            self.password,
            '+quit'
        ]
        return launch_external_program(command)

    def batch(self):
        if self.getting_steam_cmd():
            if self.unpack_bin():
                return self.init_steam()

        return False
