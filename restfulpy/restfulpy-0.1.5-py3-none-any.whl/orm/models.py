
import cgi
import functools
from datetime import datetime, date, time
from decimal import Decimal

from nanohttp import HttpBadRequest, context
from sqlalchemy import Column, event
from sqlalchemy.orm import SynonymProperty, validates, Query, CompositeProperty
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.relationships import RelationshipProperty

from restfulpy.utils import format_iso_datetime, format_iso_time
from restfulpy.orm.mixines import PaginationMixin, FilteringMixin, OrderingMixin
from restfulpy.orm.field import Field
from restfulpy.orm.metadata import MetadataField


class BaseModel(object):
    _key_serializer = None

    @classmethod
    def get_column(cls, column):
        if isinstance(column, str):
            mapper = inspect(cls)
            return mapper.columns[column]
        if isinstance(column, SynonymProperty):
            return column.parent.columns[column.name]
        return column

    @classmethod
    def import_value(cls, column, v):
        c = cls.get_column(column)
        if isinstance(c, Column):
            if c.type.python_type is bool and not isinstance(v, bool):
                return str(v).lower() == 'true'
        return v

    @classmethod
    def prepare_for_export(cls, column, v):
        param_name = column.info.get('json') or column.key

        if isinstance(column, RelationshipProperty) and column.uselist:
            result = [c.to_dict() for c in v]

        elif isinstance(column, CompositeProperty):
            result = v.__composite_values__()

        elif isinstance(v, datetime):
            result = format_iso_datetime(v)

        elif isinstance(v, date):
            result = v.isoformat()

        elif isinstance(v, time):
            result = format_iso_time(v)

        elif v is None:
            result = v

        elif hasattr(v, 'to_dict'):
            result = v.to_dict()

        elif isinstance(v, Decimal):
            result = str(v)

        elif isinstance(v, set):
            result = list(v)

        else:
            result = v

        return param_name, result

    @classmethod
    def json_metadata(cls):
        fields = {}
        for c in cls.iter_json_columns(relationships=True, include_readonly_columns=True):
            metadata_fields = MetadataField.from_column(cls.get_column(c), info=c.info)
            for f in metadata_fields:
                fields[f.json_name] = f.to_json()
        return fields

    def update_from_request(self):
        for column, value in self.extract_data_from_request():
            if isinstance(column, Field) and column.is_attachment:
                if value is not None and (isinstance(value, cgi.FieldStorage) or hasattr(value, 'read')):
                    getattr(self, column.key[1:]).from_request(column, value)
            else:
                if 'unreadable' in column.info and (not value or (isinstance(value, str) and not value.strip())):
                    continue
                setattr(
                    self,
                    column.key[1:] if column.key.startswith('_') else column.key,
                    self.import_value(column, value))

    @classmethod
    def iter_columns(cls, relationships=True, synonyms=True, composites=True, use_inspection=True):
        if use_inspection:
            mapper = inspect(cls)
            for c in mapper.columns:
                yield c

            if synonyms:
                for c in mapper.synonyms:
                    yield c

            if relationships:
                for c in mapper.relationships:
                    yield c

            if composites:
                for c in mapper.composites:
                    yield c

        else:
            # noinspection PyUnresolvedReferences
            for c in cls.__table__.c:
                yield c

    @classmethod
    def iter_json_columns(cls, include_readonly_columns=True, include_protected_columns=False, **kw):
        for c in cls.iter_columns(**kw):
            if (not include_protected_columns and c.info.get('protected')) or \
                    (not include_readonly_columns and c.info.get('readonly')):
                continue

            yield c

    @classmethod
    def extract_data_from_request(cls):
        for c in cls.iter_json_columns(include_protected_columns=True):
            param_name = c.info.get('json', c.key)

            if c.info.get('readonly') and param_name in context.form:
                if c.info.get('strict', None):
                    raise HttpBadRequest('Invalid parameter: %s' % c.info['json'])
                else:
                    continue

            if param_name in context.form:
                yield c, context.form[param_name]

    def to_dict(self):
        result = {}
        for c in self.iter_json_columns():
            result.setdefault(*self.prepare_for_export(c, getattr(self, c.key)))
        return result

    @classmethod
    def create_sort_criteria(cls, sort_columns):
        criteria = []
        for c in cls.iter_json_columns():
            json_name = c.info.get('json', c.key)
            if json_name in sort_columns:
                criteria.append((c, sort_columns[json_name] == 'desc'))
        return criteria

    @classmethod
    def dump_query(cls, query=None):
        query = query or cls.query

        if issubclass(cls, FilteringMixin):
            query = cls.filter_by_request(query)

        if issubclass(cls, OrderingMixin):
            query = cls.sort_by_request(query)

        if issubclass(cls, PaginationMixin):
            query = cls.paginate_by_request(query=query)

        return [o.to_dict() for o in query]

    @classmethod
    def expose(cls, func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, Query):
                return cls.dump_query(result)
            return result

        return wrapper


@event.listens_for(BaseModel, 'class_instrument')
def receive_class_instrument(cls):
    for field in cls.iter_columns(relationships=False, synonyms=False, use_inspection=False):
        if not isinstance(field, Field) or not field.can_validate:
            continue
        method_name = 'validate_%s' % field.name
        if not hasattr(cls, method_name):
            def validator(self, key, value):
                return self.get_column(key).validate(value)

            setattr(cls, method_name, validates(field.name)(validator))
