from ea.lib.datastructures import DTO
from ea.exc import ImplementationError
import ea.schema

RESERVED_SYMBOLS = set(['events','__publisher__','id'])


class DomainObjectType(type):

    def __new__(cls, name, bases, attrs):
        new = super(DomainObjectType, cls).__new__
        if attrs.get('__abstract__'):
            return new(cls, name, bases, attrs)

        fields = {}
        for k in list(attrs.keys()):
            if not isinstance(attrs[k], ea.schema.fields.Field):
                continue
            field = attrs.pop(k)

            # Remove the default attribute. We use it to indicate
            # the default value for a newly initialized instance.
            # The marshmallow framework uses it to specify the
            # default when dumping an object, but we don't want -
            # the schema should load and dump the exact state
            # of the object.
            field.init = None
            if field.default != ea.schema.missing:
                field.init = field.default
            field.missing = field.default = ea.schema.missing

            # A field is *never* required - the schema is used
            # solely for dumping and loading the datastructure,
            # not validating.
            field.required = False
            field.allow_none = True

            fields[k] = field

        Schema = attrs.get('__schema__')
        if fields:
            Schema = type('%sDomainSchema' % name,
                (Schema or ea.schema.Schema,), fields)

        attrs['__schema__'] = Schema

        reserved = set(attrs.keys()) & RESERVED_SYMBOLS
        if reserved:
            raise ImplementationError("Reserved symbols: %s",
                ','.join(reserved))

        return new(cls, name, bases, attrs)
