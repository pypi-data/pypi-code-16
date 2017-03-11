from ea.cqrs.command.storage.base import BaseCommandStore


class NullCommandStore(BaseCommandStore):
    storage_class = dict

    def store(self, dao):
        self.logger.debug("Not persisting %s", dao)
