import datetime


class BaseField(object):
    default = None

    def __init__(self, *args, **kwargs):
        self.values = {}
        self.dynamics = set()

        if "default" in kwargs:
            self.default = kwargs["default"]

        super(BaseField, self).__init__()

    def __get__(self, instance, owner):
        key = self._key_for_instance(instance)

        if key not in self.values:
            return self.default

        set_value = self.values.get(key, None)
        return set_value

    def __set__(self, instance, value):
        key = self._key_for_instance(instance)

        if key not in self.dynamics:
            instance._dynamic_fields.append(self)
            self.dynamics.add(key)

        self.values[key] = value

    def __delete__(self, instance):
        key = self._key_for_instance(instance)

        if key in self.dynamics:
            self.dynamics.remove(key)
        if key in self.values:
            del self.values[key]

    def _key_for_instance(self, instance):
        return id(instance)

    def clean(self, instance):
        pass


class CharField(BaseField):
    has_choices = False

    def __init__(self, *args, **kwargs):
        nullable = False
        if "null" in kwargs and kwargs["null"]:
            nullable = True

        if not nullable:
            self.default = u""

        if "choices" in kwargs:
            self.has_choices = True
            self.choices = kwargs["choices"]

        super(CharField, self).__init__(*args, **kwargs)

    def get_display(self, instance):
        val = self.__get__(instance, None)

        if not self.has_choices:
            raise Exception("No choices on field")

        for opt in self.choices:
            if opt[0] == val:
                return opt[1]


class BooleanField(BaseField):
    pass


class DateField(BaseField):
    def clean(self, instance):
        value = self.__get__(instance, None)

        if isinstance(value, type(datetime.datetime.now())):
            self.__set__(instance, value.date())


class DateTimeField(BaseField):
    pass


class DecimalField(BaseField):
    pass


class FloatField(BaseField):
    pass


class IntegerField(BaseField):
    pass


class NullBooleanField(BaseField):
    pass


class PositiveIntegerField(BaseField):
    pass


class PositiveSmallIntegerField(BaseField):
    pass


class SlugField(BaseField):
    pass


class SmallIntegerField(BaseField):
    pass


class TextField(BaseField):
    pass


class TimeField(BaseField):
    pass


class URLField(BaseField):
    pass


class ForeignKey(BaseField):
    pass
