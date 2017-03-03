import re
from restclients_core.models.fields import (BooleanField, CharField, DateField,
                                            DateTimeField, DecimalField,
                                            FloatField, ForeignKey,
                                            IntegerField, NullBooleanField,
                                            PositiveIntegerField,
                                            PositiveSmallIntegerField,
                                            SlugField, SmallIntegerField,
                                            TextField, TimeField, URLField)


class MockHTTP(object):
    """
    An alternate object to HTTPResponse, for non-HTTP DAO
    implementations to use.  Implements the API of HTTPResponse
    as needed.
    """
    status = 0
    data = ""
    headers = {}

    def read(self):
        """
        Returns the document body of the request.
        """
        return self.data

    def getheader(self, field, default=''):
        """
        Returns the HTTP response header field, case insensitively
        """
        if self.headers:
            for header in self.headers:
                if field.lower() == header.lower():
                    return self.headers[header]

        return default


class Model(object):
    _dynamic_fields = []

    def __init__(self, *args, **kwargs):
        self._dynamic_fields = []

        super(Model, self).__init__()

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __getattribute__(self, name):
        # This is in place to catch get_<attribute>_display.  If there's
        # alrady a defined attribute here, just return it.  Otherwise if the
        # attribute name matches our pattern, and we can find that name in our
        # Class's dictionary, we try to let that field type get the right
        # value.  then we return a function that returns the value.
        try:
            base_value = super(Model, self).__getattribute__(name)
            return base_value
        except AttributeError as ex:
            base_value = None
            original_exception = ex

        match = re.match('get_(.*)_display', name)
        if match:
            try:
                field = self.__class__.__dict__[match.group(1)]

                value = field.get_display(self)
                return lambda: value

            except Exception:
                pass

        raise original_exception

    def __del__(self):
        # Fields are stored in a per-object-id dictionary.  Those ids are
        # guaranteed to be unique - but only over the lifetime of the object.
        # This makes sure those values are removed when this object
        # is destroyed.
        for field in self._dynamic_fields:
            field.__delete__(self)

    def clean_fields(self):
        for field in self._dynamic_fields:
            field.clean(self)

        pass

PROTECT = None
