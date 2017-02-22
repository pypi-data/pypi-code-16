from oem_framework.models.core import ModelRegistry
from oem_framework.plugin import Plugin
from oem_framework.storage import ItemStorage
from oem_storage_file.core.base import BaseFileStorage

import os


class ItemFileStorage(ItemStorage, BaseFileStorage, Plugin):
    __key__ = 'file/item'

    def __init__(self, parent, key):
        super(ItemFileStorage, self).__init__()

        self.parent = parent
        self.key = key

        self.path = None

    @classmethod
    def open(cls, parent, key):
        storage = cls(parent, key)
        storage.initialize(parent._client)
        return storage

    def initialize(self, client):
        super(ItemFileStorage, self).initialize(client)

        self.path = os.path.join(self.parent.path, 'items', '%s.%s' % (self.key, self.format.__extension__))

    def load(self, collection, media):
        return self.format.from_path(
            collection, ModelRegistry['Item'], self.path,
            media=media,
            storage=self
        )
