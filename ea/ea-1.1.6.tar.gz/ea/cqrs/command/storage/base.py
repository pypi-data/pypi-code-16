import logging

from ea.exc import ImplementationError
from ea.lib.datastructures import ImmutableDTO
from ea.cqrs.command.storage.schema import CommandStorageSchema


class BaseCommandStore:
    schema = CommandStorageSchema()
    storage_class = None
    logger = logging.getLogger('ea.cqrs.command')

    def store(self, dto):
        raise NotImplementedError("Subclasses must override this method.")

    def persist(self, cls, meta, command):
        """Persist the command to the storage backend."""
        dto, errors = self.schema.load(meta)
        if errors:
            # Meta is assumed valid at this point.
            raise ImplementationError(errors)
        assert self.storage_class is not None,\
            "%s must declare a `storage_class` attribute." % type(self)
        dao = self.storage_class(**(dto | ImmutableDTO(params=command.dump())))
        self.store(dao)
