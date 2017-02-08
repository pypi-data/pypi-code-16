from . import mapper


class QueryException(Exception):
    pass


class MultipleObjectsReturned(QueryException):
    pass


class ObjectNotFound(QueryException):
    pass


class GenericObject(object):
    pass


class Manager(object):
    def __init__(self, adapter, mapping, model=GenericObject):
        if isinstance(mapping, str):
            mapping = mapper.Mapping(mapping, scaffold=True)
        self._adapter = adapter
        self._mapping = mapping
        self.model = model

        if not mapping.columns() and mapping.scaffold:
            mapper.scaffold(adapter, mapping)

    @property
    def database(self):
        return self._adapter

    @property
    def mapping(self):
        return self._mapping

    def begin(self):
        self._adapter.start_transaction()

    def commit(self):
        self._adapter.commit_transaction()

    def rollback(self):
        self._adapter.rollback_transaction()

    def add(self, obj):
        self._adapter.insert(self._mapping, obj)

    def add_many(self, objs):
        self._adapter.insert_many(self._mapping, objs)

    def update(self, obj):
        self._adapter.update(self._mapping, obj)

    def update_many(self, objs):
        self._adapter.update_many(self._mapping, objs)

    def delete(self, obj):
        self._adapter.delete(self._mapping, obj)

    def elete_many(self, obj):
        self._adapter.delete_many(self._mapping, obj)

    def all(self):
        return self._adapter.select_all(self._mapping, self.model)

    def query(self, sql):
        return self._adapter.raw(sql, self._mapping, self.model)
