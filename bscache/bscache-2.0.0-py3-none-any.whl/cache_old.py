# -*- coding: utf-8 -*-

import sgslib.dod
import sgslib.css
import sgslib.csgo
import sgslib.steam_cmd
import sgslib.exceptions
import bscachemng.config
import bsstatusflags.flag
from sgslib import support_games as sgslib_support_games


class Cache:
    def __init__(self, config_file):
        self.conf = bscachemng.config.Conf(config_file)
        self.repeat_deploy = self.conf.repeat_deploy
        self.support_games = self.white_list_games()

    def white_list_games(self):
        white_list = []
        for game in self.conf.support_games:
            if game in sgslib_support_games:
                white_list.append(game)

        assert white_list, 'No supported games'
        return white_list

    def define_instance(self, game):
        if game == 'dod':
            cache = sgslib.dod.DayOfDefeatSource(
                servers_dir=self.conf.cache_dir)

        elif game == 'css':
            cache = sgslib.css.CounterStrikeSource(
                servers_dir=self.conf.cache_dir)

        elif game == 'cs_go':
            cache = sgslib.csgo.CounterStrikeGlobalOffensive(
                servers_dir=self.conf.cache_dir)

        else:
            raise AssertionError('Game {} not supported'.format(game))

        return cache

    def update(self, verbose=False):
        status = bsstatusflags.flag.Flag()

        if status.action('cache', get_=True):
            print('Process already launch')
            return False
        else:
            status.action('cache', set_=True)

        try:
            for game in self.support_games:
                cache = self.define_instance(game)
                print('Update {}'.format(sgslib_support_games[game]['title']))

                # todo: retry setting flag
                if not status.action('{}_cache'.format(game), set_=True):
                    print('Cache is busy...')
                    continue

                try:
                    while self.repeat_deploy:
                        try:
                            if cache.deploy(verbose):
                                print('Success updated {}'.format(
                                    sgslib_support_games[game]['title']))
                                break
                            else:
                                print('Failed updated {}, repeat...'.format(
                                    sgslib_support_games[game]['title']))
                        except sgslib.exceptions.SteamCMDInstallFailed:
                            print('Failed install SteamCMD, remaining'
                                  ' attempts {}'.format(self.repeat_deploy))
                        finally:
                            self.repeat_deploy -= 1
                finally:
                    status.action('{}_cache'.format(game), del_=True)
        finally:
            status.action('cache', del_=True)
        return True
