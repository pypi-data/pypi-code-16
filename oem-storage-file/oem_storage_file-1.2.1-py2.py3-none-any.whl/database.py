from oem_framework.models.core import ModelRegistry
from oem_framework.plugin import Plugin
from oem_framework.storage import DatabaseStorage
from oem_storage_file.collection import CollectionFileStorage
from oem_storage_file.core.base import BaseFileStorage


class DatabaseFileStorage(DatabaseStorage, BaseFileStorage, Plugin):
    __key__ = 'file/database'

    def __init__(self, parent, source, target, path=None):
        super(DatabaseFileStorage, self).__init__()

        self.parent = parent
        self.source = source
        self.target = target

        self.path = path

    def initialize(self, client):
        super(DatabaseFileStorage, self).initialize(client)

        if self.path is None:
            self.path = self.database_path(self.source, self.target)

    @classmethod
    def open(cls, parent, source, target, path=None):
        storage = cls(parent, source, target, path)
        storage.initialize(parent._client)
        return storage

    def __repr__(self):
        return '<DatabaseFileStorage path: %r>' % self.path

    #
    # Database methods
    #

    def open_collection(self, source, target):
        return ModelRegistry['Collection'].load(
            CollectionFileStorage.open(self, source, target),
            source, target
        )
