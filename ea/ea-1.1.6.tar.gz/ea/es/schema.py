from ea.schema.fields import Nested


class BaseDomainObjectField(Nested):
    """A :class:`ea.schema.fields.Nested` implementation that
    loads and dumps domain objects.
    """

    def __init__(self, nested, *args, **kwargs):
        self.domain_class = nested
        nested = self.domain_class.__schema__
        super(BaseDomainObjectField, self).__init__(nested, *args, **kwargs)

    def deserialize(self, *args, **kwargs):
        dto = super(BaseDomainObjectField, self).deserialize(*args, **kwargs)
        if not self.many:
            value = self.domain_class()
            value.__setstate__(dto)
        else:
            value = []
            for item in dto:
                obj = self.domain_class()
                obj.__setstate__(item)
                value.append(obj)

        return value


class ValueObjectField(BaseDomainObjectField):
    pass


class EntityField(BaseDomainObjectField):
    pass
