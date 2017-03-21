# coding: utf-8

import os
import json


class BSConfBase:
    def __init__(self, path=None):
        self.path = path or '/etc/bs/bs.json'
        self.conf = {}

        self.read_config()

    def read_config(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError('Config file {} not found'.format(
                self.path
            ))

        with open(self.path) as f:
            self.conf = json.load(f)


class BSConfCommon(BSConfBase):
    def __init__(self, *args, **kwargs):
        super(BSConfCommon, self).__init__(*args, **kwargs)

    @property
    def steam_cmd_dir(self):
        try:
            return self.conf['steam_cmd_dir']
        except KeyError:
            return '/srv/bs/steam_cmd'


class BSConfCache(BSConfCommon):
    def __init__(self, *args, **kwargs):
        super(BSConfCache, self).__init__(*args, **kwargs)

    @property
    def cache_dir(self):
        try:
            return self.conf['cache']['dir']
        except KeyError:
            return '/srv/bs/cache'

    @property
    def repeat_deploy(self):
        try:
            return self.conf['cache']['repeat_deploy']
        except KeyError:
            return 3

    @property
    def support_games(self):
        try:
            return self.conf['cache']['support_games']
        except KeyError:
            return []
