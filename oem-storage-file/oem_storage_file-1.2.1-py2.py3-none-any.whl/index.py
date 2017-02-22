from oem_framework.models.core import ModelRegistry
from oem_framework.plugin import Plugin
from oem_framework.storage import IndexStorage
from oem_storage_file.core.base import BaseFileStorage
from oem_storage_file.metadata import MetadataFileStorage

import os
import six
import sys


class IndexFileStorage(IndexStorage, BaseFileStorage, Plugin):
    __key__ = 'file/index'

    def __init__(self, parent):
        super(IndexFileStorage, self).__init__()

        self.parent = parent

        self.path = None

    @classmethod
    def open(cls, parent):
        storage = cls(parent)
        storage.initialize(parent._client)
        return storage

    def initialize(self, client):
        super(IndexFileStorage, self).initialize(client)

        self.path = os.path.join(self.parent.path, 'index.%s' % self.format.__extension__)

    def get(self, index, key):
        try:
            value = index.items[str(key)]
        except KeyError:
            exc_info = sys.exc_info()

            try:
                value = index.items[key]
            except KeyError:
                six.reraise(exc_info[0], exc_info[1], exc_info[2])

        # Ensure item has been parsed
        if type(value) is dict:
            value = index.items[str(key)] = self.parse(index.collection, key, value)

        return value

    def load(self, collection):
        if not os.path.exists(self.path):
            return ModelRegistry['Index'](collection, self)

        return self.format.from_path(
            collection, ModelRegistry['Index'], self.path,
            children=False,
            storage=self
        )

    #
    # Metadata
    #

    def create(self, collection, key):
        return ModelRegistry['Metadata'](
            collection, key,
            storage=MetadataFileStorage.open(self.parent, key)
        )

    def parse(self, collection, key, value):
        return self.format.from_dict(
            collection, ModelRegistry['Metadata'], value,
            key=str(key),
            storage=MetadataFileStorage.open(self.parent, key)
        )
