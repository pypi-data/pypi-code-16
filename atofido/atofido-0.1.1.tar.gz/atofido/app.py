# -*- coding: utf-8 -*-

from yapsy.PluginManager import PluginManager
import os


class Application(object):
    def __init__(self, parser=None):
        self._parser = parser
        self._plugin_manager = PluginManager()

        self._load_plugins()

    def _load_plugins(self):
        current_path = os.path.os.path.dirname(os.path.realpath(__file__))
        plugins_path = os.path.join(current_path, 'plugins')
        self._plugin_manager.setPluginPlaces([plugins_path])
        self._plugin_manager.collectPlugins()

    def start(self, args):
        command, args = self._parser.parse_args(args)
        method = getattr(self, command)
        method(args)

    def list(self, args):
        for plugin in self._plugin_manager.getAllPlugins():
            plugin.plugin_object.list(args.name)

    def download(self, args):
        pass
