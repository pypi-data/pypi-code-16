from collections import OrderedDict

from jinja2 import Template
import six

from ea.exc import ImplementationError
from ea.lib.datastructures import ImmutableDTO
import ea.schema


class EventOptions(object):

    def __init__(self, meta, name):
        self.fields = OrderedDict()
        self.schema_class = None
        self.schema = None
        self.name = getattr(meta, 'name', name)
        self.meta = meta

    def load(self, params):
        """Invoke the schema in order to load the command parameters
        and validate them.
        """
        return self.schema.load(params)

    def add_fields(self, fields):
        """Add a sequence of fields to the :class:`EventOptions`
        registry.
        """
        for name, field in fields:
            self.fields[name] = field

    def contribute_to_class(self, name, cls):
        setattr(cls, name, self)
        fields =  {x: y for x,y in self.fields.items()}
        fields['dto_class'] = ImmutableDTO

        self.schema_class = type(cls.__name__ + 'Schema',
            (ea.schema.Schema,), fields)
        self.schema = self.schema_class()

        self.default_template = Template("{{ event }}")
        self.description = self.description_plural = self.default_template
        if hasattr(self.meta, 'description'):
            self.description = Template(self.meta.description)

        if hasattr(self.meta, 'description_plural'):
            self.description_plural = Template(self.meta.description_plural)

        delattr(self, 'meta')

    def get_field_names(self):
        """Return all field names declared on the command."""
        return list(self.schema.fields.keys())


class EventMeta(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(EventMeta, cls).__new__
        if name in ('NewBase', 'Event'):
            return super_new(cls, name, bases, attrs)

        declared_meta = attrs.pop('Meta', None)
        meta = EventOptions(declared_meta, name)

        # Loop over all fields and add them to the options
        # instance. This is used to perform various logical
        # operations related to validation, ordering, comparison,
        # etc. Also get the fields from the bases.
        fields = []

        for b in bases:
            if not issubclass(b, Event) or b.__name__ == 'Event':
                continue

            fields.extend(b.meta.fields.items())

        for attname in list(attrs.keys()):
            is_field = issubclass(type(attrs[attname]), ea.schema.fields.Field)
            if not is_field:
                continue
            fields.append([attname, attrs.pop(attname)])

        meta.add_fields(sorted(fields, key=lambda x: x[1]._creation_index))

        new_class = super_new(cls, name, bases, attrs)
        meta.contribute_to_class('meta', new_class)

        return new_class


class Event(six.with_metaclass(EventMeta)):

    @property
    def errors(self):
        return ImmutableDTO(self._errors)

    @property
    def params(self):
        return ImmutableDTO(self._params)

    @property
    def description(self):
        try:
            return self.meta.description.render(
                dto=self.params,
                event=self
            )
        except Exception:
            return "Error in formatting: %s" % self

    @classmethod
    def as_dto(cls, **params):
        instance = cls(**params)
        return instance.params

    def __init__(self, **params):
        if not params.pop('_skip_validation', False):
            self._params, self._errors = self.meta.load(params)
        else:
            self._params = params
            self._errors = None

    def dump(self):
        if not self.is_valid():
            raise ValueError("Cannot dump event in invalid state.")
        return ImmutableDTO(self.meta.schema.dump(self._params)[0])

    def is_valid(self):
        return not bool(self._errors)

    def __serialize__(self, func):
        return func(self.dump())

    def __repr__(self):
        args = []
        for name in self.meta.get_field_names():
            value = self._params.get(name)
            try:
                value = repr(value)
            except Exception:
                value = "<Error in formatting: %s>" % type(value)
            args.append("%s=%s" % (name, value))
        return "%s(%s)" % (type(self).__name__, ', '.join(args))
