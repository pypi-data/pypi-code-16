from oem_framework.plugin import Plugin
from oem_framework.storage import MetadataStorage
from oem_storage_file.core.base import BaseFileStorage

import os

from oem_storage_file.item import ItemFileStorage


class MetadataFileStorage(MetadataStorage, BaseFileStorage, Plugin):
    __key__ = 'file/metadata'

    def __init__(self, parent, key):
        super(MetadataFileStorage, self).__init__()

        self.parent = parent
        self.key = key

        self.path = None

    @classmethod
    def open(cls, parent, key):
        storage = cls(parent, key)
        storage.initialize(parent._client)
        return storage

    def initialize(self, client):
        super(MetadataFileStorage, self).initialize(client)

        self.path = os.path.join(self.parent.path, 'items', '%s.%s' % (self.key.replace(':', '_'), self.format.__extension__))

    def open_item(self, collection, media):
        storage = ItemFileStorage.open(self.parent, self.key)
        return storage.load(collection, media)
