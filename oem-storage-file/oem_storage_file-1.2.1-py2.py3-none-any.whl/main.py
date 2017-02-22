from oem_framework.models.core import ModelRegistry
from oem_framework.plugin import Plugin
from oem_framework.storage import ProviderStorage
from oem_storage_file.core.base import BaseFileStorage
from oem_storage_file.database import DatabaseFileStorage

import appdirs
import os


class ProviderFileStorage(ProviderStorage, BaseFileStorage, Plugin):
    __key__ = 'file'

    def __init__(self, path=None):
        super(ProviderFileStorage, self).__init__()

        self.path = path

        if self.path is None:
            self.path = self._create_dir()

    @classmethod
    def open(cls, client, path=None):
        storage = cls(path)
        storage.initialize(client)
        return storage

    #
    # Provider methods
    #

    def create(self, source, target):
        package_path = self.package_path(source, target)

        # Ensure cache directory exists
        if not os.path.exists(package_path):
            os.makedirs(package_path)

        return True

    def open_database(self, source, target, path=None):
        return ModelRegistry['Database'].load(
            DatabaseFileStorage.open(self, source, target, path),
            source, target
        )

    #
    # Index methods
    #

    def has_index(self, source, target):
        return os.path.exists(os.path.join(
            self._collection_path(source, target),
            'index.%s' % self.main.format.__extension__
        ))

    def update_index(self, source, target, response):
        # Build collection path
        collection_path = self._collection_path(source, target)

        # Ensure directory exists
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)

        # Write index to file
        path = os.path.join(collection_path, 'index.%s' % self.main.format.__extension__)

        with open(path, 'w') as fp:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    fp.write(chunk)

        return True

    #
    # Item methods
    #

    def has_item(self, source, target, key, metadata=None):
        return os.path.exists(os.path.join(
            self._collection_path(source, target), 'items',
            '%s.%s' % (key, self.main.format.__extension__)
        ))

    def update_item(self, source, target, key, response, metadata):
        # Build collection path
        items_path = os.path.join(self._collection_path(source, target), 'items')

        # Ensure directory exists
        if not os.path.exists(items_path):
            os.makedirs(items_path)

        # Write index to file
        path = os.path.join(items_path, '%s.%s' % (key, self.main.format.__extension__))

        with open(path, 'w') as fp:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    fp.write(chunk)

        return True

    #
    # Private methods
    #

    def _collection_path(self, source, target):
        return os.path.join(self.database_path(source, target), source)

    @staticmethod
    def _create_dir():
        # Build cache path
        path = os.path.join(
            appdirs.user_data_dir('OpenEntityMap', appauthor=False),
            'databases',
            'file'
        )

        # Ensure cache directory exists
        if not os.path.exists(path):
            os.makedirs(path)

        return path
