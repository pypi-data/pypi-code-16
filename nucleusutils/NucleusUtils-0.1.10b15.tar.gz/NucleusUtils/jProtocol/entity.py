from .helper import clean
from ..simple import Set


class Entity:
    # Use field names or tuple for aliasing (field, as_field) or [field, field_getter_method]
    public_fields = ()
    reference = None

    def __init_subclass__(cls, **kwargs):
        cls._include = Set()
        cls._exclude = Set()
        cls._extends = {}

    def field_getter(self, field, default=None):
        if hasattr(self, field):
            return getattr(self, field)
        return default

    def include(self, *fields):
        self._include.update(fields)

    def exclude(self, *fields):
        self._exclude.update(fields)

    def extends(self, data):
        self._extends.update(data)

    def get_public(self):
        public = {}
        for element in self.public_fields:
            if isinstance(element, str):
                public[element] = self.field_getter(element)
            elif isinstance(element, tuple):
                public[element[0]] = self.field_getter(element[1])
            elif isinstance(element, list):
                public[element[0]] = getattr(self, element[1])()
        return public

    def reset_data(self):
        # WARNING: experimental!
        self._include.clear()
        self._exclude.clear()
        self._extends.clear()

    def to_protocol(self):
        result = self.get_public()
        for field in self._include:
            result.update({field: self.field_getter(field)})
        for field in self._exclude:
            del result[field]
        result.update(self._extends)
        self.reset_data()
        return clean(result)

    @classmethod
    def get_reference(cls):
        if isinstance(cls.reference, (list, tuple)):
            return '.'.join(cls.reference)
        else:
            return cls.__name__


class EntityModel(Entity):
    def to_protocol(self):
        return [self.get_reference(), super(EntityModel, self).to_protocol()]
