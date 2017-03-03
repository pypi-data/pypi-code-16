# -*- coding: utf-8 -*-

import abc
import yaml


class Loader(object):
    """Load configs from external resources
    """

    @abc.abstractmethod
    def load(self):
        pass


class YamlLoader(Loader):
    def __init__(self, path):
        self.path = path

    def load(self):
        with open(self.path) as f:
            return yaml.load(f)


class Config(object):
    """Base class for config.
    """
    def __init__(self, path, loader=None):
        self._store = None
        self._path = path
        self._loader = loader or YamlLoader

    def __repr__(self):
        return '<{} path={!r}>'.format(self.__class__.__name__, self._path)

    def get(self, attr, raise_exc=False):
        """Get a config.

        This function will load config lazily

        :param attr: config name
        :param raise_exc: whether raise load exceptions
        :return: config value or None
        """
        if self._store is None:
            try:
                self._store = self._loader(self._path).load()
            except Exception:
                if raise_exc:
                    raise
                self._store = {}
        return self._store.get(attr)

    def __getattr__(self, attr):
        """Allow to get extra configs
        """
        return self.get(attr, True)

    def __getitem__(self, attr):
        """Allow to get extra configs through dict getter
        """
        return self.get(attr, True)
