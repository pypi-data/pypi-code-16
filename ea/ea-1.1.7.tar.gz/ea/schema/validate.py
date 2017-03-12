import datetime
import json

from marshmallow.validate import *
from phonenumbers.phonenumberutil import NumberParseException
import marshmallow
import phonenumbers


class Phonenumber(object):

    def __init__(self, country_codes=None):
        self.country_codes = country_codes or []

    def validate_phonenumber(self, value):
        error = False
        try:
            p = phonenumbers.parse(value)
        except NumberParseException:
            raise marshmallow.ValidationError(
                "'%s' is not a phonenumber." % repr(value)) 

        if self.country_codes and not error\
        and p.country_code not in self.country_codes:
            raise marshmallow.ValidationError(
                "Phonenumbers from %s are not accepted." % p.country_code)

        if error or not phonenumbers.is_valid_number(p):
            raise marshmallow.ValidationError(
                "%s is not a valid phonenumber" % value, 'value')

    def __call__(self, value):
        return self.validate_phonenumber(value)


class IsJson:

    def __init__(self, max_size=2048, type=dict):
        self.max_size = max_size
        self.type = type

    def __call__(self, value):
        value = value or ''
        if len(value) > self.max_size:
            raise marshmallow.ValidationError("Maximum size exceeded.")

        try:
            obj = json.loads(value)
        except ValueError:
            raise marshmallow.ValidationError("Could not be parsed as JSON.")

        if not isinstance(obj, self.type):
            raise marshmallow.ValidationError('Invalid object type: %s' % type(obj).__name__)
