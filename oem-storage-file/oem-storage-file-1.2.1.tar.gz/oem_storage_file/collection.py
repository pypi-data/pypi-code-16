from oem_framework.models.core import ModelRegistry
from oem_framework.plugin import Plugin
from oem_framework.storage import CollectionStorage
from oem_storage_file.core.base import BaseFileStorage
from oem_storage_file.index import IndexFileStorage

import os


class CollectionFileStorage(CollectionStorage, BaseFileStorage, Plugin):
    __key__ = 'file/collection'

    def __init__(self, parent, source, target, version=None):
        super(CollectionFileStorage, self).__init__()

        self.parent = parent
        self.source = source
        self.target = target
        self.version = version

        self.path = None

    @classmethod
    def open(cls, parent, source, target, version=None):
        storage = cls(parent, source, target, version)
        storage.initialize(parent._client)
        return storage

    #
    # Methods
    #

    def initialize(self, client):
        super(CollectionFileStorage, self).initialize(client)

        # Build collection path
        self.path = os.path.join(self.parent.path, self.source.replace(':', '_'))

    def open_index(self, collection):
        return ModelRegistry['Index'].load(collection, IndexFileStorage.open(self))

    def __repr__(self):
        return 'CollectionFileStorage path: %r, format: %r>' % (
            self.path, self.format
        )
