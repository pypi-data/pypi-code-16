from collections import OrderedDict

from ea.lib.datastructures import ImmutableDTO
import ea.schema


class CommandOptions(object):

    def __init__(self, meta, name):
        self.fields = OrderedDict()
        self.schema_class = None
        self.schema = None
        self.class_name = name
        self.name = getattr(meta, 'name', self.class_name)

    def load(self, params):
        """Invoke the schema in order to load the command parameters
        and validate them.
        """
        return self.schema.load(params)

    def add_fields(self, fields):
        """Add a sequence of fields to the :class:`CommandOptions`
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

    def get_field_names(self):
        """Return all field names declared on the command."""
        return list(self.schema.fields.keys())
