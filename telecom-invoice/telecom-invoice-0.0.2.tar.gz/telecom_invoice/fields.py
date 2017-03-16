# coding=utf-8

import md5
from unidecode import unidecode
from decimal import Decimal
from datetime import datetime


class Field(object):

    def __init__(self, position, default=None, blank='\0'):
        if type(position) == int:
            position = (position, position)
        self.position = position
        self.value = default
        self.blank = blank

    @property
    def length(self):
        return (self.position[1] - self.position[0]) + 1

    def serialize(self):
        raise NotImplemented("Remember to override this method")


class IntegerField(Field):

    def __init__(self, position, default=0, blank='0'):
        super(IntegerField, self).__init__(position, default, blank)

    def serialize(self):
        serialized = str(self.value)
        serialized = serialized.zfill(self.length)
        if len(serialized) != self.length:
            raise ValueError("Can't serialize %s. Tried '%s', but lengths don't match "
                             "(%s and %s)" % (self.value, serialized, len(serialized), self.length))

        return serialized[:self.length]


class DecimalField(Field):
    def __init__(self, position, default=Decimal("0.00"), blank='0', precision=2):
        super(DecimalField, self).__init__(position, default, blank)
        self.precision = precision

    def serialize(self):
        if not isinstance(self.value, Decimal):
            raise TypeError("You should use protection")
        value = self.value.quantize(Decimal((0, (1, ), -self.precision)))
        if value != self.value:
            raise TypeError("You got some cowboys here pal")

        serialized = str(value * Decimal((0, (1, ), self.precision)))
        serialized = serialized.zfill(self.length)
        if len(serialized) != self.length:
            raise ValueError("Can't serialize %s. Tried '%s', but lengths don't match "
                             "(%s and %s)" % (self.value, serialized, len(serialized), self.length))

        return serialized[:self.length]


class CharField(Field):
    def __init__(self, position, default="", blank=' '):
        super(CharField, self).__init__(position, default, blank)

    def serialize(self):
        serialized = self.value.strip()
        serialized = serialized.ljust(self.length, self.blank)
        if len(serialized) != self.length:
            raise ValueError("Can't serialize %s. Tried '%s', but lengths don't match "
                             "(%s and %s)" % (self.value, serialized, len(serialized), self.length))

        return serialized[:self.length]


class DateField(Field):
    def __init__(self, position, default=None, blank=' ', date_format="%Y%m%d"):
        super(DateField, self).__init__(position, default, blank)
        self.date_format = date_format

    def serialize(self):
        if not self.value:
            serialized = self.blank.ljust(self.length, self.blank)
        else:
            serialized = self.value.strftime(self.date_format)

        if len(serialized) != self.length:
            raise ValueError("Can't serialize %s. Tried '%s', but lengths don't match "
                             "(%s and %s)" % (self.value, serialized, len(serialized), self.length))

        return serialized[:self.length]


class ChecksumField(Field):

    def __init__(self, position, default, blank='0', fields=None):
        super(ChecksumField, self).__init__(position, default, blank)
        self.fields = fields

    def serialize(self):
        fields = []
        if not self.fields:
            fields = self.value.fields
            fields = [field for field in fields if field != self]
        else:
            fields = [getattr(self.value, field) for field in self.fields]

        hasher = md5.new()
        fields = [field.serialize() for field in fields]
        serialized = u"".join(fields).encode("latin1")
        hasher.update(serialized)
        return hasher.hexdigest()
