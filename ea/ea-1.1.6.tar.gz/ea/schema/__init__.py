from marshmallow import *
try:
    del fields
except NameError:
    pass

from . import fields
from . import validate


class Schema(Schema):
    dto_class = dict

    def load(self, *args, **kwargs):
        params, errors = super(Schema, self)\
            .load(*args, **kwargs)

        if params is None:
            return params, errors

        return (self.dto_class(params), errors)\
            if not self.many\
            else ([self.dto_class(x) for x in params], errors)
