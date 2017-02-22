
import sys

class Field():

    def to_python(self, value):
        return value

class ListField(Field):

    def __init__(self, subfield = Field()):
        self.__subfield = subfield

    def to_python(self, values):
        if values:
            return [self.__subfield.to_python(value) for value in values]
        return None

class BooleanField(Field):

    def to_python(self, value):
        if value:
            value = value.lower()
            if not(value in ["0", "false"]): return True

        return False
            

class StringField(Field): pass

class LongField(Field):

    def to_python(self, value):
        if value:
            if sys.version_info.major > 2:
                return int(value)
            else:
                return long(value)
        return None

class IntField(Field):

    def to_python(self, value):
        if value:
            return int(value)
        return None

class FloatField(Field):

    def to_python(self, value):
        if value:
            return float(value)
        return None


