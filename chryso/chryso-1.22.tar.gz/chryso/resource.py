import datetime
import logging

import attrdict
from sqlalchemy import select

import chryso.connection
import chryso.errors
import chryso.queryadapter
import chryso.schema

LOGGER = logging.getLogger(__name__)

class Resource():
    TABLE = None

    @staticmethod
    def _sanitize_kwargs(kwargs):
        if 'created' in kwargs:
            del kwargs['created']
        if 'updated' in kwargs:
            del kwargs['updated']
        if 'deleted' in kwargs:
            del kwargs['deleted']
        for k, v in kwargs.items():
            if isinstance(v, chryso.schema.BaseEnum):
                kwargs[k] = str(v)

    @staticmethod
    def update_filters(filters):
        pass

    @classmethod
    def create(cls, **kwargs):
        engine = chryso.connection.get()
        cls._sanitize_kwargs(kwargs)
        statement = cls.TABLE.insert().values(**kwargs)
        with engine.atomic():
            return engine.execute(statement).inserted_primary_key[0]

    @classmethod
    def update(cls, uuid, **kwargs):
        engine = chryso.connection.get()
        cls._sanitize_kwargs(kwargs)
        statement = (
            cls.TABLE.update() #pylint: disable=no-value-for-parameter
                .values(kwargs)
                .where(cls.TABLE.c.uuid == str(uuid))
        )
        engine.execute(statement)

    @classmethod
    def delete(cls, uuid):
        engine = chryso.connection.get()
        statement = (
            cls.TABLE.update() #pylint: disable=no-value-for-parameter
                .where(cls.TABLE.c.uuid == str(uuid))
                .values(deleted = datetime.datetime.utcnow())
        )
        engine.execute(statement)

    @classmethod
    def by_uuid(cls, uuid):
        for record in cls.by_filter({'uuid': [uuid]}):
            return record
        raise chryso.errors.RecordNotFound("Could not find a {} record by uuid: {}".format(cls.TABLE.name, uuid))

    @classmethod
    def by_filter(cls, filters):
        engine = chryso.connection.get()
        cls.update_filters(filters)
        query = cls._by_filter_query(filters)
        results = engine.execute(query).fetchall()
        return [attrdict.AttrDict(result) for result in results]

    @classmethod
    def _get_base_query(cls):
        return select([cls.TABLE])

    @classmethod
    def _by_filter_query(cls, filters):
        formatted_filters = chryso.queryadapter.format_filter(filters, {
            'uuid'        : lambda x: [str(u) for u in x],
        })
        filter_map = chryso.queryadapter.map_column_names([cls.TABLE], formatted_filters)
        base_query = cls._get_base_query()
        query = chryso.queryadapter.apply_filter(base_query, filter_map)
        if hasattr(cls.TABLE.c, 'deleted'):
            return query.where(cls.TABLE.c.deleted == None) # pylint: disable=singleton-comparison
        return query
