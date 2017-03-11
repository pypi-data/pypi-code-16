import time

from marshmallow.fields import *
import dsnparse

from ea.schema import validate
import ea.lib.timezone


class TimestampUNIX(Integer):

    def __init__(self, *args, **kwargs):
        self.auto_now = kwargs.pop('auto_now', False)
        if self.auto_now:
            kwargs['default'] = ea.lib.timezone.now
            kwargs['missing'] = ea.lib.timezone.now
            kwargs['required'] = False
        super(TimestampUNIX, self).__init__(*args, **kwargs)


class Phonenumber(String):

    def __init__(self, *args, **kwargs):
        v = kwargs.setdefault('validate', [])
        v.append(validate.Length(max=16))
        v.append(validate.Phonenumber(
            country_codes=kwargs.pop('country_codes', [])
        ))
        super(Phonenumber, self).__init__(*args, **kwargs)


class DSN(String):

    def __init__(self, *args, **kwargs):
        v = kwargs.setdefault('validate', [])
        if 'protocols' in kwargs:
            v.append(validate.OneOf(kwargs.pop('protocols')))
        super(DSN, self).__init__(*args, **kwargs)


class UUID(UUID):

    def _validated(self, value):
        value = super(UUID, self)._validated(value)
        return str(value) if value is not None else value

    def _serialize(self, value, attr, obj):
        value = super(UUID, self)._serialize(value, attr, obj)
        return str(value) if value is not None else value

    def _deserialize(self, value, attr, data):
        value = self._validated(value)
        return str(value) if value is not None else value
