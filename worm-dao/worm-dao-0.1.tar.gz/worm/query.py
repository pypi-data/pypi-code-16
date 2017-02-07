

class Query(object):
    def __init__(self, manager):
        self._mapping = manager.mapping
        self._manager = manager


class Select(Query):
    def filter(self, filterspec):
        return self

    def __iter__(self):
        return self._manager.database.select(self._mapping, self._manager.model)
